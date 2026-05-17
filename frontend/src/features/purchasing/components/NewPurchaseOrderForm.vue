<script setup lang="ts">
import { ref, computed } from 'vue'
import api from '@/api/axios.js'
import { usePurchaseOrderStore } from '@/features/purchasing/stores/usePurchaseOrderStore.js'

const props = defineProps<{ supplier: any }>()
const emit  = defineEmits<{ (e: 'saved'): void }>()

const poStore = usePurchaseOrderStore()

// ── Header ────────────────────────────────────────────────
const supplierRef  = ref('')
const currency     = ref('USD')
const fxRate       = ref('')
const fxRateDate   = ref('')
const expectedDate = ref('')
const notes        = ref('')
const headerConfirmed = ref(false)

const confirmHeader = () => { headerConfirmed.value = true }

const headerSummary = computed(() => {
  const parts = []
  if (supplierRef.value)  parts.push(`Supplier Ref: ${supplierRef.value}`)
  if (expectedDate.value) parts.push(`Expected: ${expectedDate.value}`)
  parts.push(currency.value)
  if (fxRate.value)       parts.push(`FX: ${fxRate.value}`)
  if (notes.value)        parts.push(`— ${notes.value}`)
  return parts.join('  ·  ')
})

// ── Lines ─────────────────────────────────────────────────
const lines        = ref<any[]>([])
const showLineForm = ref(false)
const editingIndex = ref<number | null>(null)

const emptyLine = () => ({
  description:  '',
  supplier_sku: '',
  quantity:     1,
  unit_cost:    '',
  currency:     'USD',
  fx_rate:      '',
  fx_rate_date: '',
  notes:        '',
})

const lineForm = ref(emptyLine())

const openAddLine = () => {
  editingIndex.value = null
  lineForm.value     = emptyLine()
  showLineForm.value = true
}

const editLine = (index: number) => {
  editingIndex.value = index
  lineForm.value     = { ...lines.value[index] }
  showLineForm.value = true
}

const confirmLine = () => {
  if (editingIndex.value !== null) {
    lines.value[editingIndex.value] = { ...lineForm.value }
  } else {
    lines.value.push({ ...lineForm.value })
  }
  showLineForm.value = false
  editingIndex.value = null
  lineForm.value     = emptyLine()
}

const cancelLine = () => {
  showLineForm.value = false
  editingIndex.value = null
  lineForm.value     = emptyLine()
}

const removeLine = (index: number) => {
  lines.value.splice(index, 1)
}

// ── Line total preview ────────────────────────────────────
const lineTotal = (line: any) => {
  const qty  = Number(line.quantity)  || 0
  const cost = Number(line.unit_cost) || 0
  return (qty * cost).toFixed(2)
}

// ── Save ──────────────────────────────────────────────────
const saving = ref(false)
const error  = ref('')

const canSave = computed(() =>
  lines.value.length > 0 && headerConfirmed.value
)

