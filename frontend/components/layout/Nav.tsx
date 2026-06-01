"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useEffect, useState } from "react"
import { BookOpen, Code2, LogOut, Menu, Shield, Trophy } from "lucide-react"

import { Button } from "@/components/ui/button"
import { clearToken, getToken } from "@/lib/auth/session"
import { cn } from "@/lib/utils"

const navLinks = [
  { href: "/problems", label: "Problems", icon: BookOpen },
  { href: "/contests", label: "Contests", icon: Trophy },
  { href: "/profile", label: "Profile", icon: Shield },
] as const

export default function Nav() {
  const pathname = usePathname()
  const [token, setToken] = useState<string | null>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const refreshToken = () => setToken(getToken())

    refreshToken()
    window.addEventListener("storage", refreshToken)

    return () => window.removeEventListener("storage", refreshToken)
  }, [])

  function handleSignOut() {
    clearToken()
    setToken(null)
    setMobileMenuOpen(false)
    window.location.href = "/"
  }

  return (
    <nav className="relative z-10 border-b border-border/70 bg-background/85 backdrop-blur supports-[backdrop-filter]:bg-background/70">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2 text-sm font-semibold tracking-tight text-foreground">
          <span className="flex size-8 items-center justify-center rounded-xl bg-foreground text-background">
            <Code2 className="size-4" />
          </span>
          Contest Platform
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {navLinks.map(({ href, label, icon: Icon }) => {
            const active = pathname?.startsWith(href)

            return (
              <Button key={href} asChild variant={active ? "secondary" : "ghost"} size="sm">
                <Link href={href} className="gap-2">
                  <Icon className="size-4" />
                  {label}
                </Link>
              </Button>
            )
          })}
        </div>

        <div className="flex items-center gap-2">
          {token ? (
            <Button type="button" variant="outline" size="sm" className="hidden gap-2 md:inline-flex" onClick={handleSignOut}>
              <LogOut className="size-4" />
              Sign out
            </Button>
          ) : (
            <Button asChild size="sm" className="hidden md:inline-flex">
              <Link href="/login">Sign in</Link>
            </Button>
          )}

          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className="md:hidden"
            onClick={() => setMobileMenuOpen((value) => !value)}
            aria-expanded={mobileMenuOpen}
            aria-label="Toggle navigation menu"
          >
            <Menu className="size-4" />
          </Button>
        </div>

        <div className={cn("w-full md:hidden", mobileMenuOpen ? "block" : "hidden")}>
          <div className="mt-2 grid gap-2 rounded-2xl border border-border/70 bg-card p-3 shadow-sm">
            {navLinks.map(({ href, label, icon: Icon }) => {
              const active = pathname?.startsWith(href)

              return (
                <Button
                  key={href}
                  asChild
                  variant={active ? "secondary" : "ghost"}
                  className="justify-start gap-2"
                  size="sm"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Link href={href}>
                    <Icon className="size-4" />
                    {label}
                  </Link>
                </Button>
              )
            })}
            {token ? (
              <Button type="button" variant="outline" className="justify-start gap-2" size="sm" onClick={handleSignOut}>
                <LogOut className="size-4" />
                Sign out
              </Button>
            ) : (
              <Button asChild size="sm" className="justify-start">
                <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                  Sign in
                </Link>
              </Button>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
