import { throwApiError } from '@/lib/api/errors'
import type { PasswordResetRequestIn, PasswordResetRequestOut } from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL

export async function requestPasswordReset(
  payload: PasswordResetRequestIn
): Promise<PasswordResetRequestOut> {
  const res = await fetch(`${API_BASE_URL}/api/v1/password-reset-requests`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    await throwApiError(res, '送信に失敗しました。入力内容をご確認ください。')
  }

  return (await res.json()) as PasswordResetRequestOut
}
