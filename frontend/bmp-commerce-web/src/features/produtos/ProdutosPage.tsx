import * as React from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Package,
  Pencil,
  Plus,
  RotateCw,
  Search,
  Trash2,
  Wallet,
  X,
} from 'lucide-react'
import { listProdutos } from '@/api/produtos'
import { cn, formatCurrency } from '@/lib/utils'
import type { Produto } from '@/types/produto'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { StatCard } from '@/components/layout/StatCard'
import { ProdutoFormDialog } from '@/features/produtos/ProdutoFormDialog'
import { DeleteProdutoDialog } from '@/features/produtos/DeleteProdutoDialog'

const PAGE_SIZE = 10

type StatusFilter = 'todos' | 'ativos' | 'inativos'

export function ProdutosPage() {
  const [search, setSearch] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState<StatusFilter>('todos')
  const [page, setPage] = React.useState(1)

  const [formOpen, setFormOpen] = React.useState(false)
  const [editingProduto, setEditingProduto] = React.useState<Produto | null>(null)
  const [deletingProduto, setDeletingProduto] = React.useState<Produto | null>(null)

  const produtosQuery = useQuery({
    queryKey: ['produtos'],
    queryFn: () => listProdutos(),
  })

  const produtos = produtosQuery.data ?? []

  const stats = React.useMemo(() => {
    const ativos = produtos.filter((produto) => produto.ativo).length
    const abaixoDoMinimo = produtos.filter((produto) => produto.estoqueAtual < produto.estoqueMinimo).length
    const valorTotalEstoque = produtos.reduce(
      (total, produto) => total + produto.precoCusto * produto.estoqueAtual,
      0,
    )

    return { total: produtos.length, ativos, abaixoDoMinimo, valorTotalEstoque }
  }, [produtos])

  const filtered = React.useMemo(() => {
    const term = search.trim().toLowerCase()

    return produtos.filter((produto) => {
      const matchesSearch =
        !term || produto.nome.toLowerCase().includes(term) || produto.sku.toLowerCase().includes(term)
      const matchesStatus =
        statusFilter === 'todos' || (statusFilter === 'ativos' ? produto.ativo : !produto.ativo)

      return matchesSearch && matchesStatus
    })
  }, [produtos, search, statusFilter])

  React.useEffect(() => {
    setPage(1)
  }, [search, statusFilter])

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const currentPage = Math.min(page, totalPages)
  const paginated = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE)

  function handleNovoProduto() {
    setEditingProduto(null)
    setFormOpen(true)
  }

  function handleEditarProduto(produto: Produto) {
    setEditingProduto(produto)
    setFormOpen(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Produtos</h1>
          <p className="text-sm text-muted-foreground">Gerencie os produtos da sua empresa.</p>
        </div>

        <Button onClick={handleNovoProduto}>
          <Plus className="size-4" />
          Novo Produto
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total cadastrados" value={String(stats.total)} icon={Package} />
        <StatCard title="Produtos ativos" value={String(stats.ativos)} icon={CheckCircle2} tone="emerald" />
        <StatCard
          title="Abaixo do estoque mínimo"
          value={String(stats.abaixoDoMinimo)}
          icon={AlertTriangle}
          tone="amber"
        />
        <StatCard title="Valor total em estoque" value={formatCurrency(stats.valorTotalEstoque)} icon={Wallet} tone="blue" />
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative max-w-sm flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Buscar por nome ou SKU..."
            className="pl-9 pr-9"
          />
          {search && (
            <button
              type="button"
              onClick={() => setSearch('')}
              aria-label="Limpar busca"
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
            >
              <X className="size-4" />
            </button>
          )}
        </div>

        <Select
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value as StatusFilter)}
          className="sm:w-40"
          aria-label="Filtrar por status"
        >
          <option value="todos">Todos</option>
          <option value="ativos">Ativos</option>
          <option value="inativos">Inativos</option>
        </Select>
      </div>

      {produtosQuery.isError && (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border p-12 text-center">
          <AlertCircle className="size-8 text-destructive" />
          <p className="text-sm text-muted-foreground">Não foi possível carregar os produtos.</p>
          <Button variant="outline" size="sm" onClick={() => produtosQuery.refetch()}>
            <RotateCw className="size-4" />
            Tentar novamente
          </Button>
        </div>
      )}

      {produtosQuery.isPending && !produtosQuery.isError && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>SKU</TableHead>
              <TableHead className="text-right">Preço</TableHead>
              <TableHead className="text-right">Estoque</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {Array.from({ length: 4 }).map((_, index) => (
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

      {!produtosQuery.isPending && !produtosQuery.isError && filtered.length === 0 && (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border p-12 text-center">
          <div className="flex size-12 items-center justify-center rounded-full bg-muted">
            <Package className="size-6 text-muted-foreground" />
          </div>
          <h2 className="text-lg font-semibold">
            {search || statusFilter !== 'todos' ? 'Nenhum produto encontrado' : 'Nenhum produto cadastrado'}
          </h2>
          <p className="max-w-sm text-sm text-muted-foreground">
            {search || statusFilter !== 'todos'
              ? 'Tente ajustar a busca ou o filtro de status.'
              : 'Cadastre o primeiro produto da sua empresa para começar.'}
          </p>
          {!search && statusFilter === 'todos' && (
            <Button onClick={handleNovoProduto}>
              <Plus className="size-4" />
              Novo Produto
            </Button>
          )}
        </div>
      )}

      {!produtosQuery.isPending && !produtosQuery.isError && filtered.length > 0 && (
        <div className="space-y-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>SKU</TableHead>
                <TableHead className="text-right">Preço</TableHead>
                <TableHead className="text-right">Estoque</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginated.map((produto) => {
                const estoqueBaixo = produto.estoqueAtual < produto.estoqueMinimo

                return (
                  <TableRow key={produto.id}>
                    <TableCell className="font-medium">{produto.nome}</TableCell>
                    <TableCell className="text-muted-foreground">{produto.sku}</TableCell>
                    <TableCell className="text-right tabular-nums">{formatCurrency(produto.precoVenda)}</TableCell>
                    <TableCell className="text-right tabular-nums">
                      <span className={cn(estoqueBaixo && 'font-medium text-amber-600 dark:text-amber-400')}>
                        {produto.estoqueAtual}
                      </span>
                      {estoqueBaixo && (
                        <span className="ml-1.5 text-xs text-amber-600 dark:text-amber-400">abaixo do mínimo</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant={produto.ativo ? 'success' : 'muted'}>
                        {produto.ativo ? 'Ativo' : 'Inativo'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleEditarProduto(produto)}
                          aria-label={`Editar ${produto.nome}`}
                        >
                          <Pencil className="size-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setDeletingProduto(produto)}
                          aria-label={`Excluir ${produto.nome}`}
                        >
                          <Trash2 className="size-4 text-destructive" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>

          <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
            <p className="text-sm text-muted-foreground">
              Mostrando {(currentPage - 1) * PAGE_SIZE + 1}–{Math.min(currentPage * PAGE_SIZE, filtered.length)} de{' '}
              {filtered.length} produtos
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

      <ProdutoFormDialog open={formOpen} onOpenChange={setFormOpen} produto={editingProduto} />
      <DeleteProdutoDialog produto={deletingProduto} onOpenChange={(open) => !open && setDeletingProduto(null)} />
    </div>
  )
}
