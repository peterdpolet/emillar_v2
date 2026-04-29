<template>
  <div class="min-h-screen bg-slate-50 flex items-center justify-center p-4">
    <div class="w-full max-w-sm">

      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-brand-600 mb-4">
          <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/>
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-slate-800">Two-factor authentication</h1>
        <p class="text-sm text-slate-400 mt-1">
          Enter the 6-digit code from your authenticator app
        </p>
      </div>

      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
        <form @submit.prevent="submit" class="space-y-5">

          <!-- 6-digit code input -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">Verification code</label>
            <input
              v-model="code"
              type="text"
              inputmode="numeric"
              pattern="[0-9]{6}"
              maxlength="6"
              required
              autofocus
              class="w-full border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm
                     text-center tracking-widest text-lg font-mono
                     focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              placeholder="000000"
            />
          </div>

          <div v-if="auth.error"
            class="bg-red-50 border border-red-200 rounded-lg px-3.5 py-2.5 text-sm text-red-600">
            {{ auth.error }}
          </div>

          <button type="submit" :disabled="auth.loading || code.length !== 6"
            class="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50
                   text-white font-medium rounded-lg py-2.5 text-sm transition-colors">
            {{ auth.loading ? 'Verifying…' : 'Verify' }}
          </button>

          <button type="button" @click="goBack"
            class="w-full text-slate-500 hover:text-slate-700 text-sm transition-colors">
            ← Back to sign in
          </button>

        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import router from '@/router/index.js'

const auth = useAuthStore()
const code = ref('')

async function submit() {
  await auth.verifyTotp(code.value)
}

function goBack() {
  auth.requiresTotp = false
  router.push('/login')
}
</script>
