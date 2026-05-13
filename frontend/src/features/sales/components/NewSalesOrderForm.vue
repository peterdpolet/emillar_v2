<script setup lang="ts">
import { ref, computed } from 'vue'
import api from '@/api/axios.js'
import { useSalesStore } from '@/features/sales/stores/useSalesStore.js'

const salesStore = useSalesStore()
const emit = defineEmits<{ (e: 'saved'): void }>()

// ── Header ────────────────────────────────────────────────
const reference = ref('')
const currency  = ref('GBP')
const notes     = ref('')

// ── Line builder ──────────────────────────────────────────
const lineForm = ref({
  stone_type:         'diamond',
  quantity:           1,
  item_type:          'certified',
  min_size:           '',
  max_size:           '',
  min_carat:          '',
  max_carat:          '',
  colour_spec:        '',
  clarity_spec:       '',
  min_price:          '',
  max_price:          '',
  certificate_type:   '',
  certificate_number: '',
  notes:              '',
  inventory_item:     null as string | null,
})

const lines = ref<any[]>([])

// ── Inventory search ──────────────────────────────────────
const itemSearch    = ref('')
const itemResults   = ref<any[]>([])
const itemSearching = ref(false)
const selectedItem  = ref<any>(null)

let searchTimeout: any = null
const onItemSearch = () => {
  clearTimeout(searchTimeout)
  if (!itemSearch.value || itemSearch.value.length < 2) {
    itemResults.value = []
    return
  }
  searchTimeout = setTimeout(async () => {
    itemSearching.value = true
    try {
      const { data } = await api.get('/inventory/items/', {
        params: { search: itemSearch.value, page_size: 10 }
      })
      itemResults.value = data.results ?? data
    } finally {
      itemSearching.value = false
    }
  }, 300)
}

const selectItem = (item: any) => {
  selectedItem.value      = item
  lineForm.value.inventory_item = item.id
  itemSearch.value        = `${item.sku} — ${item.name}`
  itemResults.value       = []
}

const clearItem = () => {
  selectedItem.value            = null
  lineForm.value.inventory_item = null
  itemSearch.value              = ''
}

// ── Lines ─────────────────────────────────────────────────
const addLine = () => {
  lines.value.push({
    ...lineForm.value,
    line_number: lines.value.length + 1,
    _itemLabel: selectedItem.value
      ? `${selectedItem.value.sku} — ${selectedItem.value.name}`
      : null,
  })
  // reset line form
  lineForm.value = {
    quantity: lineForm.value.quantity || 1,
    stone_type: 'diamond', item_type: 'certified',
    min_size: '', max_size: '', min_carat: '', max_carat: '',
    colour_spec: '', clarity_spec: '',
    min_price: '', max_price: '',
    certificate_type: '', certificate_number: '',
    notes: '', inventory_item: null,
  }
  clearItem()
}

const removeLine = (index: number) => {
  lines.value.splice(index, 1)
  lines.value.forEach((l, i) => l.line_number = i + 1)
}

// ── Save ──────────────────────────────────────────────────
const saving = ref(false)
const error  = ref('')

const canSave = computed(() => lines.value.length > 0 && salesStore.selectedCustomer)

