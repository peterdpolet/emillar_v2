<!-- frontend/src/features/inventory/views/InventoryItemDetail.vue -->
<script setup>
import { onMounted, computed } from 'vue'
import { useRoute }            from 'vue-router'
import { useInventoryStore }   from '@inventory/stores/useInventory.js'

const route = useRoute()
const store = useInventoryStore()

onMounted(() => store.fetchItem(route.params.id))

const gem = computed(() => store.item?.gem_detail ?? null)
</script>

<template>
  <div class="max-w-2xl mx-auto p-6">

    <!-- Loading -->
    <div v-if="store.loading" class="text-sm text-slate-400">Loading…</div>
    <div v-else-if="store.error" class="text-sm text-red-500">{{ store.error }}</div>

    <template v-else-if="store.item">
      <!-- Header -->
      <div class="flex items-start justify-between mb-6">
        <div>
          <p class="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">
            Stock item
          </p>
          <h1 class="text-xl font-semibold text-slate-800">
            {{ store.item.name || store.item.sku }}
          </h1>
          <p class="text-sm text-slate-500 mt-0.5">SKU: {{ store.item.sku }}</p>
        </div>
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
          :class="store.item.status?.name === 'active'
            ? 'bg-green-100 text-green-700'
            : 'bg-slate-100 text-slate-500'">
          {{ store.item.status?.name ?? '—' }}
        </span>
      </div>

      <!-- Core fields -->
      <div class="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100 mb-6">
        <div class="grid grid-cols-2 gap-0 divide-x divide-slate-100">
          <div class="px-4 py-3">
            <p class="text-xs text-slate-400 mb-0.5">Base price</p>
            <p class="text-sm font-medium text-slate-800">
              {{ store.item.currency?.code ?? '' }}
              {{ store.item.base_price ?? '—' }}
            </p>
          </div>
          <div class="px-4 py-3">
            <p class="text-xs text-slate-400 mb-0.5">Supplier</p>
            <p class="text-sm font-medium text-slate-800">
              {{ store.item.supplier?.name ?? '—' }}
            </p>
          </div>
        </div>
        <div class="px-4 py-3" v-if="store.item.description">
          <p class="text-xs text-slate-400 mb-0.5">Description</p>
          <p class="text-sm text-slate-700">{{ store.item.description }}</p>
        </div>
      </div>

      <!-- Gem detail -->
      <template v-if="gem">
        <h2 class="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-3">
          Stone detail
        </h2>
        <div class="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
          <div class="grid grid-cols-2 divide-x divide-slate-100">
            <div class="px-4 py-3">
              <p class="text-xs text-slate-400 mb-0.5">Certification</p>
              <p class="text-sm font-medium text-slate-800">
                {{ gem.certification_number || '—' }}
              </p>
            </div>
            <div class="px-4 py-3">
              <p class="text-xs text-slate-400 mb-0.5">Carat weight</p>
              <p class="text-sm font-medium text-slate-800">
                {{ gem.carat_weight ?? '—' }}
              </p>
            </div>
          </div>
          <div class="grid grid-cols-3 divide-x divide-slate-100">
            <div class="px-4 py-3">
              <p class="text-xs text-slate-400 mb-0.5">Colour</p>
              <p class="text-sm font-medium text-slate-800">
                {{ gem.color?.name ?? '—' }}
              </p>
            </div>
            <div class="px-4 py-3">
              <p class="text-xs text-slate-400 mb-0.5">Clarity</p>
              <p class="text-sm font-medium text-slate-800">
                {{ gem.clarity?.name ?? '—' }}
              </p>
            </div>
            <div class="px-4 py-3">
              <p class="text-xs text-slate-400 mb-0.5">Cut</p>
              <p class="text-sm font-medium text-slate-800">
                {{ gem.cut?.name ?? '—' }}
              </p>
            </div>
          </div>
          <div class="px-4 py-3">
            <p class="text-xs text-slate-400 mb-0.5">Origin</p>
            <p class="text-sm font-medium text-slate-800">{{ gem.origin || '—' }}</p>
          </div>
        </div>
      </template>

      <!-- Back -->
      <div class="mt-6">
        <button @click="$router.back()"
          class="text-sm text-slate-500 hover:text-slate-700">
          ← Back
        </button>
      </div>
    </template>

  </div>
</template>