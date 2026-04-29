<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  fetchPO, createPO, updatePO,
  markPOSent, cancelPO,
  addPOLine, removePOLine,
  fetchSuppliers,
} from '@/api/purchaseOrders'
import { fetchItems } from '@/api/items'

const route  = useRoute()
const router = useRouter()

const isNew     = computed(() => !route.params.id)
const po        = ref(null)
const loading   = ref(false)
const saving    = ref(false)
const error     = ref(null)
const success   = ref(null)

// Form for new PO
const form = ref({
  supplier: '', reference: '', supplier_ref: '',
  expected_date: '', notes: '',
})

// Suppliers + items for dropdowns
const suppliers  = ref([])
const availItems = ref([])

// Add line
const showAddLine = ref(false)
const newLine     = ref({ item: '', quantity: 1, unit_cost: '' })
const addingLine  = ref(false)

// Status actions
const showCancel   = ref(false)
const cancelling   = ref(false)
const markingSent  = ref(false)

const STATUS_COLOURS = {
  draft:    'bg-slate-100 text-slate-600',
  sent:     'bg-indigo-50 text-indigo-700',
  partial:  'bg-amber-50 text-amber-700',
  complete: 'bg-emerald-50 text-emerald-700',
  cancelled:'bg-rose-50 text-rose-700',
}
const MATCH_COLOURS = {
  not_received: 'text-slate-400',
  short:        'text-amber-600',
  matched:      'text-emerald-600',
  over:         'text-rose-600',
}
const MATCH_LABELS = {
  not_received: 'Not received',
  short:        'Short',
  matched:      '✓ Matched',
  over:         'Over',
}

const poTotal = computed(() => {
  if (!po.value) return '0.00'
  return po.value.lines
    .reduce((s, l) => s + parseFloat(l.unit_cost) * l.quantity, 0)
    .toFixed(2)
})

const canEdit   = computed(() =>
  isNew.value || po.value?.status === 'draft')
const canSend   = computed(() =>
  po.value?.status === 'draft' && po.value?.lines?.length > 0)
const canCancel = computed(() =>
  po.value && !['complete','cancelled'].includes(po.value.status))
const canReceipt = computed(() =>
  po.value && ['sent','partial'].includes(po.value.status))

async function loadSuppliers() {
  const { data } = await fetchSuppliers()
  suppliers.value = data.results
}

async function loadItems() {
  if (availItems.value.length) return
  const { data } = await fetchItems({
    pageSize: 200, filters: { status: 'active' }
  })
  availItems.value = data.results
}

onMounted(async () => {
  await loadSuppliers()
  if (!isNew.value) {
    loading.value = true
    try {
      const { data } = await fetchPO(route.params.id)
      po.value = data
    } catch (e) {
      error.value = 'Could not load purchase order.'
    } finally {
      loading.value = false
    }
  }
})

async function handleCreate() {
  if (!form.value.supplier) { error.value = 'Supplier is required.'; return }
  saving.value = true; error.value = null
  try {
    const { data } = await createPO({
      supplier:      form.value.supplier,
      reference:     form.value.reference,
      supplier_ref:  form.value.supplier_ref,
      expected_date: form.value.expected_date || null,
      notes:         form.value.notes,
    })
    router.replace(`/admin/purchase-orders/${data.id}`)
  } catch (e) {
    error.value = e.response?.data?.supplier?.[0]
                ?? e.response?.data?.detail
                ?? 'Could not create PO.'
  } finally {
    saving.value = false
  }
}

async function handleSaveMeta() {
  saving.value = true; error.value = null
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
  } catch (e) {
    error.value = 'Could not save changes.'
  } finally {
    saving.value = false
  }
}

async function handleMarkSent() {
  markingSent.value = true; error.value = null
  try {
    const { data } = await markPOSent(po.value.id)
    po.value      = data
    success.value = 'PO marked as sent to supplier.'
    setTimeout(() => success.value = null, 3000)
  } catch (e) {
    error.value = e.response?.data?.detail ?? 'Could not update status.'
  } finally {
    markingSent.value = false
  }
}

