<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import api from '@/api/axios.js'

const loading    = ref(true)
const approIn    = ref<any[]>([])
const approOut   = ref<any[]>([])
const error      = ref('')

const fetchAppro = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/inventory/movements/appro-summary/')
    approIn.value  = data.appro_in
    approOut.value = data.appro_out
  } catch (e: any) {
    error.value = 'Failed to load appro data'
  } finally {
    loading.value = false
  }
}

const totalApproInValue = computed(() =>
  approIn.value.reduce((sum, m) => sum + Number(m.value || 0), 0).toFixed(2)
)
const totalApproOutValue = computed(() =>
  approOut.value.reduce((sum, m) => sum + Number(m.value || 0), 0).toFixed(2)
)
const fmt = (v: any) => (v === null || v === undefined || v === '') ? '—' : v

const showForm      = ref(false)
const saving        = ref(false)
const openApproRefs = ref<string[]>([])

const fetchOpenApproRefs = async () => {
  const { data } = await api.get('/inventory/movements/open-appro-refs/')
  openApproRefs.value = data
}

const form = ref({
  transaction_type:   '',
  date:               new Date().toISOString().split('T')[0],
  parcel_description: '',
  quantity:           0,
  weight_carats:      '',
  unit_value:         '',
  currency:           'GBP',
  notes:              '',
  appro_reference:    '',
})

watch(showForm, (val) => {
  if (val) fetchOpenApproRefs()
})

const saveMovement = async () => {
  if (!form.value.transaction_type || !form.value.date) return
  saving.value = true
  try {
    await api.post('/inventory/movements/', {
      ...form.value,
      weight_carats: form.value.weight_carats || null,
      unit_value:    form.value.unit_value    || null,
    })
    await fetchAppro()
    showForm.value = false
    form.value = {
      transaction_type: '', date: new Date().toISOString().split('T')[0],
      parcel_description: '', quantity: 0,
      weight_carats: '', unit_value: '', currency: 'GBP',
      notes: '', appro_reference: '',
    }
  } finally {
    saving.value = false
  }
}

