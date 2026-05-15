<template>
  <div class="p-6 max-w-4xl mx-auto space-y-3">
    <h1 class="text-2xl font-semibold text-gray-800 mb-6">Purchase Orders</h1>

    <!-- ── SECTION 1: Supplier ─────────────────────────────── -->
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <button @click="toggleSection('supplier')"
        class="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 transition-colors">
        <div class="flex items-center gap-3">
          <span class="text-lg">🏢</span>
          <span class="font-medium text-gray-700">Supplier</span>
          <span v-if="selectedSupplier" class="ml-2 px-2 py-0.5 bg-indigo-50 text-indigo-700 text-sm rounded-full">
            {{ selectedSupplier.bp_name }}
          </span>
        </div>
        <span class="text-gray-400 transition-transform" :class="{ 'rotate-180': openSection === 'supplier' }">▼</span>
      </button>
      <div v-if="openSection === 'supplier'" class="px-5 pb-5 border-t border-gray-100">
        <div class="mt-4">
          <input v-model="supplierSearch" type="text" placeholder="Search suppliers…"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 mb-3" />
          <div class="space-y-1 max-h-60 overflow-y-auto">
            <button v-for="s in filteredSuppliers" :key="s.bp_id"
              @click="selectSupplier(s)"
              class="w-full text-left px-3 py-2 rounded-lg text-sm hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
              :class="{ 'bg-indigo-50 text-indigo-700': selectedSupplier?.bp_id === s.bp_id }">
              {{ s.bp_name }}
            </button>
            <div v-if="filteredSuppliers.length === 0" class="text-sm text-gray-400 px-3 py-2">
              No suppliers found
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── SECTION 2: Purchase Orders ─────────────────────── -->
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden"
      :class="{ 'opacity-40 pointer-events-none': !selectedSupplier }">
      <button @click="toggleSection('orders')"
        class="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 transition-colors">
        <div class="flex items-center gap-3">
          <span class="text-lg">📋</span>
          <span class="font-medium text-gray-700">Purchase Orders</span>
          <span v-if="selectedPO" class="ml-2 px-2 py-0.5 bg-indigo-50 text-indigo-700 text-sm rounded-full">
            {{ selectedPO.reference || selectedPO.id.slice(0,8) }}
          </span>
        </div>
        <span class="text-gray-400 transition-transform" :class="{ 'rotate-180': openSection === 'orders' }">▼</span>
      </button>
      <div v-if="openSection === 'orders'" class="px-5 pb-5 border-t border-gray-100">
        <!-- Date range filter -->
        <div class="flex gap-3 mt-4 mb-3">
          <div class="flex-1">
            <label class="block text-xs text-gray-500 mb-1">From</label>
            <input v-model="dateFrom" type="date"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div class="flex-1">
            <label class="block text-xs text-gray-500 mb-1">To</label>
            <input v-model="dateTo" type="date"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div class="flex items-end">
            <button @click="fetchOrders"
              class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm rounded-lg transition-colors">
              Filter
            </button>
          </div>
        </div>
        <!-- New PO button -->
        <div class="flex justify-end mb-3">
          <button @click="startNewPO"
            class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm rounded-lg transition-colors">
            + New PO
          </button>
        </div>
        <!-- PO list -->
        <div class="space-y-1">

        <div v-for="order in poStore.pos" :key="order.id"
        @click="selectPO(order)"
        class="w-full text-left px-4 py-3 rounded-lg text-sm border border-gray-100 hover:border-indigo-200 hover:bg-indigo-50 transition-colors cursor-pointer"
        :class="{ 'border-indigo-300 bg-indigo-50': selectedPO?.id === order.id }">
        <div class="flex items-center justify-between">
            <span class="font-medium text-gray-800">{{ order.reference || order.id.slice(0,8) }}</span>
            <span :class="['px-2 py-0.5 rounded-full text-xs', statusColour(order.status)]">{{ order.status }}</span>
        </div>
        <div class="text-xs text-gray-500 mt-0.5">
            {{ order.expected_date || 'No date' }} · {{ order.currency }} {{ Number(order.total).toFixed(2) }}
        </div>
        </div>


        <div v-if="!poStore.loading && poStore.pos.length === 0"
        class="text-sm text-gray-400 px-3 py-4 text-center">
        No purchase orders found
        </div>
    </div>


      </div>
    </div>

    <!-- ── SECTION 3: Order Lines ──────────────────────────── -->
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden"
      :class="{ 'opacity-40 pointer-events-none': !selectedPO }">
      <button @click="toggleSection('lines')"
        class="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 transition-colors">
        <div class="flex items-center gap-3">
          <span class="text-lg">📦</span>
          <span class="font-medium text-gray-700">Order Lines</span>
          <span v-if="selectedPO" class="ml-2 px-2 py-0.5 bg-gray-100 text-gray-600 text-sm rounded-full">
            {{ selectedPO.lines?.length || 0 }} lines
          </span>
        </div>
        <span class="text-gray-400 transition-transform" :class="{ 'rotate-180': openSection === 'lines' }">▼</span>
      </button>
      <div v-if="openSection === 'lines'" class="border-t border-gray-100">

        <!-- ── Header edit panel ── -->
        <div v-if="selectedPO?.status === 'draft'" class="px-5 py-4 bg-slate-50 border-b border-gray-200">
          <h3 class="text-xs font-semibold text-gray-500 uppercase mb-3">PO Header</h3>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-gray-500 mb-1">Our Reference</label>
              <input v-model="selectedPO.reference" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Supplier Reference</label>
              <input v-model="selectedPO.supplier_ref" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Expected Date</label>
              <input v-model="selectedPO.expected_date" type="date"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Currency</label>
              <select v-model="selectedPO.currency"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option>GBP</option><option>USD</option><option>EUR</option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">FX Rate</label>
              <input v-model.number="selectedPO.fx_rate" type="number" step="0.0001" placeholder="e.g. 1.2700"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">FX Rate Date</label>
              <input v-model="selectedPO.fx_rate_date" type="date"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div class="col-span-2">
              <label class="block text-xs text-gray-500 mb-1">Notes</label>
              <textarea v-model="selectedPO.notes" rows="2"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
            </div>
          </div>
          <button @click="savePOHeader"
            class="mt-3 px-4 py-2 text-white text-sm rounded-lg transition-colors"
            :class="headerSaved ? 'bg-green-600' : 'bg-indigo-600 hover:bg-indigo-700'">
            {{ headerSaved ? 'Saved ✓' : 'Save Header' }}
          </button>
        </div>

        <!-- Existing lines -->
        <div v-for="line in selectedPO?.lines" :key="line.id" class="border-b border-gray-50">
          <div class="w-full flex items-center justify-between px-5 py-3 hover:bg-gray-50 transition-colors cursor-pointer"
            @click="toggleLine(line.id)">
            <div class="flex items-center gap-4 flex-1">
              <span class="text-xs text-gray-400 w-4">{{ expandedLine === line.id ? '▼' : '►' }}</span>
              <span class="text-sm font-medium text-gray-800 flex-1">{{ line.description || line.item_name }}</span>
              <span class="text-xs text-gray-500 font-mono">{{ line.item_sku }}</span>
              <span class="text-sm text-gray-600">× {{ line.quantity }}</span>
              <span class="text-sm font-medium text-gray-800">{{ selectedPO.currency }} {{ Number(line.line_total).toFixed(2) }}</span>
              <span v-if="line.total_gbp" class="text-xs text-gray-400">£{{ Number(line.total_gbp).toFixed(2) }}</span>
              <span :class="['px-2 py-0.5 rounded-full text-xs', matchColour(line.match_status)]">{{ line.match_status }}</span>
            </div>
            <button v-if="selectedPO.status === 'draft'" @click.stop="removeLine(line.id)"
              class="ml-3 text-red-400 hover:text-red-600 text-xs">✕</button>
          </div>
          <!-- Expanded line detail -->
          <div v-if="expandedLine === line.id" class="px-5 pb-4 bg-gray-50 border-t border-gray-100">
            <div class="grid grid-cols-3 gap-4 mt-3 text-sm">
              <div>
                <span class="text-xs text-gray-500 block">Supplier SKU</span>
                <span class="text-gray-800">{{ line.supplier_sku || '—' }}</span>
              </div>
              <div>
                <span class="text-xs text-gray-500 block">Unit Cost</span>
                <span class="text-gray-800">{{ selectedPO.currency }} {{ Number(line.unit_cost).toFixed(2) }}</span>
              </div>
              <div>
                <span class="text-xs text-gray-500 block">GBP Equivalent</span>
                <span class="text-gray-800">{{ line.total_gbp ? '£' + Number(line.total_gbp).toFixed(2) : '—' }}</span>
              </div>
              <div>
                <span class="text-xs text-gray-500 block">Received</span>
                <span class="text-gray-800">{{ line.quantity_received }} / {{ line.quantity }}</span>
              </div>
              <div v-if="line.description" class="col-span-2">
                <span class="text-xs text-gray-500 block">Description</span>
                <span class="text-gray-800">{{ line.description }}</span>
              </div>
            </div>
            <div class="mt-3">
              <label class="text-xs text-gray-500 block mb-1">Notes</label>
              <textarea v-model="lineNotes[line.id]" rows="3" placeholder="Add notes…"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
              <button @click="saveLineNotes(line)"
                class="mt-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs rounded-lg transition-colors">
                Save Notes
              </button>
            </div>
          </div>
        </div>

        <!-- Add new line -->
        <div v-if="selectedPO?.status === 'draft'" class="px-5 py-4 bg-gray-50 border-t border-gray-200">
          <h3 class="text-xs font-semibold text-gray-500 uppercase mb-3">Add Line</h3>
          <div class="grid grid-cols-2 gap-3">
            <div class="col-span-2">
              <label class="block text-xs text-gray-500 mb-1">Item (optional — leave blank for free-text line)</label>
              <input v-model="itemSearch" type="text" placeholder="Search items…"
                @input="searchItems"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              <div v-if="itemResults.length" class="border border-gray-200 rounded-lg mt-1 max-h-40 overflow-y-auto bg-white">
                <button v-for="item in itemResults" :key="item.id"
                  @click="selectItem(item)"
                  class="w-full text-left px-3 py-2 text-sm hover:bg-indigo-50 hover:text-indigo-700 border-b border-gray-50 last:border-0">
                  <span class="font-medium">{{ item.name }}</span>
                  <span class="text-gray-400 ml-2 font-mono text-xs">{{ item.sku }}</span>
                </button>
                <button @click="showNewItemForm = true"
                  class="w-full text-left px-3 py-2 text-sm text-emerald-600 hover:bg-emerald-50 font-medium">
                  + Create new item "{{ itemSearch }}"
                </button>
              </div>
            </div>

            <!-- New item inline form -->
            <div v-if="showNewItemForm" class="col-span-2 border border-emerald-200 rounded-lg p-3 bg-emerald-50">
              <h4 class="text-xs font-semibold text-emerald-700 uppercase mb-2">New Item</h4>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="block text-xs text-gray-500 mb-1">SKU (leave blank to auto-generate)</label>
                  <input v-model="newItem.sku" type="text"
                    class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500" />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Name</label>
                  <input v-model="newItem.name" type="text"
                    class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500" />
                </div>
                <div class="col-span-2">
                  <label class="block text-xs text-gray-500 mb-1">Description</label>
                  <input v-model="newItem.description" type="text"
                    class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500" />
                </div>
              </div>
              <div class="flex gap-2 mt-2">
                <button @click="createAndSelectItem"
                  class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs rounded-lg">
                  Create Item
                </button>
                <button @click="showNewItemForm = false"
                  class="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs rounded-lg">
                  Cancel
                </button>
              </div>
            </div>

            <div class="col-span-2">
              <label class="block text-xs text-gray-500 mb-1">Description</label>
              <input v-model="newLine.description" type="text" placeholder="Free-text description (required if no item selected)"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
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
            <div>
              <label class="block text-xs text-gray-500 mb-1">Currency</label>
              <select v-model="newLine.currency"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option>GBP</option><option>USD</option><option>EUR</option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">FX Rate</label>
              <input v-model.number="newLine.fx_rate" type="number" step="0.0001" placeholder="e.g. 1.2700"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">FX Rate Date</label>
              <input v-model="newLine.fx_rate_date" type="date"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
          <button @click="addLine" :disabled="!newLine.unit_cost && !newLine.description"
            class="mt-3 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white text-sm rounded-lg transition-colors">
            Add Line
          </button>
        </div>

        <!-- PO actions -->
        <div v-if="selectedPO" class="flex gap-3 px-5 py-4 border-t border-gray-200">
          <button v-if="selectedPO.status === 'draft'" @click="markSent"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors">
            Mark as Sent
          </button>
          <button @click="printPO"
            class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-lg transition-colors">
            🖨 Print / PDF
          </button>
          <button v-if="!['complete','cancelled'].includes(selectedPO.status)" @click="cancelPO"
            class="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-700 text-sm rounded-lg transition-colors ml-auto">
            Cancel PO
          </button>
        </div>
      </div>
    </div>

    <!-- New PO Header form (shown when creating) -->
    <div v-if="showNewPOForm" class="bg-white rounded-xl border border-emerald-200 p-6">
      <h2 class="text-sm font-semibold text-emerald-700 uppercase tracking-wide mb-4">New Purchase Order</h2>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Our Reference</label>
          <input v-model="newPO.reference" type="text" placeholder="PO-2026-001"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Supplier Reference</label>
          <input v-model="newPO.supplier_ref" type="text"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Expected Date</label>
          <input v-model="newPO.expected_date" type="date"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-600 mb-1">Currency</label>
          <select v-model="newPO.currency"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500">
            <option>GBP</option><option>USD</option><option>EUR</option>
          </select>
        </div>
        <div class="col-span-2">
          <label class="block text-xs font-medium text-gray-600 mb-1">Notes</label>
          <textarea v-model="newPO.notes" rows="2"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"></textarea>
        </div>
      </div>
      <div class="flex gap-3 mt-4">
        <button @click="createPO"
          class="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg transition-colors">
          Create Purchase Order
        </button>
        <button @click="showNewPOForm = false"
          class="px-5 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-lg transition-colors">
          Cancel
        </button>
      </div>
    </div>

    <!-- ── SECTION 4: Goods Receipts ──────────────────────── -->
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden"
      :class="{ 'opacity-40 pointer-events-none': !selectedPO }">
      <button @click="toggleSection('grn')"
        class="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 transition-colors">
        <div class="flex items-center gap-3">
          <span class="text-lg">📥</span>
          <span class="font-medium text-gray-700">Goods Receipts</span>
          <span v-if="selectedPO" class="ml-2 px-2 py-0.5 bg-gray-100 text-gray-600 text-sm rounded-full">
            {{ grns.length }} GRN{{ grns.length !== 1 ? 's' : '' }}
          </span>
        </div>
        <span class="text-gray-400 transition-transform" :class="{ 'rotate-180': openSection === 'grn' }">▼</span>
      </button>
      <div v-if="openSection === 'grn'" class="border-t border-gray-100">

        <!-- Existing GRNs -->
        <div v-for="grn in grns" :key="grn.id" class="border-b border-gray-100">
          <div class="w-full flex items-center justify-between px-5 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
            @click="toggleGRN(grn.id)">
            <div class="flex items-center gap-4 flex-1">
              <span class="text-xs text-gray-400 w-4">{{ expandedGRN === grn.id ? '▼' : '►' }}</span>
              <span class="text-sm font-medium text-gray-800">
                GRN — {{ grn.received_date }}
              </span>
              <span v-if="grn.delivery_ref" class="text-xs text-gray-500">{{ grn.delivery_ref }}</span>
              <span class="text-xs text-gray-400">{{ grn.lines.length }} line{{ grn.lines.length !== 1 ? 's' : '' }}</span>
              <span class="text-xs text-gray-400">Received by: {{ grn.received_by_name }}</span>
            </div>
          </div>

          <!-- Expanded GRN detail -->
          <div v-if="expandedGRN === grn.id" class="px-5 pb-4 bg-gray-50 border-t border-gray-100">
            <!-- GRN lines -->
            <div class="mt-3 space-y-2">
              <div v-for="line in grn.lines" :key="line.id"
                class="grid grid-cols-4 gap-4 text-sm bg-white rounded-lg px-4 py-3 border border-gray-100">
                <div>
                  <span class="text-xs text-gray-500 block">Item</span>
                  <span class="text-gray-800">{{ line.item_name || '—' }}</span>
                  <span class="text-xs text-gray-400 font-mono">{{ line.item_sku }}</span>
                </div>
                <div>
                  <span class="text-xs text-gray-500 block">Qty Received</span>
                  <span class="text-gray-800 font-medium">{{ line.quantity_received }}</span>
                </div>
                <div>
                  <span class="text-xs text-gray-500 block">Discrepancy</span>
                  <span :class="line.discrepancy !== 'none' ? 'text-amber-600 font-medium' : 'text-gray-400'">
                    {{ line.discrepancy }}
                  </span>
                </div>
                <div v-if="line.discrepancy_note">
                  <span class="text-xs text-gray-500 block">Note</span>
                  <span class="text-gray-600 text-xs italic">{{ line.discrepancy_note }}</span>
                </div>
              </div>
            </div>

            <!-- Add receipt line -->
            <div class="mt-4 border-t border-gray-200 pt-4">
              <h4 class="text-xs font-semibold text-gray-500 uppercase mb-3">Add Receipt Line</h4>
              <div class="grid grid-cols-2 gap-3">
                <div class="col-span-2">
                  <label class="block text-xs text-gray-500 mb-1">PO Line</label>
                  <select v-model="newReceiptLine.po_line"
                    class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">— Select PO line —</option>
                    <option v-for="pol in selectedPO.lines" :key="pol.id" :value="pol.id">
                      {{ pol.description || pol.item_name }} — ordered: {{ pol.quantity }}, outstanding: {{ pol.outstanding }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Qty Received</label>
                  <input v-model.number="newReceiptLine.quantity_received" type="number" min="1"
                    class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Discrepancy</label>
                  <select v-model="newReceiptLine.discrepancy"
                    class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="none">None</option>
                    <option value="short">Short delivery</option>
                    <option value="over">Over delivery</option>
                    <option value="damaged">Damaged</option>
                    <option value="wrong">Wrong item</option>
                  </select>
                </div>
                <div class="col-span-2">
                  <label class="block text-xs text-gray-500 mb-1">Discrepancy Note</label>
                  <input v-model="newReceiptLine.discrepancy_note" type="text"
                    class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                </div>
              </div>
              <button @click="addReceiptLine(grn)"
                :disabled="!newReceiptLine.po_line || !newReceiptLine.quantity_received"
                class="mt-3 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white text-sm rounded-lg transition-colors">
                Add Line
              </button>
            </div>

            <!-- GRN notes -->
            <div v-if="grn.notes" class="mt-3 text-xs text-gray-500 italic">{{ grn.notes }}</div>
          </div>
        </div>

        <div v-if="!grns.length" class="px-5 py-4 text-sm text-gray-400 text-center">
          No goods receipts yet
        </div>

        <!-- New GRN form -->
        <div class="px-5 py-4 bg-gray-50 border-t border-gray-200">
          <h3 class="text-xs font-semibold text-gray-500 uppercase mb-3">New Goods Receipt</h3>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-gray-500 mb-1">Received Date</label>
              <input v-model="newGRN.received_date" type="date"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Delivery Ref</label>
              <input v-model="newGRN.delivery_ref" type="text" placeholder="Supplier delivery note ref"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Supplier Ref</label>
              <input v-model="newGRN.supplier_ref" type="text" placeholder="Their invoice / appro ref"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Notes</label>
              <input v-model="newGRN.notes" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
          <button @click="createGRN"
            :disabled="!newGRN.received_date"
            class="mt-3 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white text-sm rounded-lg transition-colors">
            Create GRN
          </button>
        </div>

      </div>
    </div>



  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePurchaseOrderStore } from '@/features/purchasing/stores/usePurchaseOrderStore.js'
