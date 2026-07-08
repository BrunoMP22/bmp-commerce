export const UNIDADES_MEDIDA = ['Unidade', 'Caixa', 'Pacote', 'Kg', 'Litro', 'Metro'] as const

export type UnidadeMedida = (typeof UNIDADES_MEDIDA)[number]

export interface Produto {
  id: string
  nome: string
  descricao: string | null
  sku: string
  codigoBarras: string | null
  categoria: string | null
  unidadeMedida: UnidadeMedida
  precoCusto: number
  precoVenda: number
  estoqueAtual: number
  estoqueMinimo: number
  ativo: boolean
  createdAt: string
  updatedAt: string | null
}

export interface CriarProdutoPayload {
  nome: string
  descricao?: string | null
  sku: string
  codigoBarras?: string | null
  categoria?: string | null
  unidadeMedida: UnidadeMedida
  precoCusto: number
  precoVenda: number
  estoqueAtual: number
  estoqueMinimo: number
}

export interface AtualizarProdutoPayload extends CriarProdutoPayload {
  ativo: boolean
}
