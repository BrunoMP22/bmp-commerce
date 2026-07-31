import { apiRequest } from '@/api/client'

export interface InfoSistema {
  nome: string
  versao: string
  ambiente: string
}

export function getInfoSistema() {
  return apiRequest<InfoSistema>('/api/sistema/info')
}
