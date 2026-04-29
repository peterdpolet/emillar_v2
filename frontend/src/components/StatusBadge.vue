<template>
  <span :class="config.cls"
    class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium">
    {{ config.label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true }
})

const map = {
  draft:      { label: 'Draft',      cls: 'bg-slate-100 text-slate-600' },
  confirmed:  { label: 'Confirmed',  cls: 'bg-blue-100 text-blue-700' },
  processing: { label: 'Processing', cls: 'bg-amber-100 text-amber-700' },
  shipped:    { label: 'Shipped',    cls: 'bg-purple-100 text-purple-700' },
  delivered:  { label: 'Delivered',  cls: 'bg-emerald-100 text-emerald-700' },
  cancelled:  { label: 'Cancelled',  cls: 'bg-red-100 text-red-600' },
  active:     { label: 'Active',     cls: 'bg-emerald-100 text-emerald-700' },
  inactive:   { label: 'Inactive',   cls: 'bg-slate-100 text-slate-500' },
  archived:   { label: 'Archived',   cls: 'bg-red-50 text-red-400' },
}

const config = computed(() =>
  map[props.status] || { label: props.status, cls: 'bg-slate-100 text-slate-600' }
)
</script>
