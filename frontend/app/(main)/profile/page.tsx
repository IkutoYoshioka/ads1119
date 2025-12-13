'use client'

import { type ReactElement } from 'react'
import { ProfileCard } from '@/features/auth/components/ProfileCard'

export default function Page(): ReactElement {
  return (
    <div className="p-6">
      <div className="mx-auto w-full max-w-2xl space-y-4">
        <ProfileCard />
      </div>
    </div>
  )
}
