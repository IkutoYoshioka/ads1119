"use client"

import * as React from "react"
import Link from "next/link"
import {
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

import { menu_items, menu_groups } from "@/lib/config/menu"
import type { MeResponse } from "@/features/auth/types"

type AppSidebarProps = React.ComponentProps<typeof Sidebar> & {
  me: MeResponse
}

export function AppSidebar({ me, ...props }: AppSidebarProps) {
  const { roleKey, isAdmin, canEvaluateMenu } = me

  const visible = menu_items.filter((item) => {
    if (item.admin_only) return isAdmin
    if (!item.allowed_roles.includes(roleKey)) return false
    if (item.requires_evaluator && !canEvaluateMenu) return false
    return true
  })

  const main_items = visible.filter((i) => !i.admin_only)
  const admin_items = visible.filter((i) => i.admin_only)

  const main_groups = (Object.entries(menu_groups) as Array<[any, any]>)
    .filter(([key]) => key !== "admin") // 管理者は別枠維持
    .map(([key, g]) => {
      const items = main_items
        .filter((i) => i.group === key)
        .map((i) => ({ title: i.label, url: i.path, icon: i.icon }))
      return { key, label: g.label, collapsible: g.collapsible, defaultOpen: g.defaultOpen, items }
    })
    .filter((g) => g.items.length > 0)

  const admin_docs_items = admin_items.map((i) => ({
    name: i.label,
    url: i.path,
    icon: i.icon,
  }))

  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild className="!p-1.5">
              <a href="/dashboard">
                <span className="text-base font-semibold">人事考課システム</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <NavMain
          groups={main_groups}
        />

        {admin_items.length > 0 && (
          <NavDocuments
            items={admin_docs_items}
          />
        )}

        <NavSecondary
          items={[
            { title: "設定", url: "/settings", icon: IconSettings },
            { title: "ヘルプ", url: "/help", icon: IconHelp },
          ]}
          className="mt-auto"
        />
      </SidebarContent>

      <SidebarFooter>
        <NavUser
          user={{
            name: me.fullName ?? me.employeeCode ?? "User",
            email: me.employeeCode ?? "-",
            avatar: "/avatars/default.jpg",
          }}
        />
      </SidebarFooter>
    </Sidebar>
  )
}