import { useSupplierListStore } from '@/features/purchasing/stores/useSupplierListStore.js'
import api from '@/api/axios.js'

const poStore       = usePurchaseOrderStore()
const supplierStore = useSupplierListStore()

onMounted(() => {
  supplierStore.fetchSuppliers()
})

// ── Section state ─────────────────────────────────────────
const openSection      = ref('supplier')
const expandedLine     = ref(null)

// ── Supplier ──────────────────────────────────────────────
const selectedSupplier = ref(null)
const supplierSearch   = ref('')

const filteredSuppliers = computed(() => {
  if (!supplierSearch.value) return supplierStore.suppliers
  const q = supplierSearch.value.toLowerCase()
  return supplierStore.suppliers.filter(s =>
    s.bp_name.toLowerCase().includes(q)
  )
})

function selectSupplier(supplier) {
  selectedSupplier.value = supplier
  selectedPO.value       = null
  openSection.value      = 'orders'
  fetchOrders()
}

// ── Purchase Orders ───────────────────────────────────────
const selectedPO   = ref(null)
const dateFrom     = ref('')
const dateTo       = ref('')
const showNewPOForm = ref(false)
const newPO = ref({
  reference: '', supplier_ref: '', expected_date: '', currency: 'GBP', notes: ''
})

async function fetchOrders() {
  const params = { supplier: selectedSupplier.value.bp_id }
  if (dateFrom.value) params.expected_date_after  = dateFrom.value
  if (dateTo.value)   params.expected_date_before = dateTo.value
  await poStore.fetchList(params)
}

