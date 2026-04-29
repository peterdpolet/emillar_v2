<script setup lang="ts">
import { ref } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'

const openItem = ref(null)

const toggleAccordion = (item) => {
  openItem.value = openItem.value === item ? null : item
}


</script>


<template>
  <div class="space-y-2">


    <div class="bg-white border border-gray-200 shadow-sm rounded-lg m-2">
      <button 
        @click="toggleAccordion(1)" 
        class="w-full px-6 py-1 text-left font-semibold flex justify-between items-center bg-blue-200 hover:bg-blue-200 transition-colors">
        <span>Stock Search</span>
        <ChevronDownIcon 
          :class="{ 'rotate-180': openItem === 1 }" 
          class="w-5 h-5 transform transition-transform" 
        />
      </button>

      <Transition name="accordion">
        <div v-show="openItem === 1" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div class="text-sm hover:bg-blue-100">
            <RouterLink class="pr-8" to="/filters">Filters</RouterLink> 
          </div>
          <div class="text-sm hover:bg-blue-100">
            <RouterLink class="pr-8" to="skus">Stock Details</RouterLink> 
          </div>


        </div>
      </Transition>
    </div>

    <div class="bg-white border border-gray-200 shadow-sm rounded-lg m-2">
      <button 
        @click="toggleAccordion(2)" 
        class="w-full px-6 py-1 text-left font-semibold flex justify-between items-center bg-blue-200 hover:bg-blue-200 transition-colors">
        <span>Customer Portal</span>
        <ChevronDownIcon 
          :class="{ 'rotate-180': openItem === 2 }" 
          class="w-5 h-5 transform transition-transform" 
        />
      </button>

      <Transition name="accordion">
        <div v-show="openItem === 2" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div class="text-sm hover:bg-blue-100">
            <RouterLink class="pr-8" to="/sales">Customers</RouterLink> 
          </div>
          <div class="text-sm hover:bg-blue-100">
            <RouterLink class="pr-8" to="/salesorders">Sales Orders</RouterLink> 
          </div>
        </div>

  
      </Transition>
    </div>



  </div>
</template>
