// app/profile/mfa/page.tsx
'use client'

import { type ReactElement } from 'react'
import { MfaSetupCard } from '@/features/auth/components/MfaSetupCard'

export default function Page(): ReactElement {
  return (
    <div className="p-6">
      <div className="mx-auto w-full max-w-2xl space-y-4">
        <MfaSetupCard />
      </div>
    </div>
  )
}
