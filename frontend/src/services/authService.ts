import { api } from './api'
import type { LoginResponse, RegisterPayload, User } from '../types/auth'

export const authService = {
  login: (email: string, password: string) =>
    api.post<LoginResponse>('/auth/login/', { email, password }).then((res) => res.data),

  register: (payload: RegisterPayload) =>
    api.post<LoginResponse>('/auth/register/', payload).then((res) => res.data),

  logout: (refresh: string) => api.post('/auth/logout/', { refresh }),

  me: () => api.get<User>('/auth/me/').then((res) => res.data),

  updateProfile: (payload: Partial<User>) => api.patch<User>('/auth/me/', payload).then((res) => res.data),

  changePassword: (old_password: string, new_password: string) =>
    api.post('/auth/change-password/', { old_password, new_password }),

  forgotPassword: (email: string) => api.post<{ detail: string }>('/auth/forgot-password/', { email }).then((res) => res.data),

  resetPassword: (uid: string, token: string, new_password: string) =>
    api.post<{ detail: string }>('/auth/reset-password/', { uid, token, new_password }).then((res) => res.data),
}
