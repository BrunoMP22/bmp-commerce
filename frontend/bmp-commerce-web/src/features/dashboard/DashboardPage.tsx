import { useQuery } from '@tanstack/react-query'
import { Building2, Database, KeyRound, Server, ShieldCheck, UserCircle } from 'lucide-react'
import { fetchCurrentUser } from '@/api/auth'
import { useAuth } from '@/lib/auth-context'
import { StatCard } from '@/components/layout/StatCard'

export function DashboardPage() {
  const { user } = useAuth()

  const meQuery = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: fetchCurrentUser,
    initialData: user ?? undefined,
  })

  const current = meQuery.data ?? user
  const connectionStatus = meQuery.isError ? 'error' : meQuery.isSuccess ? 'success' : 'pending'
  const firstName = current?.name.split(' ')[0]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          {firstName ? `Bem-vindo de volta, ${firstName}.` : 'Bem-vindo de volta.'}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Empresa"
          value={current?.tenantName ?? 'Plataforma (sem tenant)'}
          icon={Building2}
          tone="blue"
        />
        <StatCard title="Usuário" value={current?.name ?? '—'} icon={UserCircle} tone="blue" />
        <StatCard title="Cargo" value={current?.role ?? '—'} icon={ShieldCheck} tone="blue" />
        <StatCard
          title="API"
          value={meQuery.isError ? 'Indisponível' : meQuery.isSuccess ? 'Online' : 'Verificando...'}
          icon={Server}
          status={connectionStatus}
        />
        <StatCard
          title="Banco de dados"
          value={meQuery.isError ? 'Erro de conexão' : meQuery.isSuccess ? 'Conectado' : 'Verificando...'}
          icon={Database}
          status={connectionStatus}
        />
        <StatCard
          title="Autenticação"
          value={meQuery.isError ? 'Falha na validação' : meQuery.isSuccess ? 'JWT válido' : 'Verificando...'}
          icon={KeyRound}
          status={connectionStatus}
        />
      </div>
    </div>
  )
}
