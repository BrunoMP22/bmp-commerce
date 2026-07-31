import * as React from 'react'

export type ThemePreference = 'light' | 'dark' | 'system'
type ResolvedTheme = 'light' | 'dark'

const STORAGE_KEY = 'bmp_theme'

function getSystemTheme(): ResolvedTheme {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function getInitialPreference(): ThemePreference {
  const stored = localStorage.getItem(STORAGE_KEY)

  if (stored === 'light' || stored === 'dark' || stored === 'system') {
    return stored
  }

  return 'system'
}

interface ThemeContextValue {
  /** Tema efetivamente aplicado (preferência "system" já resolvida). */
  theme: ResolvedTheme
  preference: ThemePreference
  setPreference: (preference: ThemePreference) => void
  toggleTheme: () => void
}

const ThemeContext = React.createContext<ThemeContextValue | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [preference, setPreference] = React.useState<ThemePreference>(getInitialPreference)
  const [systemTheme, setSystemTheme] = React.useState<ResolvedTheme>(getSystemTheme)

  React.useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = () => setSystemTheme(media.matches ? 'dark' : 'light')

    media.addEventListener('change', handleChange)
    return () => media.removeEventListener('change', handleChange)
  }, [])

  const theme = preference === 'system' ? systemTheme : preference

  React.useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  React.useEffect(() => {
    localStorage.setItem(STORAGE_KEY, preference)
  }, [preference])

  const toggleTheme = React.useCallback(() => {
    setPreference((current) => {
      const resolved = current === 'system' ? getSystemTheme() : current
      return resolved === 'dark' ? 'light' : 'dark'
    })
  }, [])

  const value = React.useMemo<ThemeContextValue>(
    () => ({ theme, preference, setPreference, toggleTheme }),
    [theme, preference, toggleTheme],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme(): ThemeContextValue {
  const context = React.useContext(ThemeContext)

  if (context === undefined) {
    throw new Error('useTheme deve ser usado dentro de <ThemeProvider>.')
  }

  return context
}
