"use client"

import { useEffect } from "react"

import ErrorFallback from "@/components/shared/ErrorFallback"

export default function AppError({
  error,
  reset,
}: Readonly<{
  error: Error & { digest?: string }
  reset: () => void
}>) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="mx-auto flex min-h-[50vh] w-full max-w-2xl items-center px-4 py-12 sm:px-6 lg:px-8">
      <ErrorFallback error={error} onRetry={reset} />
    </div>
  )
}