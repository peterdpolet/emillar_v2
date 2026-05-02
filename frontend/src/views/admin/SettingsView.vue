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
</script>