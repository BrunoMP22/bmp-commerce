import * as React from 'react'
import { cn } from '@/lib/utils'

function Card({ className, ...props }: React.ComponentProps<'div'>) {
  return (
    <div
      className={cn(
        'rounded-xl border border-border bg-card text-card-foreground shadow-sm transition-shadow duration-200 hover:shadow-md',
        className,
      )}
      {...props}
    />
  )
}

function CardHeader({ className, ...props }: React.ComponentProps<'div'>) {
  return <div className={cn('flex flex-col gap-1 p-5', className)} {...props} />
}

function CardTitle({ className, ...props }: React.ComponentProps<'h3'>) {
  return <h3 className={cn('text-sm font-medium text-muted-foreground', className)} {...props} />
}

function CardContent({ className, ...props }: React.ComponentProps<'div'>) {
  return <div className={cn('px-5 pb-5', className)} {...props} />
}

export { Card, CardHeader, CardTitle, CardContent }
