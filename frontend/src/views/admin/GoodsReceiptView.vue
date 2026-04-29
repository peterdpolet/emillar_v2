<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchGR, createGR, addGRLine, updateGRLine } from '@/api/goodsReceipts'
import { fetchPO } from '@/api/purchaseOrders'

const route  = useRoute()
const router = useRouter()

// If ?po= param present we're creating a new GR for that PO
const poId      = computed(() => route.query.po || route.params.poId)
const isNew     = computed(() => !route.params.id)

const gr      = ref(null)
const po      = ref(null)
const loading = ref(false)
const saving  = ref(false)
const error   = ref(null)
const success = ref(null)

// New GR form
const form = ref({
  delivery_ref:  '',
  received_date: new Date().toISOString().split('T')[0],
  notes:         '',
})

// Per-line received quantities and discrepancy flags
// keyed by po_line id
const lineInputs = ref({})

const DISCREPANCY_OPTIONS = [
  { value: 'none',    label: 'None' },
  { value: 'short',   label: 'Short delivery' },
  { value: 'over',    label: 'Over delivery' },
  { value: 'damaged', label: 'Damaged' },
  { value: 'wrong',   label: 'Wrong item' },
]

const MATCH_COLOURS = {
  not_received: 'bg-slate-100 text-slate-500',
  short:        'bg-amber-50 text-amber-700',
  matched:      'bg-emerald-50 text-emerald-700',
  over:         'bg-rose-50 text-rose-700',
}
const MATCH_LABELS = {
  not_received: 'Not received',
  short:        '⚠ Short',
  matched:      '✓ Matched',
  over:         '↑ Over',
}

onMounted(async () => {
  loading.value = true
  try {
    if (!isNew.value) {
      const { data } = await fetchGR(route.params.id)
      gr.value = data
    } else if (poId.value) {
      const { data } = await fetchPO(poId.value)
      po.value = data
      // Initialise line inputs from PO lines
      po.value.lines.forEach(line => {
        lineInputs.value[line.id] = {
          quantity_received: line.outstanding,
          discrepancy:       'none',
          discrepancy_note:  '',
        }
      })
    }
  } catch (e) {
    error.value = 'Could not load data.'
  } finally {
    loading.value = false
  }
})

// Auto-set discrepancy when quantity changes
function onQuantityChange(lineId, line) {
  const input  = lineInputs.value[lineId]
  const qty    = parseInt(input.quantity_received) || 0
  const exp    = line.outstanding
  if (qty === exp)       input.discrepancy = 'none'
  else if (qty < exp)    input.discrepancy = 'short'
  else if (qty > exp)    input.discrepancy = 'over'
}

function lineStatus(lineId, line) {
  const input = lineInputs.value[lineId]
  if (!input) return 'not_received'
  const qty = parseInt(input.quantity_received) || 0
  if (qty === 0)               return 'not_received'
  if (qty < line.outstanding)  return 'short'
  if (qty === line.outstanding)return 'matched'
  return 'over'
}

const allMatched = computed(() => {
  if (!po.value) return false
  return po.value.lines.every(line => {
    const input = lineInputs.value[line.id]
    return input && parseInt(input.quantity_received) === line.outstanding
  })
})

const hasDiscrepancies = computed(() => {
  if (!po.value) return false
  return po.value.lines.some(line => {
    const input = lineInputs.value[line.id]
    return input && input.discrepancy !== 'none'
  })
})

