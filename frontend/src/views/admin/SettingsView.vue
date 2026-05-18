<template>
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-slate-200 bg-white flex-shrink-0">
      <h1 class="text-lg font-bold text-slate-800">Settings</h1>
      <p class="text-xs text-slate-400 mt-0.5">Platform configuration</p>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-6">
      <div class="max-w-2xl space-y-6">

        <!-- General -->
        <div class="bg-white rounded-xl border border-slate-200 p-6">
          <h2 class="text-sm font-semibold text-slate-700 mb-4">General</h2>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Company name</label>
              <input v-model="settings.company_name" type="text"
                class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm
                       focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Default currency</label>
              <select v-model="settings.default_currency"
                class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white
                       focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent">
                <option value="GBP">GBP — British Pound</option>
                <option value="USD">USD — US Dollar</option>
                <option value="EUR">EUR — Euro</option>
                <option value="CHF">CHF — Swiss Franc</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Invoice matching -->
        <div class="bg-white rounded-xl border border-slate-200 p-6">
          <h2 class="text-sm font-semibold text-slate-700 mb-1">Invoice Matching</h2>
          <p class="text-xs text-slate-400 mb-4">Three-way matching: PO + GRN + Invoice</p>
          <div class="space-y-4">
            <div class="flex items-center justify-between py-2 border-b border-slate-100">
              <div>
                <p class="text-sm font-medium text-slate-700">Require GRN before approval</p>
                <p class="text-xs text-slate-400 mt-0.5">Invoice must have a matched goods receipt note</p>
              </div>
              <button @click="settings.require_grn = !settings.require_grn"
                :class="settings.require_grn ? 'bg-brand-600' : 'bg-slate-200'"
                class="relative w-10 h-5 rounded-full transition-colors flex-shrink-0">
                <span :class="settings.require_grn ? 'translate-x-5' : 'translate-x-0'"
                  class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform" />
              </button>
            </div>
            <div class="flex items-center justify-between py-2">
              <div>
                <p class="text-sm font-medium text-slate-700">Auto-match on exact amount</p>
                <p class="text-xs text-slate-400 mt-0.5">Automatically match invoices where amounts match exactly</p>
              </div>
              <button @click="settings.auto_match = !settings.auto_match"
                :class="settings.auto_match ? 'bg-brand-600' : 'bg-slate-200'"
                class="relative w-10 h-5 rounded-full transition-colors flex-shrink-0">
                <span :class="settings.auto_match ? 'translate-x-5' : 'translate-x-0'"
                  class="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform" />
              </button>
            </div>
          </div>
        </div>

        <!-- ── Two-Factor Authentication ── -->
        <div class="bg-white rounded-xl border border-slate-200 p-6">
          <h2 class="text-sm font-semibold text-slate-700 mb-1">Two-Factor Authentication</h2>
          <p class="text-xs text-slate-400 mb-4">
            Secure your account with an authenticator app (Google Authenticator, Authy, etc.)
          </p>

          <!-- Already enabled -->
          <div v-if="auth.user?.totp_enabled">
            <div class="flex items-center gap-2 mb-4">
              <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
              <p class="text-sm text-emerald-700 font-medium">2FA is enabled on your account</p>
            </div>
            <div v-if="!showDisable">
              <button @click="showDisable = true"
                class="px-4 py-2 text-sm border border-red-200 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
                Disable 2FA
              </button>
            </div>
            <div v-else class="space-y-3">
              <p class="text-sm text-slate-600">Enter your current authenticator code to disable 2FA:</p>
              <input v-model="disableCode" type="text" inputmode="numeric" maxlength="6"
                placeholder="000000"
                class="w-40 border border-slate-200 rounded-lg px-3 py-2 text-sm text-center font-mono
                       focus:outline-none focus:ring-2 focus:ring-brand-500" />
              <div v-if="totpError" class="text-sm text-red-600">{{ totpError }}</div>
              <div class="flex gap-2">
                <button @click="disableTotp" :disabled="totpLoading || disableCode.length !== 6"
                  class="px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700
                         disabled:opacity-40 transition-colors">
                  {{ totpLoading ? 'Disabling…' : 'Confirm Disable' }}
                </button>
                <button @click="showDisable = false; disableCode = ''; totpError = ''"
                  class="px-4 py-2 text-sm border border-slate-200 rounded-lg hover:bg-slate-50">
                  Cancel
                </button>
              </div>
            </div>
          </div>

          <!-- Not enabled — setup flow -->
          <div v-else>
            <!-- Step 1: not started -->
            <div v-if="!qrCode && !setupConfirmed">
              <button @click="startSetup" :disabled="totpLoading"
                class="px-4 py-2 text-sm bg-brand-600 text-white rounded-lg hover:bg-brand-700
                       disabled:opacity-40 transition-colors">
                {{ totpLoading ? 'Loading…' : 'Enable 2FA' }}
              </button>
            </div>

            <!-- Step 2: show QR -->
            <div v-else-if="qrCode && !setupConfirmed" class="space-y-4">
              <div class="space-y-2">
                <p class="text-sm font-medium text-slate-700">1. Scan this QR code with your authenticator app</p>
                <div class="inline-block border border-slate-200 rounded-lg p-3 bg-white">
                  <img :src="`data:image/png;base64,${qrCode}`" alt="2FA QR Code" class="w-48 h-48" />
                </div>
              </div>
              <div class="space-y-2">
                <p class="text-sm font-medium text-slate-700">2. Or enter this key manually:</p>
                <code class="text-xs bg-slate-100 px-3 py-1.5 rounded font-mono tracking-wider">
                  {{ totpSecret }}
                </code>
              </div>
              <div class="space-y-2">
                <p class="text-sm font-medium text-slate-700">3. Enter the 6-digit code to confirm:</p>
                <input v-model="setupCode" type="text" inputmode="numeric" maxlength="6"
                  placeholder="000000"
                  class="w-40 border border-slate-200 rounded-lg px-3 py-2 text-sm text-center font-mono
                         focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </div>
              <div v-if="totpError" class="text-sm text-red-600">{{ totpError }}</div>
              <div class="flex gap-2">
                <button @click="confirmSetup" :disabled="totpLoading || setupCode.length !== 6"
                  class="px-4 py-2 text-sm bg-brand-600 text-white rounded-lg hover:bg-brand-700
                         disabled:opacity-40 transition-colors">
                  {{ totpLoading ? 'Confirming…' : 'Confirm & Enable' }}
                </button>
                <button @click="cancelSetup"
                  class="px-4 py-2 text-sm border border-slate-200 rounded-lg hover:bg-slate-50">
                  Cancel
                </button>
              </div>
            </div>

            <!-- Step 3: success -->
            <div v-else-if="setupConfirmed"
              class="bg-emerald-50 border border-emerald-200 rounded-lg px-4 py-3 text-sm text-emerald-700">
              ✓ 2FA has been enabled. You'll be asked for a code on your next login.
            </div>
          </div>
        </div>

        <!-- Save -->
        <div v-if="saved" class="bg-green-50 border border-green-200 rounded-lg px-4 py-3 text-sm text-green-700">
          Settings saved successfully.
        </div>
        <div class="flex justify-end">
          <button @click="save" :disabled="saving"
            class="px-4 py-2 text-sm font-medium text-white bg-brand-600 hover:bg-brand-700
                   rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
            {{ saving ? 'Saving…' : 'Save settings' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api/axios'
import { useAuthStore } from '@/stores/auth.js'

const auth = useAuthStore()

type Currency = 'GBP' | 'USD' | 'EUR' | 'CHF'
interface Settings {
  company_name:     string
  default_currency: Currency
  require_grn:      boolean
  auto_match:       boolean
}

const saving  = ref<boolean>(false)
const saved   = ref<boolean>(false)
const settings = ref<Settings>({
  company_name:     'Ewan Millar Ltd',
  default_currency: 'GBP',
  require_grn:      true,
  auto_match:       false,
})

onMounted(async () => {
  try {
    const { data } = await api.get<Settings>('/settings/')
    Object.assign(settings.value, data)
  } catch {
    // use defaults
  }
})

async function save(): Promise<void> {
  saving.value = true
  saved.value  = false
  try {
    await api.patch<Settings>('/settings/', settings.value)
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch {
    // TODO: show error
  } finally {
    saving.value = false
  }
}

// ── 2FA ──────────────────────────────────────────────────
const qrCode        = ref('')
const totpSecret    = ref('')
const setupCode     = ref('')
const disableCode   = ref('')
const totpLoading   = ref(false)
const totpError     = ref('')
const setupConfirmed = ref(false)
const showDisable   = ref(false)

async function startSetup() {
  totpLoading.value = true
  totpError.value   = ''
  try {
    const data = await auth.getTotpSetup()
    qrCode.value     = data.qr_code
    totpSecret.value = data.secret
  } catch {
    totpError.value = 'Failed to start 2FA setup. Please try again.'
  } finally {
    totpLoading.value = false
  }
}

async function confirmSetup() {
  totpLoading.value = true
  totpError.value   = ''
  try {
    await auth.confirmTotpSetup(setupCode.value)
    setupConfirmed.value = true
    qrCode.value         = ''
    totpSecret.value     = ''
    setupCode.value      = ''
  } catch {
    totpError.value = 'Invalid code. Please try again.'
  } finally {
    totpLoading.value = false
  }
}

function cancelSetup() {
  qrCode.value     = ''
  totpSecret.value = ''
  setupCode.value  = ''
  totpError.value  = ''
}

async function disableTotp() {
  totpLoading.value = true
  totpError.value   = ''
  try {
    await auth.disableTotp(disableCode.value)
    showDisable.value  = false
    disableCode.value  = ''
  } catch {
    totpError.value = 'Invalid code. Please try again.'
  } finally {
    totpLoading.value = false
  }
}
</script>
