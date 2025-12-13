'use client';

import Link from 'next/link';
import { useState, type FormEvent, type ReactElement } from 'react';
import { useRouter } from 'next/navigation';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { authLogin } from '@/features/auth/api';
import { LoginResponse } from '@/features/auth/types';
import { ApiError } from '@/lib/api/errors';

export default function LoginPage(): ReactElement {
  const [employeeCode, setEmployeeCode] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    if (!employeeCode || !password) {
      setError('社員コードとパスワードを入力してください');
      return;
    }

    try {
      const result: LoginResponse = await authLogin(employeeCode, password)

      if (result.requiresMfa) {
        if (!result.temporaryToken) {
          setError("MFAトークンが取得できませんでした")
          return
        }
        sessionStorage.setItem("mfa_temporary_token", result.temporaryToken)
        router.push("/mfa/verify")
        return
      }

      router.push(result.redirectPath ?? "/dashboard")
    } catch (err: unknown) {
      console.error("Login error:", err)
      if (err instanceof ApiError) {
        setError(err.message)
        return
      }
      setError("無効な社員コードまたはパスワードです")
    }

  };

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="flex w-full items-center justify-center bg-white">
        <Card className="w-full max-w-md rounded-lg p-8 shadow-lg">
          <CardHeader>
            <h1 className="mb-2 text-center text-3xl font-bold text-gray-800">
              青葉福祉会
            </h1>
            <CardDescription className="text-center text-gray-600">
              社員コードとパスワードを入力してください
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label htmlFor="employeeId" className="text-gray-700">
                  社員コード
                </Label>
                <Input
                  id="employeeId"
                  type="text"
                  placeholder="R00000"
                  className="mt-1"
                  value={employeeCode}
                  onChange={(e) => setEmployeeCode(e.target.value)}
                  autoComplete="off"
                />
              </div>

              <div>
                <Label htmlFor="password" className="text-gray-700">
                  パスワード
                </Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="******"
                  className="mt-1"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <Link
                  href="/login/forget_form"
                  className="mt-1 block text-right text-sm text-gray-500 transition hover:text-gray-800"
                >
                  パスワードを忘れた方
                </Link>
              </div>

              {error && (
                <p className="rounded bg-red-50 p-2 text-center text-sm text-red-500">
                  {error}
                </p>
              )}

              <Button
                type="submit"
                className="w-full bg-gray-800 text-white transition hover:bg-gray-700"
              >
                ログイン
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
