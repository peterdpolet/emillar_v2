<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-semibold text-gray-800">Purchase Orders</h1>
      <RouterLink
        to="/purchase-orders/new"
        class="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors"
      >
        ＋ New Purchase Order
      </RouterLink>
    </div>

    <!-- Filters -->
    <div class="flex gap-2 mb-4 flex-wrap">
      <button
        v-for="s in statuses" :key="s.value"
        @click="setStatus(s.value)"
        :class="[
          'px-3 py-1.5 rounded-full text-xs font-medium transition-colors',
          activeStatus === s.value
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        ]"
      >{{ s.label }}</button>
    </div>

    <div v-if="store.loading" class="text-center py-16 text-gray-400">Loading…</div>
    <div v-else-if="store.error" class="bg-red-50 text-red-700 p-4 rounded-lg">{{ store.error }}</div>
    <div v-else-if="!store.pos.length" class="text-center py-16 text-gray-400">No purchase orders found.</div>

    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Reference</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Supplier</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Status</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Expected</th>
            <th class="text-right px-4 py-3 font-medium text-gray-600">Total</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="po in store.pos" :key="po.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-4 py-3 font-mono text-indigo-700">{{ po.reference || '—' }}</td>
            <td class="px-4 py-3 text-gray-800">{{ po.supplier_name }}</td>
            <td class="px-4 py-3">
              <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', statusColour(po.status)]">
                {{ po.status }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500">{{ po.expected_date ?? '—' }}</td>
            <td class="px-4 py-3 text-right font-medium text-gray-800">
              {{ po.currency }} {{ Number(po.total).toFixed(2) }}
            </td>
            <td class="px-4 py-3 text-right">
              <RouterLink :to="`/purchase-orders/${po.id}`" class="text-indigo-600 hover:text-indigo-800 text-xs font-medium">
                View →
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-4">
      <button
        v-for="p in totalPages" :key="p"
        @click="store.page = p; store.fetchList({ status: activeStatus || undefined })"
        :class="['px-3 py-1 rounded text-sm', store.page === p ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']"
      >{{ p }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { usePurchaseOrderStore } from '@/features/purchasing/stores/usePurchaseOrderStore.js'

const store = usePurchaseOrderStore()
const activeStatus = ref('')

const statuses = [
  { value: '',          label: 'All' },
  { value: 'draft',     label: 'Draft' },
  { value: 'sent',      label: 'Sent' },
  { value: 'partial',   label: 'Partial' },
  { value: 'complete',  label: 'Complete' },
  { value: 'cancelled', label: 'Cancelled' },
]

const totalPages = computed(() => Math.ceil(store.total / store.pageSize))

function setStatus(s) {
  activeStatus.value = s
  store.page = 1
  store.fetchList({ status: s || undefined })
}

function statusColour(s) {
  return {
    draft:     'bg-slate-100 text-slate-600',
    sent:      'bg-blue-50 text-blue-700',
    partial:   'bg-amber-50 text-amber-700',
    complete:  'bg-emerald-50 text-emerald-700',
    cancelled: 'bg-red-50 text-red-700',
  }[s] ?? 'bg-gray-100 text-gray-600'
}

onMounted(() => store.fetchList())
</script>