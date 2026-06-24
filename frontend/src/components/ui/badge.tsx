import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-accent text-white',
        secondary: 'border-surface-border bg-surface-overlay text-text-secondary',
        destructive: 'border-transparent bg-red-500/10 text-red-400 border-red-500/20',
        outline: 'border-surface-border text-text-secondary',
        admin: 'border-accent/20 bg-accent-muted text-accent',
        manager: 'border-blue-500/20 bg-blue-500/10 text-blue-400',
        user: 'border-surface-border bg-surface-overlay text-text-muted',
        viewer: 'border-surface-border bg-surface-overlay text-text-muted',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
