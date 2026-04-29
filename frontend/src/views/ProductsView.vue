<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useItems } from '@/composables/useItems'

const router = useRouter()
const {
  items, total, page, pageSize,
  search, ordering, loading, error, load
} = useItems()

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
onMounted(load)
</script>

<template>
  <div class="flex items-center justify-between mb-6">
    <div>
      <h1 class="text-xl font-bold text-slate-900">Products</h1>
      <p class="text-sm text-slate-500 mt-0.5">{{ total }} total</p>
    </div>
    <button @click="router.push('/admin/products/new')"
      class="px-4 py-2 bg-indigo-600 text-white text-sm
             font-semibold rounded-lg hover:bg-indigo-500 transition-colors">
      + New product
    </button>
  </div>

  <div class="flex gap-3 mb-4">
    <input v-model="search" placeholder="Search products..."
      class="flex-1 px-3 py-2 bg-white border border-slate-200
             rounded-lg text-sm focus:outline-none focus:ring-2
             focus:ring-indigo-500" />
    <select v-model="ordering"
      class="px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm">
      <option value="-created_at">Newest first</option>
      <option value="created_at">Oldest first</option>
      <option value="name">Name A–Z</option>
      <option value="-price">Price high–low</option>
      <option value="price">Price low–high</option>
    </select>
  </div>

  <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
    <div v-if="loading" class="p-8 text-center text-sm text-slate-400">
      Loading...
    </div>
    <div v-else-if="error" class="p-8 text-center text-sm text-red-500">
      {{ error }}
    </div>

    <table v-else class="w-full">
      <thead>
        <tr class="border-b border-slate-200">
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Name</th>
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Description</th>
          <th class="px-4 py-3 text-right text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Price</th>
          <th class="px-4 py-3 text-left text-xs font-semibold
                     text-slate-500 uppercase tracking-wide">Status</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
        <tr v-for="item in items" :key="item.id"
          @click="router.push(`/admin/products/${item.id}`)"
          class="hover:bg-slate-50 cursor-pointer transition-colors">
          <td class="px-4 py-3 text-sm font-medium text-slate-900">
            {{ item.name }}
          </td>
          <td class="px-4 py-3 text-sm text-slate-500 max-w-xs truncate">
            {{ item.description || '—' }}
          </td>
          <td class="px-4 py-3 text-sm font-medium text-slate-900
                     tabular-nums text-right">
            £{{ item.price }}
          </td>
          <td class="px-4 py-3">
            <span :class="[
              'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold',
              item.status === 'active'
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-slate-100 text-slate-500'
            ]">
              <span :class="[
                'w-1.5 h-1.5 rounded-full',
                item.status === 'active' ? 'bg-emerald-500' : 'bg-slate-400'
              ]"></span>
              {{ item.status === 'active' ? 'Active' : 'Archived' }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!loading && !error"
      class="flex items-center justify-between px-4 py-3
             border-t border-slate-200">
      <p class="text-sm text-slate-500">
        Page {{ page }} of {{ totalPages || 1 }}
      </p>
      <div class="flex gap-2">
        <button :disabled="page === 1" @click="page--"
          class="px-3 py-1.5 text-sm bg-white border border-slate-200
                 rounded-lg disabled:opacity-40 hover:bg-slate-50">
          Previous
        </button>
        <button :disabled="page >= totalPages" @click="page++"
          class="px-3 py-1.5 text-sm bg-white border border-slate-200
                 rounded-lg disabled:opacity-40 hover:bg-slate-50">
          Next
        </button>
      </div>
    </div>
  </div>
</template>