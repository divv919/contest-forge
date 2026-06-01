import React from "react"
import Nav from "@/components/layout/Nav"
import AuthHydrator from "@/components/auth/AuthHydrator"

export default function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden bg-background text-foreground">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(0,0,0,0.05),transparent_30%)] opacity-60 dark:bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.06),transparent_30%)]" />
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(0,0,0,0.02)_1px,transparent_1px),linear-gradient(to_bottom,rgba(0,0,0,0.02)_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-15 dark:bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)]" />
      <AuthHydrator />
      <Nav />
      <main className="relative mx-auto flex w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:px-8">{children}</main>
    </div>
  )
}
