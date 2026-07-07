import {
  LayoutDashboard,
  Package,
  Settings,
  ShoppingCart,
  TrendingUp,
  Users,
  type LucideIcon,
} from 'lucide-react'

export interface NavItem {
  label: string
  path: string
  icon: LucideIcon
}

export const navItems: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { label: 'Produtos', path: '/produtos', icon: Package },
  { label: 'Clientes', path: '/clientes', icon: Users },
  { label: 'Vendas', path: '/vendas', icon: ShoppingCart },
  { label: 'Insights', path: '/insights', icon: TrendingUp },
  { label: 'Configurações', path: '/configuracoes', icon: Settings },
]
