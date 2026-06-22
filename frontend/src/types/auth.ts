export type UserRole = 'viewer' | 'user' | 'manager' | 'admin'

export interface AuthUser {
  account_id: string
  member_id: string
  username: string
  full_name: string
  email: string
  role: UserRole
  department: { id: string; code: string; name: string } | null
  avatar_url: string | null
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: AuthUser
}
