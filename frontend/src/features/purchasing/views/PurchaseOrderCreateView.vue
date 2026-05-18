<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePurchaseOrderStore } from '@/features/purchasing/stores/usePurchaseOrderStore.js'
import api from '@/api/axios.js'

const router = useRouter()
const store  = usePurchaseOrderStore()

// ── Status badge colours ──────────────────────────────────
const statusColour = (s: string) => ({
  requested:  'bg-slate-100 text-slate-600',
  rfq_sent:   'bg-blue-50 text-blue-700',
  quoted:     'bg-amber-50 text-amber-700',
  on_order:   'bg-indigo-50 text-indigo-700',
}[s] ?? 'bg-gray-100 text-gray-600')

// ── Selected SO lines ─────────────────────────────────────
const selectedLines = ref<any[]>([])

function toggleLine(line: any) {
  const idx = selectedLines.value.findIndex(l => l.sol_id === line.sol_id)
  if (idx === -1) {
    selectedLines.value.push(line)
    // Pre-populate a PO line from the SO line
    poLines.value.push({
      _key:        line.sol_id,
      description: lineLabel(line),
      supplier_sku: line.supplier_sku || '',
      quantity:    line.quantity,
      unit_cost:   '',
      currency:    poForm.value.currency,
      notes:       line.notes || '',
    })
  } else {
    selectedLines.value.splice(idx, 1)
    poLines.value = poLines.value.filter(l => l._key !== line.sol_id)
  }
}

function isSelected(line: any) {
  return selectedLines.value.some(l => l.sol_id === line.sol_id)
}

function lineLabel(line: any) {
  const parts = [line.stone_type]
  if (line.preferred_carat) parts.push(`${line.preferred_carat}ct`)
  if (line.colour_spec)     parts.push(line.colour_spec)
  if (line.clarity_spec)    parts.push(line.clarity_spec)
  return parts.join(' · ')
}

// ── Group SO lines by SO reference ────────────────────────
const groupedSOLines = computed(() => {
  const groups: Record<string, any[]> = {}
  for (const line of store.openSOLines) {
    const key = `${line.so_reference} — ${line.customer_name}`
    if (!groups[key]) groups[key] = []
    groups[key].push(line)
  }
  return groups
})

// ── PO form ───────────────────────────────────────────────
const poForm = ref({
  supplier:      '',
  currency:      'USD',
  fx_rate:       '',
  expected_date: '',
  notes:         '',
})

const poLines = ref<any[]>([])

function addBlankLine() {
  poLines.value.push({
    _key:         Date.now().toString(),
    description:  '',
    supplier_sku: '',
    quantity:     1,
    unit_cost:    '',
    currency:     poForm.value.currency,
    notes:        '',
  })
}

function removePOLine(key: string) {
  poLines.value = poLines.value.filter(l => l._key !== key)
}

// ── Totals ────────────────────────────────────────────────
const poTotal = computed(() =>
  poLines.value.reduce((sum, l) => {
    const cost = parseFloat(l.unit_cost) || 0
    const qty  = parseInt(l.quantity)    || 0
    return sum + cost * qty
  }, 0).toFixed(2)
)

// ── Save ──────────────────────────────────────────────────
const saving = ref(false)
const saveError = ref('')

