<!-- inventory/views/ItemCreate.vue -->
<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useInventoryStore } from '@inventory/stores/useInventory.js'

const router = useRouter()
const store  = useInventoryStore()

const isGem = ref(false)   // toggle shows/hides stone detail section

const form = reactive({
  sku:          '',
  name:         '',
  description:  '',
  status:       'active',
  base_price:   '',
  currency:     'GBP',
  stone_detail: null,
})

function toggleStone(val) {
  isGem.value = val
  form.gem_detail = val ? {
    certification_number: '',
    carat_weight:         '',
    origin:               '',
    colour:               null,
    clarity:              null,
    cut:                  null,
    is_treated:           false,
    has_fluorescence:     false,
  } : null
}

async function submit() {
  const item = await store.createItem(form)
  router.push(`/inventory/items/${item.id}`)
}
</script>

<template>
  <div class="max-w-2xl mx-auto p-6">
    <h1 class="text-lg font-semibold text-slate-800 mb-6">New item</h1>

    <!-- Core item fields -->
    <div class="space-y-4 mb-6">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">SKU</label>
          <input v-model="form.sku" type="text"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"/>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Status</label>
          <select v-model="form.status"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm">
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-xs font-medium text-slate-500 mb-1">Name</label>
        <input v-model="form.name" type="text"
          class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"/>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Base price</label>
          <input v-model="form.base_price" type="number" step="0.01"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"/>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Currency</label>
          <select v-model="form.currency"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm">
            <option value="GBP">GBP</option>
            <option value="USD">USD</option>
            <option value="EUR">EUR</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Stone detail toggle -->
    <div class="flex items-center gap-3 mb-4 p-3 bg-slate-50 rounded-lg">
      <input type="checkbox" id="is-stone" :checked="isGem"
        @change="toggleStone($event.target.checked)"
        class="rounded"/>
      <label for="is-stone" class="text-sm font-medium text-slate-700">
        This is a certified stone
      </label>
    </div>

    <!-- Stone detail fields — only shown if isStone -->
    <div v-if="isGem" class="space-y-4 mb-6 p-4 border border-slate-200 rounded-lg">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">
            Certification number
          </label>
          <input v-model="form.gem_detail.certification_number" type="text"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"/>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">
            Carat weight
          </label>
          <input v-model="form.gem_detail.carat_weight" type="number" step="0.001"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"/>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Colour</label>
          <select v-model="form.gem_detail.colour"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm">
            <option :value="null">—</option>
            <option v-for="c in store.colours" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Clarity</label>
          <select v-model="form.gem_detail.clarity"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm">
            <option :value="null">—</option>
            <option v-for="c in store.clarities" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-500 mb-1">Cut</label>
          <select v-model="form.gem_detail.cut"
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm">
            <option :value="null">—</option>
            <option v-for="c in store.cuts" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-xs font-medium text-slate-500 mb-1">Origin</label>
        <input v-model="form.gem_detail.origin" type="text"
          class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"/>
      </div>

      <div class="flex gap-6">
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="form.gem_detail.is_treated"/>
          Treated
        </label>
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="form.gem_detail.has_fluorescence"/>
          Fluorescence
        </label>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex justify-end gap-3">
      <button @click="$router.back()"
        class="px-4 py-2 text-sm border border-slate-200 rounded-lg">
        Cancel
      </button>
      <button @click="submit"
        class="px-4 py-2 text-sm bg-brand-600 text-white rounded-lg">
        Save item
      </button>
    </div>
  </div>
</template>