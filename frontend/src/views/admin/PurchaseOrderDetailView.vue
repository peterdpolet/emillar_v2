<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  fetchPO, createPO, updatePO,
  markPOSent, cancelPO,
  addPOLine, removePOLine,
  fetchSuppliers,
} from '@/api/purchaseOrders'
import { fetchItems } from '@/api/items'

// ── Types ─────────────────────────────────────────────────
type POStatus      = 'draft' | 'sent' | 'partial' | 'complete' | 'cancelled'
type MatchStatus   = 'not_received' | 'short' | 'matched' | 'over'

interface Supplier {
  id:   number
  name: string
}

interface Item {
  id:    number
  name:  string
  price: string
}

interface POLine {
  id:                number
  item_name:         string
  quantity:          number
  quantity_received: number
  outstanding:       number
  unit_cost:         string
  line_total:        string
  match_status:      MatchStatus
}

interface PurchaseOrder {
  id:              number
  reference:       string
  supplier_ref:    string
  supplier_name:   string
  raised_by_email: string
  status:          POStatus
  expected_date:   string | null
  notes:           string | null
  created_at:      string
  lines:           POLine[]
  receipt_count:   number
  total_expected:  number
  total_received:  number
}

interface POForm {
  supplier:      string | number
  reference:     string
  supplier_ref:  string
  expected_date: string
  notes:         string
}

interface NewLine {
  item:      string | number
  quantity:  number
  unit_cost: string | number
}

// ── Constants ─────────────────────────────────────────────
const STATUS_COLOURS: Record<POStatus, string> = {
  draft:     'bg-slate-100 text-slate-600',
  sent:      'bg-indigo-50 text-indigo-700',
  partial:   'bg-amber-50 text-amber-700',
  complete:  'bg-emerald-50 text-emerald-700',
  cancelled: 'bg-rose-50 text-rose-700',
}

const MATCH_COLOURS: Record<MatchStatus, string> = {
  not_received: 'text-slate-400',
  short:        'text-amber-600',
  matched:      'text-emerald-600',
  over:         'text-rose-600',
}

const MATCH_LABELS: Record<MatchStatus, string> = {
  not_received: 'Not received',
  short:        'Short',
  matched:      '✓ Matched',
  over:         'Over',
}

// ── Setup ─────────────────────────────────────────────────
const route  = useRoute()
const router = useRouter()

const isNew = computed<boolean>(() => !route.params.id)

const po      = ref<PurchaseOrder | null>(null)
const loading = ref<boolean>(false)
const saving  = ref<boolean>(false)
const error   = ref<string | null>(null)
const success = ref<string | null>(null)

const form = ref<POForm>({
  supplier:      '',
  reference:     '',
  supplier_ref:  '',
  expected_date: '',
  notes:         '',
})

const suppliers  = ref<Supplier[]>([])
const availItems = ref<Item[]>([])

const showAddLine = ref<boolean>(false)
const newLine     = ref<NewLine>({ item: '', quantity: 1, unit_cost: '' })
const addingLine  = ref<boolean>(false)

const showCancel  = ref<boolean>(false)
const cancelling  = ref<boolean>(false)
const markingSent = ref<boolean>(false)

// ── Computed ──────────────────────────────────────────────
const poTotal = computed<string>(() => {
  if (!po.value) return '0.00'
  return po.value.lines
    .reduce((s, l) => s + parseFloat(l.unit_cost) * l.quantity, 0)
    .toFixed(2)
})

const canEdit    = computed<boolean>(() => isNew.value || po.value?.status === 'draft')
const canSend    = computed<boolean>(() => po.value?.status === 'draft' && (po.value?.lines?.length ?? 0) > 0)
const canCancel  = computed<boolean>(() => !!po.value && !['complete', 'cancelled'].includes(po.value.status))
const canReceipt = computed<boolean>(() => !!po.value && ['sent', 'partial'].includes(po.value.status))

// ── Data loading ──────────────────────────────────────────
async function loadSuppliers(): Promise<void> {
  const { data } = await fetchSuppliers()
  suppliers.value = data.results
}

async function loadItems(): Promise<void> {
  if (availItems.value.length) return
  const { data } = await fetchItems({ pageSize: 200, filters: { status: 'active' } })
  availItems.value = data.results
}

onMounted(async () => {
  await loadSuppliers()
  if (!isNew.value) {
    loading.value = true
    try {
      const { data } = await fetchPO(route.params.id as string)
      po.value = data
    } catch {
      error.value = 'Could not load purchase order.'
    } finally {
      loading.value = false
    }
  }
})

