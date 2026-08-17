export type UserRole = 'SUPER_ADMIN' | 'ADMIN' | 'MANAGER' | 'EMPLOYEE'

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  phone: string
  photo: string | null
  position: string
  department: string
  role: UserRole
  company: number | null
  date_joined: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginResponse extends AuthTokens {
  user: User
}

export interface RegisterPayload {
  company_name: string
  email: string
  password: string
  first_name?: string
  last_name?: string
}
