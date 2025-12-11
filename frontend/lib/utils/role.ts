// lib/utils/role.ts

export type Role = "executive" | "director" | "evaluator" | "non_evaluator";

/**
 * バックエンドから返ってきた grade 文字列を UI 用の Role に落とし込む
 */
export function get_role_from_grade(grade: string): Role {
  switch (grade) {
    case "X01":
      return "executive";        // 役員
    case "G06":
      return "director";         // 施設長
    case "G05":
    case "G04":
      return "evaluator";        // その他考課者
    default:
      return "non_evaluator";    // 非考課者（その他すべて）
  }
}
