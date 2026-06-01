import StatusChip from "@/components/shared/StatusChip"
import { difficultyMeta } from "@/lib/display"
import type { Difficulty } from "@/lib/types"

type ProblemDifficultyBadgeProps = {
  difficulty: Difficulty
}

export default function ProblemDifficultyBadge({ difficulty }: ProblemDifficultyBadgeProps) {
  const meta = difficultyMeta[difficulty]

  return <StatusChip tone={meta.tone}>{meta.label}</StatusChip>
}