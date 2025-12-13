'use client';

import { type ReactElement } from 'react';
import { MfaVerifyForm } from '@/features/auth/components/MfaVerifyForm';

export default function Page(): ReactElement {
  return (
    <div className="flex h-screen bg-gray-100">
      <div className="flex w-full items-center justify-center bg-white">
        <MfaVerifyForm />
      </div>
    </div>
  );
}
