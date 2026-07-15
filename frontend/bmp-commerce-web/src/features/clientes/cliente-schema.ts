import { z } from 'zod'

export const clienteSchema = z.object({
  nome: z.string().min(1, 'Nome é obrigatório.'),
  cpfCnpj: z
    .string()
    .optional()
    .refine(
      (valor) => {
        if (!valor || valor.trim() === '') {
          return true
        }
        const digitos = valor.replace(/\D/g, '')
        return digitos.length === 11 || digitos.length === 14
      },
      { message: 'Informe 11 dígitos (CPF) ou 14 dígitos (CNPJ).' },
    ),
  telefone: z.string().optional(),
  email: z.string().email('Email inválido.').optional().or(z.literal('')),
  cidade: z.string().optional(),
  estado: z.string().optional(),
  observacoes: z.string().optional(),
  ativo: z.boolean(),
})

export type ClienteFormValues = z.infer<typeof clienteSchema>
