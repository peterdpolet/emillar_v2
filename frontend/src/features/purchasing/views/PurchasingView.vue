<script setup lang="ts">
import { ChevronDownIcon } from '@heroicons/vue/24/outline'
import { useSupplierListStore } from '@/features/purchasing/stores/useSupplierListStore.js'
import { usePurchaseOrderStore } from '@/features/purchasing/stores/usePurchaseOrderStore.js'
import { ref, watch } from 'vue'
import NewPurchaseOrderForm from '../components/NewPurchaseOrderForm.vue'
import PurchaseOrderDetailView from '../components/PurchaseOrderDetailView.vue'

const supplierStore = useSupplierListStore()
const poStore       = usePurchaseOrderStore()

const openItem          = ref(null)
const selectedSupplier  = ref<any>(null)
const selectedPO        = ref<any>(null)

const toggleAccordion = (item: any) => {
  openItem.value = openItem.value === item ? null : item
}

const onSupplierSelected = (supplier: any) => {
  selectedSupplier.value = supplier
  poStore.fetchList({ supplier: supplier.bp_id })
  openItem.value = 2
}

const onPOSelected = (po: any) => {
  selectedPO.value = po
  openItem.value = 3
}

const onPOSaved = () => {
  poStore.fetchList({ supplier: selectedSupplier.value?.bp_id })
  openItem.value = 2
}
</script>

<template>
  <div class="space-y-2">
    <p class="font-bold text-xl text-center">Purchase Orders</p>

    <!-- Supplier -->
    <div class="bg-white border border-gray-200 shadow-sm rounded-lg m-2">
      <button @click="toggleAccordion(1)"
        class="w-full px-6 py-1 text-left font-semibold flex justify-between items-center bg-blue-200 hover:bg-blue-300 transition-colors">
        <span>
          Supplier
          <span v-if="selectedSupplier" class="ml-2 font-normal text-blue-800 text-sm">
            — {{ selectedSupplier.bp_name }}
          </span>
        </span>
        <ChevronDownIcon :class="{ 'rotate-180': openItem === 1 }" class="w-5 h-5 transform transition-transform" />
      </button>
      <Transition name="accordion">
        <div v-show="openItem === 1" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <SupplierSelector @select="onSupplierSelected" />
        </div>
      </Transition>
    </div>

    <!-- Purchase Orders list -->
    <div class="bg-white border border-gray-200 shadow-sm rounded-lg m-2">
      <button @click="toggleAccordion(2)"
        class="w-full px-6 py-1 text-left font-semibold flex justify-between items-center bg-blue-200 hover:bg-blue-300 transition-colors">
        <span>Purchase Orders</span>
        <ChevronDownIcon :class="{ 'rotate-180': openItem === 2 }" class="w-5 h-5 transform transition-transform" />
      </button>
      <Transition name="accordion">
        <div v-show="openItem === 2" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div v-if="!selectedSupplier" class="text-sm text-gray-400 italic">Select a supplier first.</div>
          <div v-else-if="poStore.loading" class="text-sm text-gray-500">Loading…</div>
          <div v-else class="text-sm">
            <div v-if="!poStore.pos.length" class="text-gray-400 italic">No purchase orders yet.</div>
            <table v-else class="w-full text-sm">
              <thead class="text-xs text-gray-600 uppercase bg-gray-100">
                <tr>
                  <th class="px-3 py-2 text-left">Reference</th>
                  <th class="px-3 py-2 text-left">Status</th>
                  <th class="px-3 py-2 text-left">Currency</th>
                  <th class="px-3 py-2 text-left">Total</th>
                  <th class="px-3 py-2 text-left">Expected</th>
                  <th class="px-3 py-2 text-left">Raised</th>
                  <th class="px-3 py-2"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="po in poStore.pos" :key="po.id"
                  class="border-t hover:bg-gray-50 cursor-pointer"
                  :class="{ 'bg-blue-50': selectedPO?.id === po.id }"
                  @click="onPOSelected(po)">
                  <td class="px-3 py-2 font-medium">{{ po.reference || '—' }}</td>
                  <td class="px-3 py-2 capitalize">{{ po.status }}</td>
                  <td class="px-3 py-2">{{ po.currency }}</td>
                  <td class="px-3 py-2">{{ po.total }}</td>
                  <td class="px-3 py-2">{{ po.expected_date || '—' }}</td>
                  <td class="px-3 py-2">{{ po.raised_date }}</td>
                  <td class="px-3 py-2">
                    <button @click.stop="onPOSelected(po)"
                      class="text-blue-500 hover:text-blue-700 text-xs">View</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </Transition>
    </div>

    <!-- PO Detail -->
    <div class="bg-white border border-gray-200 shadow-sm rounded-lg m-2">
      <button @click="toggleAccordion(3)"
        class="w-full px-6 py-1 text-left font-semibold flex justify-between items-center bg-blue-200 hover:bg-blue-300 transition-colors">
        <span>
          PO Detail
          <span v-if="selectedPO" class="ml-2 font-normal text-blue-800 text-sm">
            — {{ selectedPO.reference || selectedPO.id }}
          </span>
        </span>
        <ChevronDownIcon :class="{ 'rotate-180': openItem === 3 }" class="w-5 h-5 transform transition-transform" />
      </button>
      <Transition name="accordion">
        <div v-show="openItem === 3" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div v-if="!selectedPO" class="text-sm text-gray-400 italic">Select a PO first.</div>
          <PurchaseOrderDetailView v-else :po-id="selectedPO.id"
            @updated="poStore.fetchList({ supplier: selectedSupplier?.bp_id })" />
        </div>
      </Transition>
    </div>

    <!-- New PO -->
    <div v-if="selectedSupplier" class="bg-white border border-gray-200 shadow-sm rounded-lg m-2">
      <button @click="toggleAccordion(4)"
        class="w-full px-6 py-1 text-left font-semibold flex justify-between items-center bg-green-200 hover:bg-green-300 transition-colors">
        <span>+ New Purchase Order</span>
        <ChevronDownIcon :class="{ 'rotate-180': openItem === 4 }" class="w-5 h-5 transform transition-transform" />
      </button>
      <Transition name="accordion">
        <div v-show="openItem === 4" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <NewPurchaseOrderForm :supplier="selectedSupplier" @saved="onPOSaved" />
        </div>
      </Transition>
    </div>

  </div>
</template>