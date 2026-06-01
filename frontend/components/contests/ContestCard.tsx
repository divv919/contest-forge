import Link from "next/link"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { formatContestWindow, getContestState } from "@/lib/catalog"
import type { Contest } from "@/lib/types"
import { ContestStateBadge } from "./ContestStateBadge"

export function ContestCard({ contest }: { contest: Contest }) {
  const state = getContestState(contest)

  return (
    <Card className="group h-full justify-between transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-lg">
      <CardHeader className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <ContestStateBadge state={state} />
          <span className="text-xs uppercase tracking-[0.22em] text-muted-foreground">#{contest.slug}</span>
        </div>
        <CardTitle>{contest.name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="line-clamp-2 text-sm text-muted-foreground">{formatContestWindow(contest)}</p>
        <p className="text-xs text-muted-foreground">Hosted by {contest.created_by ?? "the platform"}</p>
      </CardContent>
      <CardFooter className="justify-between gap-3">
        <span className="text-xs text-muted-foreground">Contest ID {contest.id ?? "pending"}</span>
        <Button asChild size="sm" variant="outline">
          <Link href={`/contests/${contest.slug}`}>Open contest</Link>
        </Button>
      </CardFooter>
    </Card>
  )
}