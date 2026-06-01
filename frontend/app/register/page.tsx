"use client"
import React from "react"
import { useRouter } from "next/navigation"
import { register } from "@/lib/api/auth"
import AuthForm from "@/components/auth/AuthForm"

export default function RegisterPage() {
  const router = useRouter()

  async function handleSubmit(username: string, password: string) {
    await register(username, password)
    // show a brief success then navigate to login
    router.push("/login")
  }

  return (
    <div className="max-w-md mx-auto mt-24">
      <h2 className="text-2xl font-semibold mb-4">Register</h2>
      <AuthForm submitLabel="Register" onSubmit={handleSubmit} />
    </div>
  )
}
