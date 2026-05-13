<script setup lang="ts">
import SearchForm from '@/components/filters/SearchForm.vue'
import { computed, ref, onMounted } from 'vue'
import { useCustomerListStore } from '@/features/sales/stores/useCustomerListStore.js'

const emit = defineEmits<{ (e: 'select', customer: any): void }>()

const searchFilter  = ref('')
const customerStore = useCustomerListStore()

onMounted(() => {
  customerStore.fetchCustomers()
})

const filteredItems = computed(() => {
  let items = customerStore.customers
  if (searchFilter.value) {
    const q = searchFilter.value.toLowerCase()
    items = items.filter(item => item.bp_name.toLowerCase().includes(q))
  }
  return items
})

const handleSearch = (search: string) => {
  searchFilter.value = search
}
</script>

<template>
  <div class="overflow-auto">
    <div class="bg-white relative border rounded-lg">
      <div class="flex items-center justify-between p-2">
        <SearchForm @search="handleSearch" />
      </div>
      <div v-if="customerStore.customerLoading" class="p-4 text-sm text-gray-500">
        Loading customers…
      </div>
      <table v-else class="w-full text-sm text-left">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50">
          <tr>
            <th class="px-4 py-3">Name</th>
            <th class="px-4 py-3">Ref</th>
            <th class="px-4 py-3">City</th>
            <th class="px-4 py-3">Country</th>
            <th class="px-4 py-3">Email</th>
            <th class="px-4 py-3">Tel</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in filteredItems"
            :key="item.bp_id"
            class="border-b cursor-pointer hover:bg-blue-50"
            @click="emit('select', item)"
          >
            <td class="px-4 py-3 font-medium text-gray-900">{{ item.bp_name }}</td>
            <td class="px-4 py-3 text-gray-600">{{ item.bp_int_ref }}</td>
            <td class="px-4 py-3 text-gray-600">{{ item.bp_city }}</td>
            <td class="px-4 py-3 text-gray-600">{{ item.bp_country }}</td>
            <td class="px-4 py-3 text-gray-600">{{ item.bp_email }}</td>
            <td class="px-4 py-3 text-gray-600">{{ item.bp_tel }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>