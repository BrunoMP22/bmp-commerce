import * as React from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { z } from 'zod'
import {
  Building2,
  Camera,
  IdCard,
  KeyRound,
  Loader2,
  Mail,
  ShieldCheck,
  Trash2,
  UserRound,
} from 'lucide-react'
import { toast } from 'sonner'
import { atualizarAvatar, atualizarPerfil, fetchCurrentUser, removerAvatar } from '@/api/auth'
import { useAuth } from '@/lib/auth-context'
import { getErrorMessage } from '@/lib/errors'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { UserAvatar } from '@/components/layout/UserAvatar'

const perfilSchema = z.object({
  name: z.string().trim().min(1, 'Informe o seu nome.').max(200, 'Máximo de 200 caracteres.'),
})

type PerfilFormValues = z.infer<typeof perfilSchema>

const DESCRICAO_PAPEL: Record<string, string> = {
  SuperAdmin: 'Usuário de plataforma — acesso total a todos os recursos e indicadores.',
  Admin: 'Administrador da empresa — gerencia cadastros e vendas e vê os indicadores financeiros.',
  Employee: 'Funcionário — opera vendas e cadastros; indicadores financeiros não são exibidos.',
}

const TAMANHO_AVATAR = 256

/** Redimensiona a imagem no navegador (recorte central 256×256, JPEG) antes do upload. */
async function redimensionarParaAvatar(arquivo: File): Promise<string> {
  const bitmap = await createImageBitmap(arquivo)

  const canvas = document.createElement('canvas')
  canvas.width = TAMANHO_AVATAR
  canvas.height = TAMANHO_AVATAR

  const contexto = canvas.getContext('2d')
  if (!contexto) {
    throw new Error('Canvas indisponível neste navegador.')
  }

  const escala = Math.max(TAMANHO_AVATAR / bitmap.width, TAMANHO_AVATAR / bitmap.height)
  const largura = bitmap.width * escala
  const altura = bitmap.height * escala
  contexto.drawImage(bitmap, (TAMANHO_AVATAR - largura) / 2, (TAMANHO_AVATAR - altura) / 2, largura, altura)
  bitmap.close()

  return canvas.toDataURL('image/jpeg', 0.85)
}

function formatMembroDesde(criadoEm: string | undefined) {
  if (!criadoEm) {
    return null
  }
  return new Date(criadoEm).toLocaleDateString('pt-BR', { day: 'numeric', month: 'long', year: 'numeric' })
}

function LinhaConta({
  icone: Icone,
  rotulo,
  children,
}: {
  icone: typeof Mail
  rotulo: string
  children: React.ReactNode
}) {
  return (
    <div className="flex items-start gap-3 py-3">
      <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
        <Icone className="size-4" />
      </div>
      <div className="min-w-0">
        <p className="text-xs text-muted-foreground">{rotulo}</p>
        <div className="text-sm font-medium">{children}</div>
      </div>
    </div>
  )
}

