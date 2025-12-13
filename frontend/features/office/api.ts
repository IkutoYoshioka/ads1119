import { throwApiError } from '@/lib/api/errors'
import type { Office, OfficeOption } from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL

export async function fetchOffices(): Promise<OfficeOption[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/offices`, {
    method: 'GET',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
  })

  if (!res.ok) {
    await throwApiError(res, '事業所一覧の取得に失敗しました。')
  }

  const offices = (await res.json()) as Office[]
  return offices.map((o) => ({
    value: String(o.id),
    label: o.name,
  }))
}
