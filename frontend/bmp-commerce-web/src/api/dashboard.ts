import { apiRequest } from '@/api/client'
import type { Dashboard } from '@/types/dashboard'

export function getDashboard() {
  return apiRequest<Dashboard>('/api/dashboard')
}
