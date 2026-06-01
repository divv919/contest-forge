import type { ReactNode } from "react"

import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

type StatusChipTone = "neutral" | "info" | "success" | "warning" | "danger"

const toneToVariant: Record<StatusChipTone, "secondary" | "info" | "success" | "warning" | "danger"> = {
  neutral: "secondary",
  info: "info",
  success: "success",
  warning: "warning",
  danger: "danger",
}

type StatusChipProps = {
  tone: StatusChipTone
  children: ReactNode
  className?: string
}

export default function StatusChip({ tone, children, className }: StatusChipProps) {
  return (
    <Badge variant={toneToVariant[tone]} className={cn("gap-1.5", className)}>
      {children}
    </Badge>
  )
}