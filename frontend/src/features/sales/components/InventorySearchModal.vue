<script setup lang="ts">
import { ref, watch } from 'vue'
import api from '@/api/axios.js'

const emit = defineEmits(['select', 'close'])

const query      = ref('')
const results    = ref([])
const searching  = ref(false)
let   debounce: ReturnType<typeof setTimeout>

watch(query, (val) => {
  clearTimeout(debounce)
  if (!val.trim()) { results.value = []; return }
  debounce = setTimeout(async () => {
    searching.value = true
    try {
      const { data } = await api.get('/inventory/items/', {
        params: { search: val, page_size: 20 }
      })
      results.value = data.results ?? data
    } finally {
      searching.value = false
    }
  }, 300)
})

function select(item: any) {
  emit('select', item)
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
       @click.self="$emit('close')">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-4xl mx-4 flex flex-col max-h-[80vh]">

      <!-- Modal header -->
      <div class="flex items-center justify-between px-5 py-4 border-b">
        <h2 class="text-sm font-semibold text-gray-800">Select Inventory Item</h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 text-lg leading-none">&times;</button>
      </div>

      <!-- Search input -->
      <div class="px-5 py-3 border-b">
        <input
          v-model="query"
          type="text"
          placeholder="Search by SKU, name, or description…"
          autofocus
          class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
      </div>

      <!-- Results -->
      <div class="overflow-auto flex-1">
        <div v-if="searching" class="p-4 text-sm text-gray-400">Searching…</div>
        <div v-else-if="!results.length && query" class="p-4 text-sm text-gray-400">No items found.</div>
        <div v-else-if="!query" class="p-4 text-sm text-gray-400">Start typing to search inventory.</div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase sticky top-0">
            <tr>
              <th class="px-4 py-2 text-left">SKU</th>
              <th class="px-4 py-2 text-left">Name</th>
              <th class="px-4 py-2 text-left">Carat</th>
              <th class="px-4 py-2 text-left">Colour</th>
              <th class="px-4 py-2 text-left">Clarity</th>
              <th class="px-4 py-2 text-left">Cut</th>
              <th class="px-4 py-2 text-left">Cert No</th>
              <th class="px-4 py-2 text-left">Price</th>
              <th class="px-4 py-2"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in results" :key="item.id"
                class="border-t hover:bg-blue-50 cursor-pointer"
                @click="select(item)">
              <td class="px-4 py-2 font-medium">{{ item.sku }}</td>
              <td class="px-4 py-2">{{ item.name }}</td>
              <td class="px-4 py-2">{{ item.gem_detail?.carat_weight ?? '—' }}</td>
              <td class="px-4 py-2">{{ item.gem_detail?.color?.name ?? '—' }}</td>
              <td class="px-4 py-2">{{ item.gem_detail?.clarity?.name ?? '—' }}</td>
              <td class="px-4 py-2">{{ item.gem_detail?.cut?.name ?? '—' }}</td>
              <td class="px-4 py-2">{{ item.gem_detail?.certification_number ?? '—' }}</td>
              <td class="px-4 py-2">{{ item.currency }} {{ item.base_price }}</td>
              <td class="px-4 py-2">
                <button @click.stop="select(item)"
                  class="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700">
                  Select
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>