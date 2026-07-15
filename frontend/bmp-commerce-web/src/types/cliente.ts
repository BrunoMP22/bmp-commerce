export interface Cliente {
  id: string
  nome: string
  cpfCnpj: string | null
  telefone: string | null
  email: string | null
  cidade: string | null
  estado: string | null
  observacoes: string | null
  ativo: boolean
  createdAt: string
  updatedAt: string | null
}

export interface CriarClientePayload {
  nome: string
  cpfCnpj?: string | null
  telefone?: string | null
  email?: string | null
  cidade?: string | null
  estado?: string | null
  observacoes?: string | null
}

export interface AtualizarClientePayload extends CriarClientePayload {
  ativo: boolean
}

export const UFS = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG',
  'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO',
] as const
