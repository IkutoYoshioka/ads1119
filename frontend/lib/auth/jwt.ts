// lib/auth/jwt.ts
import { jwtVerify, JWTPayload } from "jose"

const JWT_SECRET = process.env.JWT_SECRET

if (!JWT_SECRET) {
  throw new Error("JWT_SECRET is not set in environment variables")
}

const secret_key = new TextEncoder().encode(JWT_SECRET)

export type AccessTokenPayload = JWTPayload & {
  sub: string // employee_id
  grade: string
  is_admin: boolean
}

/**
 * FastAPI が発行した access_token（JWT）を検証し、ペイロードを返す
 */
export async function verify_access_token(
  token: string,
): Promise<AccessTokenPayload | null> {
  try {
    const { payload } = await jwtVerify(token, secret_key)
     console.log("JWT verify success. payload =", payload)  // ← 追加（デバッグ用）
    return payload as AccessTokenPayload
  } catch (error) {
    console.error("Failed to verify JWT:", error)
    return null
  }
}
