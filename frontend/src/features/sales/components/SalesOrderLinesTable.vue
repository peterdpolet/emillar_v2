<script setup lang="ts">
import { ref, watch, computed} from 'vue'
import api from '@/api/axios.js'
import { useSalesStore } from '@/features/sales/stores/useSalesStore.js'
import { useSupplierListStore } from '@/features/purchasing/stores/useSupplierListStore.js'
import SalesOrderPrint from './SalesOrderPrint.vue'


const salesStore = useSalesStore()
const supplierStore = useSupplierListStore()

// ── Header edit ───────────────────────────────────────────
const headerForm = ref({ reference: '', currency: 'GBP', notes: '', customer_po_ref: '', required_by: '' })
const headerSaving = ref(false)
const headerExpanded = ref(false)

const headerSummary = computed(() => {
  const o = salesStore.selectedSalesOrder
  if (!o) return ''
  const parts = []
  if (o.customer_po_ref) parts.push(`PO: ${o.customer_po_ref}`)
  if (o.required_by)     parts.push(`Required: ${o.required_by}`)
  if (o.currency)        parts.push(o.currency)
  if (o.status)          parts.push(o.status.charAt(0).toUpperCase() + o.status.slice(1))
  if (o.notes)           parts.push(`— ${o.notes}`)
  return parts.join('  ·  ')
})

