import StatusChip from "@/components/shared/StatusChip"
import { submissionStatusMeta } from "@/lib/display"
import type { SubmissionStatusCode } from "@/lib/types"

type SubmissionStatusPillProps = {
  status?: SubmissionStatusCode | null
}

export default function SubmissionStatusPill({ status }: SubmissionStatusPillProps) {
  if (status === undefined || status === null) {
    return <StatusChip tone="neutral">Unknown</StatusChip>
  }

  const meta = submissionStatusMeta[status]
  return <StatusChip tone={meta.tone}>{meta.label}</StatusChip>
}