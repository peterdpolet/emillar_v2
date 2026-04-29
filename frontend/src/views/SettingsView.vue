<template>

    <div class="flex-1 overflow-y-auto p-6">
      <h1 class="text-xl font-bold text-slate-800 mb-6">Settings</h1>

      <div class="max-w-lg space-y-6">

        <!-- Account info -->
        <div class="bg-white rounded-xl border border-slate-200 p-6">
          <h2 class="font-semibold text-slate-800 mb-4">Account</h2>
          <div class="space-y-3 text-sm">
            <div class="flex justify-between">
              <span class="text-slate-500">Email</span>
              <span class="text-slate-800 font-medium">{{ auth.user?.email }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Name</span>
              <span class="text-slate-800 font-medium">{{ auth.user?.name || '—' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Role</span>
              <span class="text-slate-800 font-medium capitalize">{{ auth.user?.role }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Company</span>
              <span class="text-slate-800 font-medium">{{ auth.user?.company || '—' }}</span>
            </div>
          </div>
        </div>

        <!-- 2FA section -->
        <div class="bg-white rounded-xl border border-slate-200 p-6">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h2 class="font-semibold text-slate-800">Two-factor authentication</h2>
              <p class="text-sm text-slate-400 mt-0.5">
                Add an extra layer of security to your account
              </p>
            </div>
            <span :class="auth.user?.totp_enabled
              ? 'bg-emerald-100 text-emerald-700'
              : 'bg-slate-100 text-slate-500'"
              class="text-xs font-medium px-2 py-0.5 rounded-full">
              {{ auth.user?.totp_enabled ? 'Enabled' : 'Disabled' }}
            </span>
          </div>

          <!-- 2FA disabled — setup flow -->
          <div v-if="!auth.user?.totp_enabled">

            <!-- Step 1 — generate QR -->
            <div v-if="!qrCode">
              <p class="text-sm text-slate-500 mb-4">
                Use an authenticator app like Google Authenticator, Authy, or 1Password
                to scan a QR code and generate login codes.
              </p>
              <button @click="startSetup" :disabled="setupLoading"
                class="bg-brand-600 hover:bg-brand-700 disabled:opacity-50
                       text-white text-sm font-medium rounded-lg px-4 py-2 transition-colors">
                {{ setupLoading ? 'Generating…' : 'Set up 2FA' }}
              </button>
            </div>

            <!-- Step 2 — scan QR and confirm -->
            <div v-else class="space-y-4">
              <p class="text-sm text-slate-600">
                Scan this QR code with your authenticator app, then enter the
                6-digit code to confirm.
              </p>

              <div class="flex justify-center">
                <img :src="`data:image/png;base64,${qrCode}`"
                  alt="2FA QR Code"
                  class="w-48 h-48 border border-slate-200 rounded-lg p-2" />
              </div>

              <div class="bg-slate-50 rounded-lg px-4 py-3 text-center">
                <p class="text-xs text-slate-400 mb-1">Or enter this code manually:</p>
                <p class="font-mono text-sm font-medium text-slate-700 tracking-widest">
                  {{ manualSecret }}
                </p>
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1.5">
                  Confirm with a code from your app
                </label>
                <input v-model="confirmCode"
                  type="text" inputmode="numeric" maxlength="6"
                  class="w-full border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm
                         text-center tracking-widest font-mono
                         focus:outline-none focus:ring-2 focus:ring-brand-500"
                  placeholder="000000" />
              </div>

              <div v-if="setupError"
                class="bg-red-50 border border-red-200 rounded-lg px-3 py-2 text-sm text-red-600">
                {{ setupError }}
              </div>

              <div class="flex gap-3">
                <button @click="cancelSetup"
                  class="flex-1 text-sm text-slate-500 hover:text-slate-700 font-medium
                         border border-slate-200 rounded-lg py-2 transition-colors">
                  Cancel
                </button>
                <button @click="confirmSetup"
                  :disabled="confirmCode.length !== 6 || confirming"
                  class="flex-1 bg-brand-600 hover:bg-brand-700 disabled:opacity-50
                         text-white text-sm font-medium rounded-lg py-2 transition-colors">
                  {{ confirming ? 'Confirming…' : 'Confirm & enable' }}
                </button>
              </div>
            </div>
          </div>

          <!-- 2FA enabled — disable flow -->
          <div v-else>
            <p class="text-sm text-slate-500 mb-4">
              2FA is active. To disable it, enter a code from your authenticator app.
            </p>

            <div v-if="!showDisableForm">
              <button @click="showDisableForm = true"
                class="text-sm text-red-600 hover:text-red-700 font-medium border border-red-200
                       hover:border-red-300 rounded-lg px-4 py-2 transition-colors">
                Disable 2FA
              </button>
            </div>

            <div v-else class="space-y-3">
              <input v-model="disableCode"
                type="text" inputmode="numeric" maxlength="6"
                class="w-full border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm
                       text-center tracking-widest font-mono
                       focus:outline-none focus:ring-2 focus:ring-brand-500"
                placeholder="000000" />

              <div v-if="disableError"
                class="bg-red-50 border border-red-200 rounded-lg px-3 py-2 text-sm text-red-600">
                {{ disableError }}
              </div>

              <div class="flex gap-3">
                <button @click="showDisableForm = false; disableCode = ''; disableError = ''"
                  class="flex-1 text-sm text-slate-500 hover:text-slate-700 font-medium
                         border border-slate-200 rounded-lg py-2 transition-colors">
                  Cancel
                </button>
                <button @click="confirmDisable"
                  :disabled="disableCode.length !== 6 || disabling"
                  class="flex-1 bg-red-600 hover:bg-red-700 disabled:opacity-50
                         text-white text-sm font-medium rounded-lg py-2 transition-colors">
                  {{ disabling ? 'Disabling…' : 'Disable 2FA' }}
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

</template>

<script setup>
import { ref } from 'vue'

import { useAuthStore } from '@/stores/auth.js'

const auth = useAuthStore()

// ── Setup flow ────────────────────────────────────────────
const qrCode       = ref('')
const manualSecret = ref('')
const confirmCode  = ref('')
const setupError   = ref('')
const setupLoading = ref(false)
const confirming   = ref(false)

async function startSetup() {
  setupError.value   = ''
  setupLoading.value = true
  try {
    const data = await auth.getTotpSetup()
    qrCode.value       = data.qr_code
    manualSecret.value = data.secret
  } catch {
    setupError.value = 'Could not generate QR code. Please try again.'
  } finally {
    setupLoading.value = false
  }
}

async function confirmSetup() {
  setupError.value = ''
  confirming.value = true
  try {
    await auth.confirmTotpSetup(confirmCode.value)
    qrCode.value       = ''
    manualSecret.value = ''
    confirmCode.value  = ''
  } catch {
    setupError.value = 'Invalid code. Please try again.'
  } finally {
    confirming.value = false
  }
}

function cancelSetup() {
  qrCode.value       = ''
  manualSecret.value = ''
  confirmCode.value  = ''
  setupError.value   = ''
}

// ── Disable flow ──────────────────────────────────────────
const showDisableForm = ref(false)
const disableCode     = ref('')
const disableError    = ref('')
const disabling       = ref(false)

async function confirmDisable() {
  disableError.value = ''
  disabling.value    = true
  try {
    await auth.disableTotp(disableCode.value)
    showDisableForm.value = false
    disableCode.value     = ''
  } catch {
    disableError.value = 'Invalid code. Please try again.'
  } finally {
    disabling.value = false
  }
}
</script>
