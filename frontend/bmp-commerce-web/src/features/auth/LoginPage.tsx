import * as React from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { AlertCircle, Loader2, Lock, Mail, Sparkles } from 'lucide-react'
import { login } from '@/api/auth'
import { useAuth } from '@/lib/auth-context'
import { getErrorMessage } from '@/lib/errors'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ThemeToggle } from '@/components/layout/ThemeToggle'
import { loginSchema, type LoginFormValues } from '@/features/auth/login-schema'

export function LoginPage() {
  const navigate = useNavigate()
  const { signIn } = useAuth()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) })

  const [formError, setFormError] = React.useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      setFormError(null)
      signIn(data)
      navigate('/dashboard', { replace: true })
    },
    onError: (error) => {
      setFormError(getErrorMessage(error, 'Não foi possível entrar. Tente novamente.'))
    },
  })

  const onSubmit = (values: LoginFormValues) => {
    setFormError(null)
    mutation.mutate(values)
  }

  return (
    <div className="flex min-h-screen">
      <div className="relative hidden flex-1 flex-col justify-between overflow-hidden bg-gradient-to-br from-blue-700 via-blue-600 to-slate-900 p-12 text-white lg:flex">
        <div className="flex items-center gap-2 text-lg font-semibold tracking-tight">
          <Sparkles className="size-5" />
          BMP
        </div>

        <div className="max-w-md space-y-3">
          <h1 className="text-3xl font-semibold tracking-tight">Data &amp; Analytics</h1>
          <p className="text-sm leading-relaxed text-blue-100">
            Plataforma de gestão comercial multi-tenant da BMP: cadastros, vendas e insights de
            negócio em um único lugar.
          </p>
        </div>

        <p className="text-xs text-blue-200/70">© {new Date().getFullYear()} BMP. Todos os direitos reservados.</p>
      </div>

      <div className="flex flex-1 flex-col justify-center px-6 py-12 sm:px-12 lg:px-20">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Bem-vindo de volta</p>
              <h2 className="text-2xl font-semibold tracking-tight">Entrar no BMP Commerce</h2>
            </div>

            <ThemeToggle variant="outline" />
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="voce@empresa.com"
                  className="pl-9"
                  aria-invalid={Boolean(errors.email)}
                  {...register('email')}
                />
              </div>
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Senha</Label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••"
                  className="pl-9"
                  aria-invalid={Boolean(errors.password)}
                  {...register('password')}
                />
              </div>
              {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
            </div>

            {formError && (
              <div className="flex items-start gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                <AlertCircle className="mt-0.5 size-4 shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            <Button type="submit" className="w-full" disabled={mutation.isPending}>
              {mutation.isPending && <Loader2 className="size-4 animate-spin" />}
              Entrar
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
