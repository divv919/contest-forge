import Link from "next/link"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import type { Problem } from "@/lib/types"
import { DifficultyBadge } from "./DifficultyBadge"

export function ProblemCard({ problem }: { problem: Problem }) {
  return (
    <Card className="group h-full justify-between transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-lg">
      <CardHeader className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <DifficultyBadge difficulty={problem.difficulty} />
          <span className="text-xs uppercase tracking-[0.22em] text-muted-foreground">#{problem.slug}</span>
        </div>
        <CardTitle>{problem.name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="line-clamp-2 text-sm text-muted-foreground">
          Open the statement, inspect the boilerplate, and start coding from the matching language stub.
        </p>
      </CardContent>
      <CardFooter className="justify-between gap-3">
        <span className="text-xs text-muted-foreground">Problem ID {problem.id ?? "pending"}</span>
        <Button asChild size="sm" variant="outline">
          <Link href={`/problems/${problem.slug}`}>Open problem</Link>
        </Button>
      </CardFooter>
    </Card>
  )
}