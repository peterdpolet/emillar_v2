<template>
  <!-- Backdrop -->
  <div class="fixed inset-0 bg-black/40 z-40 flex items-center justify-center p-4"
    @click.self="$emit('close')">

    <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col z-50">

      <!-- Modal header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 flex-shrink-0">
        <h2 class="font-bold text-slate-800 text-lg">New Order</h2>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Modal body -->
      <div class="flex-1 overflow-y-auto px-6 py-5 space-y-6">

        <!-- Shipping details -->
        <div class="space-y-4">
          <h3 class="text-sm font-semibold text-slate-700">Shipping details</h3>
          <div class="grid grid-cols-1 gap-3">
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">Recipient name</label>
              <input v-model="form.shipping_name" type="text"
                class="input" placeholder="Jane Smith" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">Address</label>
              <textarea v-model="form.shipping_addr" rows="3"
                class="input resize-none" placeholder="123 Example Street&#10;London&#10;SW1A 1AA" />
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">Notes (optional)</label>
              <input v-model="form.notes" type="text"
                class="input" placeholder="Any special instructions…" />
            </div>
          </div>
        </div>

        <!-- Line items -->
        <div class="space-y-3">
          <h3 class="text-sm font-semibold text-slate-700">Order lines</h3>

          <!-- Existing lines -->
          <div v-if="lines.length" class="border border-slate-200 rounded-lg overflow-hidden">
            <table class="w-full table-fixed text-sm">
              <colgroup>
                <col><col class="w-16"><col class="w-28"><col class="w-10">
              </colgroup>
              <thead class="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th class="text-left px-3 py-2 text-xs font-semibold text-slate-500">Item</th>
                  <th class="text-right px-3 py-2 text-xs font-semibold text-slate-500">Qty</th>
                  <th class="text-right px-3 py-2 text-xs font-semibold text-slate-500">Price</th>
                  <th class="px-3 py-2"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(line, idx) in lines" :key="idx"
                  class="border-b border-slate-100 last:border-0">
                  <td class="px-3 py-2">
                    <p class="font-medium text-slate-800 truncate">{{ line.itemName }}</p>
                    <p class="text-xs text-slate-400 font-mono">{{ line.itemSku }}</p>
                  </td>
                  <td class="px-3 py-2 text-right text-slate-600">{{ line.quantity }}</td>
                  <td class="px-3 py-2 text-right font-medium text-slate-800">
                    £{{ (line.price * line.quantity).toFixed(2) }}
                  </td>
                  <td class="px-3 py-2 text-center">
                    <button @click="removeLine(idx)"
                      class="text-slate-300 hover:text-red-400 transition-colors">
                      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <p v-else class="text-sm text-slate-400 text-center py-3 border border-dashed border-slate-200 rounded-lg">
            No lines added yet
          </p>

          <!-- Order total -->
          <div v-if="lines.length" class="text-right text-sm font-bold text-slate-800">
            Total: £{{ orderTotal }}
          </div>

          <!-- Add line form -->
          <div class="border border-slate-200 rounded-lg p-4 space-y-3 bg-slate-50">
            <p class="text-xs font-semibold text-slate-600">Add a line</p>

            <!-- Item search -->
            <div>
              <label class="block text-xs font-medium text-slate-600 mb-1">Item</label>
              <div class="relative">
                <input v-model="itemSearch" type="text"
                  class="input pr-8"
                  placeholder="Search by SKU or name…"
                  @focus="showDropdown = true"
                  @blur="hideDropdownDelayed" />
                <div v-if="showDropdown && filteredItems.length"
                  class="absolute z-10 top-full left-0 right-0 mt-1 bg-white border border-slate-200
                         rounded-lg shadow-lg max-h-48 overflow-y-auto">
                  <button v-for="item in filteredItems" :key="item.id"
                    @mousedown.prevent="selectItem(item)"
                    class="w-full text-left px-3 py-2.5 hover:bg-brand-50 border-b border-slate-100 last:border-0">
                    <p class="text-sm font-medium text-slate-800">{{ item.name }}</p>
                    <p class="text-xs text-slate-400 font-mono">{{ item.sku }} · £{{ Number(item.price).toFixed(2) }}</p>
                  </button>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-slate-600 mb-1">Quantity</label>
                <input v-model.number="newLine.quantity" type="number" min="1"
                  class="input" />
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-600 mb-1">Unit price (£)</label>
                <input v-model.number="newLine.price" type="number" step="0.01" min="0"
                  class="input" />
              </div>
            </div>

            <button @click="addLine" :disabled="!newLine.item"
              class="w-full bg-slate-800 hover:bg-slate-700 disabled:opacity-40
                     text-white text-sm font-medium rounded-lg py-2 transition-colors">
              Add line
            </button>
          </div>
        </div>

      </div>

      <!-- Modal footer -->
      <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-200 flex-shrink-0">
        <button @click="$emit('close')"
          class="text-sm text-slate-500 hover:text-slate-700 font-medium px-4 py-2">
          Cancel
        </button>
        <button @click="submit" :disabled="!lines.length || submitting"
          class="bg-brand-600 hover:bg-brand-700 disabled:opacity-50
                 text-white text-sm font-medium rounded-lg px-5 py-2 transition-colors">
          {{ submitting ? 'Creating…' : 'Create order' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useOrdersStore } from '@/stores/orders.js'

const emit = defineEmits(['close', 'created'])
const orders = useOrdersStore()

// ── Form state ────────────────────────────────────────────
const form = ref({
  shipping_name: '',
  shipping_addr: '',
  notes: '',
})

// ── Lines ─────────────────────────────────────────────────
const lines = ref([])

const newLine = ref({
  item: null,
  quantity: 1,
  price: 0,
})

const orderTotal = computed(() =>
  lines.value.reduce((sum, l) => sum + l.price * l.quantity, 0).toFixed(2)
)

function addLine() {
  if (!newLine.value.item) return
  lines.value.push({
    item:     newLine.value.item.id,
    itemName: newLine.value.item.name,
    itemSku:  newLine.value.item.sku,
    quantity: newLine.value.quantity,
    price:    newLine.value.price,
  })
  // Reset line form
  newLine.value = { item: null, quantity: 1, price: 0 }
  itemSearch.value = ''
}

function removeLine(idx) {
  lines.value.splice(idx, 1)
}

// ── Item search ───────────────────────────────────────────
const itemSearch   = ref('')
const showDropdown = ref(false)

const filteredItems = computed(() => {
  const q = itemSearch.value.toLowerCase()
  if (!q) return orders.items.slice(0, 10)
  return orders.items.filter(i =>
    i.sku.toLowerCase().includes(q) ||
    i.name.toLowerCase().includes(q)
  ).slice(0, 10)
})

function selectItem(item) {
  newLine.value.item  = item
  newLine.value.price = Number(item.price)
  itemSearch.value    = `${item.sku} — ${item.name}`
  showDropdown.value  = false
}

function hideDropdownDelayed() {
  setTimeout(() => { showDropdown.value = false }, 150)
}

// ── Submit ────────────────────────────────────────────────
const submitting = ref(false)

async function submit() {
  if (!lines.value.length) return
  submitting.value = true
  try {
    const payload = {
      ...form.value,
      lines: lines.value.map(l => ({
        item:     l.item,
        quantity: l.quantity,
        price:    l.price,
      }))
    }
    const order = await orders.createOrder(payload)
    emit('created', order)
  } catch (e) {
    console.error('Create order failed:', e)
  } finally {
    submitting.value = false
  }
}

// Load items for the picker
orders.fetchItems({ ordering: 'sku' })
</script>

<style scoped>

@reference "../assets/main.css";

.input {
  @apply w-full border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white
         focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent;
}
</style>
