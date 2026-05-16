<template>
  <div class="space-y-4">

    <!-- Section Header -->
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-semibold text-slate-300 uppercase tracking-wider">
        Invoices & Three-Way Match
      </h3>
      <button
        @click="showAddInvoice = !showAddInvoice"
        class="text-xs bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded"
      >
        + Add Invoice
      </button>
    </div>

    <!-- Add Invoice Form -->
    <div v-if="showAddInvoice" class="bg-slate-800 rounded-lg p-4 space-y-3 border border-slate-600">
      <h4 class="text-sm font-medium text-slate-200">New Invoice</h4>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-xs text-slate-400">Invoice Number</label>
          <input v-model="newInvoice.invoice_number" class="input-field" />
        </div>
        <div>
          <label class="text-xs text-slate-400">Invoice Date</label>
          <input v-model="newInvoice.invoice_date" type="date" class="input-field" />
        </div>
        <div>
          <label class="text-xs text-slate-400">Currency</label>
          <select v-model="newInvoice.currency" class="input-field">
            <option>GBP</option><option>USD</option><option>EUR</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-slate-400">FX Rate</label>
          <input v-model="newInvoice.fx_rate" type="number" step="0.000001" class="input-field" />
        </div>
      </div>
      <div>
        <label class="text-xs text-slate-400">Notes</label>
        <textarea v-model="newInvoice.notes" rows="2" class="input-field" />
      </div>
      <div class="flex gap-2">
        <button @click="createInvoice" class="btn-primary text-xs">Save Invoice</button>
        <button @click="showAddInvoice = false" class="btn-secondary text-xs">Cancel</button>
      </div>
    </div>

    <!-- No invoices -->
    <div v-if="!invoices.length" class="text-sm text-slate-500 italic">
      No invoices linked to this PO yet.
    </div>

    <!-- Invoice List -->
    <div v-for="invoice in invoices" :key="invoice.id" class="border border-slate-600 rounded-lg overflow-hidden">

      <!-- Invoice Header Row -->
      <div
        class="flex items-center justify-between px-4 py-3 bg-slate-800 cursor-pointer hover:bg-slate-750"
        @click="toggleInvoice(invoice.id)"
      >
        <div class="flex items-center gap-3">
          <span class="text-sm font-medium text-slate-200">{{ invoice.invoice_number }}</span>
          <span class="text-xs text-slate-400">{{ invoice.invoice_date }}</span>
          <span :class="statusBadge(invoice.status)" class="text-xs px-2 py-0.5 rounded-full font-medium">
            {{ invoice.status }}
          </span>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-slate-300">£{{ invoice.total_gbp }}</span>
          <button
            @click.stop="runMatch(invoice)"
            class="text-xs bg-emerald-700 hover:bg-emerald-600 text-white px-2 py-1 rounded"
          >
            Run Match
          </button>
          <ChevronDownIcon
            class="w-4 h-4 text-slate-400 transition-transform"
            :class="{ 'rotate-180': expandedInvoices.includes(invoice.id) }"
          />
        </div>
      </div>

      <!-- Expanded: Lines + Match Table -->
      <div v-if="expandedInvoices.includes(invoice.id)" class="bg-slate-900 p-4 space-y-4">

        <!-- Three-Way Match Table -->
        <div class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead>
              <tr class="text-slate-400 border-b border-slate-700">
                <th class="text-left py-2 pr-4">Description</th>
                <th class="text-right pr-4">PO Qty</th>
                <th class="text-right pr-4">PO Price</th>
                <th class="text-right pr-4">GRN Rcvd</th>
                <th class="text-right pr-4">Inv Qty</th>
                <th class="text-right pr-4">Inv Price</th>
                <th class="text-center">Match</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="line in invoice.lines"
                :key="line.id"
                class="border-b border-slate-800 hover:bg-slate-800/50"
              >
                <td class="py-2 pr-4 text-slate-300">{{ line.description }}</td>
                <td class="text-right pr-4 text-slate-400">{{ line.po_line_detail?.quantity ?? '—' }}</td>
                <td class="text-right pr-4 text-slate-400">{{ line.po_line_detail?.unit_price ?? '—' }}</td>
                <td class="text-right pr-4 text-slate-400">{{ line.grn_received ?? '—' }}</td>
                <td class="text-right pr-4 text-slate-300">{{ line.quantity }}</td>
                <td class="text-right pr-4 text-slate-300">{{ line.unit_price }}</td>
                <td class="text-center">
                  <span :class="matchBadge(line.match_status)" class="px-2 py-0.5 rounded-full text-xs font-medium">
                    {{ line.match_status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Match Notes -->
        <div v-for="line in invoice.lines.filter(l => l.match_notes)" :key="'note-' + line.id"
          class="text-xs text-slate-400 italic">
          <span class="text-slate-500">{{ line.description }}:</span> {{ line.match_notes }}
        </div>

        <!-- Add Invoice Line -->
        <div class="pt-2 border-t border-slate-700">
          <button
            @click="toggleAddLine(invoice.id)"
            class="text-xs text-indigo-400 hover:text-indigo-300"
          >
            + Add Invoice Line
          </button>

          <div v-if="addingLineFor === invoice.id" class="mt-3 grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-slate-400">PO Line</label>
              <select v-model="newLine.po_line" class="input-field">
                <option v-for="pol in poLines" :key="pol.id" :value="pol.id">
                  {{ pol.description }} ({{ pol.quantity }} @ {{ pol.unit_price }})
                </option>
              </select>
            </div>
            <div>
              <label class="text-xs text-slate-400">Description</label>
              <input v-model="newLine.description" class="input-field" />
            </div>
            <div>
              <label class="text-xs text-slate-400">Quantity</label>
              <input v-model="newLine.quantity" type="number" class="input-field" />
            </div>
            <div>
              <label class="text-xs text-slate-400">Unit Price</label>
              <input v-model="newLine.unit_price" type="number" step="0.0001" class="input-field" />
            </div>
            <div>
              <label class="text-xs text-slate-400">Currency</label>
              <select v-model="newLine.currency" class="input-field">
                <option>GBP</option><option>USD</option><option>EUR</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-slate-400">FX Rate</label>
              <input v-model="newLine.fx_rate" type="number" step="0.000001" class="input-field" />
            </div>
            <div class="col-span-2 flex gap-2">
              <button @click="addLine(invoice)" class="btn-primary text-xs">Add Line</button>
              <button @click="addingLineFor = null" class="btn-secondary text-xs">Cancel</button>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'
import axios from '@/api/axios'

const props = defineProps({
  purchaseOrder: { type: Object, required: true },
  poLines: { type: Array, default: () => [] }
})

const invoices = ref([])
const expandedInvoices = ref([])
const showAddInvoice = ref(false)
const addingLineFor = ref(null)

const newInvoice = ref({
  invoice_number: '',
  invoice_date: '',
  currency: 'GBP',
  fx_rate: 1.0,
  notes: ''
})

const newLine = ref({
  po_line: null,
  description: '',
  quantity: '',
  unit_price: '',
  currency: 'GBP',
  fx_rate: 1.0
})

async function fetchInvoices() {
  if (!props.purchaseOrder?.id) return
  const res = await axios.get(`/purchasing/invoices/?purchase_order=${props.purchaseOrder.id}`)
  invoices.value = res.data.results ?? res.data
}
async function createInvoice() {
  await axios.post('/purchasing/invoices/', {
    invoice_number: newInvoice.value.invoice_number,
    invoice_date: newInvoice.value.invoice_date,
    currency: newInvoice.value.currency,
    fx_rate: newInvoice.value.fx_rate,
    notes: newInvoice.value.notes,
    purchase_order: props.purchaseOrder.id
  })
  showAddInvoice.value = false
  newInvoice.value = { invoice_number: '', invoice_date: '', currency: 'GBP', fx_rate: 1.0, notes: '' }
  await fetchInvoices()
}





async function runMatch(invoice) {
  await axios.post(`/purchasing/invoices/${invoice.id}/run_match/`)
  await fetchInvoices()
}

async function addLine(invoice) {
  await axios.post(`/purchasing/invoices/${invoice.id}/add_line/`, newLine.value)
  addingLineFor.value = null
  newLine.value = { po_line: null, description: '', quantity: '', unit_price: '', currency: 'GBP', fx_rate: 1.0 }
  await fetchInvoices()
}

function toggleInvoice(id) {
  const idx = expandedInvoices.value.indexOf(id)
  if (idx === -1) expandedInvoices.value.push(id)
  else expandedInvoices.value.splice(idx, 1)
}

function toggleAddLine(id) {
  addingLineFor.value = addingLineFor.value === id ? null : id
}

function statusBadge(status) {
  const map = {
    draft: 'bg-slate-600 text-slate-300',
    posted: 'bg-blue-900 text-blue-300',
    matched: 'bg-emerald-900 text-emerald-300',
    disputed: 'bg-red-900 text-red-300',
    paid: 'bg-purple-900 text-purple-300',
  }
  return map[status] ?? 'bg-slate-600 text-slate-300'
}

function matchBadge(status) {
  const map = {
    matched: 'bg-emerald-900 text-emerald-300',
    unmatched: 'bg-slate-700 text-slate-400',
    price_variance: 'bg-amber-900 text-amber-300',
    qty_variance: 'bg-orange-900 text-orange-300',
    no_grn: 'bg-red-900 text-red-300',
    disputed: 'bg-red-900 text-red-300',
  }
  return map[status] ?? 'bg-slate-700 text-slate-400'
}



// Replace onMounted with a watcher
watch(() => props.purchaseOrder?.id, (newId) => {
  if (newId) fetchInvoices()
}, { immediate: true })
</script>