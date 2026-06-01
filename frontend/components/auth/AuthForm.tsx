"use client"

import React, { useState } from "react"

type Props = {
  initialUsername?: string
  initialPassword?: string
  submitLabel?: string
  onSubmit: (username: string, password: string) => Promise<void>
}

export default function AuthForm({ initialUsername = "", initialPassword = "", submitLabel = "Submit", onSubmit }: Props) {
  const [username, setUsername] = useState(initialUsername)
  const [password, setPassword] = useState(initialPassword)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await onSubmit(username, password)
    } catch (err: any) {
      setError(err?.message || "Request failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto mt-8 flex flex-col gap-3">
      <input
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="border px-3 py-2 rounded"
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="border px-3 py-2 rounded"
        required
      />

      {error && <div className="text-sm text-red-600">{error}</div>}

      <button disabled={loading} className="rounded bg-foreground px-3 py-2 text-background">
        {loading ? `${submitLabel}...` : submitLabel}
      </button>
    </form>
  )
}
