import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api',
})

api.interceptors.request.use((requestConfig) => {
  const accessToken = localStorage.getItem('access_token')
  if (accessToken) {
    requestConfig.headers.Authorization = `Bearer ${accessToken}`
  }
  return requestConfig
})
