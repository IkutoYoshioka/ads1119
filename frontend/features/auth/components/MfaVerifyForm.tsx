'use client';

import { useEffect, useState, type FormEvent, type ReactElement } from 'react';
import { useRouter } from 'next/navigation';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

import { authVerifyMfaLogin } from '../api';

export function MfaVerifyForm(): ReactElement {
  const router = useRouter();

  const [temporaryToken, setTemporaryToken] = useState<string | null>(null);
  const [totpCode, setTotpCode] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  useEffect(() => {
    const token = sessionStorage.getItem('mfa_temporary_token');
    if (!token) {
      router.replace('/login');
      return;
    }
    setTemporaryToken(token);
  }, [router]);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    if (!temporaryToken) {
      setError('MFAトークンが見つかりません。ログインからやり直してください。');
      router.replace('/login');
      return;
    }

    const normalized = totpCode.replace(/\s+/g, '');
    if (!/^\d{6}$/.test(normalized)) {
      setError('認証コードは6桁の数字で入力してください。');
      return;
    }

    setSubmitting(true);
    try {
      const res = await authVerifyMfaLogin(temporaryToken, normalized);
      sessionStorage.removeItem('mfa_temporary_token');
      router.replace(res.redirectPath ?? '/dashboard');
    } catch (err: unknown) {
      console.error(err);
      setError('認証コードが正しくないか、有効期限が切れています。');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card className="w-full max-w-md rounded-lg p-8 shadow-lg">
      <CardHeader>
        <h1 className="mb-2 text-center text-2xl font-bold text-gray-800">多要素認証</h1>
        <CardDescription className="text-center text-gray-600">
          認証アプリに表示される6桁コードを入力してください
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <Label htmlFor="totp" className="text-gray-700">
              認証コード（6桁）
            </Label>
            <Input
              id="totp"
              inputMode="numeric"
              placeholder="123456"
              className="mt-1"
              value={totpCode}
              onChange={(e) => setTotpCode(e.target.value)}
              autoComplete="one-time-code"
              maxLength={6}
            />
          </div>

          {error && (
            <p className="rounded bg-red-50 p-2 text-center text-sm text-red-500">{error}</p>
          )}

          <div className="space-y-2">
            <Button type="submit" className="w-full bg-gray-800 text-white" disabled={submitting || !temporaryToken}>
              {submitting ? '確認中...' : '認証してログイン'}
            </Button>

            <Button
              type="button"
              variant="outline"
              className="w-full"
              onClick={() => {
                sessionStorage.removeItem('mfa_temporary_token');
                router.replace('/login');
              }}
              disabled={submitting}
            >
              ログイン画面に戻る
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