function selectPO(order) {
  poStore.fetchOne(order.id).then(() => {
    selectedPO.value  = poStore.po
    openSection.value = 'lines'
    // Populate line notes
    if (poStore.po?.lines) {
      poStore.po.lines.forEach(l => {
        lineNotes.value[l.id] = l.notes || ''
      })
    }
  })
}

function startNewPO() {
  showNewPOForm.value = true
  openSection.value   = null
}

async function createPO() {
  const payload = {
    ...newPO.value,
    supplier: selectedSupplier.value.bp_id,
  }
  if (!payload.expected_date) delete payload.expected_date
  const created = await poStore.createPO(payload)
  showNewPOForm.value = false
  await fetchOrders()
  selectPO(created)
}

const headerSaved = ref(false)

async function savePOHeader() {
  await poStore.updatePO(selectedPO.value.id, {
    reference:     selectedPO.value.reference,
    supplier_ref:  selectedPO.value.supplier_ref,
    expected_date: selectedPO.value.expected_date || null,
    currency:      selectedPO.value.currency,
    fx_rate:       selectedPO.value.fx_rate || null,
    fx_rate_date:  selectedPO.value.fx_rate_date || null,
    notes:         selectedPO.value.notes,
  })
  selectedPO.value = poStore.po
  headerSaved.value = true
  setTimeout(() => headerSaved.value = false, 2000)
}



