import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium whitespace-nowrap transition-colors",
  {
    variants: {
      variant: {
        default: "border-transparent bg-foreground text-background",
        secondary: "border-transparent bg-muted text-foreground",
        outline: "border-border bg-background text-foreground",
        success: "border-emerald-500/20 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
        warning: "border-amber-500/20 bg-amber-500/10 text-amber-700 dark:text-amber-300",
        danger: "border-red-500/20 bg-red-500/10 text-red-700 dark:text-red-300",
        info: "border-sky-500/20 bg-sky-500/10 text-sky-700 dark:text-sky-300",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

export interface BadgeProps extends React.ComponentProps<"div">, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div data-slot="badge" className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { badgeVariants }
