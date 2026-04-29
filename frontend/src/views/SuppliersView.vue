<template>
  <div class="flex-1 flex flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white flex-shrink-0">
      <h1 class="text-lg font-bold text-slate-800">Suppliers</h1>
      <button @click="showCreate = true"
        class="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white
               text-sm font-medium rounded-lg px-4 py-2 transition-colors">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Add supplier
      </button>
    </div>

    <!-- Search -->
    <div class="px-6 py-3 border-b border-slate-100 bg-white flex-shrink-0">
      <input v-model="search" type="text" placeholder="Search suppliers…"
        class="w-full max-w-xs border border-slate-200 rounded-lg px-3 py-2 text-sm
               focus:outline-none focus:ring-2 focus:ring-brand-500" />
    </div>

    <!-- Table -->
    <div class="flex-1 overflow-y-auto">
      <table class="w-full table-fixed text-sm">
        <colgroup>
          <col class="w-48">
          <col class="w-48">
          <col class="w-32">
          <col class="w-32">
          <col class="w-24">
        </colgroup>
        <thead class="bg-slate-50 border-b border-slate-200 sticky top-0">
          <tr>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Name</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Contact</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Currency</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="px-4 py-8 text-center text-slate-400 text-sm">Loading…</td>
          </tr>
          <tr v-else-if="!filteredSuppliers.length">
            <td colspan="5" class="px-4 py-8 text-center text-slate-400 text-sm">No suppliers yet</td>
          </tr>
          <tr v-for="supplier in filteredSuppliers" :key="supplier.id"
            class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
            <td class="px-4 py-3">
              <p class="font-medium text-slate-800">{{ supplier.name }}</p>
              <p class="text-xs text-slate-400">{{ supplier.code }}</p>
            </td>
            <td class="px-4 py-3">
              <p class="text-slate-700">{{ supplier.contact_name }}</p>
              <p class="text-xs text-slate-400">{{ supplier.email }}</p>
            </td>
            <td class="px-4 py-3 text-slate-600 font-mono text-xs">{{ supplier.currency ?? 'GBP' }}</td>
            <td class="px-4 py-3">
              <span :class="supplier.is_active
                ? 'bg-green-50 text-green-700'
                : 'bg-slate-100 text-slate-500'"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                {{ supplier.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-4 py-3">
              <button @click="editSupplier(supplier)"
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

const loading      = ref(false)
const search       = ref('')
const showCreate   = ref(false)
const suppliers    = ref([])

const filteredSuppliers = computed(() => {
  if (!search.value) return suppliers.value
  const q = search.value.toLowerCase()
  return suppliers.value.filter(s =>
    s.name?.toLowerCase().includes(q) ||
    s.email?.toLowerCase().includes(q) ||
    s.code?.toLowerCase().includes(q)
  )
})

onMounted(fetchSuppliers)

async function fetchSuppliers() {
  loading.value = true
  try {
    const { data } = await api.get('/suppliers/')
    suppliers.value = data.results ?? data
  } catch {
    suppliers.value = []
  } finally {
    loading.value = false
  }
}

function editSupplier(supplier) {
  // TODO: open edit modal
  console.log('edit', supplier)
}
</script>
