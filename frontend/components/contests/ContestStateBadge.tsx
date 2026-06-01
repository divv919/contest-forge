import { Badge } from "@/components/ui/badge"
import { contestStateLabel, contestStateTone } from "@/lib/catalog"
import type { ContestState } from "@/lib/types"

export function ContestStateBadge({ state }: { state: ContestState }) {
  return <Badge variant={contestStateTone(state)}>{contestStateLabel(state)}</Badge>
}