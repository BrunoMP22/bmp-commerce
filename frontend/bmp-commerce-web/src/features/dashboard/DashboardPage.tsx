import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  AlertCircle,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  Lightbulb,
  Package,
  PackageX,
  Plus,
  Receipt,
  RotateCw,
  ShoppingCart,
  TrendingUp,
  Trophy,
  Users,
  Wallet,
} from 'lucide-react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { getDashboard } from '@/api/dashboard'
import { useAuth } from '@/lib/auth-context'
import { cn, formatCurrency } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { Dashboard, KpiComVariacao, UltimaVenda } from '@/types/dashboard'

const CORES_CATEGORIA = ['var(--chart-1)', 'var(--chart-2)', 'var(--chart-3)', 'var(--chart-4)']

function formatCompacto(valor: number) {
  if (valor >= 1000) {
    return `${(valor / 1000).toLocaleString('pt-BR', { maximumFractionDigits: 1 })}k`
  }
  return valor.toLocaleString('pt-BR', { maximumFractionDigits: 0 })
}

function formatDiaCurto(data: string) {
  return new Date(data).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', timeZone: 'UTC' })
}

function formatDataHora(dataHora: string) {
  return new Date(dataHora).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function saudacao() {
  const hora = new Date().getHours()
  if (hora < 12) return 'Bom dia'
  if (hora < 18) return 'Boa tarde'
  return 'Boa noite'
}

// ---------------------------------------------------------------- KPI tiles

function Delta({ kpi, boaQuandoSobe = true }: { kpi: KpiComVariacao; boaQuandoSobe?: boolean }) {
  if (kpi.variacaoPercentual === null) {
    return <p className="text-xs text-muted-foreground">sem base de comparação</p>
  }

  const subiu = kpi.variacaoPercentual >= 0
  const boa = subiu === boaQuandoSobe
  const Seta = subiu ? ArrowUpRight : ArrowDownRight
  const texto = `${subiu ? '+' : ''}${kpi.variacaoPercentual.toLocaleString('pt-BR', {
    maximumFractionDigits: 0,
  })}%`

  return (
    <p
      className={cn(
        'flex items-center gap-1 text-xs font-medium',
        boa ? 'text-emerald-600 dark:text-emerald-400' : 'text-destructive',
      )}
    >
      <Seta className="size-3.5" aria-hidden="true" />
      {texto}
      <span className="font-normal text-muted-foreground">vs 30 dias anteriores</span>
    </p>
  )
}

interface KpiTileProps {
  titulo: string
  valor: string
  icone: typeof Wallet
  rodape: ReactNode
  sparkline?: ReactNode
}

function KpiTile({ titulo, valor, icone: Icone, rodape, sparkline }: KpiTileProps) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 space-y-1">
            <p className="text-sm text-muted-foreground">{titulo}</p>
            <p className="truncate text-2xl font-semibold tracking-tight">{valor}</p>
          </div>
          <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Icone className="size-4" />
          </div>
        </div>
        <div className="mt-3 flex items-end justify-between gap-3">
          <div className="min-w-0">{rodape}</div>
          {sparkline}
        </div>
      </CardContent>
    </Card>
  )
}

