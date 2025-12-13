// features/auth/server.ts

import "server-only"

import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { verify_access_token } from "@/lib/auth/jwt"
import type { MeResponse } from "./types"

export type CurrentUser = {
  userId: string  // IDだがJWT内なので文字列
  employeeId: number
  gradeCode: string
  isAdmin: boolean
}


export async function get_current_user_or_null(): Promise<CurrentUser | null> {
  // cookies() はここで初めて RequestCookies が取れる
  const cookieStore = await cookies()
  const accessToken = cookieStore.get("access_token")?.value

  console.log("access_token from cookies:", accessToken ? "[exists]" : "null")

  if (!accessToken) return null

  const payload = await verify_access_token(accessToken)
  if (!payload) {
    console.log("verify_access_token returned null")
    return null
  }

  console.log("CurrentUser payload:", payload)
  return {
    userId: String(payload.sub),
    employeeId: Number(payload.employee_id),
    gradeCode: payload.grade,
    isAdmin: Boolean(payload.is_admin),
  }
}

export async function require_current_user(): Promise<CurrentUser> {
  const user = await get_current_user_or_null()
  if (!user) redirect("/login")
  return user
}

// 現在のユーザー情報を API 経由で取得。
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL

export async function fetch_me_or_null(): Promise<MeResponse | null> {
  const cookieStore = await cookies()
  const accessToken = cookieStore.get("access_token")?.value
  if (!accessToken) return null

  const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
    method: "GET",
    headers: {
      // Cookie は credentials ではなく headers の Cookie 伝播で送られる（Server fetch）
      Cookie: cookieStore.toString(),
      "Content-Type": "application/json",
    },
    cache: "no-store",
  })

  if (!res.ok) return null
  return (await res.json()) as MeResponse
}

export async function require_me(): Promise<MeResponse> {
  const me = await fetch_me_or_null()
  if (!me) redirect("/login")
  return me
}