async function savePO() {
  if (!poForm.value.supplier) {
    saveError.value = 'Please select a supplier.'
    return
  }
  if (!poLines.value.length) {
    saveError.value = 'Please add at least one line.'
    return
  }
  saving.value    = true
  saveError.value = ''
  try {
    // 1. Create PO header
    const po = await store.createPO({
      supplier:      poForm.value.supplier,
      currency:      poForm.value.currency,
      fx_rate:       poForm.value.fx_rate       || null,
      expected_date: poForm.value.expected_date || null,
      notes:         poForm.value.notes,
    })

    // 2. Add lines
    for (const line of poLines.value) {
      await store.addLine(po.id, {
        description:  line.description,
        supplier_sku: line.supplier_sku,
        quantity:     line.quantity,
        unit_cost:    line.unit_cost,
        currency:     line.currency || poForm.value.currency,
        fx_rate:      poForm.value.fx_rate || null,
        notes:        line.notes,
      })
    }

    // 3. Recalculate totals on the header
    await api.post(`/purchasing/purchase-orders/${po.id}/recalculate/`)

    // 4. Link sales orders
    const soIds = [...new Set(selectedLines.value.map(l => l.sales_order))]
    if (soIds.length) {
      await store.linkSalesOrders(po.id, soIds)
    }

    // 4. Navigate to the new PO
    router.push(`/purchase-orders/${po.id}`)
  } catch (e: any) {
    saveError.value = e?.response?.data?.detail ?? 'Failed to create purchase order.'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  store.fetchOpenSOLines()
  store.fetchSuppliers()
})
</script>

