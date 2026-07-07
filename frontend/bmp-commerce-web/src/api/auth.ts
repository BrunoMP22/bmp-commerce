import { apiRequest } from '@/api/client'
import type { AuthenticatedUser, LoginResponse } from '@/types/auth'

export interface LoginPayload {
  email: string
  password: string
}

export function login(payload: LoginPayload) {
  return apiRequest<LoginResponse>('/api/auth/login', {
    method: 'POST',
    body: payload,
    authenticated: false,
  })
}

export function fetchCurrentUser() {
  return apiRequest<AuthenticatedUser>('/api/auth/me')
}
