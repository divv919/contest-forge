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
import { getProblems } from "@/lib/api/catalog"
import type { Difficulty, Problem } from "@/lib/types"
import { ProblemCard } from "./ProblemCard"

type ProblemsState = {
  loading: boolean
  error: string | null
  problems: Problem[]
}

const difficultyFilters: Array<Difficulty | "ALL"> = ["ALL", "EASY", "MEDIUM", "HARD"]

export function ProblemCatalogPage() {
  const [state, setState] = useState<ProblemsState>({ loading: true, error: null, problems: [] })
  const [query, setQuery] = useState("")
  const [difficulty, setDifficulty] = useState<Difficulty | "ALL">("ALL")

  useEffect(() => {
    let active = true

    async function load() {
      try {
        const problems = await getProblems()

        if (!active) return

        setState({ loading: false, error: null, problems })
      } catch (error) {
        if (!active) return

        setState({ loading: false, error: error instanceof Error ? error.message : "Unable to load problems", problems: [] })
      }
    }

    void load()

    return () => {
      active = false
    }
  }, [])

  const filteredProblems = useMemo(() => {
    return state.problems.filter((problem) => {
      const matchesQuery = problem.name.toLowerCase().includes(query.toLowerCase()) || problem.slug.toLowerCase().includes(query.toLowerCase())
      const matchesDifficulty = difficulty === "ALL" || problem.difficulty === difficulty

      return matchesQuery && matchesDifficulty
    })
  }, [difficulty, query, state.problems])

  return (
    <div className="space-y-8 pb-12">
      <PageHeader
        eyebrow="Problem catalog"
        title="Pick a problem, inspect the statement, and open the editor with the right starter code."
        description="The filtering UI is intentionally dense so you can move from browsing to solving without waiting for a separate search experience to load."
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
            <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by name or slug" className="pl-9" />
          </div>
          <p className="text-sm text-muted-foreground">{filteredProblems.length} matching problems</p>
        </div>

        <Tabs defaultValue="ALL" value={difficulty} onValueChange={(value) => setDifficulty(value as Difficulty | "ALL")}>
          <TabsList className="flex flex-wrap h-auto gap-2 bg-transparent p-0">
            {difficultyFilters.map((filter) => (
              <TabsTrigger key={filter} value={filter} className="rounded-full border border-border bg-background px-4 data-[state=active]:border-foreground data-[state=active]:bg-foreground data-[state=active]:text-background">
                {filter === "ALL" ? "All difficulties" : filter}
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value={difficulty} className="mt-0">
            {state.loading ? (
              <ProblemsSkeleton />
            ) : state.error ? (
              <EmptyState title="Unable to load problems" description={state.error} actionHref="/login" actionLabel="Sign in and retry" />
            ) : filteredProblems.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {filteredProblems.map((problem) => (
                  <ProblemCard key={problem.slug} problem={problem} />
                ))}
              </div>
            ) : (
              <EmptyState title="No matching problems" description="Try a different keyword or switch the difficulty filter." actionHref="/problems" actionLabel="Reset catalog view" />
            )}
          </TabsContent>
        </Tabs>
      </section>
    </div>
  )
}

function ProblemsSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: 6 }).map((_, index) => (
        <Skeleton key={index} className="h-52 rounded-2xl" />
      ))}
    </div>
  )
}