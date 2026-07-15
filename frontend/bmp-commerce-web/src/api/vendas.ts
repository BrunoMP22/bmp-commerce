import { apiRequest } from '@/api/client'
import type { RegistrarVendaPayload, Venda } from '@/types/venda'

export function listVendas() {
  return apiRequest<Venda[]>('/api/vendas')
}

export function getVenda(id: string) {
  return apiRequest<Venda>(`/api/vendas/${id}`)
}

export function registrarVenda(payload: RegistrarVendaPayload) {
  return apiRequest<Venda>('/api/vendas', { method: 'POST', body: payload })
}

export function cancelarVenda(id: string) {
  return apiRequest<Venda>(`/api/vendas/${id}/cancelar`, { method: 'POST' })
}
