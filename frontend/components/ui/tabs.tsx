"use client"

import * as React from "react"

import { cn } from "@/lib/utils"

type TabsContextValue = {
  value: string
  setValue: (value: string) => void
}

const TabsContext = React.createContext<TabsContextValue | null>(null)

function Tabs({
  value,
  defaultValue,
  onValueChange,
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & {
  value?: string
  defaultValue: string
  onValueChange?: (value: string) => void
}) {
  const [internalValue, setInternalValue] = React.useState(defaultValue)
  const currentValue = value ?? internalValue

  const setValue = React.useCallback(
    (nextValue: string) => {
      if (value === undefined) {
        setInternalValue(nextValue)
      }

      onValueChange?.(nextValue)
    },
    [onValueChange, value]
  )

  return (
    <TabsContext.Provider value={{ value: currentValue, setValue }}>
      <div className={cn("w-full", className)} {...props}>
        {children}
      </div>
    </TabsContext.Provider>
  )
}

function TabsList({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("inline-flex h-10 items-center rounded-lg bg-muted p-1 text-muted-foreground", className)} {...props} />
}

function TabsTrigger({ className, value, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { value: string }) {
  const context = React.useContext(TabsContext)

  if (!context) {
    throw new Error("TabsTrigger must be used within Tabs")
  }

  const active = context.value === value

  return (
    <button
      type="button"
      data-state={active ? "active" : "inactive"}
      onClick={() => context.setValue(value)}
      className={cn(
        "inline-flex h-8 items-center justify-center rounded-md px-3 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40",
        active ? "bg-background text-foreground shadow-sm" : "hover:text-foreground",
        className
      )}
      {...props}
    />
  )
}

function TabsContent({ className, value, ...props }: React.HTMLAttributes<HTMLDivElement> & { value: string }) {
  const context = React.useContext(TabsContext)

  if (!context) {
    throw new Error("TabsContent must be used within Tabs")
  }

  if (context.value !== value) {
    return null
  }

  return <div className={cn("mt-4", className)} {...props} />
}

export { Tabs, TabsList, TabsTrigger, TabsContent }