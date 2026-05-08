<template>

    <div v-if="loading" class="flex-1 flex items-center justify-center text-slate-400">
      Loading…
    </div>

    <div v-else-if="order" class="flex-1 flex flex-col overflow-hidden">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white flex-shrink-0">
        <div class="flex items-center gap-3">
          <button @click="$router.back()" class="text-slate-400 hover:text-slate-600">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
            </svg>
          </button>
          <div>
            <h1 class="text-lg font-bold text-slate-800">Order #{{ order.id }}</h1>
            <p class="text-xs text-slate-400">{{ order.customer_name }} · {{ order.customer_email }}</p>
          </div>
        </div>
        <StatusBadge :status="order.status" />
      </div>

      <div class="flex-1 overflow-y-auto p-6 space-y-6">

        <!-- Lines table -->
        <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div class="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <h2 class="font-semibold text-slate-800">Order lines</h2>
            <p class="text-sm font-bold text-slate-800">Total: £{{ Number(order.total).toFixed(2) }}</p>
          </div>

          <table class="w-full table-fixed text-sm">
            <colgroup>
              <col class="w-28"><col><col class="w-20">
              <col class="w-24"><col class="w-24">
            </colgroup>
            <thead class="bg-slate-50 border-b border-slate-100">
              <tr>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-slate-500">SKU</th>
                <th class="text-left px-4 py-2.5 text-xs font-semibold text-slate-500">Item</th>
                <th class="text-right px-4 py-2.5 text-xs font-semibold text-slate-500">Qty</th>
                <th class="text-right px-4 py-2.5 text-xs font-semibold text-slate-500">Price</th>
                <th class="text-right px-4 py-2.5 text-xs font-semibold text-slate-500">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="line in order.lines" :key="line.id"
                class="border-b border-slate-100 last:border-0">
                <td class="px-4 py-3 font-mono text-xs text-slate-500">{{ line.item.sku }}</td>
                <td class="px-4 py-3 text-slate-800">{{ line.item.name }}</td>
                <td class="px-4 py-3 text-right text-slate-600">{{ line.quantity }}</td>
                <td class="px-4 py-3 text-right text-slate-600">£{{ Number(line.price).toFixed(2) }}</td>
                <td class="px-4 py-3 text-right font-medium text-slate-800">
                  £{{ Number(line.line_total).toFixed(2) }}
                </td>
              </tr>
              <tr v-if="!order.lines.length">
                <td colspan="5" class="px-4 py-6 text-center text-slate-400">No lines on this order</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Status history -->
        <div class="bg-white rounded-xl border border-slate-200 p-5">
          <h2 class="font-semibold text-slate-800 mb-4">Status history</h2>
          <div class="space-y-3">
            <div v-for="log in order.status_log" :key="log.id"
              class="flex items-start gap-3 text-sm">
              <div class="w-1.5 h-1.5 rounded-full bg-brand-400 mt-2 flex-shrink-0"></div>
              <div>
                <span class="text-slate-800 font-medium">{{ log.new_status }}</span>
                <span v-if="log.old_status" class="text-slate-400"> (from {{ log.old_status }})</span>
                <span class="text-slate-400 text-xs ml-2">
                  {{ new Date(log.created_at).toLocaleString('en-GB') }}
                </span>
                <span v-if="log.changed_by_email" class="text-slate-400 text-xs ml-2">
                  by {{ log.changed_by_email }}
                </span>
                <p v-if="log.note" class="text-slate-500 text-xs mt-0.5">{{ log.note }}</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'


import StatusBadge from '@/components/StatusBadge.vue'
import { useOrdersStore } from '@/stores/orders.js'


const props = defineProps(['order'])
const route  = useRoute()
const orders = useOrdersStore()
const order  = ref(null)
const loading = ref(true)

function openInvoice() {
  window.open(`/api/documents/invoices/${props.order.id}/pdf/`, '_blank')
}

function downloadInvoice() {
  window.open(`/api/documents/invoices/${props.order.id}/pdf/?download=1`, '_blank')
}
</script>

onMounted(async () => {
  order.value = await orders.fetchOrder(route.params.id)
  loading.value = false
})
</script>
