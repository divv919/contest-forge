"use client"

import { useEffect, useState } from "react"
import Link from "next/link"

import { PageHeader } from "@/components/shared/PageHeader"
import { EmptyState } from "@/components/shared/EmptyState"
import { Button } from "@/components/ui/button"
import { getContestSubmissions, getContestInfo } from "@/lib/api/contests"
import type { ContestSubmissionRecord, ContestInfo } from "@/lib/types"
import { formatContestWindow } from "@/lib/catalog"

export default function ContestSubmissionsPage({ params }: { params: { slug: string } }) {
  const { slug } = params
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [submissions, setSubmissions] = useState<ContestSubmissionRecord[] | null>(null)
  const [contest, setContest] = useState<ContestInfo | null>(null)

  useEffect(() => {
    let active = true

    async function load() {
      try {
        const [c, s] = await Promise.all([getContestInfo(slug), getContestSubmissions(slug)])
        if (!active) return
        setContest(c)
        setSubmissions(s)
        setError(null)
      } catch (err) {
        if (!active) return
        setError(err instanceof Error ? err.message : String(err))
      } finally {
        if (active) setLoading(false)
      }
    }

    void load()

    return () => {
      active = false
    }
  }, [slug])

  if (loading) return <div className="p-6">Loading contest submissions…</div>

  if (error)
    return <EmptyState title="Unable to load submissions" description={error} actionHref={`/contests/${slug}`} actionLabel="Back to contest" />

  if (!submissions || submissions.length === 0)
    return <EmptyState title="No submissions" description="You haven't made any submissions in this contest yet." actionHref={`/contests/${slug}`} actionLabel="Back to contest" />

  const problemMap = new Map<number, { slug?: string; name?: string }>()
  if (contest) {
    for (const p of contest.problems) {
      if (p.id) problemMap.set(p.id, { slug: p.slug, name: p.name })
    }
  }

  return (
    <div className="space-y-6 pb-12">
      <PageHeader eyebrow="Contest" title={`My submissions — ${slug}`} description={contest ? formatContestWindow(contest) : undefined} />

      <section className="rounded-2xl border bg-card p-6">
        <div className="grid gap-3">
          {submissions.map((r) => {
            const info = problemMap.get(r.problem_id)
            return (
              <div key={r.id} className="flex items-center justify-between gap-4 rounded-md border p-3">
                <div>
                  <div className="font-medium">{info?.name ?? `Problem #${r.problem_id}`}</div>
                  <div className="text-sm text-muted-foreground">{info?.slug ? `/${info.slug}` : `ID: ${r.problem_id}`}</div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="text-sm text-muted-foreground mr-4">Points: {r.points ?? 0}</div>
                  <Button asChild size="sm">
                    <Link href={info?.slug ? `/problems/${info.slug}?contest=${slug}` : `/contests/${slug}`}>View</Link>
                  </Button>
                </div>
              </div>
            )
          })}
        </div>
      </section>
    </div>
  )
}
