import type { User } from './auth'

export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'REVIEW' | 'DONE' | 'BLOCKED'
export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export interface Task {
  id: number
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority
  due_date: string | null
  estimated_hours: string | null
  actual_hours: string | null
  company: number
  project: number
  assigned_to: number | null
  assigned_to_detail: User | null
  comments_count: number
  created_at: string
  updated_at: string
}

export interface Comment {
  id: number
  task: number
  author: number
  author_detail: User
  content: string
  created_at: string
}

export const TASK_STATUSES: TaskStatus[] = ['TODO', 'IN_PROGRESS', 'REVIEW', 'DONE', 'BLOCKED']
export const TASK_PRIORITIES: TaskPriority[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  TODO: 'To Do',
  IN_PROGRESS: 'In Progress',
  REVIEW: 'Review',
  DONE: 'Done',
  BLOCKED: 'Blocked',
}
