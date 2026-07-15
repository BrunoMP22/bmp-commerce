import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { deleteCliente } from '@/api/clientes'
import { getErrorMessage } from '@/lib/errors'
import type { Cliente } from '@/types/cliente'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

interface DeleteClienteDialogProps {
  cliente: Cliente | null
  onOpenChange: (open: boolean) => void
}

export function DeleteClienteDialog({ cliente, onOpenChange }: DeleteClienteDialogProps) {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (id: string) => deleteCliente(id),
    onSuccess: () => {
      toast.success('Cliente excluído com sucesso.')
      queryClient.invalidateQueries({ queryKey: ['clientes'] })
      onOpenChange(false)
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, 'Não foi possível excluir o cliente.'))
    },
  })

  return (
    <AlertDialog open={cliente !== null} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Excluir cliente</AlertDialogTitle>
          <AlertDialogDescription>
            Tem certeza que deseja excluir <strong>{cliente?.nome}</strong>? Essa ação não pode ser
            desfeita.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <AlertDialogFooter>
          <AlertDialogCancel disabled={mutation.isPending}>Cancelar</AlertDialogCancel>
          <AlertDialogAction
            disabled={mutation.isPending}
            onClick={(event) => {
              event.preventDefault()
              if (cliente) {
                mutation.mutate(cliente.id)
              }
            }}
            className="bg-destructive text-destructive-foreground hover:opacity-90"
          >
            {mutation.isPending && <Loader2 className="size-4 animate-spin" />}
            Excluir
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
