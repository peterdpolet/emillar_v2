<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api/axios'

// ── Types ─────────────────────────────────────────────────
type Currency = 'GBP' | 'USD' | 'EUR' | 'CHF'

interface Settings {
  company_name:     string
  default_currency: Currency
  require_grn:      boolean
  auto_match:       boolean
}

// ── State ─────────────────────────────────────────────────
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

<template>
  <div class="flex-1 flex flex-col overflow-hidden">
    <div class="px-6 py-4 border-b border-slate-200 bg-white flex-shrink-0">
      <h1 class="text-lg font-bold text-slate-800">Settings</h1>
      <p class="text-xs text-slate-400 mt-0.5">Platform configuration</p>
    </div>
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
                <option value="EUR">