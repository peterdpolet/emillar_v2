<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/axios.js'

const route  = useRoute()
const router = useRouter()
const poId   = route.params.id as string

// ── PO ───────────────────────────────────────────────────
const po        = ref<any>(null)
const poLoading = ref(true)

const fetchPO = async () => {
  const { data } = await api.get(`/purchasing/purchase-orders/${poId}/`)
  po.value = data
  poLoading.value = false
}

// ── GRN ──────────────────────────────────────────────────
const grns            = ref<any[]>([])
const selectedGrn     = ref<any>(null)
const showGrnForm     = ref(false)
const grnForm         = ref({ delivery_ref: '', received_date: '', notes: '' })
const grnLineForm     = ref({ po_line: '', quantity_received: 1, discrepancy: 'none', discrepancy_note: '' })
const showGrnLineForm = ref(false)
const grnSaving       = ref(false)

const fetchGrns = async () => {
  const { data } = await api.get('/purchasing/goods-receipts/', {
    params: { purchase_order: poId }
  })
  grns.value = data.results ?? data
  if (grns.value.length && !selectedGrn.value) {
    selectedGrn.value = grns.value[0]
  }
}

const saveGrn = async () => {
  grnSaving.value = true
  try {
    const { data } = await api.post('/purchasing/goods-receipts/', {
      purchase_order: poId,
      ...grnForm.value,
      received_date: grnForm.value.received_date || new Date().toISOString().split('T')[0]
    })
    await fetchGrns()
    selectedGrn.value = grns.value.find((g: any) => g.id === data.id) || data
    showGrnForm.value = false
    grnForm.value = { delivery_ref: '', received_date: '', notes: '' }
  } finally {
    grnSaving.value = false
  }
}

const addGrnLine = async () => {
  if (!selectedGrn.value || !grnLineForm.value.po_line) return
  await api.post(`/purchasing/goods-receipts/${selectedGrn.value.id}/add-line/`, grnLineForm.value)
  await fetchGrns()
  selectedGrn.value = grns.value.find((g: any) => g.id === selectedGrn.value.id)
  showGrnLineForm.value = false
  grnLineForm.value = { po_line: '', quantity_received: 1, discrepancy: 'none', discrepancy_note: '' }
}

// ── Invoice ───────────────────────────────────────────────
const invoices        = ref<any[]>([])
const selectedInvoice = ref<any>(null)
const showInvoiceForm = ref(false)
const invoiceForm     = ref({ invoice_number: '', invoice_date: '', currency: 'GBP', fx_rate: '1.0', notes: '' })
const invLineForm     = ref({ description: '', quantity: 1, unit_price: '', currency: 'GBP', fx_rate: '1.0', po_line: '' })
const showInvLineForm = ref(false)
const invoiceSaving   = ref(false)
const matchRunning    = ref(false)

const fetchInvoices = async () => {
  const { data } = await api.get('/purchasing/invoices/', {
    params: { purchase_order: poId }
  })
  invoices.value = data.results ?? data
  if (invoices.value.length) {
    if (!selectedInvoice.value) {
      selectedInvoice.value = invoices.value[0]
    } else {
      // Re-sync selected invoice from fresh data
      const refreshed = invoices.value.find((i: any) => i.id === selectedInvoice.value.id)
      if (refreshed) selectedInvoice.value = refreshed
    }
  }
}

const fetchSelectedInvoice = async (id: string) => {
  const { data } = await api.get(`/purchasing/invoices/${id}/`)
  selectedInvoice.value = data
}

const saveInvoice = async () => {
  invoiceSaving.value = true
  try {
    const { data } = await api.post('/purchasing/invoices/', {
      purchase_order: poId,
      ...invoiceForm.value,
      invoice_date: invoiceForm.value.invoice_date || new Date().toISOString().split('T')[0]
    })
    await fetchInvoices()
    selectedInvoice.value = invoices.value.find((i: any) => i.id === data.id) || data
    showInvoiceForm.value = false
    invoiceForm.value = { invoice_number: '', invoice_date: '', currency: 'GBP', fx_rate: '1.0', notes: '' }
  } finally {
    invoiceSaving.value = false
  }
}

