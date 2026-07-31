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

export interface AlterarSenhaPayload {
  senhaAtual: string
  novaSenha: string
}

export function alterarSenha(payload: AlterarSenhaPayload) {
  return apiRequest<void>('/api/auth/senha', {
    method: 'PUT',
    body: payload,
  })
}

export function atualizarPerfil(payload: { name: string }) {
  return apiRequest<AuthenticatedUser>('/api/auth/perfil', {
    method: 'PUT',
    body: payload,
  })
}

export function atualizarAvatar(payload: { imagem: string }) {
  return apiRequest<AuthenticatedUser>('/api/auth/avatar', {
    method: 'PUT',
    body: payload,
  })
}

export function removerAvatar() {
  return apiRequest<AuthenticatedUser>('/api/auth/avatar', {
    method: 'DELETE',
  })
}
