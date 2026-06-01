"use client"

import { useEffect, useMemo, useState, type FormEvent } from "react"
import { useRouter } from "next/navigation"

import Protected from "@/components/auth/Protected"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { createContest } from "@/lib/api/contests"
import { fetchProblems } from "@/lib/api/problems"
import { getToken } from "@/lib/auth/session"
import type { ContestCreatePayload, ProblemOption } from "@/lib/types"

type FormState = {
  name: string
  startTime: string
  endTime: string
}

type SuccessState = {
  id: number
  name: string
  slug: string
  message: string
}

function getErrorMessage(error: unknown, fallback: string) {
  if (typeof error === "object" && error !== null && "message" in error) {
    const message = (error as { message?: unknown }).message
    if (typeof message === "string" && message.trim()) {
      return message
    }
  }

  return fallback
}

function pad(value: number) {
  return value.toString().padStart(2, "0")
}

function toLocalDateTimeInputValue(date: Date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function formatDateTime(value: string) {
  const date = new Date(value)
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date)
}

function getValidationErrors(form: FormState, selectedProblemIds: number[]) {
  const errors: string[] = []

  if (!form.name.trim()) {
    errors.push("Contest name is required.")
  }

  if (!form.startTime) {
    errors.push("Start time is required.")
  }

  if (!form.endTime) {
    errors.push("End time is required.")
  }

  if (form.startTime && form.endTime) {
    const start = new Date(form.startTime)
    const end = new Date(form.endTime)
    const now = new Date()

    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
      errors.push("Contest times must be valid date values.")
    } else {
      if (start <= now || end <= now) {
        errors.push("Please make sure start time and end time of contest both lie in future")
      }

      if (end <= start) {
        errors.push("End time should be greater than start time")
      }

      if (end.getTime() - start.getTime() < 30 * 60 * 1000) {
        errors.push("Please make sure the duration of the contest is atleast 30 minutes")
      }
    }
  }

  if (selectedProblemIds.length === 0) {
    errors.push("Select at least one problem.")
  }

  return errors
}

function difficultyStyle(difficulty?: string) {
  switch (difficulty?.toUpperCase()) {
    case "EASY":
      return "border-emerald-500/30 bg-emerald-500/10 text-emerald-700"
    case "MEDIUM":
      return "border-amber-500/30 bg-amber-500/10 text-amber-700"
    case "HARD":
      return "border-rose-500/30 bg-rose-500/10 text-rose-700"
    default:
      return "border-border bg-muted text-muted-foreground"
  }
}

