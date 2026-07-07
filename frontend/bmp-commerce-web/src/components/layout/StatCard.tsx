import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

type Status = 'success' | 'error' | 'pending'

const statusStyles: Record<Status, string> = {
  success: 'bg-emerald-500',
  error: 'bg-destructive',
  pending: 'bg-amber-500',
}

interface StatCardProps {
  title: string
  value: string
  icon: LucideIcon
  status?: Status
}

export function StatCard({ title, value, icon: Icon, status }: StatCardProps) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0 pb-0">
        <CardTitle>{title}</CardTitle>
        <div className="flex size-8 items-center justify-center rounded-lg bg-muted">
          <Icon className="size-4 text-muted-foreground" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2">
          {status && <span className={cn('size-2 rounded-full', statusStyles[status])} />}
          <p className="text-lg font-semibold tracking-tight">{value}</p>
        </div>
      </CardContent>
    </Card>
  )
}
