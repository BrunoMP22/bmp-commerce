import * as React from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  Loader2,
  Minus,
  Package,
  Plus,
  Search,
  ShoppingCart,
  Trash2,
  UserCircle,
  X,
} from 'lucide-react'
import { toast } from 'sonner'
import { listProdutos } from '@/api/produtos'
import { listClientes } from '@/api/clientes'
import { registrarVenda } from '@/api/vendas'
import { getErrorMessage } from '@/lib/errors'
import { cn, formatCurrency } from '@/lib/utils'
import type { Produto } from '@/types/produto'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

interface ItemCarrinho {
  produto: Produto
  quantidade: number
}

export function NovaVendaPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [clienteId, setClienteId] = React.useState('')
  const [busca, setBusca] = React.useState('')
  const [itens, setItens] = React.useState<ItemCarrinho[]>([])

  const produtosQuery = useQuery({ queryKey: ['produtos'], queryFn: () => listProdutos() })
  const clientesQuery = useQuery({ queryKey: ['clientes'], queryFn: listClientes })

  const clientesAtivos = (clientesQuery.data ?? []).filter((cliente) => cliente.ativo)

  const produtosDisponiveis = React.useMemo(() => {
    const term = busca.trim().toLowerCase()

    return (produtosQuery.data ?? [])
      .filter((produto) => produto.ativo && produto.estoqueAtual > 0)
      .filter(
        (produto) =>
          !term || produto.nome.toLowerCase().includes(term) || produto.sku.toLowerCase().includes(term),
      )
      .slice(0, 6)
  }, [produtosQuery.data, busca])

  const totais = React.useMemo(() => {
    const subtotal = itens.reduce((soma, item) => soma + item.produto.precoVenda * item.quantidade, 0)
    const quantidade = itens.reduce((soma, item) => soma + item.quantidade, 0)
    return { subtotal, quantidade, total: subtotal }
  }, [itens])

  function quantidadeNoCarrinho(produtoId: string) {
    return itens.find((item) => item.produto.id === produtoId)?.quantidade ?? 0
  }

  function adicionarProduto(produto: Produto) {
    setItens((atual) => {
      const existente = atual.find((item) => item.produto.id === produto.id)

      if (!existente) {
        return [...atual, { produto, quantidade: 1 }]
      }

      if (existente.quantidade >= produto.estoqueAtual) {
        toast.warning(`Estoque disponível de ${produto.nome}: ${produto.estoqueAtual}.`)
        return atual
      }

      return atual.map((item) =>
        item.produto.id === produto.id ? { ...item, quantidade: item.quantidade + 1 } : item,
      )
    })
  }

  function alterarQuantidade(produtoId: string, quantidade: number) {
    setItens((atual) =>
      atual.map((item) => {
        if (item.produto.id !== produtoId) {
          return item
        }

        const limitada = Math.max(1, Math.min(quantidade, item.produto.estoqueAtual))

        if (quantidade > item.produto.estoqueAtual) {
          toast.warning(`Estoque disponível de ${item.produto.nome}: ${item.produto.estoqueAtual}.`)
        }

        return { ...item, quantidade: limitada }
      }),
    )
  }

  function removerItem(produtoId: string) {
    setItens((atual) => atual.filter((item) => item.produto.id !== produtoId))
  }

  const mutation = useMutation({
    mutationFn: () =>
      registrarVenda({
        clienteId: clienteId || null,
        itens: itens.map((item) => ({ produtoId: item.produto.id, quantidade: item.quantidade })),
      }),
    onSuccess: (venda) => {
      toast.success(`Venda de ${formatCurrency(venda.total)} registrada com sucesso.`)
      queryClient.invalidateQueries({ queryKey: ['produtos'] })
      queryClient.invalidateQueries({ queryKey: ['vendas'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      navigate('/vendas')
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, 'Não foi possível registrar a venda.'))
      // O estoque pode ter mudado desde o carregamento — atualiza a lista de produtos.
      queryClient.invalidateQueries({ queryKey: ['produtos'] })
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Nova Venda</h1>
          <p className="text-sm text-muted-foreground">
            Selecione o cliente, adicione os produtos e finalize a venda.
          </p>
        </div>

        <Button variant="outline" onClick={() => navigate('/vendas')}>
          <ArrowLeft className="size-4" />
          Voltar para Vendas
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader className="flex-row items-center gap-2 space-y-0">
              <UserCircle className="size-4 text-muted-foreground" />
              <CardTitle>Cliente</CardTitle>
            </CardHeader>
            <CardContent>
              <Select
                value={clienteId}
                onChange={(event) => setClienteId(event.target.value)}
                aria-label="Selecionar cliente"
              >
                <option value="">Venda de balcão (sem cliente)</option>
                {clientesAtivos.map((cliente) => (
                  <option key={cliente.id} value={cliente.id}>
                    {cliente.nome}
                  </option>
                ))}
              </Select>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex-row items-center gap-2 space-y-0">
              <Package className="size-4 text-muted-foreground" />
              <CardTitle>Adicionar produtos</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  value={busca}
                  onChange={(event) => setBusca(event.target.value)}
                  placeholder="Buscar produto por nome ou SKU..."
                  className="pl-9 pr-9"
                />
                {busca && (
                  <button
                    type="button"
                    onClick={() => setBusca('')}
                    aria-label="Limpar busca"
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
                  >
                    <X className="size-4" />
                  </button>
                )}
              </div>

              {produtosQuery.isPending && (
                <div className="space-y-2">
                  {Array.from({ length: 3 }).map((_, index) => (
                    <div key={index} className="h-12 animate-pulse rounded-lg bg-muted" />
                  ))}
                </div>
              )}

              {!produtosQuery.isPending && produtosDisponiveis.length === 0 && (
                <p className="py-4 text-center text-sm text-muted-foreground">
                  Nenhum produto ativo com estoque encontrado.
                </p>
              )}

              <div className="space-y-2">
                {produtosDisponiveis.map((produto) => {
                  const restante = produto.estoqueAtual - quantidadeNoCarrinho(produto.id)

                  return (
                    <button
                      key={produto.id}
                      type="button"
                      onClick={() => adicionarProduto(produto)}
                      disabled={restante <= 0}
                      className={cn(
                        'flex w-full items-center justify-between gap-3 rounded-lg border border-border px-3 py-2.5 text-left transition-colors',
                        restante > 0 ? 'hover:border-primary/50 hover:bg-muted' : 'cursor-not-allowed opacity-50',
                      )}
                    >
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium">{produto.nome}</p>
                        <p className="text-xs text-muted-foreground">
                          {produto.sku} · {restante} em estoque
                        </p>
                      </div>
                      <div className="flex shrink-0 items-center gap-3">
                        <span className="text-sm font-semibold tabular-nums">
                          {formatCurrency(produto.precoVenda)}
                        </span>
                        <span className="flex size-7 items-center justify-center rounded-md bg-primary/10 text-primary">
                          <Plus className="size-4" />
                        </span>
                      </div>
                    </button>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex-row items-center gap-2 space-y-0">
              <ShoppingCart className="size-4 text-muted-foreground" />
              <CardTitle>Itens da venda</CardTitle>
            </CardHeader>
            <CardContent>
              {itens.length === 0 ? (
                <div className="flex flex-col items-center gap-2 py-8 text-center">
                  <ShoppingCart className="size-8 text-muted-foreground/50" />
                  <p className="text-sm text-muted-foreground">
                    Nenhum item adicionado. Busque um produto acima para começar.
                  </p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Produto</TableHead>
                      <TableHead className="text-right">Preço</TableHead>
                      <TableHead className="text-center">Qtd.</TableHead>
                      <TableHead className="text-right">Subtotal</TableHead>
                      <TableHead className="text-right">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {itens.map((item) => (
                      <TableRow key={item.produto.id}>
                        <TableCell>
                          <div className="font-medium">{item.produto.nome}</div>
                          <div className="text-xs text-muted-foreground">{item.produto.sku}</div>
                        </TableCell>
                        <TableCell className="text-right tabular-nums">
                          {formatCurrency(item.produto.precoVenda)}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center justify-center gap-1">
                            <Button
                              variant="outline"
                              size="icon"
                              className="size-7"
                              onClick={() => alterarQuantidade(item.produto.id, item.quantidade - 1)}
                              disabled={item.quantidade <= 1}
                              aria-label={`Diminuir quantidade de ${item.produto.nome}`}
                            >
                              <Minus className="size-3" />
                            </Button>
                            <Input
                              type="number"
                              min={1}
                              max={item.produto.estoqueAtual}
                              value={item.quantidade}
                              onChange={(event) =>
                                alterarQuantidade(item.produto.id, Number(event.target.value) || 1)
                              }
                              className="h-7 w-14 px-1 text-center tabular-nums"
                              aria-label={`Quantidade de ${item.produto.nome}`}
                            />
                            <Button
                              variant="outline"
                              size="icon"
                              className="size-7"
                              onClick={() => alterarQuantidade(item.produto.id, item.quantidade + 1)}
                              disabled={item.quantidade >= item.produto.estoqueAtual}
                              aria-label={`Aumentar quantidade de ${item.produto.nome}`}
                            >
                              <Plus className="size-3" />
                            </Button>
                          </div>
                        </TableCell>
                        <TableCell className="text-right font-medium tabular-nums">
                          {formatCurrency(item.produto.precoVenda * item.quantidade)}
                        </TableCell>
                        <TableCell>
                          <div className="flex justify-end">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => removerItem(item.produto.id)}
                              aria-label={`Remover ${item.produto.nome}`}
                            >
                              <Trash2 className="size-4 text-destructive" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-1">
          <Card className="lg:sticky lg:top-20">
            <CardHeader>
              <CardTitle>Resumo da venda</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <dl className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <dt className="text-muted-foreground">Itens</dt>
                  <dd className="font-medium tabular-nums">{totais.quantidade}</dd>
                </div>
                <div className="flex items-center justify-between">
                  <dt className="text-muted-foreground">Subtotal</dt>
                  <dd className="font-medium tabular-nums">{formatCurrency(totais.subtotal)}</dd>
                </div>
                <div className="flex items-center justify-between border-t border-border pt-2">
                  <dt className="text-base font-semibold">Total</dt>
                  <dd className="text-lg font-semibold tabular-nums text-primary">
                    {formatCurrency(totais.total)}
                  </dd>
                </div>
              </dl>

              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Cliente</Label>
                <p className="text-sm font-medium">
                  {clienteId
                    ? clientesAtivos.find((cliente) => cliente.id === clienteId)?.nome
                    : 'Venda de balcão'}
                </p>
              </div>

              <Button
                className="w-full"
                size="default"
                disabled={itens.length === 0 || mutation.isPending}
                onClick={() => mutation.mutate()}
              >
                {mutation.isPending && <Loader2 className="size-4 animate-spin" />}
                Finalizar Venda
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
