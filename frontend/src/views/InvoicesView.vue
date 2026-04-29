<template>
  <div class="flex-1 flex flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white flex-shrink-0">
      <h1 class="text-lg font-bold text-slate-800">Invoices</h1>
      <button @click="showUpload = true"
        class="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white
               text-sm font-medium rounded-lg px-4 py-2 transition-colors">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
        </svg>
        Upload invoice
      </button>
    </div>

    <!-- Filters -->
    <div class="px-6 py-3 border-b border-slate-100 bg-white flex-shrink-0 flex items-center gap-4">
      <input v-model="search" type="text" placeholder="Search invoices…"
        class="w-full max-w-xs border border-slate-200 rounded-lg px-3 py-2 text-sm
               focus:outline-none focus:ring-2 focus:ring-brand-500" />
      <select v-model="statusFilter"
        class="border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white
               focus:outline-none focus:ring-2 focus:ring-brand-500">
        <option value="">All statuses</option>
        <option value="pending">Pending</option>
        <option value="matched">Matched</option>
        <option value="approved">Approved</option>
        <option value="disputed">Disputed</option>
      </select>
    </div>

    <!-- Table -->
    <div class="flex-1 overflow-y-auto">
      <table class="w-full table-fixed text-sm">
        <colgroup>
          <col class="w-36">
          <col class="w-40">
          <col class="w-32">
          <col class="w-28">
          <col class="w-28">
          <col class="w-28">
          <col class="w-28">
        </colgroup>
        <thead class="bg-slate-50 border-b border-slate-200 sticky top-0">
          <tr>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Invoice #</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Supplier</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
            <th class="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Amount</th>
            <th class="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">GBP</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Invoice date</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">PO</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="px-4 py-8 text-center text-slate-400 text-sm">Loading…</td>
          </tr>
          <tr v-else-if="!filteredInvoices.length">
            <td colspan="7" class="px-4 py-8 text-center text-slate-400 text-sm">No invoices found</td>
          </tr>
          <tr v-for="invoice in filteredInvoices" :key="invoice.id"
            class="border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors"
            @click="$router.push(`/invoices/${invoice.id}`)">
            <td class="px-4 py-3 font-mono text-xs text-slate-600">{{ invoice.invoice_number }}</td>
            <td class="px-4 py-3">
              <p class="font-medium text-slate-800 truncate">{{ invoice.supplier_name }}</p>
            </td>
            <td class="px-4 py-3">
              <span :class="statusClass(invoice.status)"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                {{ invoice.status }}
              </span>
            </td>
            <td class="px-4 py-3 text-right font-medium text-slate-800">
              {{ invoice.currency }} {{ Number(invoice.amount).toFixed(2) }}
            </td>
            <td class="px-4 py-3 text-right text-slate-600">
              £{{ Number(invoice.amount_gbp ?? invoice.amount).toFixed(2) }}
            </td>
            <td class="px-4 py-3 text-slate-400 text-xs">
              {{ invoice.invoice_date ? new Date(invoice.invoice_date).toLocaleDateString('en-GB') : '—' }}
            </td>
            <td class="px-4 py-3 font-mono text-xs text-slate-500">
              {{ invoice.purchase_order ?? '—' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/axios.js'

const loading      = ref(false)
const search       = ref('')
const statusFilter = ref('')
const showUpload   = ref(false)
const invoices     = ref([])

const filteredInvoices = computed(() => {
  let list = invoices.value
  if (statusFilter.value) list = list.filter(i => i.status === statusFilter.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(i =>
      i.invoice_number?.toLowerCase().includes(q) ||
      i.supplier_name?.toLowerCase().includes(q)
    )
  }
  return list
})

function statusClass(status) {
  return {
    pending:  'bg-amber-50 text-amber-700',
    matched:  'bg-blue-50 text-blue-700',
    approved: 'bg-green-50 text-green-700',
    disputed: 'bg-red-50 text-red-700',
  }[status] ?? 'bg-slate-100 text-slate-600'
}

onMounted(fetchInvoices)

async function fetchInvoices() {
  loading.value = true
  try {
    const { data } = await api.get('/invoices/')
    invoices.value = data.results ?? data
  } catch {
    invoices.value = []
  } finally {
    loading.value = false
  }
}
</script>
