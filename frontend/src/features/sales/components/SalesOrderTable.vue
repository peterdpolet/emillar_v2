<script setup lang="ts">
import { useSalesStore } from '@/features/sales/stores/useSalesStore.js'

const salesStore = useSalesStore()

const statusColour = (status: string) => {
  const map: Record<string, string> = {
    draft:          'bg-gray-100 text-gray-600',
    active:         'bg-blue-100 text-blue-700',
    part_fulfilled: 'bg-yellow-100 text-yellow-700',
    fulfilled:      'bg-green-100 text-green-700',
    cancelled:      'bg-red-100 text-red-600',
  }
  return map[status] ?? 'bg-gray-100 text-gray-600'
}
</script>

<template>
  <div class="overflow-auto">
    <div v-if="salesStore.salesOrdersLoading" class="p-4 text-sm text-gray-500">
      Loading orders…
    </div>
    <div v-else-if="!salesStore.salesOrders.length" class="p-4 text-sm text-gray-400 italic">
      No sales orders found for this customer.
    </div>
    <table v-else class="w-full text-sm text-left">
      <thead class="text-xs text-gray-700 uppercase bg-gray-50">
        <tr>
          <th class="px-4 py-3">Reference</th>
          <th class="px-4 py-3">Date</th>
          <th class="px-4 py-3">Status</th>
          <th class="px-4 py-3">Currency</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="order in salesStore.salesOrders"
          :key="order.so_id"
          class="border-b cursor-pointer hover:bg-blue-50"
          @click="salesStore.selectSalesOrder(order)"
          :class="{ 'bg-blue-50': salesStore.selectedSalesOrder?.so_id === order.so_id }"
        >
          <td class="px-4 py-3 font-medium text-gray-900">{{ order.reference || '—' }}</td>
          <td class="px-4 py-3 text-gray-600">{{ order.raised_date }}</td>
          <td class="px-4 py-3">
            <span :class="statusColour(order.status)" class="px-2 py-1 rounded-full text-xs font-medium capitalize">
              {{ order.status.replace('_', ' ') }}
            </span>
          </td>
          <td class="px-4 py-3 text-gray-600">{{ order.currency }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>