onMounted(fetchAppro)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-gray-800">Appro Dashboard</h1>
      <button @click="fetchAppro"
        class="text-xs px-3 py-1.5 border border-gray-300 rounded hover:bg-gray-50">
        ↻ Refresh
      </button>
    </div>

    <div v-if="loading" class="text-sm text-gray-400 italic p-4">Loading…</div>
    <div v-else-if="error" class="text-sm text-red-500 p-4">{{ error }}</div>

    <div v-else class="grid grid-cols-2 gap-4">

      <!-- ── On Appro FROM Suppliers ── -->
      <div class="bg-white border border-blue-200 rounded-lg overflow-hidden">
        <div class="bg-blue-50 border-b border-blue-200 px-4 py-3 flex items-center justify-between">
          <div>
            <p class="text-sm font-semibold text-blue-800">On Appro from Suppliers</p>
            <p class="text-xs text-blue-600 mt-0.5">Items in your possession, not yet purchased</p>
          </div>
          <div class="text-right">
            <p class="text-xs text-blue-500">Total value</p>
            <p class="text-sm font-bold text-blue-800">£{{ totalApproInValue }}</p>
          </div>
        </div>

        <div v-if="!approIn.length" class="p-4 text-sm text-gray-400 italic">
          No items on appro from suppliers.
        </div>

        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-3 py-2 text-left">Item / Parcel</th>
              <th class="px-3 py-2 text-left">Ref</th>
              <th class="px-3 py-2 text-left">Supplier</th>
              <th class="px-3 py-2 text-left">Qty / Weight</th>
              <th class="px-3 py-2 text-left">Value</th>
              <th class="px-3 py-2 text-left">Date</th>
              <th class="px-3 py-2 text-left">PO</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in approIn" :key="m.id" class="border-t hover:bg-gray-50">
              <td class="px-3 py-2">
                <p class="font-medium text-gray-800">{{ m.item_name || m.parcel_description || '—' }}</p>
                <p v-if="m.item_sku" class="text-xs text-gray-400">{{ m.item_sku }}</p>
              </td>
              <td class="px-3 py-2 text-xs text-gray-400">{{ fmt(m.appro_reference) }}</td>
              <td class="px-3 py-2 text-gray-600">{{ fmt(m.supplier_name) }}</td>
              <td class="px-3 py-2 text-gray-600">
                <span v-if="m.weight_carats">{{ m.weight_carats }} ct</span>
                <span v-else>{{ m.quantity }}</span>
              </td>
              <td class="px-3 py-2 font-medium text-gray-700">
                {{ m.currency }} {{ fmt(m.value) }}
              </td>
              <td class="px-3 py-2 text-gray-500 text-xs">{{ m.date }}</td>
              <td class="px-3 py-2 text-gray-400 text-xs">{{ fmt(m.po_reference) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ── On Appro WITH Customers ── -->
      <div class="bg-white border border-amber-200 rounded-lg overflow-hidden">
        <div class="bg-amber-50 border-b border-amber-200 px-4 py-3 flex items-center justify-between">
          <div>
            <p class="text-sm font-semibold text-amber-800">Out with Customers on Appro</p>
            <p class="text-xs text-amber-600 mt-0.5">Items with customers, awaiting selection</p>
          </div>
          <div class="text-right">
            <p class="text-xs text-amber-500">Total value</p>
            <p class="text-sm font-bold text-amber-800">£{{ totalApproOutValue }}</p>
          </div>
        </div>

        <div v-if="!approOut.length" class="p-4 text-sm text-gray-400 italic">
          No items currently out with customers.
        </div>

        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th class="px-3 py-2 text-left">Item / Parcel</th>
              <th class="px-3 py-2 text-left">Ref</th>
              <th class="px-3 py-2 text-left">Customer</th>
              <th class="px-3 py-2 text-left">Qty / Weight</th>
              <th class="px-3 py-2 text-left">Value</th>
              <th class="px-3 py-2 text-left">Date</th>
              <th class="px-3 py-2 text-left">Memo</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in approOut" :key="m.id" class="border-t hover:bg-gray-50">
              <td class="px-3 py-2">
                <p class="font-medium text-gray-800">{{ m.item_name || m.parcel_description || '—' }}</p>
                <p v-if="m.item_sku" class="text-xs text-gray-400">{{ m.item_sku }}</p>
              </td>
              <td class="px-3 py-2 text-xs text-gray-400">{{ fmt(m.appro_reference) }}</td>
              <td class="px-3 py-2 text-gray-600">{{ fmt(m.customer_name) }}</td>
              <td class="px-3 py-2 text-gray-600">
                <span v-if="m.weight_carats">{{ m.weight_carats }} ct</span>
                <span v-else>{{ m.quantity }}</span>
              </td>
              <td class="px-3 py-2 font-medium text-gray-700">
                {{ m.currency }} {{ fmt(m.value) }}
              </td>
              <td class="px-3 py-2 text-gray-500 text-xs">{{ m.date }}</td>
              <td class="px-3 py-2 text-gray-400 text-xs">{{ fmt(m.memo_reference) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>

    <!-- ── Record New Movement ── -->
    <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <button @click="showForm = !showForm"
        class="w-full px-4 py-2 text-left text-sm font-semibold text-gray-600 bg-gray-50 hover:bg-gray-100 flex justify-between items-center">
        <span>+ Record Stock Movement</span>
        <span>{{ showForm ? '▲' : '▼' }}</span>
      </button>

      <div v-if="showForm" class="p-4 space-y-3">

        <!-- Row 1: Type, Appro Ref, Date, Currency -->
        <div class="grid grid-cols-4 gap-3">
          <div>
            <label class="block text-xs text-gray-500 mb-1">Transaction Type</label>
            <select v-model="form.transaction_type"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm">
              <option value="">— Select —</option>
              <option value="appro_in">Received from supplier on appro</option>
              <option value="appro_out">Issued to customer on appro</option>
              <option value="appro_return_in">Returned from customer</option>
              <option value="appro_return_out">Returned to supplier</option>
              <option value="purchased">Purchased from supplier</option>
              <option value="sold">Sold to customer</option>
              <option value="opening">Opening stock</option>
              <option value="adjustment">Manual adjustment</option>
            </select>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Appro Reference</label>
            <template v-if="form.transaction_type === 'appro_in'">
              <input type="text" value="Auto-generated" readonly
                class="w-full border border-gray-200 rounded px-2 py-1.5 text-sm bg-gray-50 text-gray-400" />
            </template>
            <template v-else-if="['appro_out','appro_return_in','appro_return_out','purchased','sold'].includes(form.transaction_type)">
              <select v-model="form.appro_reference"
                class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm">
                <option value="">— Select —</option>
                <option v-for="ref in openApproRefs" :key="ref" :value="ref">{{ ref }}</option>
              </select>
            </template>
            <template v-else>
              <input type="text" disabled placeholder="—"
                class="w-full border border-gray-200 rounded px-2 py-1.5 text-sm bg-gray-50 text-gray-400" />
            </template>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Date</label>
            <input v-model="form.date" type="date"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Currency</label>
            <select v-model="form.currency"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm">
              <option>GBP</option><option>USD</option><option>EUR</option>
            </select>
          </div>
        </div>

        <!-- Row 2: Parcel Description, Quantity, Weight, Unit Value -->
        <div class="grid grid-cols-4 gap-3">
          <div class="col-span-2">
            <label class="block text-xs text-gray-500 mb-1">Parcel Description (if no SKU)</label>
            <input v-model="form.parcel_description" type="text"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Quantity</label>
            <input v-model.number="form.quantity" type="number" min="0"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Weight (carats)</label>
            <input v-model="form.weight_carats" type="number" step="0.001"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
        </div>

        <!-- Row 3: Unit Value, Notes -->
        <div class="grid grid-cols-4 gap-3">
          <div>
            <label class="block text-xs text-gray-500 mb-1">Unit Value</label>
            <input v-model="form.unit_value" type="number" step="0.01"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
          <div class="col-span-3">
            <label class="block text-xs text-gray-500 mb-1">Notes</label>
            <input v-model="form.notes" type="text"
              class="w-full border border-gray-300 rounded px-2 py-1.5 text-sm" />
          </div>
        </div>

        <div class="flex gap-2">
          <button @click="saveMovement" :disabled="saving"
            class="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-40">
            {{ saving ? 'Saving…' : 'Save Movement' }}
          </button>
          <button @click="showForm = false"
            class="px-4 py-1.5 border border-gray-300 text-sm rounded hover:bg-gray-50">
            Cancel
          </button>
        </div>

      </div>
    </div>

  </div>
</template>