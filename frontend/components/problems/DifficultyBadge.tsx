import { Badge } from "@/components/ui/badge"
import { difficultyLabel, difficultyTone } from "@/lib/catalog"
import type { Difficulty } from "@/lib/types"

export function DifficultyBadge({ difficulty }: { difficulty: Difficulty }) {
  return <Badge variant={difficultyTone(difficulty)}>{difficultyLabel(difficulty)}</Badge>
}