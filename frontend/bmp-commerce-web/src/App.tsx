import { Navigate, Route, Routes } from 'react-router-dom'
import { Toaster } from 'sonner'
import { useTheme } from '@/hooks/use-theme'
import { ProtectedRoute, PublicOnlyRoute } from '@/components/layout/ProtectedRoute'
import { AppLayout } from '@/layouts/AppLayout'
import { LoginPage } from '@/features/auth/LoginPage'
import { DashboardPage } from '@/features/dashboard/DashboardPage'
import { ProdutosPage } from '@/features/produtos/ProdutosPage'
import { ClientesPage } from '@/features/clientes/ClientesPage'
import { VendasPage } from '@/features/vendas/VendasPage'
import { InsightsPage } from '@/features/insights/InsightsPage'
import { ConfiguracoesPage } from '@/features/configuracoes/ConfiguracoesPage'
import { PerfilPage } from '@/features/perfil/PerfilPage'

function App() {
  const { theme } = useTheme()

  return (
    <>
      <Toaster theme={theme} position="top-right" richColors closeButton />

      <Routes>
        <Route element={<PublicOnlyRoute />}>
          <Route path="/login" element={<LoginPage />} />
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/produtos" element={<ProdutosPage />} />
            <Route path="/clientes" element={<ClientesPage />} />
            <Route path="/vendas" element={<VendasPage />} />
            <Route path="/insights" element={<InsightsPage />} />
            <Route path="/configuracoes" element={<ConfiguracoesPage />} />
            <Route path="/perfil" element={<PerfilPage />} />
          </Route>
        </Route>

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </>
  )
}

export default App
