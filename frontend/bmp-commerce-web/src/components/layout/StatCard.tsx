import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

type Status = 'success' | 'error' | 'pending'
type Tone = 'default' | 'blue' | 'emerald' | 'amber'

const statusStyles: Record<Status, string> = {
  success: 'bg-emerald-500',
  error: 'bg-destructive',
  pending: 'bg-amber-500',
}

const toneStyles: Record<Tone, string> = {
  default: 'bg-muted text-muted-foreground',
  blue: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
  emerald: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
  amber: 'bg-amber-500/10 text-amber-600 dark:text-amber-400',
}

interface StatCardProps {
  title: string
  value: string
  icon: LucideIcon
  status?: Status
  tone?: Tone
}

export function StatCard({ title, value, icon: Icon, status, tone = 'default' }: StatCardProps) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0 pb-0">
        <CardTitle>{title}</CardTitle>
        <div className={cn('flex size-8 items-center justify-center rounded-lg', toneStyles[tone])}>
          <Icon className="size-4" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2">
          {status && <span className={cn('size-2 shrink-0 rounded-full', statusStyles[status])} />}
          <p className="text-lg font-semibold tracking-tight tabular-nums">{value}</p>
        </div>
      </CardContent>
    </Card>
  )
}
