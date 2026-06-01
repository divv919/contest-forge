"use client"

import { useEffect } from "react"
import { fetchMe, clearToken, getToken } from "@/lib/auth/session"

export default function AuthHydrator() {
  useEffect(() => {
    let active = true

    async function run() {
      const token = getToken()
      if (!token) return

      try {
        const user = await fetchMe()
        if (!active) return

        if (!user) {
          // invalid token: clear and reload to update UI
          clearToken()
          window.location.reload()
        }
      } catch (_err) {
        // on error, conservatively clear token and reload
        clearToken()
        if (active) window.location.reload()
      }
    }

    void run()

    return () => {
      active = false
    }
  }, [])

  return null
}
