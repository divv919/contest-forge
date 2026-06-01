"use client"
import React from "react"
import { useRouter } from "next/navigation"
import { login } from "@/lib/api/auth"
import AuthForm from "@/components/auth/AuthForm"

export default function LoginPage() {
  const router = useRouter()

  async function handleSubmit(username: string, password: string) {
    await login(username, password)
    router.replace("/")
  }

  return (
    <div className="max-w-md mx-auto mt-24">
      <h2 className="text-2xl font-semibold mb-4">Sign in</h2>
      <AuthForm submitLabel="Sign in" onSubmit={handleSubmit} />
    </div>
  )
}
