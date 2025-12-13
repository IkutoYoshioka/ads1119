import type {
  LoginResponse,
  MfaVerifyLoginResponse,
  MfaSetupInitResponse,
  MfaSetupVerifyResponse,
  MeResponse
} from './types'
import { throwApiError } from '@/lib/api/errors'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL

if (!API_BASE_URL) {
  // eslint-disable-next-line no-console
  console.warn('NEXT_PUBLIC_API_BASE_URL is not set. Please define it in .env.local.')
}


export async function authLogin(employeeCode: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ employeeCode, password }),
  })

  if (!res.ok) {
    await throwApiError(res, 'Login failed')
  }

  return (await res.json()) as LoginResponse
}

export async function authLogout(): Promise<void> {
  await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  })
}

export async function authVerifyMfaLogin(
  temporaryToken: string,
  totpCode: string,
): Promise<MfaVerifyLoginResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/mfa/verify-login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ temporaryToken, totpCode }),
  })

  if (!res.ok) {
    await throwApiError(res, 'MFA verify login failed')
  }

  return (await res.json()) as MfaVerifyLoginResponse
}

export async function authMfaSetupInit(): Promise<MfaSetupInitResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/mfa/setup-init`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({}),
  })

  if (!res.ok) {
    await throwApiError(res, 'MFA setup init failed')
  }

  return (await res.json()) as MfaSetupInitResponse
}

export async function authMfaSetupVerify(totpCode: string): Promise<MfaSetupVerifyResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/mfa/setup-verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ totpCode }),
  })

  if (!res.ok) {
    await throwApiError(res, 'MFA setup verify failed')
  }

  return (await res.json()) as MfaSetupVerifyResponse
}

export async function authMe(): Promise<MeResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  })

  if (!res.ok) {
    await throwApiError(res, "Fetch me failed")
  }

  return (await res.json()) as MeResponse
}