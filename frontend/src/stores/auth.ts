/**
 * src/stores/auth.ts
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import api from '@/api/axios'
import router from '@/router/index'
import type { User, RegisterData } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // ── State ────────────────────────────────────────────────
  const access       = ref<string>(localStorage.getItem('access') || '')
  const refresh      = ref<string>(localStorage.getItem('refresh') || '')
  const user         = ref<User | null>(null)
  const requiresTotp = ref<boolean>(false)
  const pendingUid   = ref<string>('')
  const error        = ref<string>('')
  const loading      = ref<boolean>(false)

  // ── Computed ─────────────────────────────────────────────
  const isAuthenticated = computed(() => !!access.value)

  // ── Helpers ──────────────────────────────────────────────
  function setTokens(accessToken: string, refreshToken: string): void {
    access.value  = accessToken
    refresh.value = refreshToken
    localStorage.setItem('access', accessToken)
    localStorage.setItem('refresh', refreshToken)
  }

  function clearTokens(): void {
    access.value  = ''
    refresh.value = ''
    user.value    = null
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
  }

  // ── Register ─────────────────────────────────────────────
  async function register(formData: RegisterData): Promise<{ success: boolean }> {
    error.value   = ''
    loading.value = true
    try {
      await authApi.register(formData)
      return { success: true }
    } catch (e: unknown) {
      const data = (e as any).response?.data
      if (data) {
        error.value = Object.values(data).flat().join(' ')
      } else {
        error.value = 'Registration failed. Please try again.'
      }
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  // ── Login — step 1 ───────────────────────────────────────
  async function login(email: string, password: string): Promise<void> {
    error.value   = ''
    loading.value = true
    try {
      const { data } = await authApi.login({ email, password })

      if (data.totp_required) {
        requiresTotp.value = true
        pendingUid.value   = data.uid
        return
      }

      setTokens(data.access, data.refresh)
      await fetchUser()
      router.push('/dashboard')
    } catch (e: unknown) {
      const status = (e as any).response?.status
      if (status === 401) {
        error.value = 'Invalid email or password.'
      } else if (status === 403) {
        error.value = 'Your account is awaiting activation. Please contact staff.'
      } else {
        error.value = 'Login failed. Please try again.'
      }
    } finally {
      loading.value = false
    }
  }

  // ── Login — step 2 (TOTP) ────────────────────────────────
  async function verifyTotp(code: string): Promise<void> {
    error.value   = ''
    loading.value = true
    try {
      const { data } = await authApi.totpVerify({ code })
      requiresTotp.value = false
      pendingUid.value   = ''
      setTokens(data.access, data.refresh)
      await fetchUser()
      router.push('/dashboard')
    } catch (e: unknown) {
      if ((e as any).response?.status === 400) {
        error.value = 'Invalid or expired code. Please try again.'
      } else {
        error.value = 'Verification failed. Please log in again.'
        requiresTotp.value = false
        router.push('/login')
      }
    } finally {
      loading.value = false
    }
  }

  // ── Fetch current user ───────────────────────────────────
  async function fetchUser(): Promise<void> {
    try {
      const { data } = await api.get<User>('/auth/me/')
      user.value = data
    } catch {
      // Interceptor handles logout
    }
  }

  // ── Logout ───────────────────────────────────────────────
  async function logout(): Promise<void> {
    try {
      await api.post('/auth/jwt/blacklist/', { refresh: refresh.value })
    } catch { /* ignore */ }
    clearTokens()
    router.push('/login')
  }

  // ── 2FA management ───────────────────────────────────────
  async function getTotpSetup(): Promise<{ qr_code: string; secret: string }> {
    const { data } = await api.get('/auth/totp/setup/')
    return data
  }

  async function confirmTotpSetup(code: string): Promise<void> {
    await api.post('/auth/totp/setup/', { code })
    if (user.value) user.value.totp_enabled = true
  }

  async function disableTotp(code: string): Promise<void> {
    await api.post('/auth/totp/disable/', { code })
    if (user.value) user.value.totp_enabled = false
  }

  if (access.value) fetchUser()

  return {
    access, refresh, user,
    requiresTotp, pendingUid,
    error, loading,
    isAuthenticated,
    register, login, verifyTotp,
    fetchUser, logout,
    getTotpSetup, confirmTotpSetup, disableTotp,
  }
})