import { apiRequest } from '@/api/client'
import type { AtualizarProdutoPayload, CriarProdutoPayload, Produto } from '@/types/produto'

export function listProdutos(search?: string) {
  const query = search ? `?search=${encodeURIComponent(search)}` : ''
  return apiRequest<Produto[]>(`/api/produtos${query}`)
}

export function getProduto(id: string) {
  return apiRequest<Produto>(`/api/produtos/${id}`)
}

export function createProduto(payload: CriarProdutoPayload) {
  return apiRequest<Produto>('/api/produtos', { method: 'POST', body: payload })
}

export function updateProduto(id: string, payload: AtualizarProdutoPayload) {
  return apiRequest<Produto>(`/api/produtos/${id}`, { method: 'PUT', body: payload })
}

export function deleteProduto(id: string) {
  return apiRequest<void>(`/api/produtos/${id}`, { method: 'DELETE' })
}
