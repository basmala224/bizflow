import type { User } from './auth'

export type ProjectStatus = 'PLANNED' | 'IN_PROGRESS' | 'ON_HOLD' | 'COMPLETED' | 'CANCELLED'
export type ProjectPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
export type ProjectMemberRole = 'MANAGER' | 'DEVELOPER' | 'DESIGNER' | 'TESTER' | 'EMPLOYEE'

export interface Project {
  id: number
  name: string
  description: string
  status: ProjectStatus
  priority: ProjectPriority
  start_date: string | null
  end_date: string | null
  budget: string | null
  progress: number
  company: number
  manager: number | null
  manager_detail: User | null
  members_count: number
  created_at: string
  updated_at: string
}

export interface ProjectMember {
  id: number
  project: number
  user: number
  user_detail: User
  role: ProjectMemberRole
  joined_at: string
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export const PROJECT_STATUSES: ProjectStatus[] = ['PLANNED', 'IN_PROGRESS', 'ON_HOLD', 'COMPLETED', 'CANCELLED']
export const PROJECT_PRIORITIES: ProjectPriority[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
export const PROJECT_MEMBER_ROLES: ProjectMemberRole[] = ['MANAGER', 'DEVELOPER', 'DESIGNER', 'TESTER', 'EMPLOYEE']
