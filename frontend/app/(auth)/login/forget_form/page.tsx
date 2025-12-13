'use client';

import Link from 'next/link';
import {
  Suspense,
  type ReactElement,
} from 'react';


import Loading from '@/app/loading';
import { ForgetForm } from '@/features/passwordForget/components/ForgetForm';
export default function ForgotPasswordPage(): ReactElement {
 
  return (
    <Suspense fallback={<Loading />}>
      <div className="flex h-screen bg-gray-100">
        {/* 左側：パスワードリセットフォーム */}
        <ForgetForm />

        {/* 右側：説明セクション */}
        <div className="flex w-1/2 items-center justify-center bg-gray-800 px-10 text-gray-300">
          <div className="space-y-6 text-center">
            <h2 className="mb-4 text-3xl font-bold text-white">
              パスワードを忘れた方へ
            </h2>
            <p className="text-lg leading-relaxed">
              パスワードを忘れた場合は、
              <br />
              社員コードと所属事業所名を入力して送信してください。
              <br />
              本部担当者が確認後、パスワードリセットの手続きを行います。
            </p>
            <p className="text-sm text-gray-400">
              ※ 通常、確認には1営業日程度かかります。
            </p>
          </div>
        </div>
      </div>
    </Suspense>
  );
}
