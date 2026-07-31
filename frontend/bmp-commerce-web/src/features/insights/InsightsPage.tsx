import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  AlertCircle,
  AlertTriangle,
  CalendarDays,
  Crown,
  Hourglass,
  Info,
  Lightbulb,
  PackageX,
  Percent,
  PieChart,
  Receipt,
  RotateCw,
  Sparkles,
  Store,
  TrendingDown,
  TrendingUp,
  UserX,
  Users,
  Wallet,
  type LucideIcon,
} from 'lucide-react'
import { getInsights } from '@/api/insights'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import type { Insight, SeveridadeInsight } from '@/types/insight'

type Filtro = 'Todos' | SeveridadeInsight

const severidadeStyles: Record<
  SeveridadeInsight,
  { accent: string; iconBox: string; badge: string; destaque: string; label: string }
> = {
  Alerta: {
    accent: 'bg-destructive',
    iconBox: 'bg-destructive/10 text-destructive',
    badge: 'bg-destructive/10 text-destructive',
    destaque: 'text-destructive',
    label: 'Alerta',
  },
  Oportunidade: {
    accent: 'bg-emerald-500',
    iconBox: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
    badge: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
    destaque: 'text-emerald-600 dark:text-emerald-400',
    label: 'Oportunidade',
  },
  Info: {
    accent: 'bg-blue-500',
    iconBox: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
    badge: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
    destaque: 'text-blue-600 dark:text-blue-400',
    label: 'Informativo',
  },
}

const iconePorTipo: Record<string, LucideIcon> = {
  'faturamento-em-movimento': TrendingUp,
  'ticket-medio-em-movimento': Receipt,
  'margem-em-movimento': Percent,
  'campeao-de-lucro': Crown,
  'concentracao-de-produto': PieChart,
  'previsao-de-ruptura': Hourglass,
  'produtos-encalhados': PackageX,
  'capital-parado': Wallet,
  'clientes-sumidos': UserX,
  'concentracao-de-clientes': Users,
  'melhor-dia-da-semana': CalendarDays,
  'vendas-de-balcao': Store,
}

const iconePorSeveridade: Record<SeveridadeInsight, LucideIcon> = {
  Alerta: AlertTriangle,
  Oportunidade: TrendingUp,
  Info: Info,
}

function iconeDoInsight(insight: Insight): LucideIcon {
  // Faturamento/ticket/margem em queda merecem a seta para baixo.
  if (insight.severidade === 'Alerta' && insight.valor !== null && insight.valor < 0) {
    return TrendingDown
  }
  return iconePorTipo[insight.tipo] ?? iconePorSeveridade[insight.severidade]
}

