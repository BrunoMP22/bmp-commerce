import * as React from 'react'
import { Controller, useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { createCliente, updateCliente } from '@/api/clientes'
import { getErrorMessage } from '@/lib/errors'
import { UFS, type Cliente } from '@/types/cliente'
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
import { clienteSchema, type ClienteFormValues } from '@/features/clientes/cliente-schema'

const DEFAULT_VALUES: ClienteFormValues = {
  nome: '',
  cpfCnpj: '',
  telefone: '',
  email: '',
  cidade: '',
  estado: '',
  observacoes: '',
  ativo: true,
}

interface ClienteFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  cliente: Cliente | null
}

export function ClienteFormDialog({ open, onOpenChange, cliente }: ClienteFormDialogProps) {
  const queryClient = useQueryClient()
  const isEditing = cliente !== null

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors },
  } = useForm<ClienteFormValues>({
    resolver: zodResolver(clienteSchema),
    defaultValues: DEFAULT_VALUES,
  })

  React.useEffect(() => {
    if (!open) {
      return
    }

    reset(
      cliente
        ? {
            nome: cliente.nome,
            cpfCnpj: cliente.cpfCnpj ?? '',
            telefone: cliente.telefone ?? '',
            email: cliente.email ?? '',
            cidade: cliente.cidade ?? '',
            estado: cliente.estado ?? '',
            observacoes: cliente.observacoes ?? '',
            ativo: cliente.ativo,
          }
        : DEFAULT_VALUES,
    )
  }, [open, cliente, reset])

  const mutation = useMutation({
    mutationFn: (values: ClienteFormValues) => {
      const payload = {
        nome: values.nome,
        cpfCnpj: values.cpfCnpj || null,
        telefone: values.telefone || null,
        email: values.email || null,
        cidade: values.cidade || null,
        estado: values.estado || null,
        observacoes: values.observacoes || null,
      }

      return isEditing
        ? updateCliente(cliente.id, { ...payload, ativo: values.ativo })
        : createCliente(payload)
    },
    onSuccess: () => {
      toast.success(isEditing ? 'Cliente atualizado com sucesso.' : 'Cliente cadastrado com sucesso.')
      queryClient.invalidateQueries({ queryKey: ['clientes'] })
      onOpenChange(false)
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, 'Não foi possível salvar o cliente.'))
    },
  })

  const onSubmit = (values: ClienteFormValues) => mutation.mutate(values)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Editar cliente' : 'Novo cliente'}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? 'Atualize as informações do cliente.'
              : 'Preencha os dados para cadastrar um novo cliente.'}
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
              <Label htmlFor="cpfCnpj">CPF/CNPJ</Label>
              <Input
                id="cpfCnpj"
                placeholder="Opcional"
                aria-invalid={Boolean(errors.cpfCnpj)}
                {...register('cpfCnpj')}
              />
              {errors.cpfCnpj && <p className="text-xs text-destructive">{errors.cpfCnpj.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="telefone">Telefone</Label>
              <Input id="telefone" placeholder="Opcional" {...register('telefone')} />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="Opcional"
              aria-invalid={Boolean(errors.email)}
              {...register('email')}
            />
            {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="cidade">Cidade</Label>
              <Input id="cidade" placeholder="Opcional" {...register('cidade')} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="estado">Estado</Label>
              <Select id="estado" {...register('estado')}>
                <option value="">Selecione (opcional)</option>
                {UFS.map((uf) => (
                  <option key={uf} value={uf}>
                    {uf}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="observacoes">Observações</Label>
            <Textarea id="observacoes" placeholder="Opcional" {...register('observacoes')} />
          </div>

          {isEditing && (
            <Controller
              control={control}
              name="ativo"
              render={({ field }) => (
                <label className="flex items-center gap-2.5">
                  <Checkbox checked={field.value} onCheckedChange={(checked) => field.onChange(checked === true)} />
                  <span className="text-sm font-medium">Cliente ativo</span>
                </label>
              )}
            />
          )}

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
