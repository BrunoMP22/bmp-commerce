import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { cancelarVenda } from '@/api/vendas'
import { getErrorMessage } from '@/lib/errors'
import { formatCurrency } from '@/lib/utils'
import type { Venda } from '@/types/venda'
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

interface CancelarVendaDialogProps {
  venda: Venda | null
  onOpenChange: (open: boolean) => void
}

export function CancelarVendaDialog({ venda, onOpenChange }: CancelarVendaDialogProps) {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (id: string) => cancelarVenda(id),
    onSuccess: () => {
      toast.success('Venda cancelada. O estoque dos itens foi estornado.')
      queryClient.invalidateQueries({ queryKey: ['vendas'] })
      queryClient.invalidateQueries({ queryKey: ['produtos'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      onOpenChange(false)
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, 'Não foi possível cancelar a venda.'))
    },
  })

  return (
    <AlertDialog open={venda !== null} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Cancelar venda</AlertDialogTitle>
          <AlertDialogDescription>
            Tem certeza que deseja cancelar a venda de{' '}
            <strong>{venda ? formatCurrency(venda.total) : ''}</strong>
            {venda?.clienteNome ? ` para ${venda.clienteNome}` : ''}? Os itens voltarão ao estoque e a
            venda ficará registrada como cancelada.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <AlertDialogFooter>
          <AlertDialogCancel disabled={mutation.isPending}>Voltar</AlertDialogCancel>
          <AlertDialogAction
            disabled={mutation.isPending}
            onClick={(event) => {
              event.preventDefault()
              if (venda) {
                mutation.mutate(venda.id)
              }
            }}
            className="bg-destructive text-destructive-foreground hover:opacity-90"
          >
            {mutation.isPending && <Loader2 className="size-4 animate-spin" />}
            Cancelar venda
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
