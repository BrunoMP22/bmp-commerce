import * as React from 'react'
import { Controller, useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { createProduto, updateProduto } from '@/api/produtos'
import { getErrorMessage } from '@/lib/errors'
import { UNIDADES_MEDIDA, type Produto } from '@/types/produto'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  produtoSchema,
  type ProdutoFormInput,
  type ProdutoFormValues,
} from '@/features/produtos/produto-schema'

const DEFAULT_VALUES: ProdutoFormInput = {
  nome: '',
  descricao: '',
  sku: '',
  codigoBarras: '',
  categoria: '',
  unidadeMedida: 'Unidade',
  precoCusto: 0,
  precoVenda: 0,
  estoqueAtual: 0,
  estoqueMinimo: 0,
  ativo: true,
}

interface ProdutoFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  produto: Produto | null
}

export function ProdutoFormDialog({ open, onOpenChange, produto }: ProdutoFormDialogProps) {
  const queryClient = useQueryClient()
  const isEditing = produto !== null

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors },
  } = useForm<ProdutoFormInput, unknown, ProdutoFormValues>({
    resolver: zodResolver(produtoSchema),
    defaultValues: DEFAULT_VALUES,
  })

  React.useEffect(() => {
    if (!open) {
      return
    }

    reset(
      produto
        ? {
            nome: produto.nome,
            descricao: produto.descricao ?? '',
            sku: produto.sku,
            codigoBarras: produto.codigoBarras ?? '',
            categoria: produto.categoria ?? '',
            unidadeMedida: produto.unidadeMedida,
            precoCusto: produto.precoCusto,
            precoVenda: produto.precoVenda,
            estoqueAtual: produto.estoqueAtual,
            estoqueMinimo: produto.estoqueMinimo,
            ativo: produto.ativo,
          }
        : DEFAULT_VALUES,
    )
  }, [open, produto, reset])

  const mutation = useMutation({
    mutationFn: (values: ProdutoFormValues) =>
      isEditing ? updateProduto(produto.id, values) : createProduto(values),
    onSuccess: () => {
      toast.success(isEditing ? 'Produto atualizado com sucesso.' : 'Produto cadastrado com sucesso.')
      queryClient.invalidateQueries({ queryKey: ['produtos'] })
      onOpenChange(false)
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, 'Não foi possível salvar o produto.'))
    },
  })

  const onSubmit = (values: ProdutoFormValues) => mutation.mutate(values)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Editar produto' : 'Novo produto'}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? 'Atualize as informações do produto.'
              : 'Preencha os dados para cadastrar um novo produto.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div className="space-y-2">
            <Label htmlFor="nome">Nome</Label>
            <Input id="nome" aria-invalid={Boolean(errors.nome)} {...register('nome')} />
            {errors.nome && <p className="text-xs text-destructive">{errors.nome.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="sku">SKU</Label>
              <Input id="sku" aria-invalid={Boolean(errors.sku)} {...register('sku')} />
              {errors.sku && <p className="text-xs text-destructive">{errors.sku.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="codigoBarras">Código de barras</Label>
              <Input id="codigoBarras" {...register('codigoBarras')} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="categoria">Categoria</Label>
              <Input id="categoria" placeholder="Opcional" {...register('categoria')} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="unidadeMedida">Unidade de medida</Label>
              <Select id="unidadeMedida" {...register('unidadeMedida')}>
                {UNIDADES_MEDIDA.map((unidade) => (
                  <option key={unidade} value={unidade}>
                    {unidade}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="descricao">Descrição</Label>
            <Textarea id="descricao" placeholder="Opcional" {...register('descricao')} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="precoCusto">Preço de custo</Label>
              <Input
                id="precoCusto"
                type="number"
                step="0.01"
                aria-invalid={Boolean(errors.precoCusto)}
                {...register('precoCusto')}
              />
              {errors.precoCusto && <p className="text-xs text-destructive">{errors.precoCusto.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="precoVenda">Preço de venda</Label>
              <Input
                id="precoVenda"
                type="number"
                step="0.01"
                aria-invalid={Boolean(errors.precoVenda)}
                {...register('precoVenda')}
              />
              {errors.precoVenda && <p className="text-xs text-destructive">{errors.precoVenda.message}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="estoqueAtual">Estoque atual</Label>
              <Input
                id="estoqueAtual"
                type="number"
                aria-invalid={Boolean(errors.estoqueAtual)}
                {...register('estoqueAtual')}
              />
              {errors.estoqueAtual && <p className="text-xs text-destructive">{errors.estoqueAtual.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="estoqueMinimo">Estoque mínimo</Label>
              <Input
                id="estoqueMinimo"
                type="number"
                aria-invalid={Boolean(errors.estoqueMinimo)}
                {...register('estoqueMinimo')}
              />
              {errors.estoqueMinimo && (
                <p className="text-xs text-destructive">{errors.estoqueMinimo.message}</p>
              )}
            </div>
          </div>

          <Controller
            control={control}
            name="ativo"
            render={({ field }) => (
              <label className="flex items-center gap-2.5">
                <Checkbox checked={field.value} onCheckedChange={(checked) => field.onChange(checked === true)} />
                <span className="text-sm font-medium">Produto ativo</span>
              </label>
            )}
          />

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={mutation.isPending}>
              Cancelar
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending && <Loader2 className="size-4 animate-spin" />}
              Salvar
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
