"use client"

import { useEffect, useState } from "react"
import Link from "next/link"

import { PageHeader } from "@/components/shared/PageHeader"
import { EmptyState } from "@/components/shared/EmptyState"
import { Button } from "@/components/ui/button"
import { getContestInfo } from "@/lib/api/contests"
import { formatContestWindow } from "@/lib/catalog"
import type { ContestInfo } from "@/lib/types"

export default function ContestPage({ params }: { params: { slug: string } }) {
  const { slug } = params
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [contest, setContest] = useState<ContestInfo | null>(null)

  useEffect(() => {
    let active = true

    async function load() {
      try {
        const data = await getContestInfo(slug)
        if (!active) return
        setContest(data)
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

  if (loading) return <div className="p-6">Loading contest…</div>

  if (error || !contest)
    return <EmptyState title="Unable to load contest" description={error ?? "No contest found"} actionHref="/contests" actionLabel="Back to contests" />

  return (
    <div className="space-y-6 pb-12">
      <PageHeader
        eyebrow="Contest"
        title={contest.name}
        description={formatContestWindow(contest)}
        actions={
          <>
            <Button asChild>
              <Link href={`/contests/${slug}/submissions`}>My submissions</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href={`/contests/${slug}/ranking`}>Ranking</Link>
            </Button>
          </>
        }
      />

      <section className="rounded-2xl border bg-card p-6">
        <h3 className="mb-4 text-lg font-semibold">Problems in this contest</h3>
        <div className="grid gap-3">
          {contest.problems.map((p) => (
            <div key={p.slug} className="flex items-center justify-between gap-4 rounded-md border p-3">
              <div>
                <div className="font-medium">{p.name}</div>
                <div className="text-sm text-muted-foreground">#{p.slug}</div>
              </div>
              <div className="flex items-center gap-2">
                <Button asChild size="sm">
                  <Link href={`/problems/${p.slug}?contest=${contest.slug}`}>Open problem</Link>
                </Button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
