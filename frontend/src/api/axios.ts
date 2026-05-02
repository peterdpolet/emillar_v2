/**
 * src/api/axios.ts
 */
import axios, { AxiosError } from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'

interface QueueEntry {
  resolve: (token: string) => void
  reject:  (error: unknown) => void
}

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

let isRefreshing = false
let failedQueue: QueueEntry[] = []

function processQueue(error: unknown, token: string | null = null): void {
  failedQueue.forEach(p => error ? p.reject(error) : p.resolve(token!))
  failedQueue = []
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  response => response,
  async (error: AxiosError) => {
    const original = error.config as RetryableRequestConfig
    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error)
    }
    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      }).then(token => {
        original.headers.Authorization = `Bearer ${token}`
        return api(original)
      })
    }
    original._retry = true
    isRefreshing    = true
    try {
      const refresh = localStorage.getItem('refresh')
      if (!refresh) throw new Error('No refresh token')
      const { data } = await axios.post<{ access: string; refresh?: string }>(
        '/api/auth/jwt/refresh/', { refresh }
      )
      const newAccess = data.access
      localStorage.setItem('access', newAccess)
      if (data.refresh) localStorage.setItem('refresh', data.refresh)
      processQueue(null, newAccess)
      original.headers.Authorization = `Bearer ${newAccess}`
      return api(original)
    } catch (err) {
      processQueue(err, null)
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      window.location.href = '/login'
      return Promise.reject(err)
    } finally {
      isRefreshing = false
    }
  }
)

export default api