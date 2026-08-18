import { api } from './api'
import type { Paginated } from '../types/project'
import type { Comment, Task, TaskStatus } from '../types/task'

export interface TaskFilters {
  status?: string
  priority?: string
  project?: string | number
  assigned_to?: string | number
  search?: string
}

export interface TaskPayload {
  title: string
  description?: string
  status?: string
  priority?: string
  project: number
  assigned_to?: number | null
  due_date?: string | null
  estimated_hours?: string | null
  actual_hours?: string | null
}

export const taskService = {
  list: (filters: TaskFilters = {}) =>
    api.get<Paginated<Task>>('/tasks/', { params: filters }).then((res) => res.data),

  get: (id: number) => api.get<Task>(`/tasks/${id}/`).then((res) => res.data),

  create: (payload: TaskPayload) => api.post<Task>('/tasks/', payload).then((res) => res.data),

  update: (id: number, payload: Partial<TaskPayload>) =>
    api.patch<Task>(`/tasks/${id}/`, payload).then((res) => res.data),

  remove: (id: number) => api.delete(`/tasks/${id}/`),

  setStatus: (id: number, status: TaskStatus) =>
    api.patch<Task>(`/tasks/${id}/status/`, { status }).then((res) => res.data),

  listComments: (taskId: number) =>
    api.get<Comment[]>(`/tasks/${taskId}/comments/`).then((res) => res.data),

  addComment: (taskId: number, content: string) =>
    api.post<Comment>(`/tasks/${taskId}/comments/add/`, { content }).then((res) => res.data),
}
