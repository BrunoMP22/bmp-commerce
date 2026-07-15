import { formatCurrency } from '@/lib/utils'
import type { Venda } from '@/types/venda'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

function formatDataHora(dataHora: string) {
  return new Date(dataHora).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

interface VendaDetailsDialogProps {
  venda: Venda | null
  onOpenChange: (open: boolean) => void
}

export function VendaDetailsDialog({ venda, onOpenChange }: VendaDetailsDialogProps) {
  return (
    <Dialog open={venda !== null} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <DialogTitle>Detalhes da venda</DialogTitle>
            {venda?.cancelada && <Badge variant="destructive">Cancelada</Badge>}
          </div>
          <DialogDescription>
            {venda && (
              <>
                {formatDataHora(venda.dataHora)} · {venda.clienteNome ?? 'Venda de balcão'} · registrada por{' '}
                {venda.usuarioNome}
              </>
            )}
          </DialogDescription>
        </DialogHeader>

        {venda && (
          <div className="space-y-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Produto</TableHead>
                  <TableHead className="text-center">Qtd.</TableHead>
                  <TableHead className="text-right">Preço</TableHead>
                  <TableHead className="text-right">Subtotal</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {venda.itens.map((item) => (
                  <TableRow key={item.produtoId}>
                    <TableCell>
                      <div className="font-medium">{item.produtoNome}</div>
                      <div className="text-xs text-muted-foreground">{item.produtoSku}</div>
                    </TableCell>
                    <TableCell className="text-center tabular-nums">{item.quantidade}</TableCell>
                    <TableCell className="text-right tabular-nums">
                      {formatCurrency(item.precoVendaMomento)}
                    </TableCell>
                    <TableCell className="text-right font-medium tabular-nums">
                      {formatCurrency(item.subtotal)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <div className="flex items-center justify-between rounded-lg bg-muted px-4 py-3">
              <span className="text-sm font-medium">Total da venda</span>
              <span className="text-lg font-semibold tabular-nums">{formatCurrency(venda.total)}</span>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
