import type { ReactNode } from "react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

type MetricCardProps = {
  label: string
  value: ReactNode
  description?: string
  note?: string
  trend?: ReactNode
  className?: string
}

export function MetricCard({ label, value, description, note, trend, className }: MetricCardProps) {
  const text = description ?? note ?? ""

  return (
    <Card className={cn("h-full bg-card/80", className)}>
      <CardHeader>
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-2xl leading-none">{value}</CardTitle>
      </CardHeader>
      <CardContent className="flex items-center justify-between gap-4">
        <p className="text-sm text-muted-foreground">{text}</p>
        {trend ? <div className="text-sm font-medium text-foreground">{trend}</div> : null}
      </CardContent>
    </Card>
  )
}