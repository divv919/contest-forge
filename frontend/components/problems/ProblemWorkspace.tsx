"use client"

import { useEffect, useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import { AlertCircle, ArrowLeft, Code2, ListChecks, Loader2, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import StatusPill, { getSubmissionStatusLabel } from "@/components/shared/StatusPill"
import { ApiError } from "@/lib/api/client"
import { fetchProblem } from "@/lib/api/problems"
import { fetchLanguagesMap } from "@/lib/api/languages"
import { fetchProblemSubmissions, submitProblemSubmission } from "@/lib/api/submissions"
import type { ProblemInfo, SubmissionHistoryItem } from "@/lib/types"

const PAGE_SIZE = 20

function guessLanguageLabel(languageId: number, source: string) {
  const lowered = source.toLowerCase()
  if (lowered.includes("#include") || lowered.includes("std::") || lowered.includes("using namespace std")) {
    return `C++ (${languageId})`
  }

  if (lowered.includes("def ") || lowered.includes("import ") || lowered.includes("print(")) {
    return `Python (${languageId})`
  }

  if (lowered.includes("function ") || lowered.includes("console.log") || lowered.includes("=>")) {
    return `JavaScript (${languageId})`
  }

  return `Language ${languageId}`
}

function formatMemory(memory?: number | null) {
  if (memory == null) return "-"
  if (memory >= 1024) return `${(memory / 1024).toFixed(1)} MB`
  return `${memory} KB`
}

function formatTime(totalTime?: string | null) {
  if (!totalTime) return "-"
  const seconds = Number(totalTime)
  if (Number.isFinite(seconds)) {
    return `${seconds.toFixed(3)} s`
  }
  return totalTime
}

function storageKey(slug: string, languageId: number) {
  return `contest-platform:draft:${slug}:${languageId}`
}

export default function ProblemWorkspace({ slug }: { slug: string }) {
  const router = useRouter()
  const [problem, setProblem] = useState<ProblemInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedLanguageId, setSelectedLanguageId] = useState<number | null>(null)
  const [sourcesByLanguage, setSourcesByLanguage] = useState<Record<number, string>>({})
  const [languagesMap, setLanguagesMap] = useState<Record<number, string>>({})
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [history, setHistory] = useState<SubmissionHistoryItem[]>([])
  const [historyPage, setHistoryPage] = useState(1)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function loadProblem() {
      setLoading(true)
      setError(null)
      try {
        const data = await fetchProblem(slug)
        if (!active) return

        const languageIds = Object.keys(data.boilerplate_codes)
          .map((key) => Number(key))
          .filter((value) => Number.isFinite(value))
          .sort((left, right) => left - right)

        const initialSources = languageIds.reduce<Record<number, string>>((accumulator, languageId) => {
          const draft = typeof window !== "undefined" ? window.localStorage.getItem(storageKey(slug, languageId)) : null
          accumulator[languageId] = draft ?? data.boilerplate_codes[languageId] ?? ""
          return accumulator
        }, {})

        setProblem(data)
        setSourcesByLanguage(initialSources)

        const storedLanguage = typeof window !== "undefined" ? window.localStorage.getItem(`contest-platform:selected-language:${slug}`) : null
        const preferredLanguageId = storedLanguage ? Number(storedLanguage) : languageIds[0] ?? null
        const nextLanguageId = preferredLanguageId && languageIds.includes(preferredLanguageId) ? preferredLanguageId : languageIds[0] ?? null
        setSelectedLanguageId(nextLanguageId)
      } catch (requestError) {
        const message = requestError instanceof ApiError ? requestError.message : "Failed to load problem"
        if (active) setError(message)
      } finally {
        if (active) setLoading(false)
      }
    }

    void loadProblem()

    // load language id -> name mapping from backend
    void (async () => {
      try {
        const map = await fetchLanguagesMap()
        if (active) setLanguagesMap(map)
      } catch (err) {
        // ignore mapping errors; fallback to inference
      }
    })()

    return () => {
      active = false
    }
  }, [slug])

  useEffect(() => {
    if (!problem) return
    void loadHistory(problem.id, historyPage)
  }, [problem, historyPage])

  async function loadHistory(problemId: number, page: number) {
    setHistoryLoading(true)
    setHistoryError(null)
    try {
      const submissions = await fetchProblemSubmissions({ problem_id: problemId, current_page: page })
      setHistory(submissions)
    } catch (requestError) {
      setHistoryError(requestError instanceof ApiError ? requestError.message : "Failed to load submissions")
    } finally {
      setHistoryLoading(false)
    }
  }

  const languageOptions = useMemo(() => {
    if (!problem) return []

    return Object.entries(problem.boilerplate_codes)
      .map(([languageId, source]) => {
        const id = Number(languageId)
        const backendLabel = languagesMap[id]
        return {
          id,
          label: backendLabel ?? guessLanguageLabel(id, source),
        }
      })
      .sort((left, right) => left.id - right.id)
  }, [problem, languagesMap])

  const selectedSource = selectedLanguageId == null ? "" : sourcesByLanguage[selectedLanguageId] ?? ""

  async function handleSubmit() {
    if (!problem || selectedLanguageId == null) return

    setSubmitLoading(true)
    setSubmitError(null)
    try {
      // detect active contest id from URL query (e.g. ?contest=123)
      let activeContestId: number | null = null
      try {
        const params = typeof window !== "undefined" ? new URLSearchParams(window.location.search) : null
        const maybe = params?.get("contest") ?? params?.get("active_contest_id")
        if (maybe) {
          const parsed = Number(maybe)
          if (Number.isFinite(parsed)) activeContestId = parsed
        }
      } catch (e) {
        // ignore
      }

      const response = await submitProblemSubmission({
        problem_id: problem.id,
        language_id: selectedLanguageId,
        source_code: selectedSource,
        active_contest_id: activeContestId,
      })
      router.push(`/submissions/${response.submission_id}`)
    } catch (requestError) {
      setSubmitError(requestError instanceof ApiError ? requestError.message : "Failed to submit code")
    } finally {
      setSubmitLoading(false)
    }
  }

  function updateSource(nextSource: string) {
    if (selectedLanguageId == null) return

    setSourcesByLanguage((current) => {
      const next = { ...current, [selectedLanguageId]: nextSource }
      if (typeof window !== "undefined") {
        window.localStorage.setItem(storageKey(slug, selectedLanguageId), nextSource)
      }
      return next
    })
  }

  function selectLanguage(languageId: number) {
    setSelectedLanguageId(languageId)
    if (typeof window !== "undefined") {
      window.localStorage.setItem(`contest-platform:selected-language:${slug}`, String(languageId))
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center rounded-3xl border border-dashed border-border bg-card/80 p-8 text-muted-foreground">
        <Loader2 className="mr-2 size-4 animate-spin" /> Loading problem workspace
      </div>
    )
  }

  if (error || !problem) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <AlertCircle className="size-4 text-rose-600" /> Problem unavailable
          </CardTitle>
          <CardDescription>{error ?? "No problem was returned by the backend."}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline" onClick={() => router.push("/")}> 
            <ArrowLeft className="size-4" /> Back home
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <section className="space-y-4 rounded-[2rem] border border-border bg-gradient-to-br from-card via-card to-muted/40 p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
              <button className="inline-flex items-center gap-1 text-foreground/70 transition hover:text-foreground" onClick={() => router.push("/")}>
                <ArrowLeft className="size-3.5" /> Home
              </button>
              <span>•</span>
              <span>{problem.slug}</span>
              <StatusPill status={problem.difficulty} className="uppercase tracking-wide" />
            </div>
            <h1 className="text-3xl font-semibold tracking-tight">{problem.name}</h1>
            <p className="max-w-3xl text-sm leading-6 text-muted-foreground">{problem.description}</p>
          </div>

          <Button onClick={handleSubmit} disabled={submitLoading || selectedLanguageId == null} className="min-w-36">
            {submitLoading ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}
            Submit
          </Button>
        </div>

        <div className="grid gap-3 md:grid-cols-3">
          <Card size="sm" className="bg-background/70">
            <CardHeader>
              <CardDescription>Problem</CardDescription>
              <CardTitle className="text-xl">{problem.name}</CardTitle>
            </CardHeader>
          </Card>
          <Card size="sm" className="bg-background/70">
            <CardHeader>
              <CardDescription>Difficulty</CardDescription>
              <CardTitle className="text-xl">{problem.difficulty}</CardTitle>
            </CardHeader>
          </Card>
          <Card size="sm" className="bg-background/70">
            <CardHeader>
              <CardDescription>Languages</CardDescription>
              <CardTitle className="text-xl">{languageOptions.length}</CardTitle>
            </CardHeader>
          </Card>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
        <Card className="min-h-[36rem]">
          <CardHeader className="border-b">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Code2 className="size-4" /> Editor
            </CardTitle>
            <CardDescription>Drafts are stored per problem and language in your browser.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 pt-4">
            <div className="flex flex-wrap gap-2">
              {languageOptions.map((language) => (
                <Button
                  key={language.id}
                  variant={selectedLanguageId === language.id ? "default" : "outline"}
                  size="sm"
                  onClick={() => selectLanguage(language.id)}
                >
                  {language.label}
                </Button>
              ))}
            </div>

            <textarea
              value={selectedSource}
              onChange={(event) => updateSource(event.target.value)}
              className="min-h-[28rem] w-full rounded-2xl border border-border bg-background p-4 font-mono text-sm leading-6 outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20"
              spellCheck={false}
            />

            {submitError ? <p className="text-sm text-rose-600">{submitError}</p> : null}
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader className="border-b">
              <CardTitle className="flex items-center gap-2 text-lg">
                <ListChecks className="size-4" /> Problem Statement
              </CardTitle>
              <CardDescription>Backend metadata rendered exactly as returned.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              <div>
                <h3 className="mb-2 text-sm font-medium">Metadata</h3>
                <pre className="whitespace-pre-wrap rounded-2xl border border-border bg-muted/50 p-4 text-xs leading-6 text-muted-foreground">{problem.problem_metadata}</pre>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="border-b">
              <CardTitle className="text-lg">Recent submissions</CardTitle>
              <CardDescription>History is paginated in 20-row slices, matching the backend.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              {historyLoading ? (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="size-4 animate-spin" /> Loading submissions
                </div>
              ) : historyError ? (
                <p className="text-sm text-rose-600">{historyError}</p>
              ) : history.length === 0 ? (
                <p className="text-sm text-muted-foreground">No submissions found for this problem yet.</p>
              ) : (
                <div className="space-y-3">
                  {history.map((submission) => (
                    <button
                      key={submission.id ?? `${submission.status}-${submission.language}`}
                      type="button"
                      className="flex w-full items-center justify-between rounded-xl border border-border bg-background px-3 py-3 text-left transition hover:border-ring/60 hover:bg-muted/40"
                      onClick={() => {
                        if (submission.id != null) router.push(`/submissions/${submission.id}`)
                      }}
                    >
                      <div className="space-y-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <StatusPill status={submission.status} />
                          <span className="text-sm font-medium">{submission.language}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">{formatStatus(submission.status)}</p>
                      </div>
                      <div className="text-right text-xs text-muted-foreground">
                        <div>Memory {formatMemory(submission.max_memory)}</div>
                        <div>Time {formatTime(submission.total_time)}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between gap-2 pt-2">
                <Button variant="outline" size="sm" disabled={historyPage === 1 || historyLoading} onClick={() => setHistoryPage((page) => Math.max(1, page - 1))}>
                  Previous
                </Button>
                <span className="text-xs text-muted-foreground">Page {historyPage}</span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={historyLoading || history.length < PAGE_SIZE}
                  onClick={() => setHistoryPage((page) => page + 1)}
                >
                  Next
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}