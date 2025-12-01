"use client"

import * as React from "react"
import {
  IconDashboard,
  IconListDetails,
  IconUsers,
  IconReport,
  IconDatabase,
  IconFileDescription,
  IconSettings,
  IconHelp,
} from "@tabler/icons-react"

import { NavDocuments } from "@/components/nav-documents"
import { NavMain } from "@/components/nav-main"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

import { menu_items } from "@/lib/config/menu"
import { get_role_from_grade, type Role } from "@/lib/utils/role"

// props で受け取るユーザー情報の型
type SidebarUser = {
  name: string
  email: string
  avatar?: string
  grade: string
  isAdmin: boolean          // ← ここを isAdmin に変更
}

// Sidebar 自体の props 型
type AppSidebarProps = React.ComponentProps<typeof Sidebar> & {
  user: SidebarUser
}

export function AppSidebar({ user, ...props }: AppSidebarProps) {
  const role: Role = get_role_from_grade(user.grade)

  // lib/config/menu.ts の menu_items から、ロール & 管理者権限で絞り込み
  const visible_items = menu_items.filter((item) => {
    if (!item.allowed_roles.includes(role)) return false
    if (item.admin_only && !user.isAdmin) return false   // ← ここも isAdmin
    return true
  })

  // メインメニューと管理者メニューに分割
  const main_items = visible_items.filter((item) => !item.admin_only)
  const admin_items = visible_items.filter((item) => item.admin_only)

  // 各 path に対してどのアイコンを使うか
  const icon_for_path: Record<
    string,
    React.ComponentType<React.SVGProps<SVGSVGElement>>
  > = {
    "/dashboard": IconDashboard,
    "/personal_lists": IconListDetails,
    "/assignment": IconUsers,
    "/feedbacks": IconFileDescription,
    "/my_feedbacks": IconFileDescription,
    "/facility_results": IconReport,
    "/admin/analysis": IconReport,
    "/admin/browse": IconDatabase,
    "/admin/edit_db": IconListDetails,
  }

  const default_icon = IconListDetails

  // NavMain が期待する形に変換
  const nav_main_items = main_items.map((item) => ({
    title: item.label,
    url: item.path,
    icon: icon_for_path[item.path] ?? default_icon,
  }))

  // 管理者メニューは NavDocuments に渡す
  const admin_docs_items = admin_items.map((item) => ({
    name: item.label,
    url: item.path,
    icon: icon_for_path[item.path] ?? IconDatabase,
  }))

  // 下部のセカンダリメニュー
  const nav_secondary_items = [
    {
      title: "設定",
      url: "/account",
      icon: IconSettings,
    },
    {
      title: "ヘルプ",
      url: "/help",
      icon: IconHelp,
    },
  ]

  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="data-[slot=sidebar-menu-button]:!p-1.5"
            >
              <a href="/dashboard">
                <IconListDetails className="!size-5" />
                <span className="text-base font-semibold">
                  人事考課システム
                </span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        {/* メインナビ（共通 + 評価機能） */}
        <NavMain items={nav_main_items} />

        {/* 管理者メニュー（admin_only な項目がある場合のみ） */}
        {admin_docs_items.length > 0 && (
          <NavDocuments items={admin_docs_items} />
        )}

        {/* 下部のセカンダリメニュー */}
        <NavSecondary items={nav_secondary_items} className="mt-auto" />
      </SidebarContent>

      <SidebarFooter>
        <NavUser
          user={
            {
              name: user.name,
              email: user.email,
              avatar: user.avatar ?? "/avatars/default.jpg",
            }
          }
        />
        {/* grade / 管理者表示を追加したければここに */}
        {/* 
        <div className="px-3 pb-2 text-xs text-muted-foreground">
          grade: {user.grade} {user.isAdmin ? "(管理者)" : ""}
        </div>
        */}
      </SidebarFooter>
    </Sidebar>
  )
}
