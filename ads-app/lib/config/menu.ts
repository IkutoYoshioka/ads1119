// lib/config/menu.ts

import type { Role } from "@/lib/utils/role";

export type MenuItem = {
  label: string;
  path: string;
  allowed_roles: Role[];
  admin_only?: boolean;
};

export const menu_items: MenuItem[] = [
  // 共通
  {
    label: "ダッシュボード",
    path: "/dashboard",
    allowed_roles: ["executive", "director", "evaluator", "non_evaluator"],
  },
  {
    label: "アカウント",
    path: "/account",
    allowed_roles: ["executive", "director", "evaluator", "non_evaluator"],
  },

  // 人事考課機能（personal_lists）：役員・施設長・その他考課者
  {
    label: "人事考課リスト",
    path: "/personal_lists",
    allowed_roles: ["executive", "director", "evaluator"],
  },

  // assignment：施設長のみ
  {
    label: "割当管理",
    path: "/assignment",
    allowed_roles: ["director"],
  },

  // feedbacks：役員・施設長・その他考課者
  {
    label: "フィードバック一覧",
    path: "/feedbacks",
    allowed_roles: ["executive", "director", "evaluator"],
  },

  // my_feedbacks：全ロール
  {
    label: "自分へのフィードバック",
    path: "/my_feedbacks",
    allowed_roles: ["director", "evaluator", "non_evaluator"],
  },

  // facility_results：施設長・役員
  {
    label: "施設別集計",
    path: "/facility_results",
    allowed_roles: ["executive", "director"],
  },

  // === 管理者専用 ===
  {
    label: "設問・結果分析",
    path: "/admin/analysis",
    allowed_roles: ["executive", "director", "evaluator", "non_evaluator"],
    admin_only: true,
  },
  {
    label: "進行状況・集計",
    path: "/admin/browse",
    allowed_roles: ["executive", "director", "evaluator", "non_evaluator"],
    admin_only: true,
  },
  {
    label: "データ編集",
    path: "/admin/edit_db",
    allowed_roles: ["executive", "director", "evaluator", "non_evaluator"],
    admin_only: true,
  },
];
