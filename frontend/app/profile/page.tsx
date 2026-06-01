"use client"

import { useEffect, useMemo, useState } from "react"
import { useRouter } from "next/navigation"

import Protected from "@/components/auth/Protected"
import ErrorFallback from "@/components/shared/ErrorFallback"
import Loading from "@/components/shared/Loading"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { clearToken } from "@/lib/auth/session"
import {
  dedupeContests,
  getAllProblems,
  getCurrentUser,
  getOngoingContests,
  getPastContests,
  getUpcomingContests,
  getUserSubmissions,
} from "@/lib/api/profile"
import type {
  ContestListItem,
  ContestSubmissionRecord,
  CurrentUser,
  ProblemListItem,
  ProblemSubmissionRecord,
  SubmissionStatusId,
  Submission,
} from "@/lib/types"

type ProfileBundle = {
  user: CurrentUser
  problems: ProblemListItem[]
  contests: ContestListItem[]
  problemSubmissions: Array<{ problem: ProblemListItem; submissions: ProblemSubmissionRecord[] }>
  contestSubmissions: Array<{ contest: ContestListItem; submissions: ContestSubmissionRecord[] }>
}

type TabKey = "submissions" | "contests"

const STATUS_META: Record<SubmissionStatusId, { label: string; className: string }> = {
  1: { label: "In queue", className: "bg-muted text-foreground" },
  2: { label: "Processing", className: "bg-muted text-foreground" },
  3: { label: "Accepted", className: "bg-emerald-100 text-emerald-900" },
  4: { label: "Wrong answer", className: "bg-rose-100 text-rose-900" },
  5: { label: "Time limit", className: "bg-amber-100 text-amber-900" },
  6: { label: "Compile error", className: "bg-slate-200 text-slate-900" },
  7: { label: "Segfault", className: "bg-rose-100 text-rose-900" },
  8: { label: "File limit", className: "bg-rose-100 text-rose-900" },
  9: { label: "Floating point", className: "bg-rose-100 text-rose-900" },
  10: { label: "Abort", className: "bg-rose-100 text-rose-900" },
  11: { label: "NZEC", className: "bg-rose-100 text-rose-900" },
  12: { label: "Runtime error", className: "bg-rose-100 text-rose-900" },
  13: { label: "Internal error", className: "bg-rose-100 text-rose-900" },
  14: { label: "Format error", className: "bg-rose-100 text-rose-900" },
}

function formatDate(value: string | number | Date) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value))
}

function formatTime(value: string | null) {
  if (!value) return "-"
  const parsed = Number(value)
  if (Number.isFinite(parsed)) {
    return `${parsed.toFixed(parsed < 10 ? 2 : 0)}s`
  }
  return value
}

function statusBadge(status: SubmissionStatusId) {
  return STATUS_META[status] ?? { label: `Status ${status}`, className: "bg-muted text-foreground" }
}

function countSolvedProblems(problemSubmissions: Array<{ submissions: ProblemSubmissionRecord[] }>) {
  return problemSubmissions.filter(({ submissions }) => submissions.some((submission) => submission.status === 3)).length
}