function CreateContestContent() {
  const router = useRouter()
  const [form, setForm] = useState<FormState>(() => {
    const now = new Date()
    const start = new Date(now.getTime() + 24 * 60 * 60 * 1000)
    const end = new Date(start.getTime() + 90 * 60 * 1000)

    return {
      name: "",
      startTime: toLocalDateTimeInputValue(start),
      endTime: toLocalDateTimeInputValue(end),
    }
  })
  const [problems, setProblems] = useState<ProblemOption[]>([])
  const [selectedProblemIds, setSelectedProblemIds] = useState<number[]>([])
  const [loadingProblems, setLoadingProblems] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<SuccessState | null>(null)

  useEffect(() => {
    let ignore = false

    async function loadProblems() {
      if (!getToken()) {
        return
      }

      setLoadingProblems(true)
      setError(null)

      try {
        const response = await fetchProblems()
        if (!ignore) {
          setProblems(response)
        }
      } catch (fetchError: unknown) {
        if (!ignore) {
          setError(getErrorMessage(fetchError, "Failed to load problems"))
        }
      } finally {
        if (!ignore) {
          setLoadingProblems(false)
        }
      }
    }

    void loadProblems()

    return () => {
      ignore = true
    }
  }, [])

  const filteredProblems = useMemo(() => {
    const query = searchTerm.trim().toLowerCase()

    if (!query) {
      return problems
    }

    return problems.filter((problem) => {
      return [problem.name, problem.slug, problem.difficulty]
        .filter(Boolean)
        .some((value) => value?.toLowerCase().includes(query))
    })
  }, [problems, searchTerm])

  const validationErrors = useMemo(() => getValidationErrors(form, selectedProblemIds), [form, selectedProblemIds])
  const durationMinutes = useMemo(() => {
    if (!form.startTime || !form.endTime) {
      return 0
    }

    const start = new Date(form.startTime)
    const end = new Date(form.endTime)

    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
      return 0
    }

    return Math.max(0, Math.round((end.getTime() - start.getTime()) / 60000))
  }, [form.endTime, form.startTime])

  const selectedProblems = useMemo(() => {
    const selected = new Set(selectedProblemIds)
    return problems.filter((problem) => selected.has(problem.id))
  }, [problems, selectedProblemIds])

  function toggleProblem(problemId: number) {
    setSelectedProblemIds((current) => {
      if (current.includes(problemId)) {
        return current.filter((id) => id !== problemId)
      }

      return [...current, problemId]
    })
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSuccess(null)

    const errors = validationErrors
    if (errors.length > 0) {
      setError(errors[0])
      return
    }

    setSubmitting(true)

    try {
      const payload: ContestCreatePayload = {
        name: form.name.trim(),
        startTime: new Date(form.startTime).toISOString(),
        endTime: new Date(form.endTime).toISOString(),
        problem_ids: selectedProblemIds,
      }

      const response = await createContest(payload)
      setSuccess(response)
      setForm((current) => ({ ...current, name: "" }))
      setSelectedProblemIds([])
    } catch (createError: unknown) {
      setError(getErrorMessage(createError, "Contest creation failed"))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
      <Card>
        <CardHeader>
          <CardTitle>Create contest</CardTitle>
          <CardDescription>
            Set the contest window, choose problems, and let the backend enforce the creation rules.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground" htmlFor="contest-name">
                Contest name
              </label>
              <input
                id="contest-name"
                value={form.name}
                onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                placeholder="November Sprint Round"
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20"
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground" htmlFor="contest-start">
                  Start time
                </label>
                <input
                  id="contest-start"
                  type="datetime-local"
                  value={form.startTime}
                  onChange={(event) => setForm((current) => ({ ...current, startTime: event.target.value }))}
                  className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground" htmlFor="contest-end">
                  End time
                </label>
                <input
                  id="contest-end"
                  type="datetime-local"
                  value={form.endTime}
                  onChange={(event) => setForm((current) => ({ ...current, endTime: event.target.value }))}
                  className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20"
                />
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p className="text-sm font-medium text-foreground">Problem selection</p>
                  <p className="text-sm text-muted-foreground">Search and choose the problems this contest should include.</p>
                </div>
                <div className="w-full sm:max-w-xs">
                  <input
                    value={searchTerm}
                    onChange={(event) => setSearchTerm(event.target.value)}
                    placeholder="Filter by name, slug, or difficulty"
                    className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20"
                  />
                </div>
              </div>

              <div className="rounded-xl border border-border bg-muted/30 p-3">
                {loadingProblems ? (
                  <div className="space-y-2 text-sm text-muted-foreground">Loading problems...</div>
                ) : filteredProblems.length === 0 ? (
                  <div className="text-sm text-muted-foreground">No problems match your filter.</div>
                ) : (
                  <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                    {filteredProblems.map((problem) => {
                      const checked = selectedProblemIds.includes(problem.id)

                      return (
                        <label
                          key={problem.id}
                          className={`flex cursor-pointer flex-col gap-3 rounded-xl border p-3 transition ${checked ? "border-primary bg-primary/5 ring-1 ring-primary/20" : "border-border bg-background hover:border-foreground/20"}`}
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div>
                              <div className="text-sm font-medium text-foreground">{problem.name}</div>
                              <div className="text-xs text-muted-foreground">{problem.slug}</div>
                            </div>
                            <span className={`rounded-full border px-2 py-1 text-[11px] font-medium uppercase tracking-wide ${difficultyStyle(problem.difficulty)}`}>
                              {problem.difficulty || "UNKNOWN"}
                            </span>
                          </div>

                          <div className="flex items-center justify-between gap-3">
                            <span className="text-xs text-muted-foreground">Problem #{problem.id}</span>
                            <input
                              type="checkbox"
                              checked={checked}
                              onChange={() => toggleProblem(problem.id)}
                              className="size-4 accent-foreground"
                            />
                          </div>
                        </label>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>

            {error ? (
              <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </div>
            ) : null}

            {validationErrors.length > 0 ? (
              <div className="rounded-lg border border-amber-500/20 bg-amber-500/10 px-3 py-3 text-sm text-amber-900">
                <p className="font-medium">Validation summary</p>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-amber-900/90">
                  {validationErrors.map((validationError) => (
                    <li key={validationError}>{validationError}</li>
                  ))}
                </ul>
              </div>
            ) : null}

            <div className="flex flex-wrap items-center gap-3">
              <Button type="submit" disabled={submitting || loadingProblems}>
                {submitting ? "Creating contest..." : "Create contest"}
              </Button>
              <Button type="button" variant="outline" onClick={() => router.back()}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Preview</CardTitle>
            <CardDescription>Live summary of the contest you are building.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1">
              <div className="text-xs uppercase tracking-wide text-muted-foreground">Name</div>
              <div className="text-sm font-medium text-foreground">{form.name.trim() || "Untitled contest"}</div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
              <div className="rounded-lg border border-border bg-muted/40 p-3">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Starts</div>
                <div className="mt-1 text-sm font-medium text-foreground">{form.startTime ? formatDateTime(form.startTime) : "Not set"}</div>
              </div>
              <div className="rounded-lg border border-border bg-muted/40 p-3">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Ends</div>
                <div className="mt-1 text-sm font-medium text-foreground">{form.endTime ? formatDateTime(form.endTime) : "Not set"}</div>
              </div>
              <div className="rounded-lg border border-border bg-muted/40 p-3">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Duration</div>
                <div className="mt-1 text-sm font-medium text-foreground">{durationMinutes} minutes</div>
              </div>
              <div className="rounded-lg border border-border bg-muted/40 p-3">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Problems</div>
                <div className="mt-1 text-sm font-medium text-foreground">{selectedProblemIds.length} selected</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Selected problems</CardTitle>
            <CardDescription>The backend will reject the contest if this list is empty or the ids are invalid.</CardDescription>
          </CardHeader>
          <CardContent>
            {selectedProblems.length === 0 ? (
              <div className="text-sm text-muted-foreground">No problems selected yet.</div>
            ) : (
              <ul className="space-y-2">
                {selectedProblems.map((problem) => (
                  <li key={problem.id} className="flex items-center justify-between gap-3 rounded-lg border border-border bg-background px-3 py-2 text-sm">
                    <div>
                      <div className="font-medium text-foreground">{problem.name}</div>
                      <div className="text-xs text-muted-foreground">{problem.slug}</div>
                    </div>
                    <span className={`rounded-full border px-2 py-1 text-[11px] font-medium uppercase tracking-wide ${difficultyStyle(problem.difficulty)}`}>
                      {problem.difficulty || "UNKNOWN"}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {success ? (
          <Card>
            <CardHeader>
              <CardTitle>Contest created</CardTitle>
              <CardDescription>{success.message}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div>
                <span className="font-medium text-foreground">Contest id:</span> {success.id}
              </div>
              <div>
                <span className="font-medium text-foreground">Slug:</span> {success.slug}
              </div>
            </CardContent>
              <CardFooter className="flex flex-wrap gap-2">
                <Button type="button" onClick={() => router.push(`/contests/${success.slug}`)}>
                  View contest
                </Button>
                <Button type="button" variant="outline" onClick={() => router.push(`/contests`)}>
                  Go to contests
                </Button>
                <Button type="button" variant="ghost" onClick={() => {
                  setSuccess(null)
                  router.refresh()
                }}>
                  Create another
                </Button>
              </CardFooter>
          </Card>
        ) : null}
      </div>
    </div>
  )
}

export default function CreateContestPage() {
  return (
    <Protected>
      <CreateContestContent />
    </Protected>
  )
}