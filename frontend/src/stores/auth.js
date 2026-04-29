/**
 * src/stores/auth.js
 * Handles login (including 2FA flow), registration, logout, and
 * current user state.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth.js'
import api from '@/api/axios.js'
import router from '@/router/index.js'

export const useAuthStore = defineStore('auth', () => {
  // ── State ────────────────────────────────────────────────
  const access        = ref(localStorage.getItem('access') || '')
  const refresh       = ref(localStorage.getItem('refresh') || '')
  const user          = ref(null)
  const requiresTotp  = ref(false)   // true during 2FA step
  const pendingUid    = ref('')      // uid returned by login when 2FA required
  const error         = ref('')
  const loading       = ref(false)

  // ── Computed ─────────────────────────────────────────────
  const isAuthenticated = computed(() => !!access.value)

  // ── Helpers ──────────────────────────────────────────────
  function setTokens(accessToken, refreshToken) {
    access.value  = accessToken
    refresh.value = refreshToken
    localStorage.setItem('access', accessToken)
    localStorage.setItem('refresh', refreshToken)
  }

  function clearTokens() {
    access.value  = ''
    refresh.value = ''
    user.value    = null
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
  }

  // ── Register ─────────────────────────────────────────────
  async function register(formData) {
    error.value   = ''
    loading.value = true
    try {
      await authApi.register(formData)
      return { success: true }
    } catch (e) {
      const data = e.response?.data
      if (data) {
        // Flatten DRF validation errors into a readable string
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
  async function login(email, password) {
    error.value   = ''
    loading.value = true
    try {
      const { data } = await authApi.login({ email, password })

      if (data.totp_required) {
        // 2FA required — store uid and show TOTP screen
        requiresTotp.value = true
        pendingUid.value   = data.uid
        return
      }

      // No 2FA — tokens returned directly
      setTokens(data.access, data.refresh)
      await fetchUser()
      router.push('/dashboard')
    } catch (e) {
      const status = e.response?.status
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
  async function verifyTotp(code) {
    error.value   = ''
    loading.value = true
    try {
      const { data } = await authApi.totpVerify({ code })
      requiresTotp.value = false
      pendingUid.value   = ''
      setTokens(data.access, data.refresh)
      await fetchUser()
      router.push('/dashboard')
    } catch (e) {
      if (e.response?.status === 400) {
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
  async function fetchUser() {
    try {
      const { data } = await api.get('/auth/me/')
      user.value = data
    } catch {
      // If this fails the user will be logged out by the interceptor
    }
  }

  // ── Logout ───────────────────────────────────────────────
  async function logout() {
    try {
      // Blacklist the refresh token
      await api.post('/auth/jwt/blacklist/', { refresh: refresh.value })
    } catch { /* ignore — clear tokens regardless */ }
    clearTokens()
    router.push('/login')
  }

  // ── 2FA management ───────────────────────────────────────
  async function getTotpSetup() {
    const { data } = await api.get('/auth/totp/setup/')
    return data  // { qr_code, secret }
  }

  async function confirmTotpSetup(code) {
    await api.post('/auth/totp/setup/', { code })
    if (user.value) user.value.totp_enabled = true
  }

  async function disableTotp(code) {
    await api.post('/auth/totp/disable/', { code })
    if (user.value) user.value.totp_enabled = false
  }

  // Initialise user on app load if token exists
  if (access.value) {
    fetchUser()
  }

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