// ── Handlers ──────────────────────────────────────────────
async function handleCreate(): Promise<void> {
  if (!form.value.supplier) { error.value = 'Supplier is required.'; return }
  saving.value = true
  error.value  = null
  try {
    const { data } = await createPO({
      supplier:      form.value.supplier,
      reference:     form.value.reference,
      supplier_ref:  form.value.supplier_ref,
      expected_date: form.value.expected_date || null,
      notes:         form.value.notes,
    })
    router.replace(`/admin/purchase-orders/${data.id}`)
  } catch (e: unknown) {
    const err = e as { response?: { data?: { supplier?: string[]; detail?: string } } }
    error.value = err.response?.data?.supplier?.[0]
                ?? err.response?.data?.detail
                ?? 'Could not create PO.'
  } finally {
    saving.value = false
  }
}

async function handleSaveMeta(): Promise<void> {
  if (!po.value) return
  saving.value = true
  error.value  = null
  try {
    const { data } = await updatePO(po.value.id, {
      reference:     po.value.reference,
      supplier_ref:  po.value.supplier_ref,
      expected_date: po.value.expected_date || null,
      notes:         po.value.notes,
    })
    po.value      = data
    success.value = 'Changes saved.'
    setTimeout(() => success.value = null, 3000)
  } catch {
    error.value = 'Could not save changes.'
  } finally {
    saving.value = false
  }
}

async function handleMarkSent(): Promise<void> {
  if (!po.value) return
  markingSent.value = true
  error.value       = null
  try {
    const { data } = await markPOSent(po.value.id)
    po.value      = data
    success.value = 'PO marked as sent to supplier.'
    setTimeout(() => success.value = null, 3000)
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    error.value = err.response?.data?.detail ?? 'Could not update status.'
  } finally {
    markingSent.value = false
  }
}

async function handleCancel(): Promise<void> {
  if (!po.value) return
  cancelling.value = true
  error.value      = null
  try {
    const { data } = await cancelPO(po.value.id)
    po.value         = data
    showCancel.value = false
    success.value    = 'PO cancelled.'
    setTimeout(() => success.value = null, 3000)
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    error.value = err.response?.data?.detail ?? 'Could not cancel PO.'
  } finally {
    cancelling.value = false
  }
}

async function openAddLine(): Promise<void> {
  showAddLine.value = true
  await loadItems()
}

function handleItemSelect(): void {
  const item = availItems.value.find(i => i.id === parseInt(String(newLine.value.item)))
  if (item) newLine.value.unit_cost = item.price
}

async function handleAddLine(): Promise<void> {
  if (!po.value) return
  addingLine.value = true
  error.value      = null
  try {
    const { data } = await addPOLine(po.value.id, {
      item:      parseInt(String(newLine.value.item)),
      quantity:  Number(newLine.value.quantity),
      unit_cost: parseFloat(String(newLine.value.unit_cost)).toFixed(2),
    })
    po.value          = data
    showAddLine.value = false
    newLine.value     = { item: '', quantity: 1, unit_cost: '' }
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    error.value = err.response?.data?.detail ?? 'Could not add line.'
  } finally {
    addingLine.value = false
  }
}

async function handleRemoveLine(lineId: number): Promise<void> {
  if (!po.value) return
  try {
    const { data } = await removePOLine(po.value.id, lineId)
    po.value = data
  } catch {
    error.value = 'Could not remove line.'
  }
}
</script>

