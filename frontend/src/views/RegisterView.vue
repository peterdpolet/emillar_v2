<template>
  <div class="min-h-screen bg-slate-50 flex items-center justify-center p-4">
    <div class="w-full max-w-sm">

      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-brand-600 mb-4">
          <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007z"/>
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-slate-800">Request Access</h1>
        <p class="text-sm text-slate-400 mt-1">Access is by invitation. Staff will activate your account.</p>
      </div>

      <!-- Success state -->
      <div v-if="success" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 text-center">
        <div class="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
          <svg class="w-6 h-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
        <h2 class="font-semibold text-slate-800 mb-2">Request submitted</h2>
        <p class="text-sm text-slate-500 mb-6">
          Your account is awaiting approval. We'll let you know when it's ready.
        </p>
        <RouterLink to="/login" class="text-brand-600 hover:text-brand-700 text-sm font-medium">
          Back to sign in
        </RouterLink>
      </div>

      <!-- Registration form -->
      <div v-else class="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
        <form @submit.prevent="submit" class="space-y-4">

          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">Full name</label>
            <input v-model="form.name" type="text" required
              class="input" placeholder="Jane Smith" />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">Email</label>
            <input v-model="form.email" type="email" required autocomplete="email"
              class="input" placeholder="you@company.com" />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">Company</label>
            <input v-model="form.company" type="text"
              class="input" placeholder="Your company name" />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">Password</label>
            <input v-model="form.password" type="password" required autocomplete="new-password"
              class="input" placeholder="Min. 8 characters" />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">Confirm password</label>
            <input v-model="form.re_password" type="password" required
              class="input" placeholder="Repeat password" />
          </div>

          <div v-if="auth.error"
            class="bg-red-50 border border-red-200 rounded-lg px-3.5 py-2.5 text-sm text-red-600">
            {{ auth.error }}
          </div>

          <button type="submit" :disabled="auth.loading"
            class="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50
                   text-white font-medium rounded-lg py-2.5 text-sm transition-colors mt-2">
            {{ auth.loading ? 'Submitting…' : 'Request access' }}
          </button>

        </form>
      </div>

      <p class="text-center text-sm text-slate-400 mt-6">
        Already have an account?
        <RouterLink to="/login" class="text-brand-600 hover:text-brand-700 font-medium">Sign in</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const auth    = useAuthStore()
const success = ref(false)

const form = reactive({
  name: '', email: '', company: '',
  password: '', re_password: '',
})

async function submit() {
  const result = await auth.register(form)
  if (result.success) success.value = true
}
</script>

<style scoped>

@reference "../assets/main.css";

.input {
  @apply w-full border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm
         focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent;
}
</style>
