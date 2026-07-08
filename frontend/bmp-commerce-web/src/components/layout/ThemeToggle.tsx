import { Moon, Sun } from 'lucide-react'
import { useTheme } from '@/hooks/use-theme'
import { Button } from '@/components/ui/button'
import type { VariantProps } from 'class-variance-authority'
import type { buttonVariants } from '@/components/ui/button'

interface ThemeToggleProps {
  variant?: VariantProps<typeof buttonVariants>['variant']
}

export function ThemeToggle({ variant = 'ghost' }: ThemeToggleProps) {
  const { theme, toggleTheme } = useTheme()

  return (
    <Button type="button" variant={variant} size="icon" onClick={toggleTheme} aria-label="Alternar tema">
      {theme === 'dark' ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </Button>
  )
}
