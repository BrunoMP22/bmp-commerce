import * as React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  AlertCircle,
  Ban,
  ChevronLeft,
  ChevronRight,
  Eye,
  Plus,
  RotateCw,
  Search,
  ShoppingCart,
  X,
} from 'lucide-react'
import { listVendas } from '@/api/vendas'
import { listClientes } from '@/api/clientes'
import { formatCurrency } from '@/lib/utils'
import type { Venda } from '@/types/venda'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { VendaDetailsDialog } from '@/features/vendas/VendaDetailsDialog'
import { CancelarVendaDialog } from '@/features/vendas/CancelarVendaDialog'

const PAGE_SIZE = 10

type StatusFilter = 'todas' | 'concluidas' | 'canceladas'
type Ordenacao = 'data-desc' | 'data-asc' | 'total-desc' | 'total-asc'

function formatDataHora(dataHora: string) {
  return new Date(dataHora).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

export function VendasPage() {
  const navigate = useNavigate()

  const [search, setSearch] = React.useState('')
  const [dataInicio, setDataInicio] = React.useState('')
  const [dataFim, setDataFim] = React.useState('')
  const [clienteFilter, setClienteFilter] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState<StatusFilter>('todas')
  const [ordenacao, setOrdenacao] = React.useState<Ordenacao>('data-desc')
  const [page, setPage] = React.useState(1)

  const [detalhesVenda, setDetalhesVenda] = React.useState<Venda | null>(null)
  const [cancelandoVenda, setCancelandoVenda] = React.useState<Venda | null>(null)

  const vendasQuery = useQuery({ queryKey: ['vendas'], queryFn: listVendas })
  const clientesQuery = useQuery({ queryKey: ['clientes'], queryFn: listClientes })

  const vendas = vendasQuery.data ?? []
  const clientes = clientesQuery.data ?? []

  const filtered = React.useMemo(() => {
    const term = search.trim().toLowerCase()

    const resultado = vendas.filter((venda) => {
      const matchesSearch = !term || (venda.clienteNome ?? 'balcão').toLowerCase().includes(term)
      const matchesCliente = !clienteFilter || venda.clienteId === clienteFilter
      const matchesStatus =
        statusFilter === 'todas' || (statusFilter === 'canceladas' ? venda.cancelada : !venda.cancelada)

      const dataVenda = new Date(venda.dataHora)
      const matchesInicio = !dataInicio || dataVenda >= new Date(`${dataInicio}T00:00:00`)
      const matchesFim = !dataFim || dataVenda <= new Date(`${dataFim}T23:59:59`)

      return matchesSearch && matchesCliente && matchesStatus && matchesInicio && matchesFim
    })

    return resultado.sort((a, b) => {
      switch (ordenacao) {
        case 'data-asc':
          return new Date(a.dataHora).getTime() - new Date(b.dataHora).getTime()
        case 'total-desc':
          return b.total - a.total
        case 'total-asc':
          return a.total - b.total
        default:
          return new Date(b.dataHora).getTime() - new Date(a.dataHora).getTime()
      }
    })
  }, [vendas, search, clienteFilter, statusFilter, dataInicio, dataFim, ordenacao])

  React.useEffect(() => {
    setPage(1)
  }, [search, clienteFilter, statusFilter, dataInicio, dataFim, ordenacao])

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const currentPage = Math.min(page, totalPages)
  const paginated = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE)

  const temFiltros = Boolean(search || clienteFilter || statusFilter !== 'todas' || dataInicio || dataFim)

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Vendas</h1>
          <p className="text-sm text-muted-foreground">Acompanhe e registre as vendas da sua empresa.</p>
        </div>

        <Button onClick={() => navigate('/vendas/nova')}>
          <Plus className="size-4" />
          Nova Venda
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <div className="space-y-1">
          <Label htmlFor="busca" className="text-xs text-muted-foreground">
            Buscar cliente
          </Label>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="busca"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Nome do cliente..."
              className="pl-9 pr-8"
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch('')}
                aria-label="Limpar busca"
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
              >
                <X className="size-4" />
              </button>
            )}
          </div>
        </div>

        <div className="space-y-1">
          <Label htmlFor="dataInicio" className="text-xs text-muted-foreground">
            De
          </Label>
          <Input
            id="dataInicio"
            type="date"
            value={dataInicio}
            onChange={(event) => setDataInicio(event.target.value)}
          />
        </div>

        <div className="space-y-1">
          <Label htmlFor="dataFim" className="text-xs text-muted-foreground">
            Até
          </Label>
          <Input id="dataFim" type="date" value={dataFim} onChange={(event) => setDataFim(event.target.value)} />
        </div>

        <div className="space-y-1">
          <Label htmlFor="clienteFilter" className="text-xs text-muted-foreground">
            Cliente
          </Label>
          <Select
            id="clienteFilter"
            value={clienteFilter}
            onChange={(event) => setClienteFilter(event.target.value)}
          >
            <option value="">Todos</option>
            {clientes.map((cliente) => (
              <option key={cliente.id} value={cliente.id}>
                {cliente.nome}
              </option>
            ))}
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <Label htmlFor="statusFilter" className="text-xs text-muted-foreground">
              Status
            </Label>
            <Select
              id="statusFilter"
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value as StatusFilter)}
            >
              <option value="todas">Todas</option>
              <option value="concluidas">Concluídas</option>
              <option value="canceladas">Canceladas</option>
            </Select>
          </div>

          <div className="space-y-1">
            <Label htmlFor="ordenacao" className="text-xs text-muted-foreground">
              Ordenar
            </Label>
            <Select
              id="ordenacao"
              value={ordenacao}
              onChange={(event) => setOrdenacao(event.target.value as Ordenacao)}
            >
              <option value="data-desc">Mais recentes</option>
              <option value="data-asc">Mais antigas</option>
              <option value="total-desc">Maior total</option>
              <option value="total-asc">Menor total</option>
            </Select>
          </div>
        </div>
      </div>

      {vendasQuery.isError && (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border p-12 text-center">
          <AlertCircle className="size-8 text-destructive" />
          <p className="text-sm text-muted-foreground">Não foi possível carregar as vendas.</p>
          <Button variant="outline" size="sm" onClick={() => vendasQuery.refetch()}>
            <RotateCw className="size-4" />
            Tentar novamente
          </Button>
        </div>
      )}

      {vendasQuery.isPending && !vendasQuery.isError && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Data</TableHead>
              <TableHead>Cliente</TableHead>
              <TableHead className="text-center">Itens</TableHead>
              <TableHead className="text-right">Total</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {Array.from({ length: 5 }).map((_, index) => (
              <TableRow key={index}>
                {Array.from({ length: 6 }).map((__, cell) => (
                  <TableCell key={cell}>
                    <div className="h-4 w-full max-w-32 animate-pulse rounded bg-muted" />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {!vendasQuery.isPending && !vendasQuery.isError && filtered.length === 0 && (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border p-12 text-center">
          <div className="flex size-12 items-center justify-center rounded-full bg-muted">
            <ShoppingCart className="size-6 text-muted-foreground" />
          </div>
          <h2 className="text-lg font-semibold">
            {temFiltros ? 'Nenhuma venda encontrada' : 'Nenhuma venda registrada'}
          </h2>
          <p className="max-w-sm text-sm text-muted-foreground">
            {temFiltros
              ? 'Tente ajustar os filtros ou o período.'
              : 'Registre a primeira venda da sua empresa para começar.'}
          </p>
          {!temFiltros && (
            <Button onClick={() => navigate('/vendas/nova')}>
              <Plus className="size-4" />
              Nova Venda
            </Button>
          )}
        </div>
      )}

      {!vendasQuery.isPending && !vendasQuery.isError && filtered.length > 0 && (
        <div className="space-y-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Data</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead className="text-center">Itens</TableHead>
                <TableHead className="text-right">Total</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginated.map((venda) => (
                <TableRow key={venda.id}>
                  <TableCell className="tabular-nums">{formatDataHora(venda.dataHora)}</TableCell>
                  <TableCell className="font-medium">{venda.clienteNome ?? 'Balcão'}</TableCell>
                  <TableCell className="text-center tabular-nums">{venda.quantidadeItens}</TableCell>
                  <TableCell className="text-right font-medium tabular-nums">
                    {formatCurrency(venda.total)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={venda.cancelada ? 'destructive' : 'success'}>
                      {venda.cancelada ? 'Cancelada' : 'Concluída'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setDetalhesVenda(venda)}
                        aria-label="Ver detalhes da venda"
                      >
                        <Eye className="size-4" />
                      </Button>
                      {!venda.cancelada && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setCancelandoVenda(venda)}
                          aria-label="Cancelar venda"
                        >
                          <Ban className="size-4 text-destructive" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
            <p className="text-sm text-muted-foreground">
              Mostrando {(currentPage - 1) * PAGE_SIZE + 1}–{Math.min(currentPage * PAGE_SIZE, filtered.length)} de{' '}
              {filtered.length} vendas
            </p>

            {totalPages > 1 && (
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={currentPage === 1}
                  onClick={() => setPage((current) => current - 1)}
                >
                  <ChevronLeft className="size-4" />
                  Anterior
                </Button>
                <span className="text-sm text-muted-foreground">
                  Página {currentPage} de {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={currentPage === totalPages}
                  onClick={() => setPage((current) => current + 1)}
                >
                  Próxima
                  <ChevronRight className="size-4" />
                </Button>
              </div>
            )}
          </div>
        </div>
      )}

      <VendaDetailsDialog venda={detalhesVenda} onOpenChange={(open) => !open && setDetalhesVenda(null)} />
      <CancelarVendaDialog venda={cancelandoVenda} onOpenChange={(open) => !open && setCancelandoVenda(null)} />
    </div>
  )
}