export function PerfilPage() {
  const { user, updateUser } = useAuth()
  const inputArquivoRef = React.useRef<HTMLInputElement>(null)

  // Ressincroniza a sessão com o backend ao abrir a página (sessões antigas podem
  // ter sido gravadas antes de o perfil ganhar avatar/criadoEm).
  React.useEffect(() => {
    fetchCurrentUser().then(updateUser).catch(() => {})
  }, [updateUser])

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<PerfilFormValues>({
    resolver: zodResolver(perfilSchema),
    values: { name: user?.name ?? '' },
  })

  const salvarNome = useMutation({
    mutationFn: (values: PerfilFormValues) => atualizarPerfil({ name: values.name }),
    onSuccess: (atualizado) => {
      updateUser(atualizado)
      reset({ name: atualizado.name })
      toast.success('Perfil atualizado.')
    },
    onError: (error) => toast.error(getErrorMessage(error, 'Não foi possível atualizar o perfil.')),
  })

  const enviarAvatar = useMutation({
    mutationFn: (imagem: string) => atualizarAvatar({ imagem }),
    onSuccess: (atualizado) => {
      updateUser(atualizado)
      toast.success('Foto de perfil atualizada.')
    },
    onError: (error) => toast.error(getErrorMessage(error, 'Não foi possível enviar a foto.')),
  })

  const excluirAvatar = useMutation({
    mutationFn: removerAvatar,
    onSuccess: (atualizado) => {
      updateUser(atualizado)
      toast.success('Foto de perfil removida.')
    },
    onError: (error) => toast.error(getErrorMessage(error, 'Não foi possível remover a foto.')),
  })

  const aoEscolherArquivo = async (evento: React.ChangeEvent<HTMLInputElement>) => {
    const arquivo = evento.target.files?.[0]
    evento.target.value = ''

    if (!arquivo) {
      return
    }
    if (!arquivo.type.startsWith('image/')) {
      toast.error('Escolha um arquivo de imagem (JPEG, PNG ou WebP).')
      return
    }

    try {
      const imagem = await redimensionarParaAvatar(arquivo)
      enviarAvatar.mutate(imagem)
    } catch {
      toast.error('Não foi possível ler essa imagem. Tente outro arquivo.')
    }
  }

  if (!user) {
    return null
  }

  const membroDesde = formatMembroDesde(user.criadoEm)
  const enviandoFoto = enviarAvatar.isPending || excluirAvatar.isPending

  return (
    <div className="mx-auto w-full max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Perfil</h1>
        <p className="text-sm text-muted-foreground">Sua identidade dentro do BMP Commerce.</p>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col items-center gap-5 text-center sm:flex-row sm:text-left">
            <div className="relative">
              <UserAvatar name={user.name} avatar={user.avatar} className="size-24 text-2xl" />
              <button
                type="button"
                onClick={() => inputArquivoRef.current?.click()}
                disabled={enviandoFoto}
                className="absolute -bottom-1 -right-1 flex size-8 items-center justify-center rounded-full border-2 border-card bg-primary text-primary-foreground shadow-sm transition-transform hover:scale-105 disabled:opacity-60"
                aria-label="Alterar foto de perfil"
                title="Alterar foto"
              >
                {enviandoFoto ? <Loader2 className="size-4 animate-spin" /> : <Camera className="size-4" />}
              </button>
              <input
                ref={inputArquivoRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={aoEscolherArquivo}
              />
            </div>

            <div className="min-w-0 flex-1 space-y-1.5">
              <p className="truncate text-xl font-semibold tracking-tight">{user.name}</p>
              <p className="truncate text-sm text-muted-foreground">{user.email}</p>
              <div className="flex flex-wrap items-center justify-center gap-1.5 sm:justify-start">
                <Badge variant="muted">
                  <ShieldCheck className="size-3" />
                  {user.role}
                </Badge>
                <Badge variant="muted">
                  <Building2 className="size-3" />
                  {user.tenantName ?? 'Plataforma'}
                </Badge>
              </div>
            </div>

            {user.avatar && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => excluirAvatar.mutate()}
                disabled={enviandoFoto}
              >
                <Trash2 className="size-4" />
                Remover foto
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex-row items-center gap-2 space-y-0">
          <UserRound className="size-4 text-muted-foreground" />
          <CardTitle>Dados pessoais</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleSubmit((values) => salvarNome.mutate(values))}
            className="max-w-md space-y-4"
            noValidate
          >
            <div className="space-y-1.5">
              <Label htmlFor="perfil-nome">Nome completo</Label>
              <Input id="perfil-nome" autoComplete="name" {...register('name')} />
              {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="perfil-email">Email</Label>
              <Input id="perfil-email" value={user.email} disabled />
              <p className="text-xs text-muted-foreground">
                O email é o seu login e não pode ser alterado no MVP.
              </p>
            </div>

            <Button type="submit" disabled={salvarNome.isPending || !isDirty}>
              {salvarNome.isPending && <Loader2 className="size-4 animate-spin" />}
              Salvar alterações
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex-row items-center gap-2 space-y-0">
          <IdCard className="size-4 text-muted-foreground" />
          <CardTitle>Conta e acesso</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="divide-y divide-border">
            <LinhaConta icone={ShieldCheck} rotulo="Papel">
              {user.role}
              <p className="mt-0.5 text-xs font-normal text-muted-foreground">
                {DESCRICAO_PAPEL[user.role] ?? 'Papel personalizado.'}
              </p>
            </LinhaConta>
            <LinhaConta icone={Building2} rotulo="Vínculo">
              {user.tenantName ?? 'Plataforma BMP Commerce (sem empresa vinculada)'}
            </LinhaConta>
            {membroDesde && (
              <LinhaConta icone={Mail} rotulo="Membro desde">
                {membroDesde}
              </LinhaConta>
            )}
            <LinhaConta icone={KeyRound} rotulo="Senha">
              <Link to="/configuracoes" className="text-primary underline-offset-4 hover:underline">
                Alterar senha em Configurações → Segurança
              </Link>
            </LinhaConta>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
