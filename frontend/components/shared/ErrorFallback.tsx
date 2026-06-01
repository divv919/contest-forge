"use client"

import type { ReactNode } from "react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

type ErrorFallbackProps = {
  error: Error
  onRetry?: () => void
  actions?: ReactNode
}

export default function ErrorFallback({ error, onRetry, actions }: ErrorFallbackProps) {
  return (
    <Card className="border-red-200/80 bg-red-50/50">
      <CardHeader>
        <CardTitle className="text-base text-red-900">Something went wrong</CardTitle>
        <CardDescription className="text-red-800">{error?.message}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-wrap gap-2">
        {actions}
        {onRetry ? (
          <Button type="button" variant="outline" onClick={onRetry}>
            Try again
          </Button>
        ) : null}
      </CardContent>
    </Card>
  )
}
