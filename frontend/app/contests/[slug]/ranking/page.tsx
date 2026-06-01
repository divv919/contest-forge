"use client"

import { useEffect, useState } from "react"
import Link from "next/link"

import { PageHeader } from "@/components/shared/PageHeader"
import { EmptyState } from "@/components/shared/EmptyState"
import { Button } from "@/components/ui/button"
import { getContestRanking } from "@/lib/api/contests"
import { ApiError } from "@/lib/api/client"
import type { ContestPoints } from "@/lib/types"

export default function ContestRankingPage({ params }: { params: { slug: string } }) {
  const { slug } = params
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [ranking, setRanking] = useState<ContestPoints[] | null>(null)

  useEffect(() => {
    let active = true

    async function load() {
      try {
        const data = await getContestRanking(slug)
        if (!active) return
        setRanking(data)
        setError(null)
      } catch (err) {
        if (!active) return
        if (err instanceof ApiError && err.status === 403) {
          setError(String(err.message))
        } else {
          setError(err instanceof Error ? err.message : String(err))
        }
      } finally {
        if (active) setLoading(false)
      }
    }

    void load()

    return () => {
      active = false
    }
  }, [slug])

  if (loading) return <div className="p-6">Loading ranking…</div>

  if (error)
    return <EmptyState title="Ranking unavailable" description={error} actionHref={`/contests/${slug}`} actionLabel="Back to contest" />

  if (!ranking || ranking.length === 0)
    return <EmptyState title="No ranking" description="No ranking data available for this contest." actionHref={`/contests/${slug}`} actionLabel="Back to contest" />

  return (
    <div className="space-y-6 pb-12">
      <PageHeader eyebrow="Contest" title={`Ranking — ${slug}`} />

      <section className="rounded-2xl border bg-card p-6">
        <div className="grid gap-3">
          {ranking.map((row) => (
            <div key={`${row.user_id}-${row.rank}`} className="flex items-center justify-between gap-4 rounded-md border p-3">
              <div>
                <div className="font-medium">User {row.user_id}</div>
                <div className="text-sm text-muted-foreground">Rank #{row.rank}</div>
              </div>
              <div className="flex items-center gap-2">
                <div className="text-sm text-muted-foreground mr-4">Points: {row.total_points}</div>
                <Button asChild size="sm">
                  <Link href={`/contests/${slug}`}>Contest</Link>
                </Button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