<template>
  <!-- Header -->
  <div class="flex items-start justify-between mb-6">
    <div class="flex items-center gap-3">
      <button @click="router.push('/admin/purchase-orders')"
        class="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
        ← Back
      </button>
      <div>
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-slate-900">
            {{ isNew ? 'New Purchase Order'
              : po?.reference || `PO-${String(po?.id || 0).padStart(4, '0')}` }}
          </h1>
          <span v-if="po" :class="[
            'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold capitalize',
            STATUS_COLOURS[po.status]
          ]">{{ po.status }}</span>
        </div>
        <p v-if="po" class="text-xs text-slate-400 mt-0.5">
          {{ po.supplier_name }} · Raised {{ new Date(po.created_at).toLocaleDateString('en-GB') }}
        </p>
      </div>
    </div>

    <!-- Action buttons -->
    <div v-if="po" class="flex items-center gap-2">
      <button v-if="canReceipt"
        @click="router.push(`/admin/goods-receipts/new?po=${po.id}`)"
        class="px-4 py-2 bg-emerald-600 text-white text-sm font-semibold rounded-lg hover:bg-emerald-500">
        + Goods receipt
      </button>
      <button v-if="canSend" @click="handleMarkSent" :disabled="markingSent"
        class="px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-500 disabled:opacity-50">
        {{ markingSent ? 'Sending...' : 'Mark as sent' }}
      </button>
      <div v-if="canCancel">
        <button v-if="!showCancel" @click="showCancel = true"
          class="px-3 py-2 text-sm text-rose-600 border border-rose-200 rounded-lg hover:bg-rose-50">
          Cancel PO
        </button>
        <div v-else class="flex items-center gap-2">
          <span class="text-sm text-slate-600">Are you sure?</span>
          <button @click="showCancel = false"
            class="px-3 py-1.5 text-sm border border-slate-200 rounded-lg hover:bg-slate-50">
            Cancel
          </button>
          <button @click="handleCancel" :disabled="cancelling"
            class="px-3 py-1.5 text-sm text-white bg-rose-600 rounded-lg hover:bg-rose-500 disabled:opacity-50">
            {{ cancelling ? '...' : 'Yes, cancel PO' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Alerts -->
  <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
    {{ error }}
  </div>
  <div v-if="success" class="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 text-sm rounded-lg">
    {{ success }}
  </div>

  <!-- NEW PO FORM -->
  <div v-if="isNew" class="max-w-lg">
    <div class="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
      <div class="p-5">
        <label class="block text-sm font-semibold text-slate-700 mb-1.5">
          Supplier <span class="text-rose-500">*</span>
        </label>
        <select v-model="form.supplier"
          class="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
          <option value="">Select supplier...</option>
          <option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </div>
      <div class="p-5 grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">PO Reference</label>
          <input v-model="form.reference" type="text" placeholder="e.g. PO-2026-001"
            class="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">Expected delivery</label>
          <input v-model="form.expected_date" type="date"
            class="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
      </div>
      <div class="p-5">
        <label class="block text-sm font-semibold text-slate-700 mb-1.5">Notes</label>
        <textarea v-model="form.notes" rows="3"
          class="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      </div>
    </div>
    <div class="mt-4 flex justify-end">
      <button @click="handleCreate" :disabled="saving"
        class="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg disabled:opacity-50">
        {{ saving ? 'Creating...' : 'Create PO' }}
      </button>
    </div>
  </div>

  <!-- EXISTING PO DETAIL -->
  <div v-else-if="po" class="grid grid-cols-3 gap-5">
    <div class="col-span-2 space-y-5">
      <!-- Line items -->
      <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-slate-900">Line items</h2>
          <button v-if="canEdit" @click="openAddLine"
            class="text-xs text-indigo-600 hover:text-indigo-500 font-medium">
            + Add item
          </button>
        </div>

        <!-- Add line form -->
        <div v-if="showAddLine" class="px-5 py-4 bg-slate-50 border-b border-slate-100">
          <div class="grid grid-cols-3 gap-3 mb-3">
            <div class="col-span-1">
              <label class="text-xs font-semibold text-slate-600 mb-1 block">Item</label>
              <select v-model="newLine.item" @change="handleItemSelect"
                class="w-full px-2 py-2 border border-slate-200 rounded-lg text-xs bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">Select...</option>
                <option v-for="item in availItems" :key="item.id" :value="item.id">{{ item.name }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-semibold text-slate-600 mb-1 block">Quantity</label>
              <input v-model="newLine.quantity" type="number" min="1"
                class="w-full px-2 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="text-xs font-semibold text-slate-600 mb-1 block">Unit cost (£)</label>
              <input v-model="newLine.unit_cost" type="number" step="0.01"
                class="w-full px-2 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
          <div class="flex gap-2 justify-end">
            <button @click="showAddLine = false"
              class="px-3 py-1.5 text-xs text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-100">
              Cancel
            </button>
            <button @click="handleAddLine" :disabled="!newLine.item || addingLine"
              class="px-3 py-1.5 text-xs text-white bg-indigo-600 rounded-lg hover:bg-indigo-500 disabled:opacity-50">
              {{ addingLine ? 'Adding...' : 'Add line' }}
            </button>
          </div>
        </div>

        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-100">
              <th class="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Product</th>
              <th class="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Ordered</th>
              <th class="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Received</th>
              <th class="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Outstanding</th>
              <th class="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Unit cost</th>
              <th class="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Total</th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Match</th>
              <th v-if="canEdit" class="px-5 py-3 w-8"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            <tr v-for="line in po.lines" :key="line.id">
              <td class="px-5 py-3 text-sm font-medium text-slate-900">{{ line.item_name }}</td>
              <td class="px-5 py-3 text-sm text-slate-600 tabular-nums text-right">{{ line.quantity }}</td>