async function markSent() {
  await poStore.markSent(selectedPO.value.id)
  selectedPO.value = poStore.po
}

async function cancelPO() {
  if (confirm('Cancel this purchase order?')) {
    await poStore.cancelPO(selectedPO.value.id)
    selectedPO.value = poStore.po
  }
}

// ── Lines ─────────────────────────────────────────────────
const lineNotes    = ref({})
const newLine = ref({ 
  item: '', description: '', supplier_sku: '', 
  quantity: 1, unit_cost: '', 
  currency: 'GBP', fx_rate: '', fx_rate_date: '' 
})
const itemSearch   = ref('')
const itemResults  = ref([])
const showNewItemForm = ref(false)
const newItem      = ref({ sku: '', name: '', description: '' })

function toggleLine(lineId) {
  expandedLine.value = expandedLine.value === lineId ? null : lineId
}

let searchTimeout = null
function searchItems() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(async () => {
    if (!itemSearch.value) { itemResults.value = []; return }
    const { data } = await api.get('/purchasing/items/', {
      params: { search: itemSearch.value, page_size: 10 }
    })
    itemResults.value = data.results ?? data
  }, 300)
}

function selectItem(item) {
  newLine.value.item = item.id
  itemSearch.value   = `${item.name} (${item.sku})`
  itemResults.value  = []
  showNewItemForm.value = false
}

