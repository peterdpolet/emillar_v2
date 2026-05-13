<script setup lang="ts">
import { ref, watch } from 'vue'
import api from '@/api/axios.js'
import { useSalesStore } from '@/features/sales/stores/useSalesStore.js'

const salesStore = useSalesStore()

// ── Header edit ───────────────────────────────────────────
const headerForm = ref({ reference: '', currency: 'GBP', notes: '' })
const headerSaving = ref(false)

watch(() => salesStore.selectedSalesOrder, (order) => {
  if (order) {
    headerForm.value = {
      reference: order.reference || '',
      currency:  order.currency  || 'GBP',
      notes:     order.notes     || '',
    }
  }
}, { immediate: true })

const updateHeader = async () => {
  if (!salesStore.selectedSalesOrder) return
  headerSaving.value = true
  try {
    await api.patch(`/sales/orders/${salesStore.selectedSalesOrder.so_id}/`, headerForm.value)
    await salesStore.fetchSalesOrders()
  } finally {
    headerSaving.value = false
  }
}

// ── Line editing ──────────────────────────────────────────
const editingLine  = ref<string | null>(null)
const editForm     = ref<any>({})

const startEdit = (line: any) => {
  editingLine.value = line.sol_id
  editForm.value    = { ...line }
}

const cancelEdit = () => {
  editingLine.value = null
  editForm.value    = {}
}

const saveEdit = async (line: any) => {
  try {
    await api.patch(`/sales/lines/${line.sol_id}/`, editForm.value)
    await salesStore.fetchSalesOrderLines()
    cancelEdit()
  } catch (e) {
    console.error(e)
  }
}

const deleteLine = async (line: any) => {
  if (!confirm(`Delete line ${line.line_number}?`)) return
  try {
    await api.delete(`/sales/lines/${line.sol_id}/`)
    await salesStore.fetchSalesOrderLines()
  } catch (e) {
    console.error(e)
  }
}

// ── Add line ──────────────────────────────────────────────
const showAddLine = ref(false)
const newLine = ref({
  stone_type: 'diamond', item_type: 'certified',
  quantity: 1,
  min_size: '', max_size: '', min_carat: '', max_carat: '',
  colour_spec: '', clarity_spec: '',
  min_price: '', max_price: '',
  certificate_type: '', certificate_number: '',
  notes: '',
})
const addLineSaving = ref(false)

const addLine = async () => {
  if (!salesStore.selectedSalesOrder) return
  addLineSaving.value = true
  try {
    const nextNum = (salesStore.salesOrderLines.length || 0) + 1
    await api.post('/sales/lines/', {
      sales_order:        salesStore.selectedSalesOrder.so_id,
      line_number:        nextNum,
      stone_type:         newLine.value.stone_type,
      item_type:          newLine.value.item_type,
      status:             'requested',
      min_size:           newLine.value.min_size    || null,
      max_size:           newLine.value.max_size    || null,
      min_carat:          newLine.value.min_carat   || null,
      max_carat:          newLine.value.max_carat   || null,
      colour_spec:        newLine.value.colour_spec        || '',
      clarity_spec:       newLine.value.clarity_spec       || '',
      min_price:          newLine.value.min_price   || null,
      max_price:          newLine.value.max_price   || null,
      certificate_type:   newLine.value.certificate_type   || '',
      certificate_number: newLine.value.certificate_number || '',
      notes:              newLine.value.notes               || '',
    })
    await salesStore.fetchSalesOrderLines()
    showAddLine.value = false
    newLine.value = {
      stone_type: 'diamond', item_type: 'certified',
      quantity:1,
      min_size: '', max_size: '', min_carat: '', max_carat: '',
      colour_spec: '', clarity_spec: '',
      min_price: '', max_price: '',
      certificate_type: '', certificate_number: '',
      notes: '',
    }
  } catch (e) {
    console.error(e)
  } finally {
    addLineSaving.value = false
  }
}

const statusColour = (status: string) => {
  const map: Record<string, string> = {
    requested:            'bg-gray-100 text-gray-600',
    rfq_sent:             'bg-blue-100 text-blue-700',
    quoted:               'bg-yellow-100 text-yellow-700',
    on_order:             'bg-purple-100 text-purple-700',
    on_approval:          'bg-orange-100 text-orange-700',
    confirmed:            'bg-green-100 text-green-700',
    returned:             'bg-red-100 text-red-600',
    returned_to_supplier: 'bg-red-100 text-red-600',
    cancelled:            'bg-gray-200 text-gray-500',
  }
  return map[status] ?? 'bg-gray-100 text-gray-600'
}

