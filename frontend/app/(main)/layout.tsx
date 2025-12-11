// app/(main)/layout.tsx
import type { ReactNode } from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { require_current_user } from "@/features/auth/server"
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar"
import { SiteHeader } from "@/components/site-header"

export const runtime = "nodejs"


type MainLayoutProps = {
  children: ReactNode
}

// サーバーコンポーネント（デフォルト）として動く
export default async function MainLayout({ children }: MainLayoutProps) {
  // 未ログインなら require_current_user 内で /login にリダイレクトされる
  const currentUser = await require_current_user()

  // AppSidebar に渡すユーザー情報
  const sidebarUser = {
    name: currentUser.employeeId,                // 将来、氏名を持ったら差し替え
    email: `${currentUser.employeeId}@example.com`, // 仮の表示用。不要なら空文字でもOK
    avatar: "/avatars/default.jpg",
    grade: currentUser.grade,
    isAdmin: currentUser.isAdmin,
  }

  return (
    <SidebarProvider>
      
        <AppSidebar user={sidebarUser} />

        <SidebarInset>
          {/* 上部ヘッダー */}
          <SiteHeader userName={sidebarUser.name} />

          {/* コンテンツ */}
          <main>
            {children}
          </main>
        </SidebarInset>
      
    </SidebarProvider>
  )
}


