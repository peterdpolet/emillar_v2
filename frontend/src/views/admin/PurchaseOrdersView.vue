<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePurchaseOrders } from '@/composables/usePurchaseOrders'

const router = useRouter()
const {
  pos, total, page, pageSize,
  search, ordering, filters, loading, error, load
} = usePurchaseOrders()

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
onMounted(load)

const STATUS_COLOURS = {
  draft:     'bg-slate-100 text-slate-600',
  sent:      'bg-indigo-50 text-indigo-700',
  partial:   'bg-amber-50 text-amber-700',
  complete:  'bg-emerald-50 text-emerald-700',
  cancelled: 'bg-rose-50 text-rose-700',
}

function setStatusFilter(s) {
  filters.value = s ? { status: s } : {}
  page.value    = 1
}
const activeFilter = computed(() => filters.value.status || '')
</script>

<template>
  <div class="flex items-center justify-between mb-6">
    <div>
      <h1 class="text-xl font-bold text-slate-900">Purchase Orders</h1>
      <p class="text-sm text-slate-500 mt-0.5">{{ total }} total</p>
    </div>
    <button @click="router.push('/admin/purchase-orders/new')"
      class="px-4 py-2 bg-indigo-600 text-white text-sm
             font-semibold rounded-lg hover:bg-indigo-500 transition-colors">
      + New PO
    </button>
  </div>

  <!-- Status filter pills -->
  <div class="flex gap-2 mb-4 flex-wrap">
    <button v-for="f in ['','draft','sent','partial','complete','cancelled']"
      :key="f" @click="setStatusFilter(f)"
      :class="[
        'px-3 py-1.5 rounded-full text-xs font-semibold transition-colors capitalize',
        activeFilter === f
          ? 'bg-slate-900 text-white'
          : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
      ]">
      {{ f === '' ? 'All' : f }}
    </button>
  </div>

  <!-- Search + sort -->
  <div class="flex gap-3 mb-4">
    <input v-model="search" placeholder="Search supplier or reference..."
      class="flex-1 px-3 py-2 bg-white border border-slate-200
             rounded-lg text-sm focus:outline-none focus:ring-2
             focus:ring-indigo-500" />
    <select v-model="ordering"
      class="px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm">
      <option value="-created_at">Newest first</option>
      <option value="created_at">Oldest first</option>
      <option value="expected_date">Expected date</option>
      <option value="status">Status</option>
    </select>
  </div>

  <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
    <div v-if="loading" class="p-8 text-center text-sm text-slate-400">
      Loading...
    </div>
    <div v-else-if="error" class="p-8 text-center text-sm text-red-500">
      {{ error }}
    </div>

    <table v-else class="w-full">
      <thead>
        <tr class="border-b border-slate-200">
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">PO Ref</th>
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Supplier</th>
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Lines</th>
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Expected</th>
          <th class="px-4 py-3 text-right text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Value</th>
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Received</th>
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Status</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
        <tr v-for="po in pos" :key="po.id"
          @click="router.push(`/admin/purchase-orders/${po.id}`)"
          class="hover:bg-slate-50 cursor-pointer transition-colors">
          <td class="px-4 py-3 text-sm font-mono font-semibold text-slate-700">
            {{ po.reference || `PO-${String(po.id).padStart(4,'0')}` }}
          </td>
          <td class="px-4 py-3 text-sm font-medium text-slate-900">
            {{ po.supplier_name }}
          </td>
          <td class="px-4 py-3 text-sm text-slate-500 text-center">
            {{ po.line_count }}
          </td>
          <td class="px-4 py-3 text-sm text-slate-500">
            {{ po.expected_date
              ? new Date(po.expected_date).toLocaleDateString('en-GB')
              : '—' }}
          </td>
          <td class="px-4 py-3 text-sm font-semibold text-slate-900
                     tabular-nums text-right">
            £{{ Number(po.total).toFixed(2) }}
          </td>
          <td class="px-4 py-3">
            <div class="flex items-center gap-1.5">
              <div class="flex-1 bg-slate-100 rounded-full h-1.5">
                <div class="bg-indigo-500 rounded-full h-1.5 transition-all"
                  :style="`width:${po.total_expected
                    ? Math.min(100, (po.total_received/po.total_expected)*100)
                    : 0}%`">
                </div>
              </div>
              <span class="text-xs text-slate-500 tabular-nums w-14 text-right">
                {{ po.total_received }}/{{ po.total_expected }}
              </span>
            </div>
          </td>
          <td class="px-4 py-3">
            <span :class="[
              'inline-flex items-center px-2.5 py-1 rounded-full',
              'text-xs font-semibold capitalize',
              STATUS_COLOURS[po.status] || 'bg-slate-100 text-slate-500'
            ]">{{ po.status }}</span>
          </td>
        </tr>
        <tr v-if="pos.length === 0">
          <td colspan="7"
            class="px-4 py-8 text-center text-sm text-slate-400">
            No purchase orders found.
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!loading && !error"
      class="flex items-center justify-between px-4 py-3
             border-t border-slate-200">
      <p class="text-sm text-slate-500">
        Page {{ page }} of {{ totalPages || 1 }}
      </p>
      <div class="flex gap-2">
        <button :disabled="page === 1" @click="page--"
          class="px-3 py-1.5 text-sm bg-white border border-slate-200
                 rounded-lg disabled:opacity-40 hover:bg-slate-50">
          Previous
        </button>
        <button :disabled="page >= totalPages" @click="page++"
          class="px-3 py-1.5 text-sm bg-white border border-slate-200
                 rounded-lg disabled:opacity-40 hover:bg-slate-50">
          Next
        </button>
      </div>
    </div>
  </div>
</template>