const addInvLine = async () => {
  if (!selectedInvoice.value) return
  const currentId = selectedInvoice.value.id
  await api.post(`/purchasing/invoices/${currentId}/add_line/`, invLineForm.value)
  await fetchSelectedInvoice(currentId)
  showInvLineForm.value = false
  invLineForm.value = { description: '', quantity: 1, unit_price: '', currency: 'GBP', fx_rate: '1.0', po_line: '' }
}

const runMatch = async () => {
  if (!selectedInvoice.value) return
  matchRunning.value = true
  try {
    const { data } = await api.post(`/purchasing/invoices/${selectedInvoice.value.id}/run_match/`)
    selectedInvoice.value = data
  } finally {
    matchRunning.value = false
  }
}

// ── Drag and drop ─────────────────────────────────────────
const draggedItem = ref<any>(null)
const draggedType = ref<string>('')

const onDragStart = (item: any, type: string) => {
  draggedItem.value = item
  draggedType.value = type
}

const onDropOnPoLine = async (poLine: any) => {
  if (!draggedItem.value) return

  if (draggedType.value === 'grn') {
    const currentGrnId = selectedGrn.value.id
    await api.patch(`/purchasing/goods-receipts/${currentGrnId}/update-line/${draggedItem.value.id}/`, {
      po_line: poLine.id
    })
    await fetchGrns()
    selectedGrn.value = grns.value.find((g: any) => g.id === currentGrnId)

  } else if (draggedType.value === 'inv') {
    const currentInvoiceId = selectedInvoice.value.id
    await api.patch(`/purchasing/invoices/${currentInvoiceId}/lines/${draggedItem.value.id}/`, {
      po_line: poLine.id
    })
    await fetchSelectedInvoice(currentInvoiceId)
  }

  draggedItem.value = null
  draggedType.value = ''
}

// ── Match status helpers ──────────────────────────────────
const matchColour = (status: string) => {
  const map: Record<string, string> = {
    matched:        'bg-green-100 text-green-700 border-green-200',
    price_variance: 'bg-amber-100 text-amber-700 border-amber-200',
    qty_variance:   'bg-orange-100 text-orange-700 border-orange-200',
    no_grn:         'bg-red-100 text-red-600 border-red-200',
    disputed:       'bg-red-100 text-red-700 border-red-200',
    unmatched:      'bg-gray-100 text-gray-500 border-gray-200',
  }
  return map[status] ?? 'bg-gray-100 text-gray-500 border-gray-200'
}

const matchIcon = (status: string) => {
  const map: Record<string, string> = {
    matched:        '✓',
    price_variance: '⚠',
    qty_variance:   '⚠',
    no_grn:         '✗',
    disputed:       '✗',
    unmatched:      '○',
  }
  return map[status] ?? '○'
}

// ── GRN line for a given PO line ─────────────────────────
const grnLineForPoLine = (poLineId: string) => {
  if (!selectedGrn.value?.lines) return null
  return selectedGrn.value.lines.find((l: any) => l.po_line === poLineId) || null
}

// ── Invoice line for a given PO line ─────────────────────
const invLineForPoLine = (poLineId: string) => {
  if (!selectedInvoice.value?.lines) return null
  return selectedInvoice.value.lines.find((l: any) =>
    String(l.po_line) === String(poLineId)
  ) || null
}

// ── Unmatched lines ───────────────────────────────────────
const unmatchedGrnLines = computed(() => {
  if (!selectedGrn.value?.lines) return []
  return selectedGrn.value.lines.filter((l: any) => !l.po_line)
})

const unmatchedInvLines = computed(() => {
  if (!selectedInvoice.value?.lines) return []
  return selectedInvoice.value.lines.filter((l: any) => !l.po_line)
})

