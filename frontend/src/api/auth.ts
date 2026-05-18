/**
 * src/api/auth.ts
 *
 * Auth API calls use raw axios (not the shared api instance)
 * to avoid the circular import that would occur if the interceptor
 * tried to call refresh() which would re-trigger the interceptor.
 */
import axios from 'axios'
import type { AxiosResponse } from 'axios'

import type { RegisterData, LoginData, LoginResponse, TokenResponse } from '@/types/auth'

// ── Request types ─────────────────────────────────────────


interface TotpVerifyData {
  code: string
}

interface RefreshData {
  refresh: string
}



// ── Response types ────────────────────────────────────────


const authAxios = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export interface User {
  id:           number
  email:        string
  first_name:   string
  last_name:    string
  totp_enabled: boolean
  role:         'staff' | 'customer' | 'supplier'
}

export const authApi = {
  register:   (data: RegisterData): Promise<AxiosResponse>              => authAxios.post('/auth/users/', data),
  login:      (data: LoginData): Promise<AxiosResponse<LoginResponse>>  => authAxios.post('/auth/login/', data),
  totpVerify: (data: TotpVerifyData): Promise<AxiosResponse<TokenResponse>> => authAxios.post('/auth/totp/verify/', data),
  refresh:    (data: RefreshData): Promise<AxiosResponse<TokenResponse>> => authAxios.post('/auth/jwt/refresh/', data),
  logout:     (data: RefreshData): Promise<AxiosResponse>               => authAxios.post('/auth/jwt/blacklist/', data),
}