import { useQuery } from '@tanstack/react-query'
import {
  AlertCircle,
  AlertTriangle,
  Package,
  PackageX,
  Receipt,
  RotateCw,
  ShoppingCart,
  Users,
  Wallet,
  TrendingUp,
} from 'lucide-react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { getDashboard } from '@/api/dashboard'
import { useAuth } from '@/lib/auth-context'
import { formatCurrency } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatCard } from '@/components/layout/StatCard'

function formatDia(data: string) {
  return new Date(data).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', timeZone: 'UTC' })
}

export function DashboardPage() {
  const { user } = useAuth()
  const firstName = user?.name.split(' ')[0]

  const dashboardQuery = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
  })

  const dashboard = dashboardQuery.data

  const chartData = (dashboard?.vendasPorDia ?? []).map((dia) => ({
    dia: formatDia(dia.data),
    total: dia.total,
    quantidade: dia.quantidade,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          {firstName ? `Bem-vindo de volta, ${firstName}.` : 'Bem-vindo de volta.'} Visão geral do seu
          negócio.
        </p>
      </div>

      {dashboardQuery.isError && (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border p-12 text-center">
          <AlertCircle className="size-8 text-destructive" />
          <p className="text-sm text-muted-foreground">Não foi possível carregar os indicadores.</p>
          <Button variant="outline" size="sm" onClick={() => dashboardQuery.refetch()}>
            <RotateCw className="size-4" />
            Tentar novamente
          </Button>
        </div>
      )}

      {dashboardQuery.isPending && !dashboardQuery.isError && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, index) => (
            <div key={index} className="h-28 animate-pulse rounded-xl border border-border bg-muted/40" />
          ))}
        </div>
      )}

      {dashboard && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Receita total"
              value={formatCurrency(dashboard.receitaTotal)}
              icon={Wallet}
              tone="emerald"
            />
            <StatCard
              title="Vendas realizadas"
              value={String(dashboard.quantidadeVendas)}
              icon={ShoppingCart}
              tone="blue"
            />
            <StatCard
              title="Ticket médio"
              value={formatCurrency(dashboard.ticketMedio)}
              icon={Receipt}
              tone="blue"
            />
            <StatCard
              title="Valor em estoque"
              value={formatCurrency(dashboard.valorEstoque)}
              icon={Package}
            />
            <StatCard title="Clientes cadastrados" value={String(dashboard.clientesCadastrados)} icon={Users} />
            <StatCard
              title="Produtos cadastrados"
              value={String(dashboard.produtosCadastrados)}
              icon={Package}
            />
            <StatCard
              title="Abaixo do estoque mínimo"
              value={String(dashboard.produtosAbaixoMinimo)}
              icon={AlertTriangle}
              tone="amber"
            />
            <StatCard
              title="Sem estoque"
              value={String(dashboard.produtosSemEstoque)}
              icon={PackageX}
              tone="amber"
            />
          </div>

          <Card>
            <CardHeader className="flex-row items-center gap-2 space-y-0">
              <TrendingUp className="size-4 text-muted-foreground" />
              <CardTitle>Vendas dos últimos 14 dias</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 8, right: 8, left: 8, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                    <XAxis
                      dataKey="dia"
                      tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }}
                      axisLine={{ stroke: 'var(--border)' }}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fill: 'var(--muted-foreground)', fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(value: number) =>
                        value >= 1000 ? `${(value / 1000).toFixed(1)}k` : String(value)
                      }
                      width={48}
                    />
                    <Tooltip
                      cursor={{ fill: 'var(--muted)', opacity: 0.5 }}
                      contentStyle={{
                        backgroundColor: 'var(--card)',
                        border: '1px solid var(--border)',
                        borderRadius: '0.5rem',
                        color: 'var(--card-foreground)',
                        fontSize: '0.8rem',
                      }}
                      formatter={(value) => [formatCurrency(Number(value)), 'Total']}
                      labelFormatter={(label) => `Dia ${label}`}
                    />
                    <Bar dataKey="total" fill="var(--primary)" radius={[4, 4, 0, 0]} maxBarSize={36} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
