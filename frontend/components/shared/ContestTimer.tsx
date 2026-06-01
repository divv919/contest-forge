"use client"

import { useEffect, useMemo, useState } from "react"

import StatusChip from "@/components/shared/StatusChip"
import { contestPhaseMeta, formatDuration, getContestPhase } from "@/lib/display"
import { cn } from "@/lib/utils"

type ContestTimerProps = {
  startTime: string
  endTime: string
  className?: string
}

export default function ContestTimer({ startTime, endTime, className }: ContestTimerProps) {
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    const intervalId = window.setInterval(() => setNow(Date.now()), 1000)
    return () => window.clearInterval(intervalId)
  }, [])

  const phase = getContestPhase(startTime, endTime, now)
  const phaseMeta = contestPhaseMeta[phase]
  const countdownTarget = phase === "UPCOMING" ? startTime : endTime
  const countdown = useMemo(() => formatDuration(new Date(countdownTarget).getTime() - now), [countdownTarget, now])

  return (
    <div className={cn("flex flex-wrap items-center gap-3 rounded-2xl border border-border/70 bg-card px-4 py-3", className)}>
      <StatusChip tone={phaseMeta.tone}>{phaseMeta.label}</StatusChip>
      <div className="min-w-0">
        <p className="text-sm font-medium text-foreground">
          {phase === "UPCOMING"
            ? `Starts in ${countdown}`
            : phase === "ONGOING"
              ? `Ends in ${countdown}`
              : "Contest finished"}
        </p>
        <p className="text-xs text-muted-foreground">Updated live every second</p>
      </div>
    </div>
  )
}