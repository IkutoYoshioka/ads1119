export type PasswordResetRequestIn = {
  employeeCode: string
  officeId: number
}

export type PasswordResetRequestOut = {
  status: 'accepted'
}
