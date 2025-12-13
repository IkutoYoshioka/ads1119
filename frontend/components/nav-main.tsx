"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { ChevronDown, ChevronRight } from "lucide-react"

import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { cn } from "@/lib/utils" // もし未導入なら className 直書きでもOK

type NavItem = {
  title: string
  url: string
  icon?: React.ComponentType<React.SVGProps<SVGSVGElement>>
}

type Group = {
  key: string
  label: string
  collapsible: boolean
  defaultOpen?: boolean
  items: NavItem[]
}

function isActivePath(pathname: string, url: string) {
  return pathname === url || pathname.startsWith(url + "/")
}

export function NavMain({ groups }: { groups: Group[] }) {
  const pathname = usePathname()

  return (
    <>
      {groups.map((g) => {
        const hasActive = g.items.some((i) => isActivePath(pathname, i.url))
        const initialOpen = g.collapsible ? (g.defaultOpen ?? hasActive) : true
        const [open, setOpen] = React.useState<boolean>(initialOpen)

        const header = (
          <div className="flex items-center justify-between px-3 py-2">
            <SidebarGroupLabel className="text-xs font-semibold tracking-wide text-muted-foreground">
              {g.label}
            </SidebarGroupLabel>

            {g.collapsible && (
              <CollapsibleTrigger
                aria-label={`${g.label} を${open ? "閉じる" : "開く"}`}
                className={cn(
                  "rounded-md p-1 transition",
                  "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                )}
              >
                {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
              </CollapsibleTrigger>
            )}
          </div>
        )

        const menu = (
          <SidebarGroupContent className="px-1 pb-2">
            <SidebarMenu className="gap-1">
              {g.items.map((item) => {
                const active = isActivePath(pathname, item.url)

                return (
                  <SidebarMenuItem key={item.url}>
                    <SidebarMenuButton
                      asChild
                      isActive={active}
                      className={cn(
                        "relative pl-3", 
                        "data-[active=true]:bg-sidebar-accent data-[active=true]:text-sidebar-accent-foreground",
                        "data-[active=true]:font-medium",
                      )}
                    >
                      <Link href={item.url} className="flex items-center gap-2">
                        {/* ✅ Active の左バーで「今ここ」を強くする */}
                        <span
                          className={cn(
                            "absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r",
                            active ? "bg-primary" : "bg-transparent",
                          )}
                        />
                        {item.icon && <item.icon className="h-4 w-4" />}
                        <span className="truncate">{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        )

        // ✅ “セクションカード”で囲って階層感を出す
        return (
          <SidebarGroup key={g.key} className="px-2">
            <div
              className={cn(
                "rounded-lg border bg-sidebar/40",
                "border-sidebar-border/60",
                hasActive && "ring-1 ring-sidebar-accent/40", // アクティブセクションが分かる（控えめ）
              )}
            >
              {g.collapsible ? (
                <Collapsible open={open} onOpenChange={setOpen}>
                  {header}
                  <CollapsibleContent>{menu}</CollapsibleContent>
                </Collapsible>
              ) : (
                <>
                  {header}
                  {menu}
                </>
              )}
            </div>
          </SidebarGroup>
        )
      })}
    </>
  )
}
