'use client'

import Link from 'next/link'
import { useMemo, useState, type FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { QRCodeSVG } from 'qrcode.react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

import { authMfaSetupInit, authMfaSetupVerify, authLogout } from '@/features/auth/api'
import { ApiError } from '@/lib/api/errors'

type Step = 'idle' | 'ready' | 'verified'

export function MfaSetupCard() {
  const router = useRouter()

  const [step, setStep] = useState<Step>('idle')

  const [loadingInit, setLoadingInit] = useState(false)
  const [loadingVerify, setLoadingVerify] = useState(false)

  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const [otpauthUrl, setOtpauthUrl] = useState<string | null>(null)
  const [secret, setSecret] = useState<string | null>(null)
  const [issuer, setIssuer] = useState<string | null>(null)
  const [accountName, setAccountName] = useState<string | null>(null)
  const [alreadyEnabled, setAlreadyEnabled] = useState<boolean>(false)

  const [totpCode, setTotpCode] = useState<string>('')

  const normalizedTotp = useMemo(() => totpCode.replace(/\s+/g, ''), [totpCode])
  const totpValid = useMemo(() => /^\d{6}$/.test(normalizedTotp), [normalizedTotp])

  const resetUi = () => {
    setError(null)
    setMessage(null)
    setTotpCode('')
    setOtpauthUrl(null)
    setSecret(null)
    setIssuer(null)
    setAccountName(null)
    setAlreadyEnabled(false)
    setStep('idle')
  }

  const handleInit = async () => {
    setError(null)
    setMessage(null)
    setLoadingInit(true)

    try {
      const res = await authMfaSetupInit()

      setOtpauthUrl(res.otpauthUrl)
      setSecret(res.secret ?? null)
      setIssuer(res.issuer)
      setAccountName(res.accountName)

      const enabled = Boolean(res.alreadyEnabled)
      setAlreadyEnabled(enabled)

      if (enabled) {
        setStep('verified')
        setMessage('すでにMFAは有効です。再セットアップはできません。')
      } else {
        setStep('ready')
        setMessage('認証アプリでQRコードを読み取り、表示される6桁コードを入力してください。')
      }
    } catch (e: unknown) {
      console.error(e)
      if (e instanceof ApiError) setError(e.message)
      else setError('MFAセットアップの初期化に失敗しました。')
    } finally {
      setLoadingInit(false)
    }
  }

  const handleVerify = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setMessage(null)

    if (!totpValid) {
      setError('認証コードは6桁の数字で入力してください。')
      return
    }

    setLoadingVerify(true)
    try {
      const res = await authMfaSetupVerify(normalizedTotp)

      if (res.mfaEnabled) {
        setAlreadyEnabled(true)
        setStep('verified')
        setMessage('MFAを有効化しました。次回以降、外部ログイン時に認証が求められます。')
      } else {
        setError('MFAの有効化に失敗しました。')
      }
    } catch (e: unknown) {
      console.error(e)
      if (e instanceof ApiError) setError(e.message)
      else setError('認証コードが正しくないか、有効期限が切れています。')
    } finally {
      setLoadingVerify(false)
    }
  }

  const handleReLogin = async () => {
    try {
      await authLogout()
    } finally {
      router.replace('/login')
    }
  }

  return (
    <Card className="rounded-lg shadow">
      <CardHeader>
        <h1 className="text-xl font-bold text-gray-800">MFA設定</h1>
        <CardDescription>
          認証アプリ（Google Authenticator など）を使用して、多要素認証を有効化します。
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-5">
        {/* 進捗 */}
        <div className="rounded border bg-white p-3">
          <div className="text-sm text-gray-700">
            <span className="text-gray-500">状態：</span>
            {step === 'idle' && '未開始'}
            {step === 'ready' && 'QR発行済み（コード確認待ち）'}
            {step === 'verified' && '有効'}
          </div>
          {issuer || accountName ? (
            <div className="mt-1 text-xs text-gray-500">
              発行情報：{issuer ?? '-'} / {accountName ?? '-'}
            </div>
          ) : null}
        </div>

        {/* メッセージ */}
        {message && (
          <p className="rounded bg-green-50 p-2 text-sm text-green-700">{message}</p>
        )}
        {error && (
          <p className="rounded bg-red-50 p-2 text-sm text-red-600">{error}</p>
        )}

        {/* Step 1 */}
        {step === 'idle' && (
          <div className="space-y-3">
            <Button onClick={handleInit} disabled={loadingInit} className="w-full">
              {loadingInit ? '初期化中...' : 'セットアップを開始する（QR発行）'}
            </Button>

            <Button asChild variant="outline" className="w-full">
              <Link href="/profile">プロフィールへ戻る</Link>
            </Button>

            <p className="text-xs text-gray-500">
              ※ すでにMFAが有効な場合は、開始後に「有効」と表示されます。
            </p>
          </div>
        )}

        {/* Step 2 */}
        {step === 'ready' && otpauthUrl && (
          <div className="space-y-4 rounded border p-4">
            <div className="flex justify-center">
              <QRCodeSVG value={otpauthUrl} size={200} />
            </div>

            <form onSubmit={handleVerify} className="space-y-3">
              <div>
                <Label htmlFor="totp">認証コード（6桁）</Label>
                <Input
                  id="totp"
                  inputMode="numeric"
                  placeholder="123456"
                  value={totpCode}
                  onChange={(e) => setTotpCode(e.target.value)}
                  maxLength={6}
                  autoComplete="one-time-code"
                  className="mt-1"
                  disabled={loadingVerify}
                />
                <p className="mt-1 text-xs text-gray-500">
                  認証アプリに表示される 6 桁の数字を入力してください（30秒ごとに更新されます）。
                </p>
              </div>

              <Button type="submit" disabled={loadingVerify || !totpValid} className="w-full">
                {loadingVerify ? '確認中...' : '有効化する'}
              </Button>
            </form>

            <div className="gap-2 sm:flex-row">
              <Button variant="outline" className="w-full mb-2" onClick={handleInit} disabled={loadingInit}>
                {loadingInit ? '再発行中...' : 'QRを再発行する'}
              </Button>
              <Button variant="outline" className="w-full" onClick={resetUi} disabled={loadingInit || loadingVerify}>
                やり直す
              </Button>
            </div>

            {/* 開発用の詳細は折りたたむ */}
            <details className="rounded bg-gray-50 p-2 text-xs text-gray-600">
              <summary className="cursor-pointer select-none">開発用の詳細を表示</summary>
              <div className="mt-2 space-y-1 break-all">
                <div>otpauthUrl: {otpauthUrl}</div>
                {secret ? <div>secret: {secret}</div> : null}
              </div>
            </details>
          </div>
        )}

        {/* Step 3 */}
        {step === 'verified' && (
          <div className="space-y-3 rounded border p-4">
            <p className="text-sm text-gray-700">
              MFAは{alreadyEnabled ? '有効' : '未設定'}です。
            </p>

            <div className="gap-2 sm:flex-row">
              <Button className="w-full mb-2" onClick={handleReLogin}>
                いったんログアウトしてログイン挙動を確認する
              </Button>
              <Button asChild variant="outline" className="w-full">
                <Link href="/profile">プロフィールへ戻る</Link>
              </Button>
            </div>

            <p className="text-xs text-gray-500">
              ※ 外部ログイン相当ユーザーでログインすると /mfa/verify に遷移します。
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
