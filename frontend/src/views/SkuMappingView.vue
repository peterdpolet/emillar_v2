<template>
  <div class="flex-1 flex flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white flex-shrink-0">
      <div>
        <h1 class="text-lg font-bold text-slate-800">SKU Mapping</h1>
        <p class="text-xs text-slate-400 mt-0.5">Map supplier SKUs to Ewan Millar SKUs</p>
      </div>
      <button @click="showCreate = true"
        class="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white
               text-sm font-medium rounded-lg px-4 py-2 transition-colors">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Add mapping
      </button>
    </div>

    <!-- Filters -->
    <div class="px-6 py-3 border-b border-slate-100 bg-white flex-shrink-0 flex items-center gap-4">
      <input v-model="search" type="text" placeholder="Search SKUs…"
        class="w-full max-w-xs border border-slate-200 rounded-lg px-3 py-2 text-sm
               focus:outline-none focus:ring-2 focus:ring-brand-500" />
      <select v-model="supplierFilter"
        class="border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white
               focus:outline-none focus:ring-2 focus:ring-brand-500">
        <option value="">All suppliers</option>
        <option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
      </select>
    </div>

    <!-- Table -->
    <div class="flex-1 overflow-y-auto">
      <table class="w-full table-fixed text-sm">
        <colgroup>
          <col class="w-40">
          <col class="w-40">
          <col class="w-48">
          <col class="w-48">
          <col class="w-24">
        </colgroup>
        <thead class="bg-slate-50 border-b border-slate-200 sticky top-0">
          <tr>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Supplier SKU</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">EM SKU</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Supplier</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Description</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="px-4 py-8 text-center text-slate-400 text-sm">Loading…</td>
          </tr>
          <tr v-else-if="!filteredMappings.length">
            <td colspan="5" class="px-4 py-8 text-center text-slate-400 text-sm">No SKU mappings found</td>
          </tr>
          <tr v-for="mapping in filteredMappings" :key="mapping.id"
            class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
            <td class="px-4 py-3 font-mono text-xs text-slate-700">{{ mapping.supplier_sku }}</td>
            <td class="px-4 py-3 font-mono text-xs text-brand-600 font-medium">{{ mapping.em_sku }}</td>
            <td class="px-4 py-3 text-slate-600">{{ mapping.supplier_name }}</td>
            <td class="px-4 py-3 text-slate-500 text-xs truncate">{{ mapping.description ?? '—' }}</td>
            <td class="px-4 py-3">
              <button @click="editMapping(mapping)"
                class="text-xs text-brand-600 hover:text-brand-700 font-medium">
                Edit
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/axios.js'

const loading        = ref(false)
const search         = ref('')
const supplierFilter = ref('')
const showCreate     = ref(false)
const mappings       = ref([])
const suppliers      = ref([])

const filteredMappings = computed(() => {
  let list = mappings.value
  if (supplierFilter.value) list = list.filter(m => m.supplier === supplierFilter.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(m =>
      m.supplier_sku?.toLowerCase().includes(q) ||
      m.em_sku?.toLowerCase().includes(q) ||
      m.description?.toLowerCase().includes(q)
    )
  }
  return list
})

onMounted(async () => {
  loading.value = true
  try {
    const [mappingRes, supplierRes] = await Promise.all([
      api.get('/sku-mappings/'),
      api.get('/suppliers/'),
    ])
    mappings.value  = mappingRes.data.results  ?? mappingRes.data
    suppliers.value = supplierRes.data.results ?? supplierRes.data
  } catch {
    mappings.value  = []
    suppliers.value = []
  } finally {
    loading.value = false
  }
})

function editMapping(mapping) {
  // TODO: open edit modal
  console.log('edit', mapping)
}
</script>
