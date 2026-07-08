import { NavLink } from 'react-router-dom'
import type { LucideIcon } from 'lucide-react'
import { ChevronsLeft, ChevronsRight, LogOut, Sparkles, UserCircle, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { navItems } from '@/lib/nav-items'
import { useAuth } from '@/lib/auth-context'

interface SidebarProps {
  collapsed: boolean
  onToggleCollapsed: () => void
  mobileOpen: boolean
  onCloseMobile: () => void
}

interface SidebarNavLinkProps {
  to: string
  label: string
  icon: LucideIcon
  collapsed: boolean
  onClick: () => void
}

function SidebarNavLink({ to, label, icon: Icon, collapsed, onClick }: SidebarNavLinkProps) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      title={label}
      className={({ isActive }) =>
        cn(
          'group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
          isActive ? 'bg-primary/10 text-primary' : 'text-sidebar-foreground hover:bg-muted',
          collapsed && 'lg:justify-center lg:px-2',
        )
      }
    >
      {({ isActive }) => (
        <>
          <span
            className={cn(
              'absolute inset-y-1 left-0 w-0.5 rounded-full bg-primary transition-opacity',
              isActive ? 'opacity-100' : 'opacity-0',
            )}
          />
          <Icon className="size-4 shrink-0" />
          <span className={cn(collapsed && 'lg:hidden')}>{label}</span>
        </>
      )}
    </NavLink>
  )
}

export function Sidebar({ collapsed, onToggleCollapsed, mobileOpen, onCloseMobile }: SidebarProps) {
  const { signOut } = useAuth()

  return (
    <>
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 lg:hidden"
          onClick={onCloseMobile}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex flex-col border-r border-border bg-sidebar text-sidebar-foreground transition-all duration-200 lg:sticky lg:top-0 lg:h-screen lg:translate-x-0',
          collapsed ? 'w-64 lg:w-[72px]' : 'w-64',
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        )}
      >
        <div className="flex h-16 items-center justify-between gap-2 border-b border-border px-4">
          <div className="flex items-center gap-2 overflow-hidden">
            <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Sparkles className="size-4" />
            </div>
            {!collapsed && (
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold leading-tight">BMP</p>
                <p className="truncate text-[11px] leading-tight text-muted-foreground">Data &amp; Analytics</p>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={onCloseMobile}
            className="rounded-md p-1 text-muted-foreground hover:bg-muted lg:hidden"
            aria-label="Fechar menu"
          >
            <X className="size-4" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
          {navItems.map((item) => (
            <SidebarNavLink
              key={item.path}
              to={item.path}
              label={item.label}
              icon={item.icon}
              collapsed={collapsed}
              onClick={onCloseMobile}
            />
          ))}
        </nav>

        <div className="space-y-1 border-t border-border px-3 py-4">
          <SidebarNavLink
            to="/perfil"
            label="Perfil"
            icon={UserCircle}
            collapsed={collapsed}
            onClick={onCloseMobile}
          />

          <button
            type="button"
            onClick={signOut}
            className={cn(
              'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-destructive transition-colors hover:bg-destructive/10',
              collapsed && 'lg:justify-center lg:px-2',
            )}
            title="Sair"
          >
            <LogOut className="size-4 shrink-0" />
            <span className={cn(collapsed && 'lg:hidden')}>Sair</span>
          </button>

          <button
            type="button"
            onClick={onToggleCollapsed}
            className="hidden w-full items-center justify-center gap-2 rounded-lg px-3 py-2 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted lg:flex"
          >
            {collapsed ? <ChevronsRight className="size-4" /> : <ChevronsLeft className="size-4" />}
          </button>
        </div>
      </aside>
    </>
  )
}
