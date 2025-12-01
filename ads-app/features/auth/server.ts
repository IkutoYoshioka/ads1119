// features/auth/server.ts

import "server-only"

import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { verify_access_token } from "@/lib/auth/jwt"

export type CurrentUser = {
  employeeId: string
  grade: string
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
    employeeId: payload.sub,
    grade: payload.grade,
    isAdmin: Boolean(payload.is_admin),
  }
}

export async function require_current_user(): Promise<CurrentUser> {
  const user = await get_current_user_or_null()
  if (!user) redirect("/login")
  return user
}


