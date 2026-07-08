import { z } from 'zod'
import { UNIDADES_MEDIDA } from '@/types/produto'

export const produtoSchema = z.object({
  nome: z.string().min(1, 'Nome é obrigatório.'),
  descricao: z.string().optional(),
  sku: z.string().min(1, 'SKU é obrigatório.'),
  codigoBarras: z.string().optional(),
  categoria: z.string().optional(),
  unidadeMedida: z.enum(UNIDADES_MEDIDA),
  precoCusto: z.coerce.number().min(0, 'Preço de custo não pode ser negativo.'),
  precoVenda: z.coerce.number().positive('Preço de venda deve ser maior que zero.'),
  estoqueAtual: z.coerce.number().int('Deve ser um número inteiro.').min(0, 'Estoque não pode ser negativo.'),
  estoqueMinimo: z.coerce
    .number()
    .int('Deve ser um número inteiro.')
    .min(0, 'Estoque mínimo não pode ser negativo.'),
  ativo: z.boolean(),
})

export type ProdutoFormInput = z.input<typeof produtoSchema>
export type ProdutoFormValues = z.output<typeof produtoSchema>
