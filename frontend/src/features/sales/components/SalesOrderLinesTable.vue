<script setup lang="ts">
import { useSalesStore } from '@/features/sales/stores/useSalesStore.js'

const salesStore = useSalesStore()

const statusColour = (status: string) => {
  const map: Record<string, string> = {
    requested:           'bg-gray-100 text-gray-600',
    rfq_sent:            'bg-blue-100 text-blue-700',
    quoted:              'bg-yellow-100 text-yellow-700',
    on_order:            'bg-purple-100 text-purple-700',
    on_approval:         'bg-orange-100 text-orange-700',
    confirmed:           'bg-green-100 text-green-700',
    returned:            'bg-red-100 text-red-600',
    returned_to_supplier:'bg-red-100 text-red-600',
    cancelled:           'bg-gray-200 text-gray-500',
  }
  return map[status] ?? 'bg-gray-100 text-gray-600'
}

const fmt = (val: any) => (val === null || val === undefined || val === '') ? '—' : val
</script>

<template>
  <div class="overflow-auto">
    <div v-if="salesStore.linesLoading" class="p-4 text-sm text-gray-500">
      Loading lines…
    </div>
    <div v-else-if="!salesStore.salesOrderLines.length" class="p-4 text-sm text-gray-400 italic">
      No lines on this sales order.
    </div>
    <table v-else class="w-full text-sm text-left">
      <thead class="text-xs text-gray-700 uppercase bg-gray-50">
        <tr>
          <th class="px-3 py-3">#</th>
          <th class="px-3 py-3">Stone</th>
          <th class="px-3 py-3">Type</th>
          <th class="px-3 py-3">Status</th>
          <th class="px-3 py-3">Size mm</th>
          <th class="px-3 py-3">Carat</th>
          <th class="px-3 py-3">Colour</th>
          <th class="px-3 py-3">Clarity</th>
          <th class="px-3 py-3">Price range</th>
          <th class="px-3 py-3">Agreed</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="line in salesStore.salesOrderLines" :key="line.sol_id">
          <tr class="border-b hover:bg-blue-50">
            <td class="px-3 py-2 text-gray-500">{{ line.line_number }}</td>
            <td class="px-3 py-2 font-medium text-gray-900 capitalize">{{ fmt(line.stone_type) }}</td>
            <td class="px-3 py-2 text-gray-600 capitalize">{{ fmt(line.item_type) }}</td>
            <td class="px-3 py-2">
              <span :class="statusColour(line.status)" class="px-2 py-1 rounded-full text-xs font-medium capitalize">
                {{ line.status.replace(/_/g, ' ') }}
              </span>
            </td>
            <td class="px-3 py-2 text-gray-600">
              {{ fmt(line.min_size) }}–{{ fmt(line.max_size) }}
            </td>
            <td class="px-3 py-2 text-gray-600">
              {{ fmt(line.min_carat) }}–{{ fmt(line.max_carat) }}
            </td>
            <td class="px-3 py-2 text-gray-600">{{ fmt(line.colour_spec) }}</td>
            <td class="px-3 py-2 text-gray-600">{{ fmt(line.clarity_spec) }}</td>
            <td class="px-3 py-2 text-gray-600">
              {{ fmt(line.min_price) }}–{{ fmt(line.max_price) }}
            </td>
            <td class="px-3 py-2 text-gray-600">{{ fmt(line.agreed_price) }}</td>
          </tr>
          <tr v-if="line.notes" class="bg-gray-50 border-b">
            <td colspan="10" class="px-3 py-1 text-xs text-gray-400 italic">
              {{ line.notes }}
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>