<script setup lang="ts">
import { ref, computed } from 'vue'
import api from '@/api/axios.js'
import { useSalesStore } from '@/features/sales/stores/useSalesStore.js'
import InventorySearchModal from './InventorySearchModal.vue'

const salesStore = useSalesStore()
const emit = defineEmits<{ (e: 'saved'): void }>()

// ── Header ────────────────────────────────────────────────
const reference     = ref('')
const currency      = ref('GBP')
const notes         = ref('')
const customerPoRef = ref('')
const requiredBy    = ref('')
const headerConfirmed = ref(false)

const confirmHeader = () => {
  headerConfirmed.value = true
}

const headerSummary = computed(() => {
  const parts = []
  if (customerPoRef.value) parts.push(`PO: ${customerPoRef.value}`)
  if (requiredBy.value)    parts.push(`Required: ${requiredBy.value}`)
  parts.push(currency.value)
  if (notes.value)         parts.push(`— ${notes.value}`)
  return parts.join('  ·  ')
})

// ── Line builder ──────────────────────────────────────────
const showLineForm  = ref(false)
const editingIndex  = ref<number | null>(null)

const emptyLine = () => ({
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
  _itemLabel:         null as string | null,
})

const lineForm = ref(emptyLine())
const lines    = ref<any[]>([])

// ── Inventory search ──────────────────────────────────────
const itemSearch    = ref('')
const itemResults   = ref<any[]>([])
const itemSearching = ref(false)
const selectedItem  = ref<any>(null)
const showInventoryModal = ref(false)

let searchTimeout: any = null
const onItemSearch = () => {
  clearTimeout(searchTimeout)
  if (!itemSearch.value || itemSearch.value.length < 2) { itemResults.value = []; return }
  searchTimeout = setTimeout(async () => {
    itemSearching.value = true
    try {
      const { data } = await api.get('/inventory/items/', {
        params: { search: itemSearch.value, page_size: 10 }
      })
      itemResults.value = data.results ?? data
    } finally { itemSearching.value = false }
  }, 300)
}

const selectItem = (item: any) => {
  selectedItem.value            = item
  lineForm.value.inventory_item = item.id
  itemSearch.value              = `${item.sku} — ${item.name}`
  itemResults.value             = []
}

const clearItem = () => {
  selectedItem.value            = null
  lineForm.value.inventory_item = null
  itemSearch.value              = ''
}

// ── Line actions ──────────────────────────────────────────
const openAddLine = () => {
  editingIndex.value = null
  lineForm.value     = emptyLine()
  clearItem()
  showLineForm.value = true
}

const editLine = (index: number) => {
  editingIndex.value = index
  const l = lines.value[index]
  lineForm.value = { ...l }
  if (l._itemLabel) itemSearch.value = l._itemLabel
  showLineForm.value = true
}

const confirmLine = () => {
  const entry = {
    ...lineForm.value,
    _itemLabel: selectedItem.value
      ? `${selectedItem.value.sku} — ${selectedItem.value.name}`
      : lineForm.value._itemLabel,
  }
  if (editingIndex.value !== null) {
    lines.value[editingIndex.value] = { ...entry, line_number: editingIndex.value + 1 }
  } else {
    lines.value.push({ ...entry, line_number: lines.value.length + 1 })
  }
  showLineForm.value = false
  editingIndex.value = null
  lineForm.value     = emptyLine()
  clearItem()
}

const cancelLine = () => {
  showLineForm.value = false
  editingIndex.value = null
  lineForm.value     = emptyLine()
  clearItem()
}

const removeLine = (index: number) => {
  lines.value.splice(index, 1)
  lines.value.forEach((l, i) => l.line_number = i + 1)
}

// ── Save ──────────────────────────────────────────────────
const saving = ref(false)
const error  = ref('')

const canSave = computed(() =>
  lines.value.length > 0 && salesStore.selectedCustomer && headerConfirmed.value
)