async function createAndSelectItem() {
  const payload = {
    ...newItem.value,
    status:   'pending',
    supplier: selectedSupplier.value.bp_id,
  }
  if (!payload.sku) delete payload.sku
  const { data } = await api.post('/purchasing/items/', payload)
  selectItem(data)
  showNewItemForm.value = false
  newItem.value = { sku: '', name: '', description: '' }
}

async function addLine() {
  await poStore.addLine(selectedPO.value.id, newLine.value)
  selectedPO.value = poStore.po
  newLine.value = { 
    item: '', description: '', supplier_sku: '', 
    quantity: 1, unit_cost: '', 
    currency: 'GBP', fx_rate: '', fx_rate_date: '' 
  }
  itemSearch.value = ''
}

async function removeLine(lineId) {
  await poStore.removeLine(selectedPO.value.id, lineId)
  selectedPO.value = poStore.po
}

async function saveLineNotes(line) {
  await api.patch(`/purchasing/purchase-orders/${selectedPO.value.id}/update-line-notes/${line.id}/`, {
    notes: lineNotes.value[line.id]
  })
}

// ── PDF ───────────────────────────────────────────────────
function printPO() {
  const token = localStorage.getItem('access')
  window.open('/api/purchasing/purchase-orders/' + selectedPO.value.id + '/pdf/?token=' + token, '_blank')
}

