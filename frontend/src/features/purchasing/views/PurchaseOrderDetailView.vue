<template>
  <div class="p-6 max-w-5xl mx-auto">

    <div class="flex items-center gap-3 mb-6">
      <RouterLink to="/purchase-orders" class="text-gray-400 hover:text-gray-600">←</RouterLink>
      <h1 class="text-2xl font-semibold text-gray-800">
        {{ isNew ? 'New Purchase Order' : `PO: ${po?.reference || po?.id?.slice(0,8)}` }}
      </h1>
      <span v-if="po" :class="['ml-2 px-2 py-0.5 rounded-full text-xs font-medium', statusColour(po.status)]">
        {{ po.status }}
      </span>
    </div>

    <div v-if="store.loading" class="text-center py-16 text-gray-400">Loading…</div>
    <div v-else-if="store.error" class="bg-red-50 text-red-700 p-4 rounded-lg mb-4">{{ store.error }}</div>

    <template v-if="!store.loading">
      <div class="bg-white rounded-xl border border-gray-200 p-6 mb-4">
        <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Order Details</h2>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Supplier</label>
            <select v-model="form.supplier"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="">Select supplier…</option>
              <option v-for="s in suppliers" :key="s.bp_id" :value="s.bp_id">{{ s.bp_name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Our Reference</label>
            <input v-model="form.reference" type="text" placeholder="PO-2026-001"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Supplier Reference</label>
            <input v-model="form.supplier_ref" type="text"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Expected Date</label>
            <input v-model="form.expected_date" type="date"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Currency</label>
            <select v-model="form.currency"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option>GBP</option><option>USD</option><option>EUR</option>
            </select>
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium text-gray-600 mb-1">Notes</label>
            <textarea v-model="form.notes" rows="2"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
        </div>
      </div>

      <div v-if="!isNew" class="bg-white rounded-xl border border-gray-200 p-6 mb-4">
        <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Order Lines</h2>
        <table v-if="po?.lines?.length" class="w-full text-sm mb-4">
          <thead class="border-b border-gray-100">
            <tr>
              <th class="text-left py-2 font-medium text-gray-500">Item</th>
              <th class="text-left py-2 font-medium text-gray-500">SKU</th>
              <th class="text-left py-2 font-medium text-gray-500">Supplier SKU</th>
              <th class="text-right py-2 font-medium text-gray-500">Qty</th>
              <th class="text-right py-2 font-medium text-gray-500">Received</th>
              <th class="text-right py-2 font-medium text-gray-500">Unit Cost</th>
              <th class="text-right py-2 font-medium text-gray-500">Total</th>
              <th class="text-right py-2 font-medium text-gray-500">Status</th>
              <th class="py-2"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="line in po.lines" :key="line.id">
              <td class="py-2 text-gray-800">{{ line.item_name }}</td>
              <td class="py-2 font-mono text-xs text-gray-500">{{ line.item_sku }}</td>
              <td class="py-2 font-mono text-xs text-gray-500">{{ line.supplier_sku || '—' }}</td>
              <td class="py-2 text-right">{{ line.quantity }}</td>
              <td class="py-2 text-right">{{ line.quantity_received }}</td>
              <td class="py-2 text-right">{{ Number(line.unit_cost).toFixed(2) }}</td>
              <td class="py-2 text-right font-medium">{{ Number(line.line_total).toFixed(2) }}</td>
              <td class="py-2 text-right">
                <span :class="['px-2 py-0.5 rounded-full text-xs', matchColour(line.match_status)]">
                  {{ line.match_status }}
                </span>
              </td>
              <td class="py-2 text-right">
                <button v-if="po.status === 'draft'" @click="removeLine(line.id)"
                  class="text-red-400 hover:text-red-600 text-xs">✕</button>
              </td>
            </tr>
          </tbody>
          <tfoot class="border-t border-gray-200">
            <tr>
              <td colspan="6" class="pt-3 text-right text-sm font-semibold text-gray-600">Total:</td>
              <td class="pt-3 text-right text-sm font-bold text-gray-800">
                {{ po.currency }} {{ Number(po.total).toFixed(2) }}
              </td>
              <td colspan="2"></td>
            </tr>
          </tfoot>
        </table>

        <div v-if="po?.status === 'draft'" class="border border-dashed border-gray-200 rounded-lg p-4">
          <h3 class="text-xs font-semibold text-gray-500 uppercase mb-3">Add Line</h3>
          <div class="grid grid-cols-4 gap-3">
            <div class="col-span-2">
              <label class="block text-xs text-gray-500 mb-1">Item</label>
              <select v-model="newLine.item"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="">Select item…</option>
                <option v-for="item in items" :key="item.id" :value="item.id">{{ item.name }} ({{ item.sku }})</option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Supplier SKU</label>
              <input v-model="newLine.supplier_sku" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Qty</label>
              <input v-model.number="newLine.quantity" type="number" min="1"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Unit Cost</label>
              <input v-model.number="newLine.unit_cost" type="number" step="0.01" min="0"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
          <button @click="addLine" :disabled="!newLine.item || !newLine.unit_cost"
            class="mt-3 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white text-sm rounded-lg transition-colors">
            Add Line
          </button>
        </div>
      </div>

      <div class="flex gap-3">
        <button @click="save" :disabled="saving"
          class="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white text-sm font-medium rounded-lg transition-colors">
          {{ saving ? 'Saving…' : isNew ? 'Create Purchase Order' : 'Save Changes' }}
        </button>
        <button v-if="po?.status === 'draft'" @click="markSent"
          class="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors">
          Mark as Sent
        </button>
        <button v-if="po" @click="printPO"
          class="px-5 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-lg transition-colors">
          🖨 Print / PDF
        </button>
        <button v-if="po && !['complete','cancelled'].includes(po.status)" @click="cancelPO"
          class="px-5 py-2 bg-red-50 hover:bg-red-100 text-red-700 text-sm font-medium rounded-lg transition-colors ml-auto">
          Cancel PO
        </button>
      </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { usePurchaseOrderStore } from '@/features/purchasing/stores/usePurchaseOrderStore.js'
import { useSupplierListStore } from '@/features/purchasing/stores/useSupplierListStore.js'
import api from '@/api/axios.js'

const route  = useRoute()
const router = useRouter()
const store  = usePurchaseOrderStore()
const supplierStore = useSupplierListStore()

const isNew  = computed(() => route.params.id === 'new')
const po     = computed(() => store.po)
const saving = ref(false)
const items  = ref([])

const form = ref({
  supplier: '', reference: '', supplier_ref: '',
  expected_date: '', currency: 'GBP', notes: '',
})
const newLine = ref({ item: '', supplier_sku: '', quantity: 1, unit_cost: '' })
const suppliers = computed(() => supplierStore.suppliers)

onMounted(async () => {
  await supplierStore.fetchSuppliers()
  const { data } = await api.get('/purchasing/items/')
  items.value = data.results ?? data
  if (!isNew.value) {
    await store.fetchOne(route.params.id)
    if (store.po) {
      Object.assign(form.value, {
        supplier: store.po.supplier, reference: store.po.reference,
        supplier_ref: store.po.supplier_ref, expected_date: store.po.expected_date ?? '',
        currency: store.po.currency, notes: store.po.notes,
      })
    }
  }
})

async function save() {
  saving.value = true
  try {
    const payload = { ...form.value }
    if (!payload.expected_date) delete payload.expected_date
    
    if (isNew.value) {
      const created = await store.createPO(payload)
      router.push(`/purchase-orders/${created.id}`)
    } else {
      await store.updatePO(route.params.id, payload)
    }
  } finally {
    saving.value = false
  }
}

async function addLine() {
  await store.addLine(po.value.id, newLine.value)
  newLine.value = { item: '', supplier_sku: '', quantity: 1, unit_cost: '' }
}

async function removeLine(lineId) { await store.removeLine(po.value.id, lineId) }
async function markSent() { await store.markSent(po.value.id) }
async function cancelPO() {
  if (confirm('Cancel this purchase order?')) await store.cancelPO(po.value.id)

function statusColour(s) {
  return { draft: 'bg-slate-100 text-slate-600', sent: 'bg-blue-50 text-blue-700',
    partial: 'bg-amber-50 text-amber-700', complete: 'bg-emerald-50 text-emerald-700',
    cancelled: 'bg-red-50 text-red-700' }[s] ?? 'bg-gray-100 text-gray-600'
}
function matchColour(s) {
  return { matched: 'bg-emerald-50 text-emerald-700', short: 'bg-amber-50 text-amber-700',
    over: 'bg-orange-50 text-orange-700', not_received: 'bg-gray-100 text-gray-500'
  }[s] ?? 'bg-gray-100 text-gray-500'
}

const printPO = () => {
  const token = localStorage.getItem('access')
  window.open(`/api/purchasing/purchase-orders/${po.value.id}/pdf/?token=${token}`, '_blank')
}

</script>