async function handleCancel() {
  cancelling.value = true; error.value = null
  try {
    const { data } = await cancelPO(po.value.id)
    po.value        = data
    showCancel.value = false
    success.value   = 'PO cancelled.'
    setTimeout(() => success.value = null, 3000)
  } catch (e) {
    error.value = e.response?.data?.detail ?? 'Could not cancel PO.'
  } finally {
    cancelling.value = false
  }
}

async function openAddLine() {
  showAddLine.value = true
  await loadItems()
}

function handleItemSelect() {
  const item = availItems.value.find(
    i => i.id === parseInt(newLine.value.item))
  if (item) newLine.value.unit_cost = item.price
}

async function handleAddLine() {
  addingLine.value = true; error.value = null
  try {
    const { data } = await addPOLine(po.value.id, {
      item:      parseInt(newLine.value.item),
      quantity:  parseInt(newLine.value.quantity),
      unit_cost: parseFloat(newLine.value.unit_cost).toFixed(2),
    })
    po.value          = data
    showAddLine.value = false
    newLine.value     = { item: '', quantity: 1, unit_cost: '' }
  } catch (e) {
    error.value = e.response?.data?.detail ?? 'Could not add line.'
  } finally {
    addingLine.value = false
  }
}

async function handleRemoveLine(lineId) {
  try {
    const { data } = await removePOLine(po.value.id, lineId)
    po.value = data
  } catch (e) {
    error.value = 'Could not remove line.'
  }
}
</script>

