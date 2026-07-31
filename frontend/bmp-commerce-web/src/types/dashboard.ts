export interface KpiComVariacao {
  atual: number
  anterior: number
  /** null quando a janela anterior não tem base de comparação. */
  variacaoPercentual: number | null
}

export interface VendaPorDia {
  data: string
  /** null para Funcionário — receita é indicador financeiro. */
  total: number | null
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
  /** null para Funcionário — ranking dele é por unidades. */
  receita: number | null
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
  /** Campos financeiros: null quando o papel é Funcionário (bloqueio no back-end). */
  receita30Dias: KpiComVariacao | null
  vendas30Dias: KpiComVariacao
  ticketMedio30Dias: KpiComVariacao | null
  valorEstoque: number | null

  receitaTotal: number | null
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
