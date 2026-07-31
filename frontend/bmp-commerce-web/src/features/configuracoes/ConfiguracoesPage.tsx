import type { ReactNode } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import {
  Globe,
  Info,
  KeyRound,
  Loader2,
  Monitor,
  Moon,
  Palette,
  Sun,
  type LucideIcon,
} from 'lucide-react'
import { toast } from 'sonner'
import { alterarSenha } from '@/api/auth'
import { getInfoSistema } from '@/api/sistema'
import { getErrorMessage } from '@/lib/errors'
import { useTheme, type ThemePreference } from '@/lib/theme-context'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  alterarSenhaSchema,
  type AlterarSenhaFormValues,
} from '@/features/configuracoes/configuracoes-schema'

const API_URL = import.meta.env.VITE_API_URL as string

interface OpcaoTema {
  valor: ThemePreference
  rotulo: string
  descricao: string
  icone: LucideIcon
}

const OPCOES_TEMA: OpcaoTema[] = [
  { valor: 'light', rotulo: 'Claro', descricao: 'Fundo claro, ideal para ambientes iluminados.', icone: Sun },
  { valor: 'dark', rotulo: 'Escuro', descricao: 'Menos brilho, confortável à noite.', icone: Moon },
  {
    valor: 'system',
    rotulo: 'Sistema',
    descricao: 'Acompanha automaticamente o tema do seu dispositivo.',
    icone: Monitor,
  },
]

function SecaoAparencia() {
  const { preference, setPreference } = useTheme()

  return (
    <Card>
      <CardHeader className="flex-row items-center gap-2 space-y-0">
        <Palette className="size-4 text-muted-foreground" />
        <CardTitle>Aparência</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {OPCOES_TEMA.map(({ valor, rotulo, descricao, icone: Icone }) => {
            const selecionado = preference === valor
            return (
              <button
                key={valor}
                type="button"
                onClick={() => setPreference(valor)}
                aria-pressed={selecionado}
                className={cn(
                  'flex flex-col items-start gap-2 rounded-xl border p-4 text-left transition-colors',
                  selecionado
                    ? 'border-primary bg-primary/5 ring-1 ring-primary'
                    : 'border-border hover:bg-muted/60',
                )}
              >
                <div
                  className={cn(
                    'flex size-8 items-center justify-center rounded-lg',
                    selecionado ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground',
                  )}
                >
                  <Icone className="size-4" />
                </div>
                <span className="text-sm font-medium">{rotulo}</span>
                <span className="text-xs leading-relaxed text-muted-foreground">{descricao}</span>
              </button>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

function SecaoSeguranca() {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<AlterarSenhaFormValues>({
    resolver: zodResolver(alterarSenhaSchema),
    defaultValues: { senhaAtual: '', novaSenha: '', confirmarNovaSenha: '' },
  })

  const mutation = useMutation({
    mutationFn: (values: AlterarSenhaFormValues) =>
      alterarSenha({ senhaAtual: values.senhaAtual, novaSenha: values.novaSenha }),
    onSuccess: () => {
      toast.success('Senha alterada com sucesso.')
      reset()
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, 'Não foi possível alterar a senha.'))
    },
  })

  return (
    <Card>
      <CardHeader className="flex-row items-center gap-2 space-y-0">
        <KeyRound className="size-4 text-muted-foreground" />
        <CardTitle>Segurança</CardTitle>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={handleSubmit((values) => mutation.mutate(values))}
          className="max-w-md space-y-4"
          noValidate
        >
          <div className="space-y-1.5">
            <Label htmlFor="senha-atual">Senha atual</Label>
            <Input
              id="senha-atual"
              type="password"
              autoComplete="current-password"
              {...register('senhaAtual')}
            />
            {errors.senhaAtual && <p className="text-xs text-destructive">{errors.senhaAtual.message}</p>}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="nova-senha">Nova senha</Label>
            <Input id="nova-senha" type="password" autoComplete="new-password" {...register('novaSenha')} />
            {errors.novaSenha ? (
              <p className="text-xs text-destructive">{errors.novaSenha.message}</p>
            ) : (
              <p className="text-xs text-muted-foreground">Mínimo de 8 caracteres.</p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="confirmar-nova-senha">Confirmar nova senha</Label>
            <Input
              id="confirmar-nova-senha"
              type="password"
              autoComplete="new-password"
              {...register('confirmarNovaSenha')}
            />
            {errors.confirmarNovaSenha && (
              <p className="text-xs text-destructive">{errors.confirmarNovaSenha.message}</p>
            )}
          </div>

          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending && <Loader2 className="size-4 animate-spin" />}
            Alterar senha
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

function LinhaInfo({ rotulo, children }: { rotulo: string; children: ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4 py-2.5">
      <span className="text-sm text-muted-foreground">{rotulo}</span>
      <span className="flex items-center gap-2 text-sm font-medium">{children}</span>
    </div>
  )
}

function SecaoIdiomaERegiao() {
  return (
    <Card>
      <CardHeader className="flex-row items-center gap-2 space-y-0">
        <Globe className="size-4 text-muted-foreground" />
        <CardTitle>Idioma e região</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="divide-y divide-border">
          <LinhaInfo rotulo="Idioma">
            Português (Brasil) <Badge variant="muted">pt-BR</Badge>
          </LinhaInfo>
          <LinhaInfo rotulo="Moeda">
            Real <Badge variant="muted">R$</Badge>
          </LinhaInfo>
        </div>
        <p className="mt-3 text-xs text-muted-foreground">
          Único idioma disponível no MVP — novas opções chegam junto com a internacionalização.
        </p>
      </CardContent>
    </Card>
  )
}

function SecaoSobre() {
  const infoQuery = useQuery({
    queryKey: ['sistema-info'],
    queryFn: getInfoSistema,
  })

  const info = infoQuery.data
  const ambienteDev = info?.ambiente.toLowerCase() === 'development'

  return (
    <Card>
      <CardHeader className="flex-row items-center gap-2 space-y-0">
        <Info className="size-4 text-muted-foreground" />
        <CardTitle>Sobre o sistema</CardTitle>
      </CardHeader>
      <CardContent>
        {infoQuery.isPending ? (
          <div className="h-24 animate-pulse rounded-lg bg-muted/40" />
        ) : infoQuery.isError ? (
          <p className="text-sm text-muted-foreground">Não foi possível carregar as informações da API.</p>
        ) : info ? (
          <div className="divide-y divide-border">
            <LinhaInfo rotulo="Sistema">{info.nome}</LinhaInfo>
            <LinhaInfo rotulo="Versão da API">{info.versao}</LinhaInfo>
            <LinhaInfo rotulo="Ambiente">
              <Badge variant={ambienteDev ? 'warning' : 'success'}>{info.ambiente}</Badge>
            </LinhaInfo>
            <LinhaInfo rotulo="Documentação da API">
              <a
                href={`${API_URL}/docs`}
                target="_blank"
                rel="noreferrer"
                className="text-primary underline-offset-4 hover:underline"
              >
                {API_URL}/docs
              </a>
            </LinhaInfo>
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}

export function ConfiguracoesPage() {
  return (
    <div className="mx-auto w-full max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Configurações</h1>
        <p className="text-sm text-muted-foreground">
          Aparência, segurança da conta e informações do sistema.
        </p>
      </div>

      <SecaoAparencia />
      <SecaoSeguranca />
      <SecaoIdiomaERegiao />
      <SecaoSobre />
    </div>
  )
}
