<script setup>
import { ref, watch } from 'vue'

import StatusBadge from '@/components/StatusBadge.vue'
import CreateOrderModal from '@/components/CreateOrderModal.vue'
import { useOrdersStore } from '@/stores/orders.js'
import { useRouter } from 'vue-router'

import BusinessPartnerList from '@/components/tables/BusinessPartnerList.vue'

const orders     = useOrdersStore()
const router     = useRouter()
const search     = ref('')
const showCreate = ref(false)

orders.fetchOrders()

watch(search, (val) => {
  orders.fetchOrders({ search: val })
}, { debounce: 300 })

function onCreated(order) {
  showCreate.value = false
  router.push(`/orders/${order.id}`)
}

</script>


<template>
<!-- 
    <BusinessPartnerList/> -->
  Orders View
    <div class="flex-1 flex flex-col overflow-hidden bg-yellow-400">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white flex-shrink-0">
        <h1 class="text-lg font-bold text-slate-800">Orders</h1>
        <button @click="showCreate = true"
          class="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white
                 text-sm font-medium rounded-lg px-4 py-2 transition-colors">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
          </svg>
          New order
        </button>
      </div>

      <!-- Search -->
      <div class="px-6 py-3 border-b border-slate-100 bg-white flex-shrink-0">
        <input v-model="search" type="text" placeholder="Search orders…"
          class="w-full max-w-xs border border-slate-200 rounded-lg px-3 py-2 text-sm
                 focus:outline-none focus:ring-2 focus:ring-brand-500" />
      </div>

      <!-- Table -->
      <div class="flex-1 overflow-y-auto">
        <table class="w-full table-fixed text-sm">
          <colgroup>
            <col class="w-16">
            <col class="w-48">
            <col class="w-32">
            <col class="w-24">
            <col class="w-24">
            <col class="w-32">
          </colgroup>
          <thead class="bg-slate-50 border-b border-slate-200 sticky top-0">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">#</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Customer</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Lines</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Total</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="orders.ordersLoading">
              <td colspan="6" class="px-4 py-8 text-center text-slate-400 text-sm">Loading…</td>
            </tr>
            <tr v-else-if="!orders.orders.length">
              <td colspan="6" class="px-4 py-8 text-center text-slate-400 text-sm">No orders yet</td>
            </tr>
            <tr v-for="order in orders.orders" :key="order.id"
              @click="$router.push(`/orders/${order.id}`)"
              class="border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors">
              <td class="px-4 py-3 text-slate-500 font-mono text-xs">#{{ order.id }}</td>
              <td class="px-4 py-3">
                <p class="font-medium text-slate-800 truncate">{{ order.customer_name }}</p>
                <p class="text-xs text-slate-400 truncate">{{ order.customer_email }}</p>
              </td>
              <td class="px-4 py-3">
                <StatusBadge :status="order.status" />
              </td>
              <td class="px-4 py-3 text-right text-slate-600">{{ order.line_count }}</td>
              <td class="px-4 py-3 text-right font-medium text-slate-800">
                £{{ Number(order.total).toFixed(2) }}
              </td>
              <td class="px-4 py-3 text-slate-400 text-xs">
                {{ new Date(order.created_at).toLocaleDateString('en-GB') }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>


    <!-- Create order modal -->
    <CreateOrderModal v-if="showCreate" @close="showCreate = false" @created="onCreated" />

</template>
