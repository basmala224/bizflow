import { api } from './api'
import type { Paginated, Project, ProjectMember } from '../types/project'

export interface ProjectFilters {
  status?: string
  priority?: string
  search?: string
}

export interface ProjectPayload {
  name: string
  description?: string
  status?: string
  priority?: string
  start_date?: string | null
  end_date?: string | null
  budget?: string | null
  progress?: number
  manager?: number | null
}

export const projectService = {
  list: (filters: ProjectFilters = {}) =>
    api.get<Paginated<Project>>('/projects/', { params: filters }).then((res) => res.data),

  get: (id: number) => api.get<Project>(`/projects/${id}/`).then((res) => res.data),

  create: (payload: ProjectPayload) => api.post<Project>('/projects/', payload).then((res) => res.data),

  update: (id: number, payload: Partial<ProjectPayload>) =>
    api.patch<Project>(`/projects/${id}/`, payload).then((res) => res.data),

  remove: (id: number) => api.delete(`/projects/${id}/`),

  listMembers: (projectId: number) =>
    api.get<ProjectMember[]>(`/projects/${projectId}/members/`).then((res) => res.data),

  addMember: (projectId: number, userId: number, role: string) =>
    api.post<ProjectMember>(`/projects/${projectId}/members/add/`, { user: userId, role }).then((res) => res.data),

  removeMember: (projectId: number, userId: number) => api.delete(`/projects/${projectId}/members/${userId}/`),
}
