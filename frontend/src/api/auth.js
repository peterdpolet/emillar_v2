/**
 * src/api/auth.js
 *
 * Auth API calls use raw axios (not the shared api instance)
 * to avoid the circular import that would occur if the interceptor
 * tried to call refresh() which would re-trigger the interceptor.
 */
import axios from 'axios'

const authAxios = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export const authApi = {
  register:    (data) => authAxios.post('/auth/users/', data),
  login:  (data) => authAxios.post('/auth/jwt/create/', data),
  totpVerify:  (data) => authAxios.post('/auth/totp/verify/', data),
  refresh:     (data) => authAxios.post('/auth/jwt/refresh/', data),
  logout: (data) => authAxios.post('/auth/jwt/blacklist/', data),
}
