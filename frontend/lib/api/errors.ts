// /lib/api/errors.ts
// API エラー処理ユーティリティ

export type FastApiDetail =
  | string
  | {
      code?: string
      message?: string
      [k: string]: unknown
    }

export type FastApiErrorBody =
  | string
  | {
      detail?: FastApiDetail
      message?: unknown
      error?: unknown
      [k: string]: unknown
    }
  | null

export class ApiError extends Error {
  status?: number
  code?: string
  body?: FastApiErrorBody

  constructor(message: string, opts?: { status?: number; code?: string; body?: FastApiErrorBody }) {
    super(message)
    this.name = 'ApiError'
    this.status = opts?.status
    this.code = opts?.code
    this.body = opts?.body
  }
}

/**
 * Response を text で受け、JSON ならパース。失敗したら生テキストで返す。
 * FastAPI が HTML を返してしまうケース（nginx/500等）にも耐える。
 */
export async function parseJsonOrText(res: Response): Promise<FastApiErrorBody> {
  const text = await res.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}

function extractDetail(body: FastApiErrorBody): FastApiDetail | undefined {
  if (!body) return undefined
  if (typeof body === 'string') return body
  if (typeof body === 'object') {
    // FastAPI標準は detail。APIによっては message/error の場合も救う
    return (body as any).detail ?? (body as any).message ?? (body as any).error
  }
  return undefined
}

export function extractErrorMessage(body: FastApiErrorBody, fallback: string): string {
  const d = extractDetail(body)

  if (typeof d === 'string') return d
  if (d && typeof d === 'object') return (d as any).message ?? (d as any).code ?? fallback

  // ここまで来たら完全に想定外
  return fallback
}

export function extractErrorCode(body: FastApiErrorBody): string | undefined {
  const d = extractDetail(body)

  if (typeof d === 'string') return d
  if (d && typeof d === 'object') return (d as any).code

  return undefined
}

/**
 * res.ok === false のときに呼ぶ。ApiError を throw する。
 */
export async function throwApiError(res: Response, fallbackMessage: string): Promise<never> {
  const body = await parseJsonOrText(res)
  const message = extractErrorMessage(body, fallbackMessage)
  const code = extractErrorCode(body)

  throw new ApiError(message, { status: res.status, code, body })
}
