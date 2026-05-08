<template>
  Create Order View
  <div class="flex-1 flex flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white flex-shrink-0">
      <div class="flex items-center gap-3">
        <button @click="router.back()"
          class="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <h1 class="text-lg font-bold text-slate-800">Create Order</h1>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-6">
      <div class="max-w-2xl space-y-6">

        <!-- Customer -->
        <div class="bg-white rounded-xl border border-slate-200 p-6">
          <h2 class="text-sm font-semibold text-slate-700 mb-4">Customer</h2>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Customer</label>
              <select v-model="form.customer"
                class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white
                       focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent">
                <option value="">Select a customer…</option>
                <option v-for="c in customers" :key="c.id" :value="c.id">
                  {{ c.name }} — {{ c.email }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Notes</label>
              <textarea v-model="form.notes" rows="3"
                placeholder="Order notes (optional)"
                class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm
                       focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent resize-none" />
            </div>
          </div>
        </div>

        <!-- Error -->
        <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-600">
          {{ error }}
        </div>

        <!-- Actions -->
        <div class="flex items-center justify-end gap-3">
          <button @click="router.back()"
            class="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200
                   rounded-lg hover:bg-slate-50 transition-colors">
            Cancel
          </button>
          <button @click="submit" :disabled="loading || !form.customer"
            class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white
                   bg-brand-600 hover:bg-brand-700 rounded-lg transition-colors
                   disabled:opacity-50 disabled:cursor-not-allowed">
            <span v-if="loading">Creating…</span>
            <span v-else>Create Order</span>
          </button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useOrdersStore } from '@/stores/orders.js'
import api from '@/api/axios.js'

const router  = useRouter()
const orders  = useOrdersStore()
const loading = ref(false)
const error   = ref('')

const customers = ref([])

const form = ref({
  customer: '',
  notes: '',
})

onMounted(async () => {
  try {
    const { data } = await api.get('/auth/users/')
    customers.value = data.results ?? data
  } catch {
    // customers will be empty — handle gracefully
  }
})

async function submit() {
  if (!form.value.customer) return
  loading.value = true
  error.value   = ''
  try {
    const order = await orders.createOrder({
      customer: form.value.customer,
      notes:    form.value.notes,
    })
    router.push(`/orders/${order.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail ?? 'Failed to create order. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
