import * as React from 'react'
import { clearStoredAuth, readStoredAuth, writeStoredAuth, type StoredAuth } from '@/lib/auth-storage'
import type { AuthenticatedUser } from '@/types/auth'

interface AuthContextValue {
  user: AuthenticatedUser | null
  token: string | null
  isAuthenticated: boolean
  signIn: (auth: StoredAuth) => void
  signOut: () => void
  /** Atualiza o usuário mantido em sessão (ex: após editar o perfil), preservando o token. */
  updateUser: (user: AuthenticatedUser) => void
}

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [auth, setAuth] = React.useState<StoredAuth | null>(() => readStoredAuth())

  const signIn = React.useCallback((next: StoredAuth) => {
    writeStoredAuth(next)
    setAuth(next)
  }, [])

  const signOut = React.useCallback(() => {
    clearStoredAuth()
    setAuth(null)
  }, [])

  const updateUser = React.useCallback((user: AuthenticatedUser) => {
    setAuth((current) => {
      if (!current) {
        return current
      }
      const next = { ...current, user }
      writeStoredAuth(next)
      return next
    })
  }, [])

  const value = React.useMemo<AuthContextValue>(
    () => ({
      user: auth?.user ?? null,
      token: auth?.token ?? null,
      isAuthenticated: auth !== null,
      signIn,
      signOut,
      updateUser,
    }),
    [auth, signIn, signOut, updateUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = React.useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider.')
  }

  return context
}
