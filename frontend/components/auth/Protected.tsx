"use client"
import React, { useEffect } from "react"
import { useRouter } from "next/navigation"
import { getToken } from "@/lib/auth/session"
import Loading from "@/components/shared/Loading"

export default function Protected({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [ready, setReady] = React.useState(false)

  useEffect(() => {
    const token = getToken()
    if (!token) router.replace("/login")
    else setReady(true)
  }, [router])

  if (!ready) {
    return <Loading />
  }

  return <>{children}</>
}
