import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { deleteProduto } from '@/api/produtos'
import { getErrorMessage } from '@/lib/errors'
import type { Produto } from '@/types/produto'
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

interface DeleteProdutoDialogProps {
  produto: Produto | null
  onOpenChange: (open: boolean) => void
}

export function DeleteProdutoDialog({ produto, onOpenChange }: DeleteProdutoDialogProps) {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (id: string) => deleteProduto(id),
    onSuccess: () => {
      toast.success('Produto excluído com sucesso.')
      queryClient.invalidateQueries({ queryKey: ['produtos'] })
      onOpenChange(false)
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, 'Não foi possível excluir o produto.'))
    },
  })

  return (
    <AlertDialog open={produto !== null} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Excluir produto</AlertDialogTitle>
          <AlertDialogDescription>
            Tem certeza que deseja excluir <strong>{produto?.nome}</strong>? Essa ação não pode ser
            desfeita.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <AlertDialogFooter>
          <AlertDialogCancel disabled={mutation.isPending}>Cancelar</AlertDialogCancel>
          <AlertDialogAction
            disabled={mutation.isPending}
            onClick={(event) => {
              event.preventDefault()
              if (produto) {
                mutation.mutate(produto.id)
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