const save = async () => {
  if (!canSave.value) return
  saving.value = true
  error.value  = ''
  try {
    // 1. Create the SO header
    const { data: order } = await api.post('/sales/orders/', {
      customer:  salesStore.selectedCustomer!.bp_id,
      reference: reference.value || null,
      currency:  currency.value,
      notes:     notes.value,
    })
    // 2. Post each line
    for (const line of lines.value) {
      await api.post('/sales/lines/', {
        sales_order:        order.so_id,
        line_number:        line.line_number,
        quantity:           line.quantity,
        stone_type:         line.stone_type,
        item_type:          line.item_type,
        status:             'requested',
        min_size:           line.min_size   || null,
        max_size:           line.max_size   || null,
        min_carat:          line.min_carat  || null,
        max_carat:          line.max_carat  || null,
        colour_spec:        line.colour_spec        || '',
        clarity_spec:       line.clarity_spec       || '',
        min_price:          line.min_price  || null,
        max_price:          line.max_price  || null,
        certificate_type:   line.certificate_type   || '',
        certificate_number: line.certificate_number || '',
        notes:              line.notes              || '',
        inventory_item:     line.inventory_item     || null,
      })
    }
    // 3. Refresh orders list and reset form
    await salesStore.fetchSalesOrders()
    reference.value = ''
    currency.value  = 'GBP'
    notes.value     = ''
    lines.value     = []
    emit('saved')
  } catch (e: any) {
    error.value = e?.response?.data
      ? JSON.stringify(e.response.data)
      : 'Save failed — check console'
    console.error(e)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="space-y-4 text-sm">

    <!-- Header fields -->
    <div class="grid grid-cols-3 gap-3">
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Reference</label>
        <input v-model="reference" type="text" placeholder="Auto-generated if blank"
          class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Currency</label>
        <select v-model="currency"
          class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400">
          <option>GBP</option>
          <option>USD</option>
          <option>EUR</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Notes</label>
        <input v-model="notes" type="text"
          class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
      </div>
    </div>

    <!-- Line builder -->
    <div class="border border-gray-200 rounded-lg p-3 bg-white space-y-3">
      <p class="font-semibold text-gray-700">Add Line</p>

      <div class="grid grid-cols-5 gap-2">
        <div>
          <label class="block text-xs text-gray-500 mb-1">Qty</label>
          <input v-model.number="lineForm.quantity" type="number" min="1" step="1"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Stone Type</label>
          <select v-model="lineForm.stone_type"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm">
            <option value="diamond">Diamond</option>
            <option value="ruby">Ruby</option>
            <option value="sapphire">Sapphire</option>
            <option value="emerald">Emerald</option>
            <option value="pearl">Pearl</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Item Type</label>
          <select v-model="lineForm.item_type"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm">
            <option value="certified">Certified</option>
            <option value="uncertified">Uncertified</option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Colour Spec</label>
          <input v-model="lineForm.colour_spec" type="text" placeholder="e.g. D-F"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Clarity Spec</label>
          <input v-model="lineForm.clarity_spec" type="text" placeholder="e.g. VS1-VVS2"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
        </div>
      </div>

      <div class="grid grid-cols-4 gap-2">
        <div>
          <label class="block text-xs text-gray-500 mb-1">Size mm (min–max)</label>
          <div class="flex gap-1">
            <input v-model="lineForm.min_size" type="number" step="0.01" placeholder="min"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
            <input v-model="lineForm.max_size" type="number" step="0.01" placeholder="max"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Carat (min–max)</label>
          <div class="flex gap-1">
            <input v-model="lineForm.min_carat" type="number" step="0.001" placeholder="min"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
            <input v-model="lineForm.max_carat" type="number" step="0.001" placeholder="max"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Price range (min–max)</label>
          <div class="flex gap-1">
            <input v-model="lineForm.min_price" type="number" step="0.01" placeholder="min"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
            <input v-model="lineForm.max_price" type="number" step="0.01" placeholder="max"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Cert Type / Number</label>
          <div class="flex gap-1">
            <select v-model="lineForm.certificate_type"
              class="w-24 border border-gray-300 rounded px-2 py-1.5 text-sm">
              <option value="">—</option>
              <option>GIA</option>
              <option>IGI</option>
              <option>HRD</option>
              <option>AGS</option>
            </select>
            <input v-model="lineForm.certificate_number" type="text" placeholder="number"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
        </div>
      </div>

      <!-- Inventory search -->
      <div class="relative">
        <label class="block text-xs text-gray-500 mb-1">Link Inventory Item (optional)</label>
        <div class="flex gap-2">
          <input v-model="itemSearch" @input="onItemSearch" type="text"
            placeholder="Search by SKU or name…"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          <button v-if="selectedItem" @click="clearItem"
            class="text-xs text-red-500 hover:underline whitespace-nowrap">Clear</button>
        </div>
        <ul v-if="itemResults.length"
          class="absolute z-10 w-full bg-white border border-gray-200 rounded shadow mt-1 max-h-40 overflow-auto">
          <li v-for="item in itemResults" :key="item.id"
            @click="selectItem(item)"
            class="px-3 py-2 hover:bg-blue-50 cursor-pointer text-sm">
            <span class="font-medium">{{ item.sku }}</span>
            <span class="text-gray-500 ml-2">{{ item.name }}</span>
          </li>
          <li v-if="itemSearching" class="px-3 py-2 text-gray-400 text-xs">Searching…</li>
        </ul>
      </div>

      <div>
        <label class="block text-xs text-gray-500 mb-1">Line Notes</label>
        <input v-model="lineForm.notes" type="text"
          class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
      </div>

      <button @click="addLine"
        class="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
        + Add Line
      </button>
    </div>

    <!-- Lines preview -->
    <div v-if="lines.length" class="border border-gray-200 rounded-lg overflow-auto">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-xs text-gray-600 uppercase">
          <tr>
            <th class="px-3 py-2">#</th>
            <th class="px-3 py-2">Qty</th>
            <th class="px-3 py-2">Stone</th>
            <th class="px-3 py-2">Type</th>
            <th class="px-3 py-2">Carat</th>
            <th class="px-3 py-2">Colour</th>
            <th class="px-3 py-2">Clarity</th>
            <th class="px-3 py-2">Price range</th>
            <th class="px-3 py-2">Item</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(line, i) in lines" :key="i" class="border-t">
            <td class="px-3 py-2 text-gray-500">{{ line.line_number }}</td>
            <td class="px-3 py-2">{{ line.quantity }}</td>
            <td class="px-3 py-2 capitalize">{{ line.stone_type }}</td>
            <td class="px-3 py-2 capitalize">{{ line.item_type }}</td>
            <td class="px-3 py-2">{{ line.min_carat }}–{{ line.max_carat }}</td>
            <td class="px-3 py-2">{{ line.colour_spec || '—' }}</td>
            <td class="px-3 py-2">{{ line.clarity_spec || '—' }}</td>
            <td class="px-3 py-2">{{ line.min_price }}–{{ line.max_price }}</td>
            <td class="px-3 py-2 text-gray-400 text-xs">{{ line._itemLabel || '—' }}</td>
            <td class="px-3 py-2">
              <button @click="removeLine(i)" class="text-red-400 hover:text-red-600 text-xs">✕</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Error -->
    <div v-if="error" class="text-red-500 text-xs p-2 bg-red-50 rounded">{{ error }}</div>

    <!-- Save -->
    <div class="flex justify-end">
      <button @click="save" :disabled="!canSave || saving"
        class="px-6 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-40">
        {{ saving ? 'Saving…' : 'Save Sales Order' }}
      </button>
    </div>

  </div>
</template>