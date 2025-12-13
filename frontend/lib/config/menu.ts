// lib/config/menu.ts

import type { RoleKey } from "@/features/auth/types"
import {
  IconDashboard,
  IconDatabase,
  IconFileDescription,
  IconListDetails,
  IconDatabaseEdit,
  IconUsers,
  IconChartHistogram,
  IconFolder,
  IconBuilding,
  IconLogs,
  IconFileExport
} from "@tabler/icons-react"
import type { Icon } from "@tabler/icons-react"

export type MenuGroupKey = "home" | "evaluation" | "personal" | "management" | "admin"

export const menu_groups: Record<MenuGroupKey, { label: string; collapsible: boolean; defaultOpen?: boolean }> = {
  home: { label: "ホーム", collapsible: false },
  evaluation: { label: "評価", collapsible: true, defaultOpen: true },
  personal: { label: "個人", collapsible: true, defaultOpen: true },
  management: { label: "管理", collapsible: true, defaultOpen: true },
  admin: { label: "管理者", collapsible: true, defaultOpen: false },
}

export type MenuItem = {
  label: string;
  path: string;
  icon: Icon;
  group: MenuGroupKey;
  allowed_roles: RoleKey[];
  admin_only?: boolean;
  requires_evaluator?: boolean;
};


export const menu_items: MenuItem[] = [
  // 共通
  {
    label: "ダッシュボード",
    path: "/dashboard",
    icon: IconDashboard,
    group: "home",
    allowed_roles: ["executive", "site_head", "employee"],
  },

  // 人事考課機能（personal_lists）：役員・施設長・その他考課者
  {
    label: "人事考課リスト",
    path: "/personal_lists",
    icon: IconListDetails,
    group: "evaluation",
    allowed_roles: ["executive", "site_head", "employee"],
    requires_evaluator: true,
  },

  // assignment：役員・施設長
  {
    label: "割当管理",
    path: "/assignment",
    icon: IconUsers,
    group: "management",
    allowed_roles: ["executive", "site_head"],
  },

  // feedbacks：役員・施設長・その他考課者
  {
    label: "フィードバック一覧",
    path: "/feedbacks",
    icon: IconFolder,
    group: "evaluation",
    allowed_roles: ["executive", "site_head", "employee"],
    requires_evaluator: true,
  },

  // my_feedbacks：全ロール
  {
    label: "自分へのフィードバック",
    path: "/my_feedbacks",
    icon: IconFileDescription,
    group: "personal",
    allowed_roles: ["site_head", "employee"],
  },

  // facility_results：施設長・役員
  {
    label: "施設別集計",
    path: "/facility_results",
    icon: IconBuilding,
    group: "management",
    allowed_roles: ["executive", "site_head"],
  },
  {
    label: "データ出力",
    path: "/exports",
    icon: IconFileExport,
    group: "management",
    allowed_roles: ["executive", "site_head"],
  },

  // === 管理者専用 ===
  {
    label: "設問・結果分析",
    path: "/admin/analysis",
    icon: IconChartHistogram,
    group: "admin",
    allowed_roles: ["executive", "site_head", "employee"],
    admin_only: true,
  },
  {
    label: "進行状況・集計",
    path: "/admin/browse",
    icon: IconDatabase,
    group: "admin",
    allowed_roles: ["executive", "site_head", "employee"],
    admin_only: true,
  },
  {
    label: "データ編集",
    path: "/admin/edit_db",
    icon: IconDatabaseEdit,
    group: "admin",
    allowed_roles: ["executive", "site_head", "employee"],
    admin_only: true,
  },
  {
    label: "履歴・ログ",
    path: "/admin/logs",
    icon: IconLogs,
    group: "admin",
    allowed_roles: ["executive", "site_head", "employee"],
    admin_only: true,
  }
];
