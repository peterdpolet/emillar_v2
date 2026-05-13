import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/axios.js'

export const useCustomerListStore = defineStore('customers', () => {
  const customers       = ref([])
  const customerLoading = ref(false)

  async function fetchCustomers() {
    customerLoading.value = true
    try {
      const { data } = await api.get('/partners/customers/')
      customers.value = data.results
    } finally {
      customerLoading.value = false
    }
  }

  return { customers, customerLoading, fetchCustomers }
})