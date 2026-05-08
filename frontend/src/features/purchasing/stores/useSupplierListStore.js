import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/axios.js'

export const useSupplierListStore = defineStore('suppliers', () => {

  const suppliers      = ref([])
  const supplierLoading = ref(false)

  async function  fetchSuppliers() {
    supplierLoading.value = true
    try {
      const { data } = await api.get('/partners/suppliers/')
      suppliers.value = data.results
    } finally {
     supplierLoading.value = false
    }
  }

  return { suppliers,  fetchSuppliers }
})