async function handleCreateAndSave() {
  saving.value = true; error.value = null
  try {
    // Step 1: Create the GR header
    const { data: grData } = await createGR({
      purchase_order: parseInt(poId.value),
      delivery_ref:   form.value.delivery_ref,
      received_date:  form.value.received_date,
      notes:          form.value.notes,
    })

    // Step 2: Add a receipt line for each PO line
    let latest = grData
    for (const line of po.value.lines) {
      const input = lineInputs.value[line.id]
      if (!input) continue
      const { data } = await addGRLine(grData.id, {
        po_line:           line.id,
        quantity_received: parseInt(input.quantity_received) || 0,
        discrepancy:       input.discrepancy,
        discrepancy_note:  input.discrepancy_note,
      })
      latest = data
    }

    gr.value      = latest
    success.value = 'Goods receipt saved. PO lines updated.'
    // Navigate to the saved GR
    router.replace(`/admin/goods-receipts/${grData.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail ?? 'Could not save receipt.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <!-- Header -->
  <div class="flex items-center justify-between mb-6">
    <div class="flex items-center gap-3">
      <button @click="router.back()"
        class="p-2 text-slate-400 hover:text-slate-600
               hover:bg-slate-100 rounded-lg">
        ← Back
      </button>
      <div>
        <h1 class="text-xl font-bold text-slate-900">
          {{ isNew ? 'New Goods Receipt' : `GR-${String(gr?.id||0).padStart(4,'0')}` }}
        </h1>
        <p v-if="po || gr" class="text-xs text-slate-400 mt-0.5">
          {{ isNew ? `Against: ${po?.reference || 'PO-'+String(poId).padStart(4,'0')}`
            : `Supplier: ${gr?.supplier_name}` }}
        </p>
      </div>
    </div>
  </div>

  <div v-if="loading" class="text-center py-8 text-sm text-slate-400">
    Loading...
  </div>

  <!-- EXISTING GR — read-only view -->
  <div v-else-if="!isNew && gr">
    <div v-if="success"
      class="mb-4 p-3 bg-green-50 border border-green-200
             text-green-700 text-sm rounded-lg">{{ success }}</div>

    <div class="grid grid-cols-3 gap-5">
      <div class="col-span-2">
        <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div class="px-5 py-4 border-b border-slate-100">
            <h2 class="text-sm font-semibold text-slate-900">Lines received</h2>
          </div>
          <table class="w-full">
            <thead>
              <tr class="border-b border-slate-100">
                <th class="px-5 py-3 text-left text-xs font-semibold
                           text-slate-500 uppercase tracking-wide">Item</th>
                <th class="px-5 py-3 text-right text-xs font-semibold
                           text-slate-500 uppercase tracking-wide">Expected</th>
                <th class="px-5 py-3 text-right text-xs font-semibold
                           text-slate-500 uppercase tracking-wide">Received</th>
                <th class="px-5 py-3 text-left text-xs font-semibold
                           text-slate-500 uppercase tracking-wide">Discrepancy</th>
                <th class="px-5 py-3 text-left text-xs font-semibold
                           text-slate-500 uppercase tracking-wide">Match</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-for="line in gr.lines" :key="line.id">
                <td class="px-5 py-3 text-sm font-medium text-slate-900">
                  {{ line.item_name }}
                </td>
                <td class="px-5 py-3 text-sm tabular-nums text-right text-slate-600">
                  {{ line.quantity_expected }}
                </td>
                <td class="px-5 py-3 text-sm tabular-nums text-right font-semibold text-slate-900">
                  {{ line.quantity_received }}
                </td>
                <td class="px-5 py-3 text-sm text-slate-500">
                  {{ line.discrepancy_display }}
                  <span v-if="line.discrepancy_note"
                    class="text-xs text-slate-400 ml-1">
                    — {{ line.discrepancy_note }}
                  </span>
                </td>
                <td class="px-5 py-3">
                  <span :class="[
                    'inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold',
                    MATCH_COLOURS[line.quantity_received === line.quantity_expected
                      ? 'matched'
                      : line.quantity_received < line.quantity_expected
                      ? 'short' : 'over']
                  ]">
                    {{ line.quantity_received === line.quantity_expected ? '✓ Matched'
                      : line.quantity_received < line.quantity_expected ? '⚠ Short'
                      : '↑ Over' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="space-y-5">
        <div class="bg-white rounded-xl border border-slate-200 p-5">
          <h2 class="text-sm font-semibold text-slate-900 mb-3">Receipt details</h2>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-slate-500">Delivery ref</span>
              <span class="font-mono font-medium">
                {{ gr.delivery_ref || '—' }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Date received</span>
              <span>{{ new Date(gr.received_date).toLocaleDateString('en-GB') }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Received by</span>
              <span>{{ gr.received_by_email }}</span>
            </div>
          </div>
          <div v-if="gr.notes" class="mt-3 pt-3 border-t border-slate-100">
            <p class="text-xs font-semibold text-slate-500 mb-1">Notes</p>
            <p class="text-sm text-slate-600">{{ gr.notes }}</p>
          </div>
        </div>
        <button @click="router.push(`/admin/purchase-orders/${gr.purchase_order}`)"
          class="w-full px-4 py-2 text-sm border border-slate-200 rounded-lg
                 hover:bg-slate-50 text-slate-600">
          View Purchase Order →
        </button>
      </div>
    </div>
  </div>

  <!-- NEW GR — matching form -->
  <div v-else-if="isNew && po">
    <div v-if="error"
      class="mb-4 p-3 bg-red-50 border border-red-200
             text-red-700 text-sm rounded-lg">{{ error }}</div>

    <!-- Summary banner -->
    <div class="mb-5 p-4 rounded-xl border"
      :class="allMatched
        ? 'bg-emerald-50 border-emerald-200'
        : hasDiscrepancies
        ? 'bg-amber-50 border-amber-200'
        : 'bg-slate-50 border-slate-200'">
      <div class="flex items-center gap-3">
        <span class="text-lg">
          {{ allMatched ? '✓' : hasDiscrepancies ? '⚠' : '○' }}
        </span>
        <div>
          <p class="text-sm font-semibold"
            :class="allMatched ? 'text-emerald-800'
              : hasDiscrepancies ? 'text-amber-800' : 'text-slate-700'">
            {{ allMatched ? 'All lines matched'
              : hasDiscrepancies ? 'Discrepancies detected — review before saving'
              : 'Enter quantities received for each line' }}
          </p>
          <p class="text-xs mt-0.5"
            :class="allMatched ? 'text-emerald-600'
              : hasDiscrepancies ? 'text-amber-600' : 'text-slate-500'">
            {{ po.supplier_name }} ·
            {{ po.lines.length }} line{{ po.lines.length !== 1 ? 's' : '' }}
          </p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-3 gap-5">

      <!-- Matching table -->
      <div class="col-span-2">
        <div class="bg-white rounded-xl border border-slate-200 overflow-hidden mb-5">
          <div class="px-5 py-4 border-b border-slate-100">
            <h2 class="text-sm font-semibold text-slate-900">
              Match received quantities to PO lines
            </h2>
          </div>
          <table class="w-full">
            <thead>
              <tr class="border-b border-slate-100">
                <th class="px-5 py-3 text-left text-xs font-semibold
                           text-slate-500 uppercase tracking-wide">Item</th>
                <th class="px-5 py-3 text-right text-xs font-semibold
                           text-slate-500 uppercase tracking-wide">Outstanding</th>
                <th class="px-5 py-3 text-right text-xs font-semibold
                           text-slate-500 uppercase tracking-wide">Received</th>
                <th class="px-5 py-3 text-left text-xs font-semibold
                           text-slate-500 uppercase tracking-wide">Discrepancy</th>
                <th class="px-5 py-3 text-left text-xs font-semibold
                           text-slate-500 uppercase tracking-wide">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-for="line in po.lines" :key="line.id">
                <td class="px-5 py-4 text-sm font-medium text-slate-900">
                  {{ line.item_name }}
                  <p class="text-xs text-slate-400 mt-0.5">
                    Total ordered: {{ line.quantity }}
                    · Previously received: {{ line.quantity_received }}
                  </p>
                </td>
                <td class="px-5 py-4 text-sm tabular-nums text-right
                           font-semibold text-slate-900">
                  {{ line.outstanding }}
                </td>
                <td class="px-5 py-4">
                  <input
                    v-if="lineInputs[line.id]"
                    v-model="lineInputs[line.id].quantity_received"
                    type="number" min="0"
                    @input="onQuantityChange(line.id, line)"
                    class="w-20 px-2 py-1.5 border border-slate-200
                           rounded-lg text-sm tabular-nums text-right
                           focus:outline-none focus:ring-2 focus:ring-indigo-500
                           ml-auto block" />
                </td>
                <td class="px-5 py-4">
                  <div v-if="lineInputs[line.id]" class="space-y-1">
                    <select v-model="lineInputs[line.id].discrepancy"
                      class="w-full px-2 py-1.5 border border-slate-200
                             rounded-lg text-xs bg-white focus:outline-none
                             focus:ring-2 focus:ring-indigo-500">
                      <option v-for="opt in DISCREPANCY_OPTIONS"
                        :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                    <input
                      v-if="lineInputs[line.id].discrepancy !== 'none'"
                      v-model="lineInputs[line.id].discrepancy_note"
                      type="text" placeholder="Note..."
                      class="w-full px-2 py-1.5 border border-slate-200
                             rounded-lg text-xs focus:outline-none
                             focus:ring-2 focus:ring-indigo-500" />
                  </div>
                </td>
                <td class="px-5 py-4">
                  <span v-if="lineInputs[line.id]" :class="[
                    'inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold',
                    MATCH_COLOURS[lineStatus(line.id, line)]
                  ]">
                    {{ MATCH_LABELS[lineStatus(line.id, line)] }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Receipt header form -->
      <div class="space-y-5">
        <div class="bg-white rounded-xl border border-slate-200 p-5">
          <h2 class="text-sm font-semibold text-slate-900 mb-4">
            Receipt details
          </h2>
          <div class="space-y-4">
            <div>
              <label class="text-xs font-semibold text-slate-500
                            uppercase tracking-wide block mb-1">
                Delivery note ref
              </label>
              <input v-model="form.delivery_ref" type="text"
                placeholder="e.g. DN-12345"
                class="w-full px-3 py-2 border border-slate-200 rounded-lg
                       text-sm font-mono focus:outline-none focus:ring-2
                       focus:ring-indigo-500" />
            </div>
            <div>
              <label class="text-xs font-semibold text-slate-500
                            uppercase tracking-wide block mb-1">
                Date received <span class="text-rose-500">*</span>
              </label>
              <input v-model="form.received_date" type="date"
                class="w-full px-3 py-2 border border-slate-200 rounded-lg
                       text-sm focus:outline-none focus:ring-2
                       focus:ring-indigo-500" />
            </div>
            <div>
              <label class="text-xs font-semibold text-slate-500
                            uppercase tracking-wide block mb-1">Notes</label>
              <textarea v-model="form.notes" rows="3"
                class="w-full px-3 py-2 border border-slate-200 rounded-lg
                       text-sm resize-none focus:outline-none focus:ring-2
                       focus:ring-indigo-500" />
            </div>
          </div>
        </div>

        <!-- Discrepancy warning -->
        <div v-if="hasDiscrepancies"
          class="p-4 bg-amber-50 border border-amber-200 rounded-xl">
          <p class="text-sm font-semibold text-amber-800 mb-1">
            ⚠ Discrepancies found
          </p>
          <p class="text-xs text-amber-700">
            One or more lines have a discrepancy recorded. These will be
            flagged on the purchase order for supplier follow-up.
            You can still save the receipt.
          </p>
        </div>

        <button @click="handleCreateAndSave" :disabled="saving"
          class="w-full px-4 py-3 bg-indigo-600 hover:bg-indigo-500 text-white
                 text-sm font-semibold rounded-xl disabled:opacity-50
                 transition-colors">
          {{ saving ? 'Saving receipt...' : 'Save goods receipt' }}
        </button>
        <p class="text-xs text-slate-400 text-center">
          Saving will update received quantities on the purchase order
        </p>
      </div>
    </div>
  </div>
</template>