const fmt = (v: any) => (v === null || v === undefined || v === '') ? '—' : v

onMounted(async () => {
  await fetchPO()
  await fetchGrns()
  await fetchInvoices()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">

    <!-- ── Top bar ── -->
    <div class="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <span class="font-bold text-gray-800">Ewan Millar Ltd</span>
        <span class="text-gray-300">|</span>
        <span class="text-sm font-semibold text-gray-600">Three-Way Match</span>
        <span class="text-gray-300">|</span>
        <span v-if="po" class="text-sm text-gray-700">
          {{ po.supplier_name }}
          <span v-if="po.reference" class="ml-2 text-gray-500">· {{ po.reference }}</span>
          <span class="ml-2 text-gray-500">· {{ po.currency }}</span>
          <span v-if="po.expected_date" class="ml-2 text-gray-500">· Expected {{ po.expected_date }}</span>
        </span>
      </div>
      <button @click="router.back()"
        class="px-4 py-1.5 text-sm text-gray-600 border border-gray-300 rounded hover:bg-gray-50">
        ✕ Close
      </button>
    </div>

    <!-- ── Loading ── -->
    <div v-if="poLoading" class="flex-1 flex items-center justify-center text-gray-400">
      Loading…
    </div>

    <div v-else class="flex-1 flex flex-col overflow-hidden">

      <!-- ── Three columns ── -->
      <div class="flex-1 grid grid-cols-3 gap-0 overflow-auto border-b border-gray-200">

        <!-- ── Column 1: PO Lines ── -->
        <div class="border-r border-gray-200 flex flex-col">
          <div class="bg-gray-50 border-b border-gray-200 px-4 py-2">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Purchase Order</p>
          </div>

          <!-- PO line rows -->
          <div class="flex-1 overflow-auto">
            <div v-for="line in po.lines" :key="line.id"
              class="border-b border-gray-100 px-4 py-3 bg-white"
              :class="{ 'bg-blue-50': draggedItem }"
              @dragover.prevent
              @drop="onDropOnPoLine(line)">
              <div class="flex items-start justify-between gap-2">
                <div>
                  <p class="text-xs text-gray-400 mb-0.5">Line {{ line.id?.slice(-4) }}</p>
                  <p class="text-sm font-medium text-gray-800">{{ line.description || line.item_name || '—' }}</p>
                  <p class="text-xs text-gray-500 mt-0.5">
                    SKU: {{ line.supplier_sku || line.item_sku || '—' }}
                    · Qty: {{ line.quantity }}
                    · {{ line.currency }} {{ line.unit_cost }}
                  </p>
                </div>
                <div class="text-right text-xs text-gray-500 whitespace-nowrap">
                  <span class="font-medium text-gray-700">{{ line.currency }} {{ line.line_total }}</span>
                </div>
              </div>
            </div>

            <!-- Drop zone hint when dragging -->
            <div v-if="draggedItem"
              class="mx-4 my-3 border-2 border-dashed border-blue-300 rounded-lg p-3 text-center text-xs text-blue-400">
              Drop here to link to a PO line
            </div>
          </div>
        </div>

        <!-- ── Column 2: GRN ── -->
        <div class="border-r border-gray-200 flex flex-col">
          <div class="bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center justify-between">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Goods Receipt</p>
            <div class="flex items-center gap-2">

              <select v-if="grns.length"
                :value="selectedGrn?.id"
                @change="selectedGrn = grns.find((g: any) => g.id === ($event.target as HTMLSelectElement).value)"
                class="text-xs border border-gray-300 rounded px-2 py-1">
                <option v-for="g in grns" :key="g.id" :value="g.id">
                  {{ g.delivery_ref || g.id.slice(-6) }} · {{ g.received_date }}
                </option>
              </select>

              <button @click="showGrnForm = !showGrnForm"
                class="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
                + New GRN
              </button>
            </div>
          </div>

          <!-- New GRN form -->
          <div v-if="showGrnForm" class="px-4 py-3 bg-blue-50 border-b border-blue-100 space-y-2">
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Delivery Ref</label>
                <input v-model="grnForm.delivery_ref" type="text"
                  class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Received Date</label>
                <input v-model="grnForm.received_date" type="date"
                  class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
              </div>
              <div class="col-span-2">
                <label class="block text-xs text-gray-500 mb-1">Notes</label>
                <input v-model="grnForm.notes" type="text"
                  class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
              </div>
            </div>
            <div class="flex gap-2">
              <button @click="saveGrn" :disabled="grnSaving"
                class="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-40">
                {{ grnSaving ? 'Saving…' : 'Save GRN' }}
              </button>
              <button @click="showGrnForm = false"
                class="px-3 py-1 border border-gray-300 text-xs rounded hover:bg-gray-50">
                Cancel
              </button>
            </div>
          </div>

          <!-- GRN lines matched to PO lines -->
          <div class="flex-1 overflow-auto">
            <template v-if="selectedGrn">
              <!-- One row per PO line showing matched GRN line -->
              <div v-for="poLine in po.lines" :key="poLine.id"
                class="border-b border-gray-100 px-4 py-3 min-h-[72px] flex items-center">
                <div v-if="grnLineForPoLine(poLine.id)" class="w-full">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="text-sm font-medium text-gray-800">
                        {{ grnLineForPoLine(poLine.id).item_name || grnLineForPoLine(poLine.id).item_sku || '—' }}
                      </p>
                      <p class="text-xs text-gray-500 mt-0.5">
                        Received: {{ grnLineForPoLine(poLine.id).quantity_received }}
                        <span v-if="grnLineForPoLine(poLine.id).discrepancy !== 'none'"
                          class="ml-2 text-amber-600">
                          ⚠ {{ grnLineForPoLine(poLine.id).discrepancy }}
                        </span>
                      </p>
                    </div>
                    <span class="text-green-500 text-lg">✓</span>
                  </div>
                </div>
                <div v-else class="text-xs text-gray-300 italic">No GRN line linked</div>
              </div>

              <!-- Unmatched GRN lines (draggable) -->
              <div v-if="unmatchedGrnLines.length" class="border-t border-gray-200 bg-gray-50 px-4 py-2">
                <p class="text-xs text-gray-400 uppercase mb-2">Unlinked — drag to match</p>
                <div v-for="line in unmatchedGrnLines" :key="line.id"
                  draggable="true"
                  @dragstart="onDragStart(line, 'grn')"
                  class="bg-white border border-gray-200 rounded px-3 py-2 mb-1 cursor-grab text-xs text-gray-700 hover:border-blue-300 hover:bg-blue-50">
                  {{ line.item_name || line.item_sku || '—' }} · Qty: {{ line.quantity_received }}
                </div>
              </div>

              <!-- Add GRN line -->
              <div class="px-4 py-2 border-t border-gray-100">
                <button v-if="!showGrnLineForm" @click="showGrnLineForm = true"
                  class="text-xs text-blue-600 hover:underline">+ Add GRN Line</button>
                <div v-else class="space-y-2 pt-1">
                  <div class="grid grid-cols-2 gap-2">
                    <div class="col-span-2">
                      <label class="block text-xs text-gray-500 mb-1">PO Line</label>
                      <select v-model="grnLineForm.po_line"
                        class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs">
                        <option value="">— Select PO line —</option>
                        <option v-for="l in po.lines" :key="l.id" :value="l.id">
                          {{ l.description || l.item_name }} · Qty {{ l.quantity }}
                        </option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Qty Received</label>
                      <input v-model.number="grnLineForm.quantity_received" type="number" min="0"
                        class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Discrepancy</label>
                      <select v-model="grnLineForm.discrepancy"
                        class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs">
                        <option value="none">None</option>
                        <option value="short">Short</option>
                        <option value="over">Over</option>
                        <option value="damaged">Damaged</option>
                        <option value="wrong">Wrong item</option>
                      </select>
                    </div>
                  </div>
                  <div class="flex gap-2">
                    <button @click="addGrnLine"
                      class="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700">
                      Confirm
                    </button>
                    <button @click="showGrnLineForm = false"
                      class="px-3 py-1 border border-gray-300 text-xs rounded">
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </template>
            <div v-else class="p-4 text-xs text-gray-400 italic">
              Create or select a GRN above.
            </div>
          </div>
        </div>

        <!-- ── Column 3: Invoice ── -->
        <div class="flex flex-col">
          <div class="bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center justify-between">
            <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Invoice</p>
            <div class="flex items-center gap-2">

            <select v-if="invoices.length"
              :value="selectedInvoice?.id"
              @change="selectedInvoice = invoices.find((i: any) => i.id === ($event.target as HTMLSelectElement).value)"
              class="text-xs border border-gray-300 rounded px-2 py-1">
              <option v-for="inv in invoices" :key="inv.id" :value="inv.id">
                {{ inv.invoice_number }} · {{ inv.invoice_date }}
              </option>
            </select>

              <button @click="showInvoiceForm = !showInvoiceForm"
                class="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
                + New Invoice
              </button>
            </div>
          </div>

          <!-- New invoice form -->
          <div v-if="showInvoiceForm" class="px-4 py-3 bg-blue-50 border-b border-blue-100 space-y-2">
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Invoice Number</label>
                <input v-model="invoiceForm.invoice_number" type="text"
                  class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Invoice Date</label>
                <input v-model="invoiceForm.invoice_date" type="date"
                  class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Currency</label>
                <select v-model="invoiceForm.currency"
                  class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs">
                  <option>GBP</option><option>USD</option><option>EUR</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">FX Rate</label>
                <input v-model="invoiceForm.fx_rate" type="number" step="0.0001"
                  class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
              </div>
              <div class="col-span-2">
                <label class="block text-xs text-gray-500 mb-1">Notes</label>
                <input v-model="invoiceForm.notes" type="text"
                  class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
              </div>
            </div>
            <div class="flex gap-2">
              <button @click="saveInvoice" :disabled="invoiceSaving"
                class="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-40">
                {{ invoiceSaving ? 'Saving…' : 'Save Invoice' }}
              </button>
              <button @click="showInvoiceForm = false"
                class="px-3 py-1 border border-gray-300 text-xs rounded hover:bg-gray-50">
                Cancel
              </button>
            </div>
          </div>

          <!-- Invoice lines matched to PO lines -->
          <div class="flex-1 overflow-auto">
            <template v-if="selectedInvoice">

              <!-- One row per PO line -->
              <div v-for="poLine in po.lines" :key="poLine.id"
                class="border-b border-gray-100 px-4 py-3 min-h-[72px] flex items-center">
                <div v-if="invLineForPoLine(poLine.id)" class="w-full">
                  <div class="flex items-center justify-between">
                    <div>
                      <p class="text-sm font-medium text-gray-800">
                        {{ invLineForPoLine(poLine.id).description }}
                      </p>
                      <p class="text-xs text-gray-500 mt-0.5">
                        Qty: {{ invLineForPoLine(poLine.id).quantity }}
                        · {{ invLineForPoLine(poLine.id).currency }}
                        {{ invLineForPoLine(poLine.id).unit_price }}
                      </p>
                    </div>
                    <span v-if="invLineForPoLine(poLine.id).match_status"
                      :class="matchColour(invLineForPoLine(poLine.id).match_status)"
                      class="text-xs px-2 py-0.5 rounded-full border font-medium">
                      {{ matchIcon(invLineForPoLine(poLine.id).match_status) }}
                      {{ invLineForPoLine(poLine.id).match_status.replace(/_/g, ' ') }}
                    </span>
                  </div>
                  <p v-if="invLineForPoLine(poLine.id).match_notes"
                    class="text-xs text-gray-400 mt-1 italic">
                    {{ invLineForPoLine(poLine.id).match_notes }}
                  </p>
                </div>
                <div v-else class="text-xs text-gray-300 italic">No invoice line linked</div>
              </div>

              <!-- Unmatched invoice lines (draggable) -->
              <div v-if="unmatchedInvLines.length" class="border-t border-gray-200 bg-gray-50 px-4 py-2">
                <p class="text-xs text-gray-400 uppercase mb-2">Unlinked — drag to match</p>
                <div v-for="line in unmatchedInvLines" :key="line.id"
                  draggable="true"
                  @dragstart="onDragStart(line, 'inv')"
                  class="bg-white border border-gray-200 rounded px-3 py-2 mb-1 cursor-grab text-xs text-gray-700 hover:border-blue-300 hover:bg-blue-50">
                  {{ line.description }} · Qty: {{ line.quantity }} · {{ line.currency }} {{ line.unit_price }}
                </div>
              </div>

              <!-- Add invoice line -->
              <div class="px-4 py-2 border-t border-gray-100">
                <button v-if="!showInvLineForm" @click="showInvLineForm = true"
                  class="text-xs text-blue-600 hover:underline">+ Add Invoice Line</button>
                <div v-else class="space-y-2 pt-1">
                  <div class="grid grid-cols-2 gap-2">
                    <div class="col-span-2">
                      <label class="block text-xs text-gray-500 mb-1">Description</label>
                      <input v-model="invLineForm.description" type="text"
                        class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Qty</label>
                      <input v-model.number="invLineForm.quantity" type="number" min="1"
                        class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Unit Price</label>
                      <input v-model="invLineForm.unit_price" type="number" step="0.01"
                        class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Currency</label>
                      <select v-model="invLineForm.currency"
                        class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs">
                        <option>GBP</option><option>USD</option><option>EUR</option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">FX Rate</label>
                      <input v-model="invLineForm.fx_rate" type="number" step="0.0001"
                        class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs" />
                    </div>
                    <div class="col-span-2">
                      <label class="block text-xs text-gray-500 mb-1">Link to PO Line (optional)</label>
                      <select v-model="invLineForm.po_line"
                        class="w-full border border-gray-300 rounded px-2 py-1.5 text-xs">
                        <option value="">— Auto-match —</option>
                        <option v-for="l in po.lines" :key="l.id" :value="l.id">
                          {{ l.description || l.item_name }} · Qty {{ l.quantity }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="flex gap-2">
                    <button @click="addInvLine"
                      class="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700">
                      Confirm
                    </button>
                    <button @click="showInvLineForm = false"
                      class="px-3 py-1 border border-gray-300 text-xs rounded">
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </template>
            <div v-else class="p-4 text-xs text-gray-400 italic">
              Create or select an invoice above.
            </div>
          </div>
        </div>
      </div>

      <!-- ── Match results footer ── -->
      <div class="bg-white border-t border-gray-200 px-6 py-3 flex items-center justify-between">
        <div class="flex items-center gap-4 flex-wrap">
          <template v-if="selectedInvoice?.lines?.length">
            <div v-for="line in selectedInvoice.lines" :key="line.id"
              :class="matchColour(line.match_status)"
              class="text-xs px-3 py-1 rounded-full border">
              {{ matchIcon(line.match_status) }} {{ line.description }} — {{ line.match_status?.replace(/_/g, ' ') }}
            </div>
          </template>
          <span v-else class="text-xs text-gray-400 italic">Run match to see results</span>
        </div>
        <div class="flex gap-2">
          <button @click="runMatch" :disabled="!selectedInvoice || matchRunning"
            class="px-4 py-1.5 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 disabled:opacity-40">
            {{ matchRunning ? 'Running…' : 'Run Match' }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>