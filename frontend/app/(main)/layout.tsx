import type { ReactNode } from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar"
import { SiteHeader } from "@/components/site-header"
import { require_me } from "@/features/auth/server"

export const runtime = "nodejs"

type MainLayoutProps = { children: ReactNode }

export default async function MainLayout({ children }: MainLayoutProps) {
  const me = await require_me()

  const displayName =
    me.fullName ??
    (me.lastName && me.firstName ? `${me.lastName} ${me.firstName}` : null) ??
    me.employeeCode ??
    `user:${me.userId}`

  const sidebarUser = {
    name: displayName,
    email: me.employeeCode ? `${me.employeeCode}@example.com` : `user-${me.userId}@example.com`,
    avatar: "/avatars/default.jpg",
    grade: me.gradeCode ?? "",      // AppSidebar の grade: string に合わせる
    isAdmin: me.isAdmin,
  }

  return (
    <SidebarProvider>
      <AppSidebar me={me} />
      <SidebarInset>
        <SiteHeader userName={sidebarUser.name} />
        <main>{children}</main>
      </SidebarInset>
    </SidebarProvider>
  )
}
