<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api/axios'

const router = useRouter()
const route  = useRoute()
const grs    = ref([])
const loading = ref(false)
const error   = ref(null)

// Optional: filter by PO if ?po= query param present
const poFilter = computed(() => route.query.po || null)

onMounted(async () => {
  loading.value = true
  try {
    const params = { page_size: 50, ordering: '-received_date' }
    if (poFilter.value) params.purchase_order = poFilter.value
    const { data } = await api.get('/goods-receipts/', { params })
    grs.value = data.results
  } catch (e) {
    error.value = 'Could not load goods receipts.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="flex items-center justify-between mb-6">
    <div>
      <h1 class="text-xl font-bold text-slate-900">Goods Receipts</h1>
      <p v-if="poFilter" class="text-sm text-slate-500 mt-0.5">
        Filtered by PO #{{ poFilter }}
      </p>
    </div>
    <button @click="router.push('/admin/goods-receipts/new')"
      class="px-4 py-2 bg-indigo-600 text-white text-sm
             font-semibold rounded-lg hover:bg-indigo-500">
      + New receipt
    </button>
  </div>

  <div v-if="loading" class="text-sm text-slate-400 py-8 text-center">
    Loading...
  </div>
  <div v-else-if="error" class="text-sm text-red-500 py-8 text-center">
    {{ error }}
  </div>

  <div v-else class="bg-white rounded-xl border border-slate-200 overflow-hidden">
    <table class="w-full">
      <thead>
        <tr class="border-b border-slate-200">
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">GR Ref</th>
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Supplier</th>
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">PO Ref</th>
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Delivery ref</th>
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Date received</th>
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Received by</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
        <tr v-for="gr in grs" :key="gr.id"
          @click="router.push(`/admin/goods-receipts/${gr.id}`)"
          class="hover:bg-slate-50 cursor-pointer transition-colors">
          <td class="px-4 py-3 text-sm font-mono font-semibold text-slate-700">
            GR-{{ String(gr.id).padStart(4,'0') }}
          </td>
          <td class="px-4 py-3 text-sm font-medium text-slate-900">
            {{ gr.supplier_name }}
          </td>
          <td class="px-4 py-3 text-sm font-mono text-slate-500">
            {{ gr.po_reference || `PO-${String(gr.purchase_order).padStart(4,'0')}` }}
          </td>
          <td class="px-4 py-3 text-sm text-slate-500">
            {{ gr.delivery_ref || '—' }}
          </td>
          <td class="px-4 py-3 text-sm text-slate-500">
            {{ new Date(gr.received_date).toLocaleDateString('en-GB') }}
          </td>
          <td class="px-4 py-3 text-sm text-slate-500">
            {{ gr.received_by_email }}
          </td>
        </tr>
        <tr v-if="grs.length === 0">
          <td colspan="6"
            class="px-4 py-8 text-center text-sm text-slate-400">
            No goods receipts found.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>