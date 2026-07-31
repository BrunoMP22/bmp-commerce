export interface AuthenticatedUser {
  userId: string
  name: string
  email: string
  role: string
  tenantId: string | null
  tenantName: string | null
  avatar: string | null
  criadoEm: string
}

export interface LoginResponse {
  token: string
  user: AuthenticatedUser
}