const fmt = (val: any) => (val === null || val === undefined || val === '') ? '—' : val
const canEdit = (line: any) => line.status === 'requested'
</script>

<template>
  <div class="space-y-4 text-sm">

    <!-- SO Header edit -->
    <div class="border border-gray-200 rounded-lg p-3 bg-white">
      <p class="font-semibold text-gray-700 mb-2">Order Header</p>
      <div class="grid grid-cols-3 gap-3">
        <div>
          <label class="block text-xs text-gray-500 mb-1">Reference</label>
          <input v-model="headerForm.reference" type="text"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Currency</label>
          <select v-model="headerForm.currency"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm">
            <option>GBP</option>
            <option>USD</option>
            <option>EUR</option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Notes</label>
          <input v-model="headerForm.notes" type="text"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
        </div>
      </div>
      <div class="flex justify-end mt-2">
        <button @click="updateHeader" :disabled="headerSaving"
          class="px-4 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-40">
          {{ headerSaving ? 'Saving…' : 'Update Header' }}
        </button>
      </div>
    </div>

    <!-- Lines table -->
    <div v-if="salesStore.linesLoading" class="text-sm text-gray-500 p-4">Loading lines…</div>
    <div v-else-if="!salesStore.salesOrderLines.length" class="text-sm text-gray-400 italic p-4">
      No lines on this order.
    </div>
    <div v-else class="border border-gray-200 rounded-lg overflow-auto">
      <table class="w-full text-sm text-left">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50">
          <tr>
            <th class="px-3 py-2">#</th>
            <th class="px-3 py-2">Qty</th>
            <th class="px-3 py-2">Stone</th>
            <th class="px-3 py-2">Type</th>
            <th class="px-3 py-2">Status</th>
            <th class="px-3 py-2">Carat</th>
            <th class="px-3 py-2">Colour</th>
            <th class="px-3 py-2">Clarity</th>
            <th class="px-3 py-2">Price range</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="line in salesStore.salesOrderLines" :key="line.sol_id">
            <!-- View row -->
            <tr v-if="editingLine !== line.sol_id" class="border-t hover:bg-gray-50">
              <td class="px-3 py-2 text-gray-500">{{ line.line_number }}</td>
              <td class="px-3 py-2">{{ line.quantity }}</td>
              <td class="px-3 py-2 capitalize">{{ line.stone_type }}</td>
              <td class="px-3 py-2 capitalize">{{ line.item_type }}</td>
              <td class="px-3 py-2">
                <span :class="statusColour(line.status)"
                  class="px-2 py-0.5 rounded-full text-xs font-medium capitalize">
                  {{ line.status.replace(/_/g, ' ') }}
                </span>
              </td>
              <td class="px-3 py-2">{{ fmt(line.min_carat) }}–{{ fmt(line.max_carat) }}</td>
              <td class="px-3 py-2">{{ fmt(line.colour_spec) }}</td>
              <td class="px-3 py-2">{{ fmt(line.clarity_spec) }}</td>
              <td class="px-3 py-2">{{ fmt(line.min_price) }}–{{ fmt(line.max_price) }}</td>
              <td class="px-3 py-2 flex gap-2">
                <button v-if="canEdit(line)" @click="startEdit(line)"
                  class="text-blue-500 hover:text-blue-700 text-xs">Edit</button>
                <button v-if="canEdit(line)" @click="deleteLine(line)"
                  class="text-red-400 hover:text-red-600 text-xs">Delete</button>
              </td>
            </tr>
            <!-- Edit row -->
            <tr v-else class="border-t bg-blue-50">
              <td class="px-3 py-2 text-gray-500">{{ line.line_number }}</td>
              <td class="px-3 py-2">
                <input v-model="editForm.quantity" type="number" min="1"
                class="w-14 border border-gray-300 rounded px-1 py-1 text-xs" />
            </td>  
              <td class="px-3 py-2">
                <select v-model="editForm.stone_type"
                  class="border border-gray-300 rounded px-1 py-1 text-xs w-24">
                  <option value="diamond">Diamond</option>
                  <option value="ruby">Ruby</option>
                  <option value="sapphire">Sapphire</option>
                  <option value="emerald">Emerald</option>
                  <option value="pearl">Pearl</option>
                  <option value="other">Other</option>
                </select>
              </td>
              <td class="px-3 py-2">
                <select v-model="editForm.item_type"
                  class="border border-gray-300 rounded px-1 py-1 text-xs w-24">
                  <option value="certified">Certified</option>
                  <option value="uncertified">Uncertified</option>
                </select>
              </td>
              <td class="px-3 py-2">
                <span :class="statusColour(line.status)"
                  class="px-2 py-0.5 rounded-full text-xs font-medium capitalize">
                  {{ line.status.replace(/_/g, ' ') }}
                </span>
              </td>
              <td class="px-3 py-2">
                <div class="flex gap-1">
                  <input v-model="editForm.min_carat" type="number" step="0.001" placeholder="min"
                    class="w-14 border border-gray-300 rounded px-1 py-1 text-xs" />
                  <input v-model="editForm.max_carat" type="number" step="0.001" placeholder="max"
                    class="w-14 border border-gray-300 rounded px-1 py-1 text-xs" />
                </div>
              </td>
              <td class="px-3 py-2">
                <input v-model="editForm.colour_spec" type="text"
                  class="w-16 border border-gray-300 rounded px-1 py-1 text-xs" />
              </td>
              <td class="px-3 py-2">
                <input v-model="editForm.clarity_spec" type="text"
                  class="w-16 border border-gray-300 rounded px-1 py-1 text-xs" />
              </td>
              <td class="px-3 py-2">
                <div class="flex gap-1">
                  <input v-model="editForm.min_price" type="number" step="0.01" placeholder="min"
                    class="w-16 border border-gray-300 rounded px-1 py-1 text-xs" />
                  <input v-model="editForm.max_price" type="number" step="0.01" placeholder="max"
                    class="w-16 border border-gray-300 rounded px-1 py-1 text-xs" />
                </div>
              </td>
              <td class="px-3 py-2 flex gap-2">
                <button @click="saveEdit(line)"
                  class="text-green-600 hover:text-green-800 text-xs font-medium">Save</button>
                <button @click="cancelEdit"
                  class="text-gray-400 hover:text-gray-600 text-xs">Cancel</button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Add line -->
    <div>
      <button v-if="!showAddLine" @click="showAddLine = true"
        class="px-4 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700">
        + Add Line
      </button>
      <div v-else class="border border-gray-200 rounded-lg p-3 bg-white space-y-3">
        <p class="font-semibold text-gray-700 text-xs uppercase">New Line</p>
        <div class="grid grid-cols-5 gap-2">

          <div>
            <label class="block text-xs text-gray-500 mb-1">Qty</label>
            <input v-model="newLine.quantity" type="number" min="1" value="1"
                class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
         
          <div>
            <label class="block text-xs text-gray-500 mb-1">Stone Type</label>
            <select v-model="newLine.stone_type"
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
            <select v-model="newLine.item_type"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm">
              <option value="certified">Certified</option>
              <option value="uncertified">Uncertified</option>
            </select>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Colour</label>
            <input v-model="newLine.colour_spec" type="text"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Clarity</label>
            <input v-model="newLine.clarity_spec" type="text"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
        </div>
        <div class="grid grid-cols-3 gap-2">
          <div>
            <label class="block text-xs text-gray-500 mb-1">Carat (min–max)</label>
            <div class="flex gap-1">
              <input v-model="newLine.min_carat" type="number" step="0.001" placeholder="min"
                class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
              <input v-model="newLine.max_carat" type="number" step="0.001" placeholder="max"
                class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
            </div>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Price range (min–max)</label>
            <div class="flex gap-1">
              <input v-model="newLine.min_price" type="number" step="0.01" placeholder="min"
                class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
              <input v-model="newLine.max_price" type="number" step="0.01" placeholder="max"
                class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
            </div>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Notes</label>
            <input v-model="newLine.notes" type="text"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
        </div>
        <div class="flex gap-2">
          <button @click="addLine" :disabled="addLineSaving"
            class="px-4 py-1.5 bg-green-600 text-white text-xs rounded hover:bg-green-700 disabled:opacity-40">
            {{ addLineSaving ? 'Saving…' : 'Save Line' }}
          </button>
          <button @click="showAddLine = false"
            class="px-4 py-1.5 bg-gray-200 text-gray-700 text-xs rounded hover:bg-gray-300">
            Cancel
          </button>
        </div>
      </div>
    </div>

  </div>
</template>