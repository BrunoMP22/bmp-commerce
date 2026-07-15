import { apiRequest } from '@/api/client'
import type { AtualizarClientePayload, Cliente, CriarClientePayload } from '@/types/cliente'

export function listClientes() {
  return apiRequest<Cliente[]>('/api/clientes')
}

export function getCliente(id: string) {
  return apiRequest<Cliente>(`/api/clientes/${id}`)
}

export function createCliente(payload: CriarClientePayload) {
  return apiRequest<Cliente>('/api/clientes', { method: 'POST', body: payload })
}

export function updateCliente(id: string, payload: AtualizarClientePayload) {
  return apiRequest<Cliente>(`/api/clientes/${id}`, { method: 'PUT', body: payload })
}

export function deleteCliente(id: string) {
  return apiRequest<void>(`/api/clientes/${id}`, { method: 'DELETE' })
}
