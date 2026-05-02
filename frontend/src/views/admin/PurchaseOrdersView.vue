<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePurchaseOrders } from '@/composables/usePurchaseOrders'
import type { POStatus } from '@/types/purchaseOrders'

const router = useRouter()
const {
  pos, total, page, pageSize,
  search, ordering, filters, loading, error, load
} = usePurchaseOrders()

const totalPages = computed<number>(() => Math.ceil(total.value / pageSize.value))
onMounted(load)

const STATUS_COLOURS: Record<POStatus, string> = {
  draft:     'bg-slate-100 text-slate-600',
  sent:      'bg-indigo-50 text-indigo-700',
  partial:   'bg-amber-50 text-amber-700',
  complete:  'bg-emerald-50 text-emerald-700',
  cancelled: 'bg-rose-50 text-rose-700',
}

function setStatusFilter(s: POStatus | ''): void {
  filters.value = s ? { status: s } : {}
  page.value    = 1
}

const activeFilter = computed<POStatus | ''>(() =>
  (filters.value.status as POStatus) || ''
)
</script>

<template>
  <!-- (template unchanged — no TypeScript needed in templates) -->
</template>