function InsightCard({ insight }: { insight: Insight }) {
  const styles = severidadeStyles[insight.severidade]
  const Icone = iconeDoInsight(insight)

  return (
    <Card className="relative overflow-hidden">
      <span className={cn('absolute inset-y-0 left-0 w-1', styles.accent)} aria-hidden="true" />
      <CardContent className="space-y-3 p-5 pl-6">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className={cn('flex size-9 shrink-0 items-center justify-center rounded-lg', styles.iconBox)}>
              <Icone className="size-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold leading-tight">{insight.titulo}</h3>
              <span
                className={cn(
                  'mt-0.5 inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium',
                  styles.badge,
                )}
              >
                {styles.label}
              </span>
            </div>
          </div>
          {insight.destaque && (
            <p className={cn('shrink-0 text-xl font-bold tracking-tight tabular-nums', styles.destaque)}>
              {insight.destaque}
            </p>
          )}
        </div>

        <p className="text-sm leading-relaxed text-foreground">{insight.mensagem}</p>

        {insight.acao && (
          <div className="flex items-start gap-2 rounded-lg bg-muted/60 p-3">
            <Lightbulb className="mt-0.5 size-4 shrink-0 text-amber-500" />
            <p className="text-sm leading-relaxed text-muted-foreground">
              <span className="font-medium text-foreground">Ação sugerida: </span>
              {insight.acao}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

interface FiltroChipProps {
  ativo: boolean
  onClick: () => void
  children: React.ReactNode
}

function FiltroChip({ ativo, onClick, children }: FiltroChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors',
        ativo
          ? 'border-primary bg-primary/10 text-primary'
          : 'border-border bg-transparent text-muted-foreground hover:bg-muted',
      )}
    >
      {children}
    </button>
  )
}

export function InsightsPage() {
  const [filtro, setFiltro] = useState<Filtro>('Todos')

  const insightsQuery = useQuery({
    queryKey: ['insights'],
    queryFn: getInsights,
  })

  const dados = insightsQuery.data
  const visiveis = (dados?.insights ?? []).filter(
    (insight) => filtro === 'Todos' || insight.severidade === filtro,
  )

  const horaGeracao = dados
    ? new Date(dados.geradoEm).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    : null

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Insights</h1>
          <p className="text-sm text-muted-foreground">
            Não mostramos dados. Explicamos o seu negócio — em frases, com o que fazer a seguir.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {horaGeracao && (
            <span className="text-xs text-muted-foreground">Gerado às {horaGeracao}</span>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={() => insightsQuery.refetch()}
            disabled={insightsQuery.isFetching}
          >
            <RotateCw className={cn('size-4', insightsQuery.isFetching && 'animate-spin')} />
            Atualizar
          </Button>
        </div>
      </div>

      {insightsQuery.isError && (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border p-12 text-center">
          <AlertCircle className="size-8 text-destructive" />
          <p className="text-sm text-muted-foreground">Não foi possível gerar os insights.</p>
          <Button variant="outline" size="sm" onClick={() => insightsQuery.refetch()}>
            <RotateCw className="size-4" />
            Tentar novamente
          </Button>
        </div>
      )}

      {insightsQuery.isPending && !insightsQuery.isError && (
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="h-44 animate-pulse rounded-xl border border-border bg-muted/40" />
          ))}
        </div>
      )}

      {dados && (
        <>
          <div className="flex flex-wrap items-center gap-2">
            <FiltroChip ativo={filtro === 'Todos'} onClick={() => setFiltro('Todos')}>
              Todos
              <span className="tabular-nums">{dados.insights.length}</span>
            </FiltroChip>
            <FiltroChip ativo={filtro === 'Alerta'} onClick={() => setFiltro('Alerta')}>
              <AlertTriangle className="size-3.5 text-destructive" />
              Alertas
              <span className="tabular-nums">{dados.resumo.alertas}</span>
            </FiltroChip>
            <FiltroChip ativo={filtro === 'Oportunidade'} onClick={() => setFiltro('Oportunidade')}>
              <TrendingUp className="size-3.5 text-emerald-600 dark:text-emerald-400" />
              Oportunidades
              <span className="tabular-nums">{dados.resumo.oportunidades}</span>
            </FiltroChip>
            <FiltroChip ativo={filtro === 'Info'} onClick={() => setFiltro('Info')}>
              <Info className="size-3.5 text-blue-600 dark:text-blue-400" />
              Informativos
              <span className="tabular-nums">{dados.resumo.informativos}</span>
            </FiltroChip>
          </div>

          {dados.insights.length === 0 ? (
            <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border p-12 text-center">
              <Sparkles className="size-8 text-muted-foreground" />
              <p className="text-sm font-medium">Tudo quieto por aqui</p>
              <p className="max-w-md text-sm text-muted-foreground">
                O motor precisa de movimento para falar: registre vendas, produtos e clientes e os
                insights aparecem sozinhos — sem configuração.
              </p>
            </div>
          ) : visiveis.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
              Nenhum insight nessa categoria agora — o que é uma boa notícia.
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
              {visiveis.map((insight) => (
                <InsightCard key={insight.tipo} insight={insight} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
