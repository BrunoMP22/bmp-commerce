export interface ItemVenda {
  produtoId: string
  produtoNome: string
  produtoSku: string
  quantidade: number
  precoVendaMomento: number
  subtotal: number
}

export interface Venda {
  id: string
  clienteId: string | null
  clienteNome: string | null
  usuarioNome: string
  dataHora: string
  total: number
  quantidadeItens: number
  cancelada: boolean
  itens: ItemVenda[]
}

export interface RegistrarVendaPayload {
  clienteId: string | null
  itens: { produtoId: string; quantidade: number }[]
}