// ── Helpers ───────────────────────────────────────────────
function toggleSection(section) {
  openSection.value = openSection.value === section ? null : section
  if (section === 'grn' && openSection.value === 'grn') {
    fetchGRNs()
  }
}

// ── GRN ───────────────────────────────────────────────────
const grns        = ref([])
const expandedGRN = ref(null)
const newGRN      = ref({ received_date: '', delivery_ref: '', supplier_ref: '', notes: '' })
const newReceiptLine = ref({ po_line: '', quantity_received: 1, discrepancy: 'none', discrepancy_note: '' })

async function fetchGRNs() {
  if (!selectedPO.value) return
  const { data } = await api.get('/purchasing/goods-receipts/', {
    params: { purchase_order: selectedPO.value.id }
  })
  grns.value = data.results ?? data
}

function toggleGRN(grnId) {
  expandedGRN.value = expandedGRN.value === grnId ? null : grnId
  newReceiptLine.value = { po_line: '', quantity_received: 1, discrepancy: 'none', discrepancy_note: '' }
}

async function createGRN() {
  await api.post('/purchasing/goods-receipts/', {
    ...newGRN.value,
    purchase_order: selectedPO.value.id,
  })
  newGRN.value = { received_date: '', delivery_ref: '', supplier_ref: '', notes: '' }
  await fetchGRNs()
}

async function addReceiptLine(grn) {
  await api.post(`/purchasing/goods-receipts/${grn.id}/add-line/`, newReceiptLine.value)
  newReceiptLine.value = { po_line: '', quantity_received: 1, discrepancy: 'none', discrepancy_note: '' }
  await fetchGRNs()
  // Refresh PO to update outstanding quantities
  await poStore.fetchOne(selectedPO.value.id)
  selectedPO.value = poStore.po
}


function statusColour(s) {
  return { draft: 'bg-slate-100 text-slate-600', sent: 'bg-blue-50 text-blue-700',
    partial: 'bg-amber-50 text-amber-700', complete: 'bg-emerald-50 text-emerald-700',
    cancelled: 'bg-red-50 text-red-700' }[s] ?? 'bg-gray-100 text-gray-600'
}

function matchColour(s) {
  return { matched: 'bg-emerald-50 text-emerald-700', short: 'bg-amber-50 text-amber-700',
    over: 'bg-orange-50 text-orange-700', not_received: 'bg-gray-100 text-gray-600' }[s] ?? 'bg-gray-100 text-gray-600'
}

</script>