<template>
  <!-- Header -->
  <div class="flex items-start justify-between mb-6">
    <div class="flex items-center gap-3">
      <button @click="router.push('/admin/purchase-orders')"
        class="p-2 text-slate-400 hover:text-slate-600
               hover:bg-slate-100 rounded-lg transition-colors">
        ← Back
      </button>
      <div>
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-slate-900">
            {{ isNew ? 'New Purchase Order'
              : po?.reference || `PO-${String(po?.id||0).padStart(4,'0')}` }}
          </h1>
          <span v-if="po" :class="[
            'inline-flex items-center px-2.5 py-1 rounded-full',
            'text-xs font-semibold capitalize',
            STATUS_COLOURS[po.status]
          ]">{{ po.status }}</span>
        </div>
        <p v-if="po" class="text-xs text-slate-400 mt-0.5">
          {{ po.supplier_name }} ·
          Raised {{ new Date(po.created_at).toLocaleDateString('en-GB') }}
        </p>
      </div>
    </div>

    <!-- Action buttons -->
    <div v-if="po" class="flex items-center gap-2">
      <button v-if="canReceipt"
        @click="router.push(`/admin/goods-receipts/new?po=${po.id}`)"
        class="px-4 py-2 bg-emerald-600 text-white text-sm
               font-semibold rounded-lg hover:bg-emerald-500">
        + Goods receipt
      </button>
      <button v-if="canSend" @click="handleMarkSent"
        :disabled="markingSent"
        class="px-4 py-2 bg-indigo-600 text-white text-sm
               font-semibold rounded-lg hover:bg-indigo-500
               disabled:opacity-50">
        {{ markingSent ? 'Sending...' : 'Mark as sent' }}
      </button>
      <div v-if="canCancel">
        <button v-if="!showCancel" @click="showCancel = true"
          class="px-3 py-2 text-sm text-rose-600 border border-rose-200
                 rounded-lg hover:bg-rose-50">
          Cancel PO
        </button>
        <div v-else class="flex items-center gap-2">
          <span class="text-sm text-slate-600">Are you sure?</span>
          <button @click="showCancel = false"
            class="px-3 py-1.5 text-sm border border-slate-200
                   rounded-lg hover:bg-slate-50">Cancel</button>
          <button @click="handleCancel" :disabled="cancelling"
            class="px-3 py-1.5 text-sm text-white bg-rose-600
                   rounded-lg hover:bg-rose-500 disabled:opacity-50">
            {{ cancelling ? '...' : 'Yes, cancel PO' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Alerts -->
  <div v-if="error"
    class="mb-4 p-3 bg-red-50 border border-red-200
           text-red-700 text-sm rounded-lg">{{ error }}</div>
  <div v-if="success"
    class="mb-4 p-3 bg-green-50 border border-green-200
           text-green-700 text-sm rounded-lg">{{ success }}</div>

  <!-- NEW PO FORM -->
  <div v-if="isNew" class="max-w-lg">
    <div class="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
      <div class="p-5">
        <label class="block text-sm font-semibold text-slate-700 mb-1.5">
          Supplier <span class="text-rose-500">*</span>
        </label>
        <select v-model="form.supplier"
          class="w-full px-3 py-2.5 border border-slate-200 rounded-lg
                 text-sm bg-white focus:outline-none focus:ring-2
                 focus:ring-indigo-500">
          <option value="">Select supplier...</option>
          <option v-for="s in suppliers" :key="s.id" :value="s.id">
            {{ s.name }}
          </option>
        </select>
      </div>
      <div class="p-5 grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">
            PO Reference
          </label>
          <input v-model="form.reference" type="text"
            placeholder="e.g. PO-2026-001"
            class="w-full px-3 py-2.5 border border-slate-200 rounded-lg
                   text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">
            Expected delivery
          </label>
          <input v-model="form.expected_date" type="date"
            class="w-full px-3 py-2.5 border border-slate-200 rounded-lg
                   text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
      </div>
      <div class="p-5">
        <label class="block text-sm font-semibold text-slate-700 mb-1.5">
          Notes
        </label>
        <textarea v-model="form.notes" rows="3"
          class="w-full px-3 py-2.5 border border-slate-200 rounded-lg
                 text-sm resize-none focus:outline-none focus:ring-2
                 focus:ring-indigo-500" />
      </div>
    </div>
    <div class="mt-4 flex justify-end">
      <button @click="handleCreate" :disabled="saving"
        class="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white
               text-sm font-semibold rounded-lg disabled:opacity-50">
        {{ saving ? 'Creating...' : 'Create PO' }}
      </button>
    </div>
  </div>

  <!-- EXISTING PO DETAIL -->
  <div v-else-if="po" class="grid grid-cols-3 gap-5">

    <!-- Left 2/3: lines + notes -->
    <div class="col-span-2 space-y-5">

      <!-- Line items -->
      <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-slate-100 flex items-center
                    justify-between">
          <h2 class="text-sm font-semibold text-slate-900">Line items</h2>
          <button v-if="canEdit" @click="openAddLine"
            class="text-xs text-indigo-600 hover:text-indigo-500 font-medium">
            + Add item
          </button>
        </div>

        <!-- Add line form -->
        <div v-if="showAddLine"
          class="px-5 py-4 bg-slate-50 border-b border-slate-100">
          <div class="grid grid-cols-3 gap-3 mb-3">
            <div class="col-span-1">
              <label class="text-xs font-semibold text-slate-600 mb-1 block">
                Item
              </label>
              <select v-model="newLine.item" @change="handleItemSelect"
                class="w-full px-2 py-2 border border-slate-200 rounded-lg
                       text-xs bg-white focus:outline-none focus:ring-2
                       focus:ring-indigo-500">
                <option value="">Select...</option>
                <option v-for="item in availItems" :key="item.id"
                  :value="item.id">
                  {{ item.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="text-xs font-semibold text-slate-600 mb-1 block">
                Quantity
              </label>
              <input v-model="newLine.quantity" type="number" min="1"
                class="w-full px-2 py-2 border border-slate-200 rounded-lg
                       text-xs focus:outline-none focus:ring-2
                       focus:ring-indigo-500" />
            </div>
            <div>
              <label class="text-xs font-semibold text-slate-600 mb-1 block">
                Unit cost (£)
              </label>
              <input v-model="newLine.unit_cost" type="number" step="0.01"
                class="w-full px-2 py-2 border border-slate-200 rounded-lg
                       text-xs focus:outline-none focus:ring-2
                       focus:ring-indigo-500" />
            </div>
          </div>
          <div class="flex gap-2 justify-end">
            <button @click="showAddLine = false"
              class="px-3 py-1.5 text-xs text-slate-600 border border-slate-200
                     rounded-lg hover:bg-slate-100">Cancel</button>
            <button @click="handleAddLine"
              :disabled="!newLine.item || addingLine"
              class="px-3 py-1.5 text-xs text-white bg-indigo-600
                     rounded-lg hover:bg-indigo-500 disabled:opacity-50">
              {{ addingLine ? 'Adding...' : 'Add line' }}
            </button>
          </div>
        </div>

        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-100">
              <th class="px-5 py-3 text-left text-xs font-semibold
                         text-slate-500 uppercase tracking-wide">Product</th>
              <th class="px-5 py-3 text-right text-xs font-semibold
                         text-slate-500 uppercase tracking-wide">Ordered</th>
              <th class="px-5 py-3 text-right text-xs font-semibold
                         text-slate-500 uppercase tracking-wide">Received</th>
              <th class="px-5 py-3 text-right text-xs font-semibold
                         text-slate-500 uppercase tracking-wide">Outstanding</th>
              <th class="px-5 py-3 text-right text-xs font-semibold
                         text-slate-500 uppercase tracking-wide">Unit cost</th>
              <th class="px-5 py-3 text-right text-xs font-semibold
                         text-slate-500 uppercase tracking-wide">Total</th>
              <th class="px-5 py-3 text-left text-xs font-semibold
                         text-slate-500 uppercase tracking-wide">Match</th>
              <th v-if="canEdit" class="px-5 py-3 w-8"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            <tr v-for="line in po.lines" :key="line.id">
              <td class="px-5 py-3 text-sm font-medium text-slate-900">
                {{ line.item_name }}
              </td>
              <td class="px-5 py-3 text-sm text-slate-600 tabular-nums text-right">
                {{ line.quantity }}
              </td>
              <td class="px-5 py-3 text-sm text-slate-600 tabular-nums text-right">
                {{ line.quantity_received }}
              </td>
              <td class="px-5 py-3 text-sm tabular-nums text-right"
                :class="line.outstanding > 0 ? 'text-amber-600 font-semibold'
                                              : 'text-slate-400'">
                {{ line.outstanding }}
              </td>
              <td class="px-5 py-3 text-sm text-slate-600 tabular-nums text-right">
                £{{ Number(line.unit_cost).toFixed(2) }}
              </td>
              <td class="px-5 py-3 text-sm font-semibold text-slate-900
                         tabular-nums text-right">
                £{{ Number(line.line_total).toFixed(2) }}
              </td>
              <td class="px-5 py-3 text-xs font-semibold"
                :class="MATCH_COLOURS[line.match_status]">
                {{ MATCH_LABELS[line.match_status] }}
              </td>
              <td v-if="canEdit" class="px-5 py-3 text-center">
                <button @click="handleRemoveLine(line.id)"
                  class="text-slate-300 hover:text-rose-500 transition-colors">
                  ×
                </button>
              </td>
            </tr>
            <tr v-if="po.lines.length === 0">
              <td colspan="8"
                class="px-5 py-6 text-sm text-slate-400 text-center">
                No lines added yet.
              </td>
            </tr>
          </tbody>
          <tfoot class="border-t-2 border-slate-200">
            <tr>
              <td colspan="5"
                class="px-5 py-3 text-sm font-semibold text-slate-700 text-right">
                PO total
              </td>
              <td class="px-5 py-3 text-base font-bold text-slate-900
                         tabular-nums text-right">
                £{{ poTotal }}
              </td>
              <td colspan="2"></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- Notes (editable if draft) -->
      <div class="bg-white rounded-xl border border-slate-200 p-5">
        <h2 class="text-sm font-semibold text-slate-900 mb-3">Notes</h2>
        <textarea v-model="po.notes" rows="3" :disabled="!canEdit"
          class="w-full px-3 py-2 border border-slate-200 rounded-lg
                 text-sm resize-none focus:outline-none focus:ring-2
                 focus:ring-indigo-500 disabled:bg-slate-50
                 disabled:text-slate-400" />
        <div v-if="canEdit" class="mt-2 flex justify-end">
          <button @click="handleSaveMeta" :disabled="saving"
            class="px-4 py-1.5 text-xs font-semibold text-white
                   bg-indigo-600 rounded-lg hover:bg-indigo-500
                   disabled:opacity-50">
            Save changes
          </button>
        </div>
      </div>

      <!-- Goods receipts linked to this PO -->
      <div class="bg-white rounded-xl border border-slate-200 p-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-slate-900">
            Goods receipts
            <span class="text-slate-400 font-normal ml-1">
              ({{ po.receipt_count }})
            </span>
          </h2>
          <button v-if="canReceipt"
            @click="router.push(`/admin/goods-receipts/new?po=${po.id}`)"
            class="text-xs text-emerald-600 hover:text-emerald-500 font-medium">
            + New receipt
          </button>
        </div>
        <p v-if="po.receipt_count === 0" class="text-sm text-slate-400">
          No goods receipts recorded yet.
        </p>
        <button v-else
          @click="router.push(`/admin/goods-receipts?po=${po.id}`)"
          class="text-sm text-indigo-600 hover:text-indigo-500">
          View all receipts for this PO →
        </button>
      </div>
    </div>

    <!-- Right 1/3: supplier + meta -->
    <div class="space-y-5">

      <!-- Supplier -->
      <div class="bg-white rounded-xl border border-slate-200 p-5">
        <h2 class="text-sm font-semibold text-slate-900 mb-3">Supplier</h2>
        <p class="text-sm font-medium text-slate-900">{{ po.supplier_name }}</p>
        <p v-if="po.raised_by_email" class="text-xs text-slate-400 mt-1">
          Raised by {{ po.raised_by_email }}
        </p>
      </div>

      <!-- References -->
      <div class="bg-white rounded-xl border border-slate-200 p-5">
        <h2 class="text-sm font-semibold text-slate-900 mb-3">References</h2>
        <div class="space-y-3">
          <div>
            <label class="text-xs font-semibold text-slate-500
                          uppercase tracking-wide">Your PO ref</label>
            <input v-model="po.reference" type="text"
              :disabled="!canEdit"
              class="mt-1 w-full px-3 py-2 border border-slate-200
                     rounded-lg text-sm font-mono disabled:bg-slate-50
                     disabled:text-slate-400 focus:outline-none
                     focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="text-xs font-semibold text-slate-500
                          uppercase tracking-wide">Supplier ref</label>
            <input v-model="po.supplier_ref" type="text"
              :disabled="!canEdit"
              class="mt-1 w-full px-3 py-2 border border-slate-200
                     rounded-lg text-sm font-mono disabled:bg-slate-50
                     disabled:text-slate-400 focus:outline-none
                     focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="text-xs font-semibold text-slate-500
                          uppercase tracking-wide">Expected date</label>
            <input v-model="po.expected_date" type="date"
              :disabled="!canEdit"
              class="mt-1 w-full px-3 py-2 border border-slate-200
                     rounded-lg text-sm disabled:bg-slate-50
                     disabled:text-slate-400 focus:outline-none
                     focus:ring-2 focus:ring-indigo-500" />
          </div>
        </div>
        <button v-if="canEdit" @click="handleSaveMeta"
          :disabled="saving"
          class="mt-4 w-full px-3 py-2 text-xs font-semibold text-white
                 bg-indigo-600 rounded-lg hover:bg-indigo-500
                 disabled:opacity-50">
          Save references
        </button>
      </div>

      <!-- Receipt summary -->
      <div class="bg-white rounded-xl border border-slate-200 p-5">
        <h2 class="text-sm font-semibold text-slate-900 mb-3">
          Receipt progress
        </h2>
        <div class="space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-slate-500">Total ordered</span>
            <span class="font-semibold tabular-nums">
              {{ po.total_expected }} units
            </span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-slate-500">Total received</span>
            <span class="font-semibold tabular-nums text-emerald-600">
              {{ po.total_received }} units
            </span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-slate-500">Outstanding</span>
            <span class="font-semibold tabular-nums"
              :class="(po.total_expected-po.total_received) > 0
                ? 'text-amber-600' : 'text-slate-400'">
              {{ po.total_expected - po.total_received }} units
            </span>
          </div>
          <div class="mt-3 bg-slate-100 rounded-full h-2">
            <div class="bg-emerald-500 rounded-full h-2 transition-all"
              :style="`width:${po.total_expected
                ? Math.min(100,(po.total_received/po.total_expected)*100)
                : 0}%`">
            </div>
          </div>
          <p class="text-xs text-slate-400 text-right">
            {{ po.total_expected
              ? Math.round((po.total_received/po.total_expected)*100)
              : 0 }}% received
          </p>
        </div>
      </div>

    </div>
  </div>
</template>