"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { AlertCircle, ArrowLeft, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import StatusPill from "@/components/shared/StatusPill"
import { ApiError } from "@/lib/api/client"
import { fetchSubmissionInfo, fetchSubmissionStatus } from "@/lib/api/submissions"
import type { SubmissionInfo, SubmissionStatusResponse } from "@/lib/types"

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

function renderPayload(payload?: SubmissionInfo | SubmissionStatusResponse | null) {
  if (!payload) return null

  return (
    <dl className="grid gap-4 sm:grid-cols-2">
      <div className="rounded-2xl border border-border bg-background p-4">
        <dt className="text-xs uppercase tracking-wide text-muted-foreground">Passed cases</dt>
        <dd className="mt-2 text-2xl font-semibold">{payload.total_passed_cases ?? 0}</dd>
      </div>
      <div className="rounded-2xl border border-border bg-background p-4">
        <dt className="text-xs uppercase tracking-wide text-muted-foreground">Total cases</dt>
        <dd className="mt-2 text-2xl font-semibold">{payload.total_testcases ?? 0}</dd>
      </div>
      <div className="rounded-2xl border border-border bg-background p-4">
        <dt className="text-xs uppercase tracking-wide text-muted-foreground">Memory</dt>
        <dd className="mt-2 text-2xl font-semibold">{formatMemory(payload.max_memory)}</dd>
      </div>
      <div className="rounded-2xl border border-border bg-background p-4">
        <dt className="text-xs uppercase tracking-wide text-muted-foreground">Time</dt>
        <dd className="mt-2 text-2xl font-semibold">{formatTime(payload.total_time)}</dd>
      </div>
    </dl>
  )
}

export default function SubmissionDetail({ submissionId }: { submissionId: number }) {
  const router = useRouter()
  const [status, setStatus] = useState<SubmissionStatusResponse | null>(null)
  const [detail, setDetail] = useState<SubmissionInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    let intervalId: ReturnType<typeof setInterval> | null = null

    async function loadStatus() {
      try {
        const nextStatus = await fetchSubmissionStatus(submissionId)
        if (!active) return

        setStatus(nextStatus)

        if (nextStatus.state === "FINISH") {
          const nextDetail = await fetchSubmissionInfo(submissionId)
          if (!active) return
          setDetail(nextDetail)
          if (intervalId) clearInterval(intervalId)
        }
      } catch (requestError) {
        if (active) {
          setError(requestError instanceof ApiError ? requestError.message : "Failed to load submission")
        }
      } finally {
        if (active) setLoading(false)
      }
    }

    void loadStatus()
    intervalId = setInterval(() => {
      if (!status || status.state === "PENDING") {
        void loadStatus()
      }
    }, 2000)

    return () => {
      active = false
      if (intervalId) clearInterval(intervalId)
    }
  }, [submissionId])

  if (loading && !status) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center rounded-3xl border border-dashed border-border bg-card/80 p-8 text-muted-foreground">
        <Loader2 className="mr-2 size-4 animate-spin" /> Loading submission
      </div>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <AlertCircle className="size-4 text-rose-600" /> Submission unavailable
          </CardTitle>
          <CardDescription>{error}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline" onClick={() => router.push("/")}> 
            <ArrowLeft className="size-4" /> Back home
          </Button>
        </CardContent>
      </Card>
    )
  }

  const displayPayload = detail ?? status

  return (
    <div className="space-y-6">
      <section className="rounded-[2rem] border border-border bg-gradient-to-br from-card via-card to-muted/40 p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-2">
            <button type="button" className="inline-flex items-center gap-1 text-sm text-muted-foreground transition hover:text-foreground" onClick={() => router.back()}>
              <ArrowLeft className="size-3.5" /> Back
            </button>
            <h1 className="text-3xl font-semibold tracking-tight">Submission #{submissionId}</h1>
            <p className="max-w-2xl text-sm text-muted-foreground">The status view updates until Judge0 finishes, then pulls the final contest-aware details.</p>
          </div>
          <StatusPill status={displayPayload?.status} state={status?.state} />
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <CardHeader className="border-b">
            <CardTitle>Result summary</CardTitle>
            <CardDescription>Accepted, rejected, and truncated contest states are all handled by the backend.</CardDescription>
          </CardHeader>
          <CardContent className="pt-4">{renderPayload(displayPayload)}</CardContent>
        </Card>

        <Card>
          <CardHeader className="border-b">
            <CardTitle>Detailed output</CardTitle>
            <CardDescription>{status?.message ?? detail?.message ?? "Judge output and compiler output appear here when available."}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 pt-4">
            {status?.state === "PENDING" ? (
              <div className="flex items-center gap-2 rounded-2xl border border-dashed border-border bg-muted/40 p-4 text-sm text-muted-foreground">
                <Loader2 className="size-4 animate-spin" /> Waiting for Judge0 to finish
              </div>
            ) : null}

            {displayPayload?.is_truncated_for_contest ? (
              <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
                {displayPayload.message ?? "Only truncated info will be shown for active contest"}
              </div>
            ) : null}

            <div className="grid gap-4">
              <div>
                <h3 className="mb-2 text-sm font-medium">Compile output</h3>
                <pre className="whitespace-pre-wrap rounded-2xl border border-border bg-muted/40 p-4 text-xs leading-6 text-muted-foreground">{displayPayload?.compile_output ?? "-"}</pre>
              </div>
              <div>
                <h3 className="mb-2 text-sm font-medium">Stdout</h3>
                <pre className="whitespace-pre-wrap rounded-2xl border border-border bg-muted/40 p-4 text-xs leading-6 text-muted-foreground">{displayPayload?.stdout ?? "-"}</pre>
              </div>
              <div>
                <h3 className="mb-2 text-sm font-medium">Stderr</h3>
                <pre className="whitespace-pre-wrap rounded-2xl border border-border bg-muted/40 p-4 text-xs leading-6 text-muted-foreground">{displayPayload?.stderr ?? "-"}</pre>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}