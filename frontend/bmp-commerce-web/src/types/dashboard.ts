export interface KpiComVariacao {
  atual: number
  anterior: number
  /** null quando a janela anterior não tem base de comparação. */
  variacaoPercentual: number | null
}

export interface VendaPorDia {
  data: string
  total: number
  quantidade: number
}

export interface CategoriaReceita {
  categoria: string
  receita: number
  participacaoPercentual: number
}

export interface TopProduto {
  produtoId: string
  nome: string
  sku: string
  quantidade: number
  receita: number
}

export interface UltimaVenda {
  id: string
  clienteNome: string | null
  dataHora: string
  total: number
  quantidadeItens: number
  cancelada: boolean
}

export interface ProdutoEstoqueAlerta {
  produtoId: string
  nome: string
  sku: string
  estoqueAtual: number
  estoqueMinimo: number
  semEstoque: boolean
}

export interface Dashboard {
  receita30Dias: KpiComVariacao
  vendas30Dias: KpiComVariacao
  ticketMedio30Dias: KpiComVariacao
  valorEstoque: number

  receitaTotal: number
  quantidadeVendas: number
  clientesCadastrados: number
  produtosCadastrados: number
  produtosAbaixoMinimo: number
  produtosSemEstoque: number

  vendasPorDia: VendaPorDia[]
  receitaPorCategoria: CategoriaReceita[]
  topProdutos: TopProduto[]
  ultimasVendas: UltimaVenda[]
  estoqueEmAlerta: ProdutoEstoqueAlerta[]
}
