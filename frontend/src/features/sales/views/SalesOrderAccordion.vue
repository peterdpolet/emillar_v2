<script setup lang="ts">
import { ChevronDownIcon } from '@heroicons/vue/24/outline'
import { useCustomerListStore } from '@/features/sales/stores/useCustomerListStore.js'
import { useSalesStore } from '@/features/sales/stores/useSalesStore.js'
import CustomerSelectorView from '../components/CustomerSelectorView.vue'
import SalesOrderTable from '../components/SalesOrderTable.vue'
import { ref, watch } from 'vue'

const customerStore = useCustomerListStore()
const salesStore    = useSalesStore()

const openItem = ref(null)
const toggleAccordion = (item: any) => {
  openItem.value = openItem.value === item ? null : item
}

const onCustomerSelected = (customer: any) => {
  salesStore.selectCustomer(customer)
  openItem.value = 2   // auto-advance to Sales Orders accordion
}

watch(() => salesStore.selectedSalesOrder, (val) => {
  if (val) openItem.value = 3
})

</script>

<template>
  <div class="space-y-2">
    <p class="font-bold text-xl text-center">Sales Orders</p>

    <!-- Customer -->
    <div class="bg-white border border-gray-200 shadow-sm rounded-lg m-2">
      <button
        @click="toggleAccordion(1)"
        class="w-full px-6 py-1 text-left font-semibold flex justify-between items-center bg-blue-200 hover:bg-blue-300 transition-colors">
        <span>
          Customer
          <span v-if="salesStore.selectedCustomer" class="ml-2 font-normal text-blue-800 text-sm">
            — {{ salesStore.selectedCustomer.bp_name }}
          </span>
        </span>
        <ChevronDownIcon :class="{ 'rotate-180': openItem === 1 }" class="w-5 h-5 transform transition-transform" />
      </button>
      <Transition name="accordion">
        <div v-show="openItem === 1" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <CustomerSelectorView @select="onCustomerSelected" />
        </div>
      </Transition>
    </div>

    <!-- Sales Orders -->
    <div class="bg-white border border-gray-200 shadow-sm rounded-lg m-2">
      <button
        @click="toggleAccordion(2)"
        class="w-full px-6 py-1 text-left font-semibold flex justify-between items-center bg-blue-200 hover:bg-blue-300 transition-colors">
        <span>Sales Orders</span>
        <ChevronDownIcon :class="{ 'rotate-180': openItem === 2 }" class="w-5 h-5 transform transition-transform" />
      </button>
      <Transition name="accordion">
        <div v-show="openItem === 2" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div v-if="!salesStore.selectedCustomer" class="text-sm text-gray-400 italic">
            Select a customer first.
          </div>
          <div v-else-if="salesStore.salesOrdersLoading" class="text-sm text-gray-500">
            Loading orders…
          </div>
          <div v-else class="text-sm">
            <SalesOrderTable />
          </div>
        </div>
      </Transition>
    </div>

    <!-- Sales Order Lines -->
    <div class="bg-white border border-gray-200 shadow-sm rounded-lg m-2">
      <button
        @click="toggleAccordion(3)"
        class="w-full px-6 py-1 text-left font-semibold flex justify-between items-center bg-blue-200 hover:bg-blue-300 transition-colors">
        <span>Sales Order Lines</span>
        <ChevronDownIcon :class="{ 'rotate-180': openItem === 3 }" class="w-5 h-5 transform transition-transform" />
      </button>
      <Transition name="accordion">
        <div v-show="openItem === 3" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div v-if="!salesStore.selectedSalesOrder" class="text-sm text-gray-400 italic">
            Select a sales order first.
          </div>
          <div v-else-if="salesStore.linesLoading" class="text-sm text-gray-500">
            Loading lines…
          </div>
          <div v-else class="text-sm">
            Sales Order Lines — {{ salesStore.salesOrderLines.length }} lines
          </div>
        </div>
      </Transition>
    </div>

  </div>
</template>