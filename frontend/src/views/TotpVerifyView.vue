<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth.js'

const auth = useAuthStore()
const code = ref('')

async function submit() {
  await auth.verifyTotp(code.value)
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex items-center justify-center p-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-slate-800">Two-Factor Auth</h1>
        <p class="text-sm text-slate-400 mt-1">Enter the 6-digit code from your authenticator app</p>
      </div>
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
        <form @submit.prevent="submit" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">Authentication Code</label>
            <input v-model="code" type="text" inputmode="numeric" pattern="[0-9]{6}"
              maxlength="6" autocomplete="one-time-code" required autofocus placeholder="000000"
              class="w-full border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm text-center
                     tracking-widest text-lg font-mono focus:outline-none focus:ring-2
                     focus:ring-brand-500 focus:border-transparent" />
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
          <button type="button" @click="auth.logout()"
            class="w-full text-sm text-slate-400 hover:text-slate-600 transition-colors">
            ← Back to login
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
