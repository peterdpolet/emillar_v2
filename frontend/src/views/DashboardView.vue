<template>

    <div class="flex-1 overflow-y-auto p-6">
      <h1 class="text-xl font-bold text-slate-800 mb-6">Dashboard</h1>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <StatCard label="Total Orders"  :value="stats.totalOrders"  color="blue" />
        <StatCard label="Draft Orders"  :value="stats.draftOrders"  color="amber" />
        <StatCard label="Active Items"  :value="stats.activeItems"  color="emerald" />
      </div>

      <div class="bg-white rounded-xl border border-slate-200 p-5">
        <h2 class="font-semibold text-slate-800 mb-4">Recent Orders</h2>
        <p class="text-sm text-slate-400">
          Navigate to <RouterLink to="/orders" class="text-brand-600 hover:underline">Orders</RouterLink>
          to view and manage all orders.
        </p>
      </div>
    </div>

</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useOrdersStore } from '@/stores/orders.js'

const ordersStore = useOrdersStore()

const stats = reactive({
  totalOrders: 0,
  draftOrders: 0,
  activeItems: 0,
})

const StatCard = {
  props: ['label', 'value', 'color'],
  template: `
    <div class="bg-white rounded-xl border border-slate-200 p-5">
      <p class="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">{{ label }}</p>
      <p class="text-3xl font-bold text-slate-800">{{ value }}</p>
    </div>
  `
}

onMounted(async () => {
  await ordersStore.fetchOrders()
  await ordersStore.fetchItems()
  stats.totalOrders = ordersStore.ordersTotal
  stats.draftOrders = ordersStore.orders.filter(o => o.status === 'draft').length
  stats.activeItems = ordersStore.items.filter(i => i.status === 'active').length
})
</script>
