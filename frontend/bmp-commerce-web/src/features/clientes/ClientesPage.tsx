import * as React from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Pencil,
  Plus,
  RotateCw,
  Search,
  Trash2,
  UserCheck,
  UserPlus,
  UserX,
  Users,
  X,
} from 'lucide-react'
import { listClientes } from '@/api/clientes'
import type { Cliente } from '@/types/cliente'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Select } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { StatCard } from '@/components/layout/StatCard'
import { ClienteFormDialog } from '@/features/clientes/ClienteFormDialog'
import { DeleteClienteDialog } from '@/features/clientes/DeleteClienteDialog'

const PAGE_SIZE = 10

type StatusFilter = 'todos' | 'ativos' | 'inativos'

function formatCpfCnpj(valor: string | null) {
  if (!valor) {
    return '—'
  }

  if (valor.length === 11) {
    return `${valor.slice(0, 3)}.${valor.slice(3, 6)}.${valor.slice(6, 9)}-${valor.slice(9)}`
  }

  if (valor.length === 14) {
    return `${valor.slice(0, 2)}.${valor.slice(2, 5)}.${valor.slice(5, 8)}/${valor.slice(8, 12)}-${valor.slice(12)}`
  }

  return valor
}

export function ClientesPage() {
  const [search, setSearch] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState<StatusFilter>('todos')
  const [page, setPage] = React.useState(1)

  const [formOpen, setFormOpen] = React.useState(false)
  const [editingCliente, setEditingCliente] = React.useState<Cliente | null>(null)
  const [deletingCliente, setDeletingCliente] = React.useState<Cliente | null>(null)

  const clientesQuery = useQuery({
    queryKey: ['clientes'],
    queryFn: listClientes,
  })

  const clientes = clientesQuery.data ?? []

  const stats = React.useMemo(() => {
    const ativos = clientes.filter((cliente) => cliente.ativo).length
    const inicioDoMes = new Date()
    inicioDoMes.setDate(1)
    inicioDoMes.setHours(0, 0, 0, 0)
    const novosEsteMes = clientes.filter((cliente) => new Date(cliente.createdAt) >= inicioDoMes).length

    return { total: clientes.length, ativos, inativos: clientes.length - ativos, novosEsteMes }
  }, [clientes])

  const filtered = React.useMemo(() => {
    const term = search.trim().toLowerCase()

    return clientes.filter((cliente) => {
      const matchesSearch =
        !term ||
        cliente.nome.toLowerCase().includes(term) ||
        (cliente.email ?? '').toLowerCase().includes(term) ||
        (cliente.cidade ?? '').toLowerCase().includes(term) ||
        (cliente.cpfCnpj ?? '').includes(term.replace(/\D/g, '') || term)
      const matchesStatus =
        statusFilter === 'todos' || (statusFilter === 'ativos' ? cliente.ativo : !cliente.ativo)

      return matchesSearch && matchesStatus
    })
  }, [clientes, search, statusFilter])

  React.useEffect(() => {
    setPage(1)
  }, [search, statusFilter])

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const currentPage = Math.min(page, totalPages)
  const paginated = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE)

  function handleNovoCliente() {
    setEditingCliente(null)
    setFormOpen(true)
  }

  function handleEditarCliente(cliente: Cliente) {
    setEditingCliente(cliente)
    setFormOpen(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Clientes</h1>
          <p className="text-sm text-muted-foreground">Gerencie os clientes da sua empresa.</p>
        </div>

        <Button onClick={handleNovoCliente}>
          <Plus className="size-4" />
          Novo Cliente
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total de clientes" value={String(stats.total)} icon={Users} />
        <StatCard title="Clientes ativos" value={String(stats.ativos)} icon={UserCheck} tone="emerald" />
        <StatCard title="Clientes inativos" value={String(stats.inativos)} icon={UserX} tone="amber" />
        <StatCard title="Novos este mês" value={String(stats.novosEsteMes)} icon={UserPlus} tone="blue" />
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative max-w-sm flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Buscar por nome, email, cidade ou CPF/CNPJ..."
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

      {clientesQuery.isError && (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border p-12 text-center">
          <AlertCircle className="size-8 text-destructive" />
          <p className="text-sm text-muted-foreground">Não foi possível carregar os clientes.</p>
          <Button variant="outline" size="sm" onClick={() => clientesQuery.refetch()}>
            <RotateCw className="size-4" />
            Tentar novamente
          </Button>
        </div>
      )}

      {clientesQuery.isPending && !clientesQuery.isError && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>CPF/CNPJ</TableHead>
              <TableHead>Telefone</TableHead>
              <TableHead>Cidade/UF</TableHead>
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

      {!clientesQuery.isPending && !clientesQuery.isError && filtered.length === 0 && (
        <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border p-12 text-center">
          <div className="flex size-12 items-center justify-center rounded-full bg-muted">
            <Users className="size-6 text-muted-foreground" />
          </div>
          <h2 className="text-lg font-semibold">
            {search || statusFilter !== 'todos' ? 'Nenhum cliente encontrado' : 'Nenhum cliente cadastrado'}
          </h2>
          <p className="max-w-sm text-sm text-muted-foreground">
            {search || statusFilter !== 'todos'
              ? 'Tente ajustar a busca ou o filtro de status.'
              : 'Cadastre o primeiro cliente da sua empresa para começar.'}
          </p>
          {!search && statusFilter === 'todos' && (
            <Button onClick={handleNovoCliente}>
              <Plus className="size-4" />
              Novo Cliente
            </Button>
          )}
        </div>
      )}

      {!clientesQuery.isPending && !clientesQuery.isError && filtered.length > 0 && (
        <div className="space-y-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>CPF/CNPJ</TableHead>
                <TableHead>Telefone</TableHead>
                <TableHead>Cidade/UF</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginated.map((cliente) => (
                <TableRow key={cliente.id}>
                  <TableCell>
                    <div className="font-medium">{cliente.nome}</div>
                    {cliente.email && <div className="text-xs text-muted-foreground">{cliente.email}</div>}
                  </TableCell>
                  <TableCell className="text-muted-foreground tabular-nums">
                    {formatCpfCnpj(cliente.cpfCnpj)}
                  </TableCell>
                  <TableCell className="text-muted-foreground">{cliente.telefone ?? '—'}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {cliente.cidade ? `${cliente.cidade}${cliente.estado ? ` / ${cliente.estado}` : ''}` : '—'}
                  </TableCell>
                  <TableCell>
                    <Badge variant={cliente.ativo ? 'success' : 'muted'}>
                      {cliente.ativo ? 'Ativo' : 'Inativo'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEditarCliente(cliente)}
                        aria-label={`Editar ${cliente.nome}`}
                      >
                        <Pencil className="size-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setDeletingCliente(cliente)}
                        aria-label={`Excluir ${cliente.nome}`}
                      >
                        <Trash2 className="size-4 text-destructive" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <div className="flex flex-col items-center justify-between gap-3 sm:flex-row">
            <p className="text-sm text-muted-foreground">
              Mostrando {(currentPage - 1) * PAGE_SIZE + 1}–{Math.min(currentPage * PAGE_SIZE, filtered.length)} de{' '}
              {filtered.length} clientes
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

      <ClienteFormDialog open={formOpen} onOpenChange={setFormOpen} cliente={editingCliente} />
      <DeleteClienteDialog cliente={deletingCliente} onOpenChange={(open) => !open && setDeletingCliente(null)} />
    </div>
  )
}
