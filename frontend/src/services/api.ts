import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

export const api = axios.create({ baseURL })

api.interceptors.request.use((requestConfig) => {
  const accessToken = localStorage.getItem('access_token')
  if (accessToken) {
    requestConfig.headers.Authorization = `Bearer ${accessToken}`
  }
  return requestConfig
})

let refreshPromise: Promise<string> | null = null

async function refreshAccessToken(): Promise<string> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) throw new Error('No refresh token available')

  const response = await axios.post(`${baseURL}/auth/refresh/`, { refresh: refreshToken })
  const { access, refresh } = response.data as { access: string; refresh?: string }

  localStorage.setItem('access_token', access)
  if (refresh) localStorage.setItem('refresh_token', refresh)
  return access
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const isAuthEndpoint = originalRequest?.url?.includes('/auth/login') || originalRequest?.url?.includes('/auth/refresh')

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true
      try {
        refreshPromise ??= refreshAccessToken().finally(() => {
          refreshPromise = null
        })
        const access = await refreshPromise
        originalRequest.headers.Authorization = `Bearer ${access}`
        return api(originalRequest)
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  },
)
