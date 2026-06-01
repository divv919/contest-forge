"use client"

import { useEffect, useMemo, useState } from "react"
import { Search } from "lucide-react"

import { EmptyState } from "@/components/shared/EmptyState"
import Link from "next/link"
import { PageHeader } from "@/components/shared/PageHeader"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { getOngoingContests, getPastContests, getUpcomingContests } from "@/lib/api/catalog"
import { getContestState } from "@/lib/catalog"
import type { Contest, ContestStatus } from "@/lib/types"
import { ContestCard } from "./ContestCard"

type ContestStateModel = {
  loading: boolean
  error: string | null
  contests: Contest[]
}

const filters: Array<ContestStatus> = ["all", "ongoing", "upcoming", "past"]

export function ContestCatalogPage() {
  const [state, setState] = useState<ContestStateModel>({ loading: true, error: null, contests: [] })
  const [query, setQuery] = useState("")
  const [filter, setFilter] = useState<ContestStatus>("all")

  useEffect(() => {
    let active = true

    async function load() {
      try {
        const [upcoming, ongoing, past] = await Promise.all([getUpcomingContests(), getOngoingContests(), getPastContests()])

        if (!active) return

        setState({ loading: false, error: null, contests: [...ongoing, ...upcoming, ...past] })
      } catch (error) {
        if (!active) return

        setState({ loading: false, error: error instanceof Error ? error.message : "Unable to load contests", contests: [] })
      }
    }

    void load()

    return () => {
      active = false
    }
  }, [])

  const filteredContests = useMemo(() => {
    return state.contests.filter((contest) => {
      const contestState = getContestState(contest)
      const matchesQuery = contest.name.toLowerCase().includes(query.toLowerCase()) || contest.slug.toLowerCase().includes(query.toLowerCase())
      const matchesFilter = filter === "all" || contestState === filter

      return matchesQuery && matchesFilter
    })
  }, [filter, query, state.contests])

  return (
    <div className="space-y-8 pb-12">
      <PageHeader
        eyebrow="Contest schedule"
        title="Track the contest lifecycle from upcoming to ongoing and into the archived rankings."
        description="This page keeps the state model explicit so it is obvious which contests are live, which are queued, and which are already finalized."
        actions={
          <Button asChild variant="outline">
              <Link href="/">Back to home</Link>
            </Button>
        }
      />

      <section className="space-y-4 rounded-3xl border border-border/70 bg-card/70 p-4 shadow-sm backdrop-blur sm:p-6">
        <div className="grid gap-3 md:grid-cols-[1fr_auto] md:items-center">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by contest name or slug" className="pl-9" />
          </div>
          <p className="text-sm text-muted-foreground">{filteredContests.length} matching contests</p>
        </div>

        <Tabs defaultValue="all" value={filter} onValueChange={(value) => setFilter(value as ContestStatus)}>
          <TabsList className="flex h-auto flex-wrap gap-2 bg-transparent p-0">
            {filters.map((item) => (
              <TabsTrigger key={item} value={item} className="rounded-full border border-border bg-background px-4 capitalize data-[state=active]:border-foreground data-[state=active]:bg-foreground data-[state=active]:text-background">
                {item === "all" ? "All contests" : item}
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value={filter} className="mt-0">
            {state.loading ? (
              <ContestsSkeleton />
            ) : state.error ? (
              <EmptyState title="Unable to load contests" description={state.error} actionHref="/login" actionLabel="Sign in and retry" />
            ) : filteredContests.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {filteredContests.map((contest) => (
                  <ContestCard key={contest.slug} contest={contest} />
                ))}
              </div>
            ) : (
              <EmptyState title="No matching contests" description="Try a broader search or clear the current state filter." actionHref="/contests" actionLabel="Reset contest view" />
            )}
          </TabsContent>
        </Tabs>
      </section>
    </div>
  )
}

function ContestsSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: 6 }).map((_, index) => (
        <Skeleton key={index} className="h-52 rounded-2xl" />
      ))}
    </div>
  )
}