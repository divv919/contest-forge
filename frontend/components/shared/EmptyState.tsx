import Link from "next/link"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export function EmptyState({
  title,
  description,
  actionHref,
  actionLabel,
}: {
  title: string
  description: string
  actionHref?: string
  actionLabel?: string
}) {
  return (
    <Card className="border-dashed bg-muted/20">
      <CardContent className="flex flex-col items-start gap-4 py-8">
        <div className="space-y-1">
          <h3 className="text-base font-semibold">{title}</h3>
          <p className="max-w-xl text-sm text-muted-foreground">{description}</p>
        </div>
        {actionHref && actionLabel ? (
          <Button asChild>
            <Link href={actionHref}>{actionLabel}</Link>
          </Button>
        ) : null}
      </CardContent>
    </Card>
  )
}