/**
 * src/api/axios.js
 *
 * Shared Axios instance used for ALL authenticated API calls.
 * Attaches the Bearer token automatically and silently refreshes
 * on 401 responses using the queuing pattern to avoid multiple
 * simultaneous refresh calls.
 *
 * Rule: NEVER use raw axios in components or stores.
 *       Always import this `api` instance instead.
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

let isRefreshing = false
let failedQueue  = []

function processQueue(error, token = null) {
  failedQueue.forEach(p => error ? p.reject(error) : p.resolve(token))
  failedQueue = []
}

// ── Request interceptor — attach Bearer token ──────────────────────────────
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Response interceptor — silent refresh on 401 ──────────────────────────
api.interceptors.response.use(
  response => response,
  async error => {
    const original = error.config

    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      }).then(token => {
        original.headers.Authorization = `Bearer ${token}`
        return api(original)
      })
    }

    original._retry = true
    isRefreshing = true

    try {
      const refresh = localStorage.getItem('refresh')
      if (!refresh) throw new Error('No refresh token')

      const { data } = await axios.post('/api/auth/jwt/refresh/', { refresh })
      const newAccess = data.access

      localStorage.setItem('access', newAccess)
      if (data.refresh) localStorage.setItem('refresh', data.refresh)

      processQueue(null, newAccess)
      original.headers.Authorization = `Bearer ${newAccess}`
      return api(original)
    } catch (err) {
      processQueue(err, null)
      // Refresh failed — force logout
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
