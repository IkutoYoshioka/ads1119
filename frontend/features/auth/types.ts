// 型定義

export type LoginResponse = {
  employeeId?: number
  gradeCode?: string | null
  isAdmin?: boolean
  redirectPath?: string | null
  requiresMfa: boolean
  temporaryToken?: string | null
  mustChangePasswordAtNextLogin?: boolean | null
}

export type MfaVerifyLoginRequest = {
  temporaryToken: string
  totpCode: string
}

export type MfaVerifyLoginResponse = {
  employeeId: number
  gradeCode: string
  isAdmin: boolean
  redirectPath: string
  mfaEnabled?: boolean
  mustChangePasswordAtNextLogin: boolean
}

export type MfaSetupInitResponse = {
  otpauthUrl: string
  secret?: string | null
  issuer: string
  accountName: string
  alreadyEnabled: boolean
}

export type MfaSetupVerifyResponse = {
  mfaEnabled: boolean
}

export type RoleKey = "employee" | "site_head" | "executive"

export type MeResponse = {
  userId: number
  employeeId: number | null
  employeeCode: string | null

  firstName: string | null
  lastName: string | null
  fullName: string | null

  gradeCode: string | null
  gradeName: string | null
  gradeRankOrder: number | null

  officeId: number | null
  officeName: string | null

  siteId: number | null
  siteName: string | null

  isAdmin: boolean
  mustChangePassword: boolean
  mfaEnabled: boolean

  roleKey: RoleKey
  canEvaluateMenu: boolean
  defaultParticipates: boolean
  participatesInEvaluation: boolean
  evaluatedAsGradeCode: string | null
}

// 4) UI: AppSidebar に渡す形（UI都合の型）
export type SidebarUser = {
  name: string
  email: string
  avatar?: string
  grade: string
  isAdmin: boolean
}