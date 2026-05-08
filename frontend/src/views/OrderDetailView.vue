<template>
  <div class="flex gap-2">
    <button @click="openInvoice"
      class="flex items-center gap-2 border border-slate-200 rounded-lg px-4 py-2 text-sm">
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7
             -1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
      </svg>
      Preview
    </button>

    <button @click="downloadInvoice"
      class="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white
             rounded-lg px-4 py-2 text-sm">
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
      </svg>
      Download PDF
    </button>
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
