<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api/axios.js'

const emit = defineEmits<{ (e: 'select', supplier: any): void }>()

const suppliers   = ref<any[]>([])
const loading     = ref(false)
const search      = ref('')
const currentPage = ref(1)
const totalCount  = ref(0)
const pageSize    = 15

let searchTimeout: any = null

const fetchSuppliers = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/partners/suppliers/', {
      params: {
        search:    search.value || undefined,
        page:      currentPage.value,
        page_size: pageSize,
      }
    })
    suppliers.value = data.results ?? data
    totalCount.value = data.count ?? suppliers.value.length
  } finally {
    loading.value = false
  }
}

const onSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchSuppliers()
  }, 300)
}

const totalPages = () => Math.ceil(totalCount.value / pageSize)

const goTo = (page: number) => {
  currentPage.value = page
  fetchSuppliers()
}

onMounted(fetchSuppliers)
</script>

<template>
  <div class="overflow-auto">
    <div class="bg-white relative border rounded-lg">

      <!-- Search + count -->
      <div class="flex items-center justify-between p-2 gap-3">
        <input
          v-model="search"
          @input="onSearch"
          type="text"
          placeholder="Search suppliers…"
          class="border border-gray-300 rounded px-3 py-1.5 text-sm w-64 focus:outline-none focus:ring-1 focus:ring-blue-400" />
        <span class="text-xs text-gray-400">
          {{ totalCount }} supplier{{ totalCount !== 1 ? 's' : '' }}
        </span>
      </div>

      <!-- Table -->
      <div v-if="loading" class="p-4 text-sm text-gray-500">Loading suppliers…</div>
      <table v-else class="w-full text-sm text-left">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50">
          <tr>
            <th class="px-4 py-3">Name</th>
            <th class="px-4 py-3">Ref</th>
            <th class="px-4 py-3">City</th>
            <th class="px-4 py-3">Country</th>
            <th class="px-4 py-3">Email</th>
            <th class="px-4 py-3">Tel</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!suppliers.length">
            <td colspan="6" class="px-4 py-3 text-gray-400 italic text-center">No suppliers found.</td>
          </tr>
          <tr
            v-for="item in suppliers"
            :key="item.bp_id"
            class="border-b cursor-pointer hover:bg-blue-50"
            @click="emit('select', item)">
            <td class="px-4 py-3 font-medium text-gray-900">{{ item.bp_name }}</td>
            <td class="px-4 py-3 text-gray-600">{{ item.bp_int_ref }}</td>
            <td class="px-4 py-3 text-gray-600">{{ item.bp_city }}</td>
            <td class="px-4 py-3 text-gray-600">{{ item.bp_country }}</td>
            <td class="px-4 py-3 text-gray-600">{{ item.bp_email }}</td>
            <td class="px-4 py-3 text-gray-600">{{ item.bp_tel }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="totalPages() > 1"
        class="flex items-center justify-between px-4 py-2 border-t border-gray-100 bg-gray-50 text-xs text-gray-500">
        <button
          :disabled="currentPage === 1"
          @click="goTo(currentPage - 1)"
          class="px-3 py-1 rounded border border-gray-300 hover:bg-gray-100 disabled:opacity-40">
          ← Prev
        </button>
        <span>Page {{ currentPage }} of {{ totalPages() }}</span>
        <button
          :disabled="currentPage >= totalPages()"
          @click="goTo(currentPage + 1)"
          class="px-3 py-1 rounded border border-gray-300 hover:bg-gray-100 disabled:opacity-40">
          Next →
        </button>
      </div>

    </div>
  </div>
</template>