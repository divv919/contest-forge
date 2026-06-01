import { cn } from "@/lib/utils"
import type { SubmissionState, SubmissionStatusId } from "@/lib/types"

type StatusPillProps = {
  status?: SubmissionStatusId | string | null
  state?: SubmissionState | null
  className?: string
}

const STATUS_LABELS: Record<number, string> = {
  1: "In queue",
  2: "Processing",
  3: "Accepted",
  4: "Wrong answer",
  5: "Time limit",
  6: "Compile error",
  7: "Segfault",
  8: "Memory limit",
  9: "Floating point",
  10: "Abort",
  11: "NZEC",
  12: "Runtime error",
  13: "Internal error",
  14: "Format error",
}

export function getSubmissionStatusLabel(status?: SubmissionStatusId | string | null) {
  if (typeof status === "number") {
    return STATUS_LABELS[status] ?? `Status ${status}`
  }

  return status ?? "Unknown"
}

function getPillClasses(status?: SubmissionStatusId | string | null, state?: SubmissionState | null) {
  if (state === "PENDING" || status === 1 || status === 2) {
    return "border-amber-200 bg-amber-50 text-amber-800"
  }

  if (status === 3) {
    return "border-emerald-200 bg-emerald-50 text-emerald-800"
  }

  if (status === 4 || status === 5 || status === 6 || status === 7 || status === 8 || status === 9 || status === 10 || status === 11 || status === 12 || status === 13 || status === 14) {
    return "border-rose-200 bg-rose-50 text-rose-800"
  }

  return "border-border bg-muted text-foreground"
}

export default function StatusPill({ status, state, className }: StatusPillProps) {
  const label = state === "PENDING" ? "Pending" : getSubmissionStatusLabel(status)

  return (
    <span className={cn("inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium", getPillClasses(status, state), className)}>
      {label}
    </span>
  )
}