const save = async () => {
  if (!canSave.value) return
  saving.value = true
  error.value  = ''
  try {
    const po = await poStore.createPO({
      supplier:      props.supplier.bp_id,
      supplier_ref:  supplierRef.value  || '',
      currency:      currency.value,
      fx_rate:       fxRate.value       || null,
      fx_rate_date:  fxRateDate.value   || null,
      expected_date: expectedDate.value || null,
      notes:         notes.value,
    })
    for (const line of lines.value) {
      await api.post(`/purchasing/purchase-orders/${po.id}/add-line/`, {
        description:  line.description,
        supplier_sku: line.supplier_sku,
        quantity:     line.quantity,
        unit_cost:    line.unit_cost,
        currency:     line.currency,
        fx_rate:      line.fx_rate      || null,
        fx_rate_date: line.fx_rate_date || null,
        notes:        line.notes,
      })
    }
    // Recalculate totals after all lines saved
    await api.post(`/purchasing/purchase-orders/${po.id}/recalculate/`)

    const canSave = computed(() =>
      lines.value.length > 0 && headerConfirmed.value && !showLineForm.value
    )

    // Reset
    supplierRef.value  = ''
    currency.value     = 'USD'
    fxRate.value       = ''
    fxRateDate.value   = ''
    expectedDate.value = ''
    notes.value        = ''
    lines.value        = []
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
    <div v-if="headerConfirmed"
      class="flex items-center justify-between bg-gray-100 border border-gray-200 rounded-lg px-4 py-2.5">
      <div class="flex items-center gap-3">
        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">PO Header</span>
        <span class="text-gray-700 text-sm">{{ props.supplier.bp_name }}  ·  {{ headerSummary }}</span>
      </div>
      <button @click="headerConfirmed = false" class="text-xs text-blue-600 hover:underline">Edit</button>
    </div>

    <div v-else class="border border-gray-200 rounded-lg p-4 bg-white space-y-3">
      <p class="font-semibold text-gray-700 text-xs uppercase tracking-wide">PO Header</p>
      <div class="text-sm text-gray-600 mb-1">Supplier: <span class="font-medium text-gray-800">{{ props.supplier.bp_name }}</span></div>
      <div class="grid grid-cols-3 gap-3">
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Supplier Ref</label>
          <input v-model="supplierRef" type="text" placeholder="Their order reference"
            class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Currency</label>
          <select v-model="currency"
            class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400">
            <option>USD</option><option>GBP</option><option>EUR</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Expected Date</label>
          <input v-model="expectedDate" type="date"
            class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">FX Rate</label>
          <input v-model="fxRate" type="number" step="0.0001" placeholder="e.g. 1.2700"
            class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">FX Rate Date</label>
          <input v-model="fxRateDate" type="date"
            class="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400" />
        </div>
        <div>
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

    <!-- ── Lines ── -->
    <div v-if="headerConfirmed" class="border border-gray-200 rounded-lg overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-xs text-gray-600 uppercase">
          <tr>
            <th class="px-3 py-2 text-left">Description</th>
            <th class="px-3 py-2 text-left">Supplier SKU</th>
            <th class="px-3 py-2 text-left">Qty</th>
            <th class="px-3 py-2 text-left">Unit Cost</th>
            <th class="px-3 py-2 text-left">Currency</th>
            <th class="px-3 py-2 text-left">Total</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(line, i) in lines" :key="i">
            <!-- Summary row -->
            <tr v-if="editingIndex !== i" class="border-t hover:bg-gray-50">
              <td class="px-3 py-2">{{ line.description || '—' }}</td>
              <td class="px-3 py-2 text-gray-500">{{ line.supplier_sku || '—' }}</td>
              <td class="px-3 py-2">{{ line.quantity }}</td>
              <td class="px-3 py-2">{{ line.unit_cost }}</td>
              <td class="px-3 py-2">{{ line.currency }}</td>
              <td class="px-3 py-2 font-medium">{{ lineTotal(line) }}</td>
              <td class="px-3 py-2 flex gap-2">
                <button @click="editLine(i)" class="text-blue-400 hover:text-blue-600 text-xs">Edit</button>
                <button @click="removeLine(i)" class="text-red-400 hover:text-red-600 text-xs">✕</button>
              </td>
            </tr>

            <!-- Inline edit row -->
            <tr v-else class="border-t bg-blue-50">
              <td colspan="7" class="px-3 py-3">
                <div class="grid grid-cols-4 gap-2 mb-2">
                  <div class="col-span-2">
                    <label class="block text-xs text-gray-500 mb-1">Description</label>
                    <input v-model="lineForm.description" type="text"
                      class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">Supplier SKU</label>
                    <input v-model="lineForm.supplier_sku" type="text"
                      class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">Qty</label>
                    <input v-model.number="lineForm.quantity" type="number" min="1"
                      class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">Unit Cost</label>
                    <input v-model="lineForm.unit_cost" type="number" step="0.01"
                      class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">Currency</label>
                    <select v-model="lineForm.currency"
                      class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm">
                      <option>USD</option><option>GBP</option><option>EUR</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">FX Rate</label>
                    <input v-model="lineForm.fx_rate" type="number" step="0.0001"
                      class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">FX Rate Date</label>
                    <input v-model="lineForm.fx_rate_date" type="date"
                      class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
                  <div class="col-span-4">
                    <label class="block text-xs text-gray-500 mb-1">Notes</label>
                    <input v-model="lineForm.notes" type="text"
                      class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                  </div>
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
              </td>
            </tr>
          </template>

          <!-- Add line form row -->
          <tr v-if="showLineForm && editingIndex === null" class="border-t bg-blue-50">
            <td colspan="7" class="px-3 py-3">
              <div class="grid grid-cols-4 gap-2 mb-2">
                <div class="col-span-2">
                  <label class="block text-xs text-gray-500 mb-1">Description</label>
                  <input v-model="lineForm.description" type="text"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Supplier SKU</label>
                  <input v-model="lineForm.supplier_sku" type="text"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Qty</label>
                  <input v-model.number="lineForm.quantity" type="number" min="1"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Unit Cost</label>
                  <input v-model="lineForm.unit_cost" type="number" step="0.01"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Currency</label>
                  <select v-model="lineForm.currency"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm">
                    <option>USD</option><option>GBP</option><option>EUR</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">FX Rate</label>
                  <input v-model="lineForm.fx_rate" type="number" step="0.0001"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">FX Rate Date</label>
                  <input v-model="lineForm.fx_rate_date" type="date"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                </div>
                <div class="col-span-4">
                  <label class="block text-xs text-gray-500 mb-1">Notes</label>
                  <input v-model="lineForm.notes" type="text"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
                </div>
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
            </td>
          </tr>
        </tbody>
      </table>

      <div class="px-3 py-2 border-t border-gray-200 bg-gray-50">
        <button v-if="!showLineForm" @click="openAddLine"
          class="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
          + Add Line
        </button>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="text-red-500 text-xs p-2 bg-red-50 rounded">{{ error }}</div>

    <!-- Save -->
    <div v-if="headerConfirmed && lines.length" class="flex justify-end">
      <button @click="save" :disabled="!canSave || saving"
        class="px-6 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-40">
        {{ saving ? 'Saving…' : 'Save Purchase Order' }}
      </button>
    </div>

  </div>
</template>