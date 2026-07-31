import { Menu } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/lib/auth-context'
import { Button } from '@/components/ui/button'
import { Breadcrumb } from '@/components/layout/Breadcrumb'
import { ThemeToggle } from '@/components/layout/ThemeToggle'
import { UserAvatar } from '@/components/layout/UserAvatar'

interface HeaderProps {
  onOpenMobileMenu: () => void
}

export function Header({ onOpenMobileMenu }: HeaderProps) {
  const { user } = useAuth()

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between gap-4 border-b border-border bg-background/80 px-4 backdrop-blur sm:px-6">
      <div className="flex items-center gap-3">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onOpenMobileMenu}
          aria-label="Abrir menu"
        >
          <Menu className="size-4" />
        </Button>
        <Breadcrumb />
      </div>

      <div className="flex items-center gap-3">
        <ThemeToggle />

        {user && (
          <Link
            to="/perfil"
            className="flex items-center gap-2.5 rounded-lg border-l border-border py-1 pl-3 pr-1 transition-colors hover:bg-muted/60"
            title="Ver perfil"
          >
            <UserAvatar name={user.name} avatar={user.avatar} className="size-8 text-xs" />
            <div className="hidden leading-tight sm:block">
              <p className="text-sm font-medium">{user.name}</p>
              <p className="text-xs text-muted-foreground">{user.role}</p>
            </div>
          </Link>
        )}
      </div>
    </header>
  )
}
