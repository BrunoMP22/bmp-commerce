export interface VendaPorDia {
  data: string
  total: number
  quantidade: number
}

export interface Dashboard {
  receitaTotal: number
  quantidadeVendas: number
  clientesCadastrados: number
  produtosCadastrados: number
  produtosAbaixoMinimo: number
  produtosSemEstoque: number
  ticketMedio: number
  valorEstoque: number
  vendasPorDia: VendaPorDia[]
}
