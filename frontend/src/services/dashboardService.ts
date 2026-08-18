import { api } from './api'
import type { DashboardData } from '../types/dashboard'

export const dashboardService = {
  get: () => api.get<DashboardData>('/dashboard/').then((res) => res.data),
}