<template>
  <div class="p-6 space-y-4">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-gray-800">Create Purchase Order</h1>
        <p class="text-xs text-gray-500 mt-0.5">Select SO lines to fulfil, then build the PO</p>
      </div>
      <button @click="router.back()"
        class="text-xs px-3 py-1.5 border border-gray-300 rounded hover:bg-gray-50">
        ← Back
      </button>
    </div>

    <div class="grid grid-cols-2 gap-4 items-start">

      <!-- ── Left: Open SO Lines ── -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-50 border-b border-gray-200 px-4 py-3">
          <p class="text-sm font-semibold text-gray-700">Open Sales Order Lines</p>
          <p class="text-xs text-gray-500 mt-0.5">Click lines to add them to the PO</p>
        </div>

        <div v-if="store.soLinesLoading" class="p-4 text-sm text-gray-400 italic">Loading…</div>
        <div v-else-if="!store.openSOLines.length" class="p-4 text-sm text-gray-400 italic">
          No open SO lines.
        </div>

        <div v-else class="divide-y divide-gray-100">
          <div v-for="(lines, soRef) in groupedSOLines" :key="soRef">
            <!-- SO group header -->
            <div class="px-4 py-2 bg-gray-50 text-xs font-semibold text-gray-600 uppercase tracking-wide">
              {{ soRef }}
            </div>
            <!-- Lines -->
            <div
              v-for="line in lines" :key="line.sol_id"
              @click="toggleLine(line)"
              :class="[
                'px-4 py-3 cursor-pointer transition-colors',
                isSelected(line)
                  ? 'bg-indigo-50 border-l-4 border-indigo-500'
                  : 'hover:bg-gray-50 border-l-4 border-transparent'
              ]"
            >
              <div class="flex items-start justify-between gap-2">
                <div>
                  <p class="text-sm font-medium text-gray-800">
                    Line {{ line.line_number }} · {{ line.stone_type }}
                    <span v-if="line.item_type === 'certified'"
                      class="ml-1 text-xs bg-violet-100 text-violet-700 px-1.5 py-0.5 rounded">
                      Certified
                    </span>
                  </p>
                  <p class="text-xs text-gray-500 mt-0.5">
                    <span v-if="line.preferred_carat">{{ line.preferred_carat }}ct · </span>
                    <span v-if="line.colour_spec">{{ line.colour_spec }} · </span>
                    <span v-if="line.clarity_spec">{{ line.clarity_spec }} · </span>
                    Qty: {{ line.quantity }}
                  </p>
                  <p v-if="line.min_price || line.max_price" class="text-xs text-gray-400 mt-0.5">
                    Budget: {{ line.min_price ?? '—' }} – {{ line.max_price ?? '—' }} GBP
                  </p>
                </div>
                <div class="flex flex-col items-end gap-1">
                  <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', statusColour(line.status)]">
                    {{ line.status }}
                  </span>
                  <span v-if="line.supplier_name" class="text-xs text-gray-400">
                    {{ line.supplier_name }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Right: PO Builder ── -->
      <div class="space-y-4">

        <!-- PO Header fields -->
        <div class="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
          <p class="text-sm font-semibold text-gray-700">PO Details</p>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-gray-500 mb-1">Supplier <span class="text-red-500">*</span></label>
              <select v-model="poForm.supplier"
                class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm">
                <option value="">— Select supplier —</option>
                <option v-for="s in store.suppliers" :key="s.bp_id" :value="s.bp_id">
                  {{ s.bp_name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Currency</label>
              <select v-model="poForm.currency"
                class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm">
                <option>USD</option>
                <option>GBP</option>
                <option>EUR</option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">FX Rate (to GBP)</label>
              <input v-model="poForm.fx_rate" type="number" step="0.000001" placeholder="e.g. 1.27"
                class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Expected Delivery</label>
              <input v-model="poForm.expected_date" type="date"
                class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
            </div>
          </div>

          <div>
            <label class="block text-xs text-gray-500 mb-1">Notes</label>
            <input v-model="poForm.notes" type="text"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
        </div>

        <!-- PO Lines -->
        <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div class="bg-gray-50 border-b border-gray-200 px-4 py-3 flex items-center justify-between">
            <p class="text-sm font-semibold text-gray-700">Lines</p>
            <button @click="addBlankLine"
              class="text-xs px-2 py-1 border border-gray-300 rounded hover:bg-gray-100">
              + Add Line
            </button>
          </div>

          <div v-if="!poLines.length" class="p-4 text-sm text-gray-400 italic">
            Select SO lines on the left or click + Add Line.
          </div>

          <div v-else class="divide-y divide-gray-100">
            <div v-for="line in poLines" :key="line._key" class="p-3 space-y-2">
              <div class="grid grid-cols-4 gap-2">
                <div class="col-span-2">
                  <label class="block text-xs text-gray-500 mb-1">Description</label>
                  <input v-model="line.description" type="text"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Supplier SKU</label>
                  <input v-model="line.supplier_sku" type="text"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Qty</label>
                  <input v-model.number="line.quantity" type="number" min="1"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
                </div>
              </div>
              <div class="grid grid-cols-4 gap-2">
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Unit Cost</label>
                  <input v-model="line.unit_cost" type="number" step="0.01"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Currency</label>
                  <select v-model="line.currency"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs">
                    <option>USD</option><option>GBP</option><option>EUR</option>
                  </select>
                </div>
                <div class="col-span-2">
                  <label class="block text-xs text-gray-500 mb-1">Notes</label>
                  <input v-model="line.notes" type="text"
                    class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
                </div>
              </div>
              <div class="flex justify-end">
                <button @click="removePOLine(line._key)"
                  class="text-xs text-red-500 hover:text-red-700">
                  Remove
                </button>
              </div>
            </div>
          </div>

          <!-- Total -->
          <div v-if="poLines.length"
            class="px-4 py-2 bg-gray-50 border-t border-gray-200 flex justify-end">
            <p class="text-sm font-semibold text-gray-700">
              Total: {{ poForm.currency }} {{ poTotal }}
            </p>
          </div>
        </div>

        <!-- Selected SO lines summary -->
        <div v-if="selectedLines.length"
          class="bg-indigo-50 border border-indigo-200 rounded-lg px-4 py-3">
          <p class="text-xs font-semibold text-indigo-700 mb-1">Linked SO Lines</p>
          <p v-for="l in selectedLines" :key="l.sol_id" class="text-xs text-indigo-600">
            {{ l.so_reference }} / Line {{ l.line_number }} — {{ l.stone_type }}
          </p>
        </div>

        <!-- Error -->
        <div v-if="saveError" class="bg-red-50 border border-red-200 rounded px-4 py-2 text-sm text-red-600">
          {{ saveError }}
        </div>

        <!-- Save -->
        <div class="flex gap-2">
          <button @click="savePO" :disabled="saving"
            class="px-5 py-2 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 disabled:opacity-40">
            {{ saving ? 'Creating PO…' : 'Create Purchase Order' }}
          </button>
          <button @click="router.back()"
            class="px-4 py-2 border border-gray-300 text-sm rounded hover:bg-gray-50">
            Cancel
          </button>
        </div>

      </div>
    </div>
  </div>
</template>