import { z } from 'zod'

export const alterarSenhaSchema = z
  .object({
    senhaAtual: z.string().min(1, 'Informe a senha atual.'),
    novaSenha: z.string().min(8, 'A nova senha deve ter pelo menos 8 caracteres.'),
    confirmarNovaSenha: z.string().min(1, 'Confirme a nova senha.'),
  })
  .refine((valores) => valores.novaSenha === valores.confirmarNovaSenha, {
    message: 'A confirmação não confere com a nova senha.',
    path: ['confirmarNovaSenha'],
  })

export type AlterarSenhaFormValues = z.infer<typeof alterarSenhaSchema>