function buildContestRollup(entries: Array<{ contest: ContestListItem; submissions: ContestSubmissionRecord[] }>) {
  return entries
    .map(({ contest, submissions }) => {
      const sortedSubmissions = [...submissions].sort(
        (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime()
      )

      return {
        contest,
        submissions: sortedSubmissions,
        totalSubmissions: submissions.length,
        acceptedSubmissions: submissions.filter((submission) => submission.status === 3).length,
        points: submissions.reduce((total, submission) => total + (submission.points || 0), 0),
        latestSubmission: sortedSubmissions[0] ?? null,
      }
    })
    .sort((left, right) => {
      const rightTime = right.latestSubmission ? new Date(right.latestSubmission.created_at).getTime() : 0
      const leftTime = left.latestSubmission ? new Date(left.latestSubmission.created_at).getTime() : 0
      return rightTime - leftTime
    })
}

function buildProblemRows(entries: Array<{ problem: ProblemListItem; submissions: ProblemSubmissionRecord[] }>) {
  return entries
    .flatMap(({ problem, submissions }) =>
      submissions.map((submission) => ({
        problem,
        submission,
      }))
    )
    .sort((left, right) => (right.submission.id ?? 0) - (left.submission.id ?? 0))
}

async function loadProfileBundle(page = 1): Promise<ProfileBundle> {
  const user = await getCurrentUser()
  const [problems, upcoming, ongoing, past] = await Promise.all([
    getAllProblems(),
    getUpcomingContests(),
    getOngoingContests(),
    getPastContests(),
  ])

  const contests = dedupeContests([...upcoming, ...ongoing, ...past])
  // Fetch user's recent submissions in a single paginated request to avoid N+1 fan-out
  const userSubmissions = await getUserSubmissions(page)

  // Group submissions by problem
  const problemMap = new Map<number, { problem: ProblemListItem; submissions: ProblemSubmissionRecord[] }>()
  for (const sub of userSubmissions) {
    if (!sub.problem_id) continue
    const pid = sub.problem_id
    const problem = problems.find((p) => p.id === pid)
    if (!problem) continue
    const existing = problemMap.get(pid)
    const record: ProblemSubmissionRecord = {
      id: sub.id ?? null,
      status: sub.status,
      language: sub.language,
      max_memory: sub.max_memory ?? null,
      total_time: sub.total_time ?? null,
    }
    if (existing) existing.submissions.push(record)
    else problemMap.set(pid, { problem, submissions: [record] })
  }

  // Group submissions by contest (using contest id)
  const contestMap = new Map<number, { contest: ContestListItem; submissions: ContestSubmissionRecord[] }>()
  for (const sub of userSubmissions) {
    if (!sub.active_contest_id) continue
    const cid = sub.active_contest_id
    const contest = contests.find((c) => c.id === cid)
    if (!contest) continue
    const existing = contestMap.get(cid)
    const record: ContestSubmissionRecord = {
      id: sub.id ?? 0,
      problem_id: sub.problem_id ?? 0,
      active_contest_id: sub.active_contest_id ?? 0,
      language_id: 0,
      status: sub.status,
      total_testcases: null,
      total_passed_cases: null,
      max_memory: sub.max_memory ?? null,
      total_time: sub.total_time ?? null,
      created_at: sub.created_at ?? new Date().toISOString(),
      points: 0,
    }
    if (existing) existing.submissions.push(record)
    else contestMap.set(cid, { contest, submissions: [record] })
  }

  return {
    user,
    problems,
    contests,
    problemSubmissions: Array.from(problemMap.values()),
    contestSubmissions: Array.from(contestMap.values()),
  }
}

export default function ProfilePage() {
  const router = useRouter()
  const [bundle, setBundle] = useState<ProfileBundle | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<TabKey>("submissions")
  const [refreshTick, setRefreshTick] = useState(0)
  const [submissionsPage, setSubmissionsPage] = useState(1)

  useEffect(() => {
    let active = true

    async function run() {
      setLoading(true)
      setError(null)

      try {
        const loadedBundle = await loadProfileBundle(submissionsPage)
        if (!active) return
        setBundle(loadedBundle)
      } catch (requestError: any) {
        if (!active) return

        if (requestError?.status === 401) {
          clearToken()
          router.replace("/login")
          return
        }

        setError(requestError?.message || "Failed to load profile data")
      } finally {
        if (active) setLoading(false)
      }
    }

    void run()

    return () => {
      active = false
    }
  }, [refreshTick, router, submissionsPage])

  const problemRows = useMemo(() => {
    if (!bundle) return []
    return buildProblemRows(bundle.problemSubmissions)
  }, [bundle])

  const contestRows = useMemo(() => {
    if (!bundle) return []
    return buildContestRollup(bundle.contestSubmissions)
  }, [bundle])

  const totalProblemSubmissions = problemRows.length
  const acceptedProblemSubmissions = problemRows.filter(({ submission }) => submission.status === 3).length
  const solvedProblems = bundle ? countSolvedProblems(bundle.problemSubmissions) : 0
  const totalContestSubmissions = contestRows.reduce((total, row) => total + row.totalSubmissions, 0)
  const acceptedContestSubmissions = contestRows.reduce((total, row) => total + row.acceptedSubmissions, 0)
  const totalContestPoints = contestRows.reduce((total, row) => total + row.points, 0)

  return (
    <Protected>
      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorFallback error={new Error(error)} />
      ) : bundle ? (
        <div className="space-y-8">
          <section className="overflow-hidden rounded-3xl border border-foreground/10 bg-[radial-gradient(circle_at_top_left,_rgba(0,0,0,0.08),_transparent_42%),linear-gradient(180deg,_rgba(255,255,255,0.96),_rgba(244,244,245,0.88))] p-6 shadow-sm dark:bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.08),_transparent_42%),linear-gradient(180deg,_rgba(24,24,27,0.96),_rgba(9,9,11,0.96))]">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="space-y-3">
                <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">Profile</p>
                <h1 className="text-3xl font-semibold tracking-tight text-balance">{bundle.user.username}</h1>
                <p className="max-w-2xl text-sm text-muted-foreground">
                  A read-only snapshot of your account, submissions, and contest participation pulled from the actual backend history endpoints.
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Button variant="outline" onClick={() => setRefreshTick((value) => value + 1)}>
                  Refresh history
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => {
                    clearToken()
                    router.replace("/login")
                  }}
                >
                  Sign out
                </Button>
              </div>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <Card>
                <CardHeader>
                  <CardDescription>Problems solved</CardDescription>
                  <CardTitle>{solvedProblems}</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">Out of {bundle.problems.length} accessible problems</CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardDescription>Recent problem submissions</CardDescription>
                  <CardTitle>{totalProblemSubmissions}</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">{acceptedProblemSubmissions} accepted submissions in the fetched history</CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardDescription>Contest submissions</CardDescription>
                  <CardTitle>{totalContestSubmissions}</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">{acceptedContestSubmissions} accepted entries across {contestRows.length} contest snapshots</CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardDescription>Contest points</CardDescription>
                  <CardTitle>{totalContestPoints}</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground">Points are rolled up from the backend contest submissions feed</CardContent>
              </Card>
            </div>
          </section>

          <section className="grid gap-4 xl:grid-cols-[1.7fr_1fr]">
            <Card>
              <CardHeader>
                <CardDescription>Activity</CardDescription>
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <CardTitle>Submission and contest history</CardTitle>
                  <div className="inline-flex rounded-full border border-foreground/10 bg-muted p-1">
                    <button
                      type="button"
                      onClick={() => setActiveTab("submissions")}
                      className={`rounded-full px-3 py-1.5 text-sm transition ${
                        activeTab === "submissions" ? "bg-background shadow-sm" : "text-muted-foreground"
                      }`}
                    >
                      Problem submissions
                    </button>
                    <button
                      type="button"
                      onClick={() => setActiveTab("contests")}
                      className={`rounded-full px-3 py-1.5 text-sm transition ${
                        activeTab === "contests" ? "bg-background shadow-sm" : "text-muted-foreground"
                      }`}
                    >
                      Contests
                    </button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {activeTab === "submissions" ? (
                  <div className="overflow-hidden rounded-2xl border border-foreground/10">
                    <table className="w-full border-collapse text-sm">
                      <thead className="bg-muted/70 text-left text-xs uppercase tracking-[0.2em] text-muted-foreground">
                        <tr>
                          <th className="px-4 py-3 font-medium">Problem</th>
                          <th className="px-4 py-3 font-medium">Submission</th>
                          <th className="px-4 py-3 font-medium">Status</th>
                          <th className="px-4 py-3 font-medium">Language</th>
                          <th className="px-4 py-3 font-medium">Time</th>
                          <th className="px-4 py-3 font-medium">Memory</th>
                        </tr>
                      </thead>
                      <tbody>
                        {problemRows.slice(0, 12).map(({ problem, submission }) => {
                          const meta = statusBadge(submission.status)

                          return (
                            <tr key={`${problem.id}-${submission.id ?? "latest"}`} className="border-t border-foreground/5">
                              <td className="px-4 py-3">
                                <div className="font-medium">{problem.name}</div>
                                <div className="text-xs text-muted-foreground">{problem.slug}</div>
                              </td>
                              <td className="px-4 py-3">{submission.id ?? "-"}</td>
                              <td className="px-4 py-3">
                                <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${meta.className}`}>{meta.label}</span>
                              </td>
                              <td className="px-4 py-3">{submission.language}</td>
                              <td className="px-4 py-3">{formatTime(submission.total_time)}</td>
                              <td className="px-4 py-3">{submission.max_memory ?? "-"}</td>
                            </tr>
                          )
                        })}
                        {problemRows.length === 0 ? (
                          <tr>
                            <td colSpan={6} className="px-4 py-10 text-center text-sm text-muted-foreground">
                              No problem submissions were returned by the backend yet.
                            </td>
                          </tr>
                        ) : null}
                      </tbody>
                    </table>
                    <div className="flex items-center justify-end gap-2 px-4 py-3">
                      <Button
                        variant="ghost"
                        onClick={() => setSubmissionsPage((p) => Math.max(1, p - 1))}
                        disabled={submissionsPage === 1}
                      >
                        Previous
                      </Button>
                      <div className="text-sm text-muted-foreground">Page {submissionsPage}</div>
                      <Button variant="ghost" onClick={() => setSubmissionsPage((p) => p + 1)}>
                        Next
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="overflow-hidden rounded-2xl border border-foreground/10">
                    <table className="w-full border-collapse text-sm">
                      <thead className="bg-muted/70 text-left text-xs uppercase tracking-[0.2em] text-muted-foreground">
                        <tr>
                          <th className="px-4 py-3 font-medium">Contest</th>
                          <th className="px-4 py-3 font-medium">Submissions</th>
                          <th className="px-4 py-3 font-medium">Accepted</th>
                          <th className="px-4 py-3 font-medium">Points</th>
                          <th className="px-4 py-3 font-medium">Latest activity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {contestRows.slice(0, 12).map((row) => (
                          <tr key={row.contest.slug} className="border-t border-foreground/5">
                            <td className="px-4 py-3">
                              <div className="font-medium">{row.contest.name}</div>
                              <div className="text-xs text-muted-foreground">{row.contest.slug}</div>
                            </td>
                            <td className="px-4 py-3">{row.totalSubmissions}</td>
                            <td className="px-4 py-3">{row.acceptedSubmissions}</td>
                            <td className="px-4 py-3">{row.points}</td>
                            <td className="px-4 py-3">{row.latestSubmission ? formatDate(row.latestSubmission.created_at) : "-"}</td>
                          </tr>
                        ))}
                        {contestRows.length === 0 ? (
                          <tr>
                            <td colSpan={5} className="px-4 py-10 text-center text-sm text-muted-foreground">
                              No contest submissions were returned by the backend yet.
                            </td>
                          </tr>
                        ) : null}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardDescription>Account</CardDescription>
                <CardTitle>Identity snapshot</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-sm">
                <div className="rounded-2xl border border-foreground/10 bg-muted/40 p-4">
                  <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Username</div>
                  <div className="mt-1 font-medium">{bundle.user.username}</div>
                </div>
                <div className="rounded-2xl border border-foreground/10 bg-muted/40 p-4">
                  <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Provider</div>
                  <div className="mt-1 font-medium">{bundle.user.provider}</div>
                </div>
                <div className="rounded-2xl border border-foreground/10 bg-muted/40 p-4">
                  <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Provider user id</div>
                  <div className="mt-1 break-all font-medium">{bundle.user.provider_user_id}</div>
                </div>
                <div className="rounded-2xl border border-foreground/10 bg-muted/40 p-4">
                  <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Email</div>
                  <div className="mt-1 break-all font-medium">{bundle.user.email || "Not provided"}</div>
                </div>
                <div className="rounded-2xl border border-foreground/10 bg-muted/40 p-4 text-muted-foreground">
                  This page stays read-only and uses only the current backend profile and history endpoints.
                </div>
              </CardContent>
            </Card>
          </section>
        </div>
      ) : null}
    </Protected>
  )
}