const save = async () => {
  if (!canSave.value) return
  saving.value = true
  error.value  = ''
  try {
    const { data: order } = await api.post('/sales/orders/', {
      customer:        salesStore.selectedCustomer!.bp_id,
      reference:       reference.value || null,
      currency:        currency.value,
      notes:           notes.value,
      customer_po_ref: customerPoRef.value || '',
      required_by:     requiredBy.value || null,
    })
    for (const line of lines.value) {
      await api.post('/sales/lines/', {
        sales_order:        order.so_id,
        line_number:        line.line_number,
        quantity:           line.quantity,
        stone_type:         line.stone_type,
        item_type:          line.item_type,
        status:             'requested',
        min_size:           line.min_size           || null,
        max_size:           line.max_size           || null,
        min_carat:          line.min_carat          || null,
        max_carat:          line.max_carat          || null,
        colour_spec:        line.colour_spec        || '',
        clarity_spec:       line.clarity_spec       || '',
        min_price:          line.min_price          || null,
        max_price:          line.max_price          || null,
        certificate_type:   line.certificate_type   || '',
        certificate_number: line.certificate_number || '',
        notes:              line.notes              || '',
        inventory_item:     line.inventory_item     || null,
      })
    }
    await salesStore.fetchSalesOrders()
    reference.value     = ''
    currency.value      = 'GBP'
    notes.value         = ''
    customerPoRef.value = ''
    requiredBy.value    = ''
    lines.value         = []
    headerConfirmed.value = false
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
  <div class="space-y-3 text-sm">

    <!-- ── Header ── -->
    <!-- Collapsed summary bar -->
    <div v-if="headerConfirmed"
      class="flex items-center justify-between bg-gray-100 border border-gray-200 rounded-lg px-4 py-2.5">
      <div class="flex items-center gap-3">
        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Order Header</span>
        <span class="text-gray-700 text-sm">{{ headerSummary }}</span>
      </div>
      <button @click="headerConfirmed = false"
        class="text-xs text-blue-600 hover:underline">Edit</button>
    </div>

    <!-- Expanded header form -->
    <div v-else class="border border-gray-200 rounded-lg p-4 bg-white space-y-3">
      <p class="font-semibold text-gray-700 text-xs uppercase tracking-wide">Order Header</p>
      <div class="grid grid-cols-3 gap-3">
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Reference</label>
          <input v-model="reference" type="text" placeholder="Auto-generated if blank"
            class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Customer PO Ref</label>
          <input v-model="customerPoRef" type="text" placeholder="Customer's own PO number"
            class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Required By</label>
          <input v-model="requiredBy" type="date"
            class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Currency</label>
          <select v-model="currency"
            class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400">
            <option>GBP</option><option>USD</option><option>EUR</option>
          </select>
        </div>
        <div class="col-span-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Notes</label>
          <input v-model="notes" type="text"
            class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
        </div>
      </div>
      <div class="flex justify-end">
        <button @click="confirmHeader"
          class="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
          Confirm Header →
        </button>
      </div>
    </div>

    <!-- ── Lines ── (only show once header confirmed) -->
    <div v-if="headerConfirmed" class="border border-gray-200 rounded-lg overflow-hidden">

      <!-- Lines table -->
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-xs text-gray-600 uppercase">
          <tr>
            <th class="px-3 py-2 text-left">#</th>
            <th class="px-3 py-2 text-left">Qty</th>
            <th class="px-3 py-2 text-left">Stone</th>
            <th class="px-3 py-2 text-left">Type</th>
            <th class="px-3 py-2 text-left">Carat</th>
            <th class="px-3 py-2 text-left">Colour</th>
            <th class="px-3 py-2 text-left">Clarity</th>
            <th class="px-3 py-2 text-left">Price range</th>
            <th class="px-3 py-2 text-left">Item</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(line, i) in lines" :key="i">
            <!-- Summary row -->
            <tr v-if="editingIndex !== i" class="border-t hover:bg-gray-50">
              <td class="px-3 py-2 text-gray-500">{{ line.line_number }}</td>
              <td class="px-3 py-2">{{ line.quantity }}</td>
              <td class="px-3 py-2 capitalize">{{ line.stone_type }}</td>
              <td class="px-3 py-2 capitalize">{{ line.item_type }}</td>
              <td class="px-3 py-2">{{ line.min_carat || '—' }}–{{ line.max_carat || '—' }}</td>
              <td class="px-3 py-2">{{ line.colour_spec || '—' }}</td>
              <td class="px-3 py-2">{{ line.clarity_spec || '—' }}</td>
              <td class="px-3 py-2">{{ line.min_price || '—' }}–{{ line.max_price || '—' }}</td>
              <td class="px-3 py-2 text-gray-400 text-xs">{{ line._itemLabel || '—' }}</td>
              <td class="px-3 py-2 flex gap-2">
                <button @click="editLine(i)" class="text-blue-400 hover:text-blue-600 text-xs">Edit</button>
                <button @click="removeLine(i)" class="text-red-400 hover:text-red-600 text-xs">✕</button>
              </td>
            </tr>

            <!-- Inline edit form row -->
            <tr v-else class="border-t bg-blue-50">
              <td colspan="10" class="px-3 py-3">
                <div class="space-y-3">
                  <div class="grid grid-cols-5 gap-2">
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Qty</label>
                      <input v-model.number="lineForm.quantity" type="number" min="1"
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
                      <label class="block text-xs text-gray-500 mb-1">Colour</label>
                      <input v-model="lineForm.colour_spec" type="text"
                        class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Clarity</label>
                      <input v-model="lineForm.clarity_spec" type="text"
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
                          <option>GIA</option><option>IGI</option>
                          <option>HRD</option><option>AGS</option>
                        </select>
                        <input v-model="lineForm.certificate_number" type="text" placeholder="number"
                          class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center gap-3">
                    <button type="button" @click="showInventoryModal = true"
                      class="px-3 py-1.5 border border-gray-300 rounded text-sm text-gray-600 hover:bg-gray-50">
                      {{ selectedItem ? `${selectedItem.sku} — ${selectedItem.name}` : 'Browse Inventory…' }}
                    </button>
                    <button v-if="selectedItem" @click="clearItem"
                      class="text-xs text-red-500 hover:underline">Clear</button>
                  </div>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">Line Notes</label>
                    <input v-model="lineForm.notes" type="text"
                      class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                  <div class="flex gap-2">
                    <button @click="confirmLine"
                      class="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
                      Confirm Line
                    </button>
                    <button @click="cancelLine"
                      class="px-4 py-1.5 border border-gray-300 text-sm rounded hover:bg-gray-50">
                      Cancel
                    </button>
                  </div>
                </div>
              </td>
            </tr>
          </template>

          <!-- Add line form row -->
          <tr v-if="showLineForm && editingIndex === null" class="border-t bg-blue-50">
            <td colspan="10" class="px-3 py-3">
              <div class="space-y-3">
                <div class="grid grid-cols-5 gap-2">
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">Qty</label>
                    <input v-model.number="lineForm.quantity" type="number" min="1"
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
                    <label class="block text-xs text-gray-500 mb-1">Colour</label>
                    <input v-model="lineForm.colour_spec" type="text"
                      class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">Clarity</label>
                    <input v-model="lineForm.clarity_spec" type="text"
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
                        <option>GIA</option><option>IGI</option>
                        <option>HRD</option><option>AGS</option>
                      </select>
                      <input v-model="lineForm.certificate_number" type="text" placeholder="number"
                        class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                    </div>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <button type="button" @click="showInventoryModal = true"
                    class="px-3 py-1.5 border border-gray-300 rounded text-sm text-gray-600 hover:bg-gray-50">
                    {{ selectedItem ? `${selectedItem.sku} — ${selectedItem.name}` : 'Browse Inventory…' }}
                  </button>
                  <button v-if="selectedItem" @click="clearItem"
                    class="text-xs text-red-500 hover:underline">Clear</button>
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Line Notes</label>
                  <input v-model="lineForm.notes" type="text"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                </div>
                <div class="flex gap-2">
                  <button @click="confirmLine"
                    class="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
                    Confirm Line
                  </button>
                  <button @click="cancelLine"
                    class="px-4 py-1.5 border border-gray-300 text-sm rounded hover:bg-gray-50">
                    Cancel
                  </button>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Add Line button -->
      <div class="px-3 py-2 border-t border-gray-200 bg-gray-50">
        <button v-if="!showLineForm" @click="openAddLine"
          class="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
          + Add Line
        </button>
      </div>
    </div>

    <!-- Inventory modal -->
    <InventorySearchModal
      v-if="showInventoryModal"
      @select="(item) => { selectItem(item); showInventoryModal = false }"
      @close="showInventoryModal = false" />

    <!-- Error -->
    <div v-if="error" class="text-red-500 text-xs p-2 bg-red-50 rounded">{{ error }}</div>

    <!-- Save -->
    <div v-if="headerConfirmed && lines.length" class="flex justify-end">
      <button @click="save" :disabled="!canSave || saving"
        class="px-6 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-40">
        {{ saving ? 'Saving…' : 'Save Sales Order' }}
      </button>
    </div>

  </div>
</template>