import { api } from './api'
import type { User } from '../types/auth'
import type { Paginated } from '../types/project'

export const userService = {
  list: () => api.get<Paginated<User>>('/users/').then((res) => res.data),
}
