import { ApiError } from '@/api/client'

export function getErrorMessage(error: unknown, fallback: string): string {
  return error instanceof ApiError ? error.message : fallback
}