function Sparkline({
  dados,
  metrica,
}: {
  dados: Dashboard['vendasPorDia']
  metrica: 'total' | 'quantidade'
}) {
  return (
    <div className="h-9 w-24 shrink-0" aria-hidden="true">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={dados} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
          <Area
            type="monotone"
            dataKey={metrica}
            stroke="var(--chart-1)"
            strokeWidth={1.5}
            fill="var(--chart-1)"
            fillOpacity={0.12}
            isAnimationActive={false}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

// ------------------------------------------- gráfico de 30 dias (por métrica)

function GraficoVendas({
  dados,
  financeiro,
}: {
  dados: Dashboard['vendasPorDia']
  financeiro: boolean
}) {
  const chartData = dados.map((dia) => ({ ...dia, rotulo: formatDiaCurto(dia.data) }))
  const metrica = financeiro ? 'total' : 'quantidade'

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 8, right: 12, left: 4, bottom: 0 }}>
          <defs>
            <linearGradient id="serie-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.18} />
              <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="var(--border)" strokeWidth={1} vertical={false} />
          <XAxis
            dataKey="rotulo"
            tick={{ fill: 'var(--muted-foreground)', fontSize: 11 }}
            axisLine={{ stroke: 'var(--border)' }}
            tickLine={false}
            interval={4}
            tickMargin={8}
          />
          <YAxis
            tick={{ fill: 'var(--muted-foreground)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={financeiro ? formatCompacto : String}
            allowDecimals={false}
            width={44}
          />
          <Tooltip
            cursor={{ stroke: 'var(--muted-foreground)', strokeWidth: 1 }}
            contentStyle={{
              backgroundColor: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: '0.5rem',
              fontSize: '0.8rem',
              boxShadow: '0 4px 12px rgb(0 0 0 / 0.08)',
            }}
            labelStyle={{ color: 'var(--muted-foreground)', marginBottom: 4 }}
            formatter={(value, _name, item) => {
              const quantidade = (item?.payload as { quantidade?: number } | undefined)?.quantidade ?? 0
              const vendas = `${quantidade} ${quantidade === 1 ? 'venda' : 'vendas'}`
              return [financeiro ? `${formatCurrency(Number(value))} · ${vendas}` : vendas, null]
            }}
            labelFormatter={(label) => `Dia ${label}`}
          />
          <Area
            type="monotone"
            dataKey={metrica}
            stroke="var(--chart-1)"
            strokeWidth={2}
            strokeLinejoin="round"
            strokeLinecap="round"
            fill="url(#serie-fill)"
            activeDot={{ r: 4.5, strokeWidth: 2, stroke: 'var(--card)', fill: 'var(--chart-1)' }}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

// ------------------------------------------------------ receita por categoria

function ReceitaPorCategoria({ categorias }: { categorias: Dashboard['receitaPorCategoria'] }) {
  if (categorias.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">Sem vendas nos últimos 30 dias.</p>
  }

  return (
    <div className="space-y-4">
      <div className="flex h-3 w-full gap-[2px] overflow-hidden rounded-full" role="img" aria-label="Participação de cada categoria na receita">
        {categorias.map((categoria, indice) => (
          <div
            key={categoria.categoria}
            className="h-full first:rounded-l-full last:rounded-r-full"
            style={{
              width: `${categoria.participacaoPercentual}%`,
              backgroundColor: CORES_CATEGORIA[indice % CORES_CATEGORIA.length],
            }}
          />
        ))}
      </div>

      <ul className="space-y-2.5">
        {categorias.map((categoria, indice) => (
          <li key={categoria.categoria} className="flex items-center justify-between gap-3 text-sm">
            <span className="flex min-w-0 items-center gap-2">
              <span
                className="size-2.5 shrink-0 rounded-[3px]"
                style={{ backgroundColor: CORES_CATEGORIA[indice % CORES_CATEGORIA.length] }}
                aria-hidden="true"
              />
              <span className="truncate">{categoria.categoria}</span>
            </span>
            <span className="flex shrink-0 items-baseline gap-2">
              <span className="font-medium tabular-nums">
                {categoria.participacaoPercentual.toLocaleString('pt-BR', { maximumFractionDigits: 0 })}%
              </span>
              <span className="text-xs text-muted-foreground tabular-nums">
                {formatCurrency(categoria.receita)}
              </span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}

// ------------------------------------------------------------- top produtos

function TopProdutos({ produtos }: { produtos: Dashboard['topProdutos'] }) {
  if (produtos.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">Sem vendas nos últimos 30 dias.</p>
  }

  // Admin ranqueia por receita; Funcionário (receita null) por unidades vendidas.
  const financeiro = produtos[0].receita !== null
  const magnitude = (produto: Dashboard['topProdutos'][number]) =>
    financeiro ? (produto.receita ?? 0) : produto.quantidade
  const maior = Math.max(magnitude(produtos[0]), 1)

  return (
    <ul className="space-y-3.5">
      {produtos.map((produto, indice) => (
        <li key={produto.produtoId} className="space-y-1.5">
          <div className="flex items-baseline justify-between gap-3 text-sm">
            <span className="flex min-w-0 items-baseline gap-2">
              <span className="w-4 shrink-0 text-xs text-muted-foreground tabular-nums">{indice + 1}.</span>
              <span className="truncate font-medium">{produto.nome}</span>
            </span>
            <span className="shrink-0 text-sm font-medium tabular-nums">
              {financeiro ? formatCurrency(produto.receita ?? 0) : `${produto.quantidade} un`}
            </span>
          </div>
          <div className="ml-6 flex items-center gap-2">
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-primary"
                style={{ width: `${Math.max((magnitude(produto) / maior) * 100, 4)}%` }}
              />
            </div>
            {financeiro && (
              <span className="shrink-0 text-xs text-muted-foreground tabular-nums">
                {produto.quantidade} un
              </span>
            )}
          </div>
        </li>
      ))}
    </ul>
  )
}

// ------------------------------------------------------------ últimas vendas

function UltimasVendas({ vendas }: { vendas: UltimaVenda[] }) {
  if (vendas.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">Nenhuma venda registrada ainda.</p>
  }

  return (
    <ul className="divide-y divide-border">
      {vendas.map((venda) => (
        <li key={venda.id} className="flex items-center justify-between gap-3 py-2.5 first:pt-0 last:pb-0">
          <div className="min-w-0">
            <p className="truncate text-sm font-medium">
              {venda.clienteNome ?? 'Venda de balcão'}
              {venda.cancelada && (
                <Badge variant="destructive" className="ml-2 align-middle">
                  Cancelada
                </Badge>
              )}
            </p>
            <p className="text-xs text-muted-foreground">
              {formatDataHora(venda.dataHora)} · {venda.quantidadeItens}{' '}
              {venda.quantidadeItens === 1 ? 'item' : 'itens'}
            </p>
          </div>
          <span
            className={cn(
              'shrink-0 text-sm font-medium tabular-nums',
              venda.cancelada && 'text-muted-foreground line-through',
            )}
          >
            {formatCurrency(venda.total)}
          </span>
        </li>
      ))}
    </ul>
  )
}

// --------------------------------------------------------- estoque em alerta

function EstoqueEmAlerta({ produtos }: { produtos: Dashboard['estoqueEmAlerta'] }) {
  if (produtos.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        Nenhum produto abaixo do estoque mínimo. 👌
      </p>
    )
  }

  return (
    <ul className="divide-y divide-border">
      {produtos.map((produto) => (
        <li key={produto.produtoId} className="flex items-center justify-between gap-3 py-2.5 first:pt-0 last:pb-0">
          <div className="min-w-0">
            <p className="truncate text-sm font-medium">{produto.nome}</p>
            <p className="text-xs text-muted-foreground">
              {produto.sku} · {produto.estoqueAtual} de {produto.estoqueMinimo} mín.
            </p>
          </div>
          {produto.semEstoque ? (
            <Badge variant="destructive" className="shrink-0">
              <PackageX className="size-3" />
              Sem estoque
            </Badge>
          ) : (
            <Badge variant="warning" className="shrink-0">
              <AlertCircle className="size-3" />
              Baixo
            </Badge>
          )}
        </li>
      ))}
    </ul>
  )
}

// ------------------------------------------------------------------- página

function CardSecao({
  titulo,
  icone: Icone,
  acao,
  children,
  className,
}: {
  titulo: string
  icone: typeof Wallet
  acao?: ReactNode
  children: ReactNode
  className?: string
}) {
  return (
    <Card className={className}>
      <CardHeader className="flex-row items-center justify-between gap-2 space-y-0">
        <div className="flex items-center gap-2">
          <Icone className="size-4 text-muted-foreground" />
          <CardTitle>{titulo}</CardTitle>
        </div>
        {acao}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  )
}

export function DashboardPage() {
  const { user } = useAuth()
  const firstName = user?.name.split(' ')[0]

  const dashboardQuery = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
  })

  const dashboard = dashboardQuery.data
  const hoje = new Date().toLocaleDateString('pt-BR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {saudacao()}
            {firstName ? `, ${firstName}` : ''} 👋
          </h1>
          <p className="text-sm capitalize text-muted-foreground">{hoje}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link to="/insights">
              <Lightbulb className="size-4" />
              Ver insights
            </Link>
          </Button>
          <Button size="sm" asChild>
            <Link to="/vendas/nova">
              <Plus className="size-4" />
              Nova venda
            </Link>
          </Button>
        </div>
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
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="h-32 animate-pulse rounded-xl border border-border bg-muted/40" />
            ))}
          </div>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <div className="h-80 animate-pulse rounded-xl border border-border bg-muted/40 lg:col-span-2" />
            <div className="h-80 animate-pulse rounded-xl border border-border bg-muted/40" />
          </div>
        </div>
      )}

      {dashboard && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {dashboard.receita30Dias !== null ? (
              <KpiTile
                titulo="Receita (30 dias)"
                valor={formatCurrency(dashboard.receita30Dias.atual)}
                icone={Wallet}
                rodape={<Delta kpi={dashboard.receita30Dias} />}
                sparkline={<Sparkline dados={dashboard.vendasPorDia} metrica="total" />}
              />
            ) : (
              <KpiTile
                titulo="Vendas (30 dias)"
                valor={String(dashboard.vendas30Dias.atual)}
                icone={ShoppingCart}
                rodape={<Delta kpi={dashboard.vendas30Dias} />}
                sparkline={<Sparkline dados={dashboard.vendasPorDia} metrica="quantidade" />}
              />
            )}
            {dashboard.receita30Dias !== null && (
              <KpiTile
                titulo="Vendas (30 dias)"
                valor={String(dashboard.vendas30Dias.atual)}
                icone={ShoppingCart}
                rodape={<Delta kpi={dashboard.vendas30Dias} />}
              />
            )}
            {dashboard.ticketMedio30Dias !== null && (
              <KpiTile
                titulo="Ticket médio (30 dias)"
                valor={formatCurrency(dashboard.ticketMedio30Dias.atual)}
                icone={Receipt}
                rodape={<Delta kpi={dashboard.ticketMedio30Dias} />}
              />
            )}
            {dashboard.valorEstoque !== null ? (
              <KpiTile
                titulo="Valor em estoque"
                valor={formatCurrency(dashboard.valorEstoque)}
                icone={Package}
                rodape={<p className="text-xs text-muted-foreground">a preço de custo</p>}
              />
            ) : (
              <>
                <KpiTile
                  titulo="Clientes cadastrados"
                  valor={String(dashboard.clientesCadastrados)}
                  icone={Users}
                  rodape={<p className="text-xs text-muted-foreground">base ativa da loja</p>}
                />
                <KpiTile
                  titulo="Produtos cadastrados"
                  valor={String(dashboard.produtosCadastrados)}
                  icone={Package}
                  rodape={<p className="text-xs text-muted-foreground">no catálogo</p>}
                />
                <KpiTile
                  titulo="Estoque em alerta"
                  valor={String(dashboard.produtosAbaixoMinimo + dashboard.produtosSemEstoque)}
                  icone={PackageX}
                  rodape={
                    <p className="text-xs text-muted-foreground">
                      {dashboard.produtosSemEstoque} sem estoque · {dashboard.produtosAbaixoMinimo} baixos
                    </p>
                  }
                />
              </>
            )}
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <CardSecao
              titulo={
                dashboard.receita30Dias !== null
                  ? 'Receita dos últimos 30 dias'
                  : 'Vendas dos últimos 30 dias'
              }
              icone={TrendingUp}
              className="lg:col-span-2"
            >
              <GraficoVendas dados={dashboard.vendasPorDia} financeiro={dashboard.receita30Dias !== null} />
            </CardSecao>
            {dashboard.receita30Dias !== null ? (
              <CardSecao titulo="Receita por categoria" icone={Package}>
                <ReceitaPorCategoria categorias={dashboard.receitaPorCategoria} />
              </CardSecao>
            ) : (
              <CardSecao
                titulo="Estoque em alerta"
                icone={PackageX}
                acao={
                  <Button variant="ghost" size="sm" asChild className="text-xs text-muted-foreground">
                    <Link to="/produtos">
                      Ver produtos
                      <ArrowRight className="size-3.5" />
                    </Link>
                  </Button>
                }
              >
                <EstoqueEmAlerta produtos={dashboard.estoqueEmAlerta} />
              </CardSecao>
            )}
          </div>

          <div
            className={cn(
              'grid grid-cols-1 gap-4',
              dashboard.receita30Dias !== null ? 'lg:grid-cols-3' : 'lg:grid-cols-2',
            )}
          >
            <CardSecao titulo="Top produtos (30 dias)" icone={Trophy}>
              <TopProdutos produtos={dashboard.topProdutos} />
            </CardSecao>
            <CardSecao
              titulo="Últimas vendas"
              icone={ShoppingCart}
              acao={
                <Button variant="ghost" size="sm" asChild className="text-xs text-muted-foreground">
                  <Link to="/vendas">
                    Ver todas
                    <ArrowRight className="size-3.5" />
                  </Link>
                </Button>
              }
            >
              <UltimasVendas vendas={dashboard.ultimasVendas} />
            </CardSecao>
            {dashboard.receita30Dias !== null && (
              <CardSecao
                titulo="Estoque em alerta"
                icone={PackageX}
                acao={
                  <Button variant="ghost" size="sm" asChild className="text-xs text-muted-foreground">
                    <Link to="/produtos">
                      Ver produtos
                      <ArrowRight className="size-3.5" />
                    </Link>
                  </Button>
                }
              >
                <EstoqueEmAlerta produtos={dashboard.estoqueEmAlerta} />
              </CardSecao>
            )}
          </div>

          <p className="text-center text-xs text-muted-foreground">
            Histórico completo:{' '}
            {dashboard.receitaTotal !== null && <>{formatCurrency(dashboard.receitaTotal)} em </>}
            {dashboard.quantidadeVendas} {dashboard.quantidadeVendas === 1 ? 'venda' : 'vendas'} ·{' '}
            {dashboard.clientesCadastrados} clientes · {dashboard.produtosCadastrados} produtos cadastrados
          </p>
        </>
      )}
    </div>
  )
}
