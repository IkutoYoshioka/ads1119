'use client'

import Link from 'next/link'
import { useEffect, useMemo, useRef, useState, type FormEvent, type ChangeEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

import { fetchOffices } from '@/features/office/api'
import type { OfficeOption } from '@/features/office/types'
import { requestPasswordReset } from '@/features/passwordForget/api'
import { ApiError } from '@/lib/api/errors'

export function ForgetForm() {
  const [employeeCode, setEmployeeCode] = useState('')
  const [officeId, setOfficeId] = useState('') // Select の都合で string
  const [offices, setOffices] = useState<OfficeOption[]>([])
  const [officesLoading, setOfficesLoading] = useState(false)

  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // ✅ 成功後は完了画面に切り替える
  const [submitted, setSubmitted] = useState(false)

  const employeeCodeRef = useRef<HTMLInputElement | null>(null)

  const canSubmit = useMemo(() => {
    if (submitting) return false
    const code = employeeCode.trim()
    if (!code) return false
    const idNum = Number(officeId)
    if (!Number.isInteger(idNum) || idNum <= 0) return false
    return true
  }, [employeeCode, officeId, submitting])

  async function loadOffices() {
    setOfficesLoading(true)
    setError(null)
    try {
      const data = await fetchOffices()
      setOffices(data)
    } catch (e) {
      console.error('Failed to fetch offices:', e)
      setOffices([])
      setError('事業所一覧の取得に失敗しました。ネットワーク状況をご確認ください。')
    } finally {
      setOfficesLoading(false)
    }
  }

  useEffect(() => {
    void loadOffices()
  }, [])

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)

    const normalizedEmployeeCode = employeeCode.trim()
    const officeIdNum = Number(officeId)

    if (!normalizedEmployeeCode) {
      setError('社員IDを入力してください')
      employeeCodeRef.current?.focus()
      return
    }

    if (!Number.isInteger(officeIdNum) || officeIdNum <= 0) {
      setError('事業所を正しく選択してください')
      return
    }

    setSubmitting(true)
    try {
      await requestPasswordReset({
        employeeCode: normalizedEmployeeCode,
        officeId: officeIdNum,
      })

      // ✅ 送信成功：フォームは以後表示しない
      setSubmitted(true)

      // （任意）入力値はクリアしておく
      setEmployeeCode('')
      setOfficeId('')
    } catch (e) {
      console.error('Password reset request error:', e)
      if (e instanceof ApiError) setError(e.message)
      else setError('送信に失敗しました。入力内容をご確認ください。')
    } finally {
      setSubmitting(false)
    }
  }

  const handleEmployeeCodeChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (error) setError(null)
    setEmployeeCode(e.target.value)
  }

  // ✅ 完了画面（成功後）
  if (submitted) {
    return (
      <Card className="w-full max-w-md rounded-xl p-6 shadow-xl">
        <CardHeader className="text-center">
          <CardTitle className="mb-2 text-2xl font-bold text-gray-800">送信完了</CardTitle>
          <CardDescription className="text-gray-600">
            本部担当者が確認後、パスワードリセットの手続きを行います。
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <p className="rounded bg-green-50 p-3 text-center text-sm text-green-700">
            送信が完了しました。本部からの連絡をお待ちください。
          </p>

          <Button asChild className="w-full bg-gray-800 text-white transition hover:bg-gray-700">
            <Link href="/">ログイン画面へ戻る</Link>
          </Button>

          <p className="text-center text-xs text-gray-500">
            ※ 通常、確認には1営業日程度かかります。
          </p>
        </CardContent>
      </Card>
    )
  }

  // ✅ 通常（入力フォーム）
  return (
    <Card className="w-full max-w-md rounded-xl p-6 shadow-xl">
      <CardHeader className="text-center">
        <CardTitle className="mb-2 text-3xl font-bold text-gray-800">青葉福祉会</CardTitle>
        <CardDescription className="text-gray-600">
          以下の項目を入力して本部へ送信してください。
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <Label htmlFor="employeeCode" className="text-gray-700">社員コード</Label>
            <Input
              ref={employeeCodeRef}
              id="employeeCode"
              type="text"
              placeholder="R00000"
              className="mt-1"
              value={employeeCode}
              onChange={handleEmployeeCodeChange}
              autoComplete="off"
              disabled={submitting}
            />
          </div>

          <div>
            <Label htmlFor="office" className="text-gray-700">事業所</Label>

            <Select
              value={officeId}
              onValueChange={(v) => {
                if (error) setError(null)
                setOfficeId(v)
              }}
              disabled={submitting || officesLoading}
            >
              <SelectTrigger id="office" className="mt-1">
                <SelectValue
                  placeholder={officesLoading ? '事業所を読み込み中...' : '事業所を選択してください'}
                />
              </SelectTrigger>
              <SelectContent>
                {offices.length > 0 ? (
                  offices.map((o) => (
                    <SelectItem key={o.value} value={o.value}>
                      {o.label}
                    </SelectItem>
                  ))
                ) : (
                  <div className="px-3 py-2 text-sm text-gray-400">事業所情報を取得できません</div>
                )}
              </SelectContent>
            </Select>

            {!officesLoading && offices.length === 0 && (
              <div className="mt-2">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() => void loadOffices()}
                  disabled={submitting}
                >
                  事業所一覧を再取得
                </Button>
              </div>
            )}
          </div>

          {error && (
            <p className="rounded bg-red-50 p-2 text-center text-sm text-red-500">
              {error}
            </p>
          )}

          <Button
            type="submit"
            className="w-full bg-gray-800 text-white transition hover:bg-gray-700"
            disabled={!canSubmit}
          >
            {submitting ? '送信中...' : '送信する'}
          </Button>
        </form>

        <div className="mt-4 text-center">
          <Link href="/" className="text-sm text-gray-500 transition hover:text-gray-800">
            ログイン画面へ戻る
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}
