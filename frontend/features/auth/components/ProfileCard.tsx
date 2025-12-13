'use client'

import Link from 'next/link'
import { useEffect, useMemo, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'

import { authMe, authLogout } from '@/features/auth/api'
import type { MeResponse } from '@/features/auth/types'
import { ApiError } from '@/lib/api/errors'

function Field({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="space-y-1">
      <div className="text-xs text-gray-500">{label}</div>
      <div className="text-sm font-medium text-gray-800">{value}</div>
    </div>
  )
}

export function ProfileCard() {
  const [me, setMe] = useState<MeResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const displayName = useMemo(() => {
    if (!me) return '-'
    const name = me.fullName ?? [me.lastName, me.firstName].filter(Boolean).join(' ')
    return name || '-'
  }, [me])

  const gradeLabel = useMemo(() => {
    if (!me) return '-'
    const parts = [me.gradeCode ?? null, me.gradeName ?? null].filter(Boolean)
    return parts.length ? parts.join(' / ') : '-'
  }, [me])

  const officeLabel = useMemo(() => {
    if (!me) return '-'
    return me.officeName ?? (me.officeId != null ? `Office #${me.officeId}` : '-')
  }, [me])

  const siteLabel = useMemo(() => {
    if (!me) return '-'
    return me.siteName ?? (me.siteId != null ? `Site #${me.siteId}` : '-')
  }, [me])

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await authMe()
        setMe(res)
      } catch (e) {
        console.error(e)
        if (e instanceof ApiError) setError(e.message)
        else setError('プロフィール情報の取得に失敗しました。')
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [])

  const handleLogout = async () => {
    try {
      await authLogout()
    } finally {
      window.location.href = '/login'
    }
  }

  const mfaCtaLabel = me?.mfaEnabled ? 'MFA設定を確認' : 'MFAを設定（推奨）'
  const mfaBadgeVariant = me?.mfaEnabled ? 'secondary' : 'destructive'

  return (
    <Card className="rounded-xl shadow">
      <CardHeader className="space-y-2">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1">
            <h1 className="text-xl font-bold text-gray-800">プロフィール</h1>
            <CardDescription>アカウント情報とセキュリティ設定を確認します。</CardDescription>
          </div>

          {/* 右上の状態バッジ群 */}
          <div className="flex flex-wrap items-center justify-end gap-2">
            {me && (
              <>
                <Badge variant={me.isAdmin ? 'default' : 'secondary'}>
                  {me.isAdmin ? '管理者' : '一般'}
                </Badge>
                <Badge variant={mfaBadgeVariant}>
                  MFA: {me.mfaEnabled ? '有効' : '未設定'}
                </Badge>
                {me.mustChangePassword && (
                  <Badge variant="destructive">要パスワード変更</Badge>
                )}
              </>
            )}
          </div>
        </div>

        {error && (
          <p className="rounded bg-red-50 p-2 text-sm text-red-600">{error}</p>
        )}
      </CardHeader>

      <CardContent className="space-y-5">
        {/* 概要 */}
        <div className="rounded-lg border p-4">
          <div className="mb-3 text-sm font-semibold text-gray-800">概要</div>

          {loading && !me ? (
            <div className="space-y-3">
              <Skeleton className="h-5 w-1/2" />
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-4 w-1/4" />
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="氏名" value={displayName} />
              <Field label="社員コード" value={me?.employeeCode ?? '-'} />
              <Field label="ユーザーID" value={me ? String(me.userId) : '-'} />
              <Field label="社員ID" value={me?.employeeId != null ? String(me.employeeId) : '-'} />
            </div>
          )}
        </div>

        <Separator />

        {/* 所属情報 */}
        <div className="rounded-lg border p-4">
          <div className="mb-3 text-sm font-semibold text-gray-800">所属</div>

          {loading && !me ? (
            <div className="grid gap-4 sm:grid-cols-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="等級" value={gradeLabel} />
              <Field label="事業所" value={officeLabel} />
              <Field label="拠点（Site）" value={siteLabel} />
              <Field
                label="等級順位"
                value={me?.gradeRankOrder != null ? String(me.gradeRankOrder) : '-'}
              />
            </div>
          )}
        </div>

        <Separator />

        {/* セキュリティ */}
        <div className="rounded-lg border p-4">
          <div className="mb-3 text-sm font-semibold text-gray-800">セキュリティ</div>

          {loading && !me ? (
            <div className="space-y-3">
              <Skeleton className="h-4 w-2/3" />
              <Skeleton className="h-4 w-1/2" />
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant={mfaBadgeVariant}>
                  MFA: {me?.mfaEnabled ? '有効' : '未設定'}
                </Badge>
                {me?.mustChangePassword ? (
                  <Badge variant="destructive">次回パスワード変更が必要</Badge>
                ) : (
                  <Badge variant="secondary">パスワード状態: OK</Badge>
                )}
              </div>

              {!me?.mfaEnabled && (
                <p className="rounded bg-amber-50 p-2 text-sm text-amber-800">
                  外部ログインを行う可能性がある場合、MFAの設定を推奨します。
                </p>
              )}

              {me?.mustChangePassword && (
                <p className="rounded bg-yellow-50 p-2 text-sm text-yellow-800">
                  現在、パスワード変更が必要です。速やかに変更してください。
                </p>
              )}
            </div>
          )}
        </div>

        {/* アクション */}
        <div className="flex flex-col gap-2 sm:flex-row">
          <Button asChild className="w-full sm:w-auto">
            <Link href="/profile/mfa">{mfaCtaLabel}</Link>
          </Button>

          <Button variant="outline" onClick={handleLogout} className="w-full sm:w-auto">
            ログアウト
          </Button>

          <Button asChild variant="ghost" className="w-full sm:w-auto">
            <Link href="/dashboard">ダッシュボードへ</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
