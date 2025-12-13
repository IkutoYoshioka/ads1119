// app/(main)/(admin)/layout.tsx
import { redirect } from "next/navigation"
import { authMe } from "@/features/auth/api"

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const me = await authMe()
  if (!me) redirect("/login")

  // 管理者のみ許可（役員も isAdmin=true 前提）
  if (!me.isAdmin) redirect("/dashboard")

  return <>{children}</>
}