watch(() => salesStore.selectedSalesOrder, (order) => {
  if (order) {
    headerForm.value = {
    reference:       order.reference      || '',
    currency:        order.currency       || 'GBP',
    notes:           order.notes          || '',
    customer_po_ref: order.customer_po_ref || '',
    required_by:     order.required_by    || '',
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

const posting = ref(false)
const postOrder = async () => {
  if (!salesStore.selectedSalesOrder) return
  posting.value = true
  try {
    await api.patch(`/sales/orders/${salesStore.selectedSalesOrder.so_id}/`, { status: 'active' })
    await salesStore.fetchSalesOrders()
    // Re-select the order to refresh its status
    const updated = salesStore.salesOrders.find(
      o => o.so_id === salesStore.selectedSalesOrder.so_id
    )
    if (updated) salesStore.selectedSalesOrder = updated
  } finally {
    posting.value = false
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

// ── Quotes ────────────────────────────────────────────────
const expandedQuotesLine = ref<string | null>(null)
const quotesByLine       = ref<Record<string, any[]>>({})
const quoteFormLine      = ref<string | null>(null)
const editingQuote       = ref<any | null>(null)


const quoteForm = ref({
  supplier: '', status: 'requested', supplier_sku: '',
  price: '', currency: 'USD', fx_rate: '', fx_rate_date: '',
  valid_until: '', notes: '',
})

const resetQuoteForm = () => {
  quoteForm.value = {
    supplier: '', status: 'requested', supplier_sku: '',
    price: '', currency: 'USD', fx_rate: '', fx_rate_date: '',
    valid_until: '', notes: '',
  }
  editingQuote.value = null
}

async function fetchSuppliers() {
  await supplierStore.fetchSuppliers()
}

async function fetchQuotes(line: any) {
  const { data } = await api.get('/purchasing/quotes/', {
    params: { so_line: line.sol_id }
  })
  quotesByLine.value[line.sol_id] = data.results ?? data
}

async function toggleQuotes(line: any) {
  if (expandedQuotesLine.value === line.sol_id) {
    expandedQuotesLine.value = null
    quoteFormLine.value = null
    resetQuoteForm()
    return
  }
  expandedQuotesLine.value = line.sol_id
  quoteFormLine.value = null
  await fetchSuppliers()
  await fetchQuotes(line)
}

async function openAddQuote(line: any) {
  resetQuoteForm()
  await fetchSuppliers()
  quoteFormLine.value = line.sol_id
}

async function openEditQuote(quote: any) {
  await fetchSuppliers()
  editingQuote.value = quote
  quoteForm.value = {
    supplier:     quote.supplier,
    status:       quote.status,
    supplier_sku: quote.supplier_sku || '',
    price:        quote.price || '',
    currency:     quote.currency || 'USD',
    fx_rate:      quote.fx_rate || '',
    fx_rate_date: quote.fx_rate_date || '',
    valid_until:  quote.valid_until || '',
    notes:        quote.notes || '',
  }
  quoteFormLine.value = quote.so_line
}
function closeQuoteForm() {
  quoteFormLine.value = null
  resetQuoteForm()
}

async function saveQuote(line: any) {
  const payload = {
    ...quoteForm.value,
    so_line: line.sol_id,
    price:        quoteForm.value.price    || null,
    fx_rate:      quoteForm.value.fx_rate  || null,
    fx_rate_date: quoteForm.value.fx_rate_date || null,
    valid_until:  quoteForm.value.valid_until  || null,
  }
  if (editingQuote.value) {
    await api.patch(`/purchasing/quotes/${editingQuote.value.id}/`, payload)
  } else {
    await api.post('/purchasing/quotes/', payload)
  }
  await fetchQuotes(line)
  closeQuoteForm()
}

async function acceptQuote(quote: any, line: any) {
  if (!confirm(`Accept quote from ${quote.supplier_name}? All other quotes for this line will be rejected.`)) return
  await api.post(`/purchasing/quotes/${quote.id}/accept/`)
  await fetchQuotes(line)
  await salesStore.fetchSalesOrderLines()
}

function quoteStatusColour(status: string) {
  const map: Record<string, string> = {
    requested: 'bg-gray-100 text-gray-600',
    received:  'bg-blue-100 text-blue-700',
    accepted:  'bg-emerald-100 text-emerald-700',
    rejected:  'bg-red-100 text-red-600',
    expired:   'bg-amber-100 text-amber-700',
  }
  return map[status] ?? 'bg-gray-100 text-gray-600'
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
const printingLine = ref<string | null>(null)

const printLine = async (line: any) => {
  printingLine.value = line.sol_id
  try {
    const so       = salesStore.selectedSalesOrder
    const sku      = `${line.stone_type}-L${line.line_number}`.toUpperCase()
    const soNumber = so?.reference || so?.so_id
    const itemUrl  = `https://ewanmillarltd.co.uk/sales-orders-v2`
    await api.post('/inventory/print-label/', {
      sku,
      so_number: soNumber,
      item_url:  itemUrl,
    })
  } catch (e) {
    console.error('Print failed', e)
  } finally {
    printingLine.value = null
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

    <!-- SO Header -->
    <!-- Collapsed summary bar -->
    <div v-if="!headerExpanded"
      class="flex items-center justify-between bg-gray-100 border border-gray-200 rounded-lg px-4 py-2.5">
      <div class="flex items-center gap-3">
        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Order Header</span>
        <span class="text-gray-700 text-sm">{{ headerSummary }}</span>
      </div>
      <button @click="headerExpanded = true"
        class="text-xs text-blue-600 hover:underline">Edit</button>
    </div>

    <!-- Expanded header form -->
    <div v-else class="border border-gray-200 rounded-lg p-3 bg-white space-y-3">
      <div class="flex items-center justify-between">
        <p class="font-semibold text-gray-700">Order Header</p>
        <button @click="headerExpanded = false" class="text-xs text-gray-400 hover:text-gray-600">✕ Close</button>
      </div>

      <!-- Read-only info row -->
      <div class="grid grid-cols-4 gap-3 text-xs text-gray-500 bg-gray-50 rounded p-2">
        <div>Raised by: <span class="text-gray-700 font-medium">{{ salesStore.selectedSalesOrder?.raised_by_name || '—' }}</span></div>
        <div>Date: <span class="text-gray-700 font-medium">{{ salesStore.selectedSalesOrder?.raised_date || '—' }}</span></div>
        <div>Status: <span class="text-gray-700 font-medium capitalize">{{ salesStore.selectedSalesOrder?.status || '—' }}</span></div>
        <div>Required By: <span class="text-gray-700 font-medium">{{ salesStore.selectedSalesOrder?.required_by || '—' }}</span></div>
      </div>

      <!-- Editable fields -->
      <div class="grid grid-cols-3 gap-3">
        <div>
          <label class="block text-xs text-gray-500 mb-1">Reference</label>
          <input v-model="headerForm.reference" type="text"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Customer PO Ref</label>
          <input v-model="headerForm.customer_po_ref" type="text"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Required By</label>
          <input v-model="headerForm.required_by" type="date"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Currency</label>
          <select v-model="headerForm.currency"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm">
            <option>GBP</option><option>USD</option><option>EUR</option>
          </select>
        </div>
        <div class="col-span-2">
          <label class="block text-xs text-gray-500 mb-1">Notes</label>
          <input v-model="headerForm.notes" type="text"
            class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
        </div>
      </div>

      <div class="flex justify-end gap-2">
        <button
          v-if="salesStore.selectedSalesOrder?.status === 'draft'"
          @click="postOrder" :disabled="posting"
          class="px-4 py-1.5 bg-green-600 text-white text-xs rounded hover:bg-green-700 disabled:opacity-40">
          {{ posting ? 'Posting…' : 'Post Order' }}
        </button>
        <button @click="updateHeader(); headerExpanded = false" :disabled="headerSaving"
          class="px-4 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-40">
          {{ headerSaving ? 'Saving…' : 'Update Header' }}
        </button>
      </div>
      <SalesOrderPrint />
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
                <button @click="printLine(line)"
                  :disabled="printingLine === line.sol_id"
                  class="text-gray-400 hover:text-gray-600 text-xs disabled:opacity-40">
                  {{ printingLine === line.sol_id ? '…' : 'Print' }}
                </button>
                <button @click="toggleQuotes(line)"
                  class="text-indigo-400 hover:text-indigo-600 text-xs">
                  Quotes{{ quotesByLine[line.sol_id]?.length ? ` (${quotesByLine[line.sol_id].length})` : '' }}
                </button>
              </td>
            </tr>

            <!-- Quotes panel -->
            <tr v-if="editingLine !== line.sol_id && expandedQuotesLine === line.sol_id">
              <td :colspan="10" class="px-0 pb-3 bg-indigo-50 border-b border-indigo-100">
                <div class="px-5 pt-3">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-semibold text-indigo-700 uppercase tracking-wide">
                      Supplier Quotes — Line {{ line.line_number }}
                    </span>
                    <button @click="openAddQuote(line)"
                      class="px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs rounded-lg">
                      + Request Quote
                    </button>
                  </div>

                  <!-- Quote list -->
                  <div v-if="quotesByLine[line.sol_id]?.length" class="space-y-2 mb-2">
                    <div v-for="quote in quotesByLine[line.sol_id]" :key="quote.id"
                      class="bg-white rounded-lg border border-indigo-100 px-4 py-3 flex items-center gap-4">
                      <div class="flex-1">
                        <div class="flex items-center gap-2">
                          <span class="text-sm font-medium text-gray-800">{{ quote.supplier_name }}</span>
                          <span :class="quoteStatusColour(quote.status)"
                            class="px-2 py-0.5 rounded-full text-xs font-medium">
                            {{ quote.status }}
                          </span>
                        </div>
                        <div class="text-xs text-gray-500 mt-0.5 flex gap-4">
                          <span v-if="quote.price">
                            {{ quote.currency }} {{ Number(quote.price).toFixed(2) }}
                            <span v-if="quote.price_gbp && quote.currency !== 'GBP'" class="text-gray-400">
                              (£{{ Number(quote.price_gbp).toFixed(2) }})
                            </span>
                          </span>
                          <span v-else class="text-gray-400 italic">No price yet</span>
                          <span v-if="quote.supplier_sku">SKU: {{ quote.supplier_sku }}</span>
                          <span v-if="quote.valid_until">Valid until: {{ quote.valid_until }}</span>
                        </div>
                        <div v-if="quote.notes" class="text-xs text-gray-400 mt-0.5 italic">{{ quote.notes }}</div>
                      </div>
                      <div class="flex gap-2 items-center">
                        <button @click="openEditQuote(quote)"
                          class="text-xs text-blue-500 hover:text-blue-700">Edit</button>
                        <button
                          v-if="quote.status === 'received'"
                          @click="acceptQuote(quote, line)"
                          class="px-2 py-1 bg-emerald-600 hover:bg-emerald-700 text-white text-xs rounded-lg">
                          Accept
                        </button>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-xs text-gray-400 italic mb-2">No quotes yet</div>

                  <!-- Supplier shown on line if accepted -->
                  <div v-if="line.supplier_name" class="text-xs text-emerald-700 font-medium">
                    ✓ Accepted supplier: {{ line.supplier_name }} {{ line.supplier_sku ? `(${line.supplier_sku})` : '' }}
                  </div>
                </div>
              </td>
            </tr>

            <!-- Add / Edit quote form row -->
            <tr v-if="quoteFormLine === line.sol_id">
              <td :colspan="10" class="px-0 pb-3 bg-white border-b border-indigo-100">
                <div class="px-5 pt-3">
                  <h4 class="text-xs font-semibold text-gray-600 uppercase mb-3">
                    {{ editingQuote ? 'Edit Quote' : 'Request Quote' }}
                  </h4>
                  <div class="grid grid-cols-3 gap-3">
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Supplier</label>
                      <select v-model="quoteForm.supplier"
                        class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <option value="">— Select supplier —</option>
                        <option v-for="s in supplierStore.suppliers" :key="s.bp_id" :value="s.bp_id">{{ s.bp_name }}</option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Status</label>
                      <select v-model="quoteForm.status"
                        class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <option value="requested">Requested</option>
                        <option value="received">Received</option>
                        <option value="rejected">Rejected</option>
                        <option value="expired">Expired</option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Supplier SKU</label>
                      <input v-model="quoteForm.supplier_sku" type="text"
                        class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Price</label>
                      <input v-model.number="quoteForm.price" type="number" step="0.01"
                        class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Currency</label>
                      <select v-model="quoteForm.currency"
                        class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <option>GBP</option><option>USD</option><option>EUR</option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">FX Rate</label>
                      <input v-model.number="quoteForm.fx_rate" type="number" step="0.0001" placeholder="e.g. 1.2700"
                        class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">FX Rate Date</label>
                      <input v-model="quoteForm.fx_rate_date" type="date"
                        class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                    </div>
                    <div>
                      <label class="block text-xs text-gray-500 mb-1">Valid Until</label>
                      <input v-model="quoteForm.valid_until" type="date"
                        class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                    </div>
                    <div class="col-span-3">
                      <label class="block text-xs text-gray-500 mb-1">Notes</label>
                      <input v-model="quoteForm.notes" type="text"
                        class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                    </div>
                  </div>
                  <div class="flex gap-2 mt-3">
                    <button @click="saveQuote(line)"
                      :disabled="!quoteForm.supplier"
                      class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white text-sm rounded-lg">
                      {{ editingQuote ? 'Update Quote' : 'Save Quote' }}
                    </button>
                    <button @click="closeQuoteForm"
                      class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-lg">
                      Cancel
                    </button>
                  </div>
                </div>
              </td>
            </tr>

            <!-- Edit row -->
            <tr v-if="editingLine === line.sol_id" class="border-t bg-blue-50">
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