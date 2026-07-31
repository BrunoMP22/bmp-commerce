import { apiRequest } from '@/api/client'
import type { InsightsResponse } from '@/types/insight'

export function getInsights() {
  return apiRequest<InsightsResponse>('/api/insights')
}
