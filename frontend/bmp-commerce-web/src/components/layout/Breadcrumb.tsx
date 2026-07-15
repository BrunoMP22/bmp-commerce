import { Link, useLocation } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import { navItems } from '@/lib/nav-items'

const extraLabels: Record<string, string> = {
  '/perfil': 'Perfil',
  '/vendas/nova': 'Nova Venda',
}

export function Breadcrumb() {
  const { pathname } = useLocation()
  const currentLabel =
    navItems.find((item) => item.path === pathname)?.label ?? extraLabels[pathname] ?? 'Página'

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm text-muted-foreground">
      <Link to="/dashboard" className="hover:text-foreground">
        BMP Commerce
      </Link>
      <ChevronRight className="size-3.5" />
      <span className="font-medium text-foreground">{currentLabel}</span>
    </nav>
  )
}
