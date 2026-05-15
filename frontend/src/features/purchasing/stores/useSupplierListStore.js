import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/axios.js'

export const useSupplierListStore = defineStore('suppliers', () => {

  const suppliers      = ref([])
  const supplierLoading = ref(false)

async function fetchSuppliers() {
  if (suppliers.value.length) return
  const { data } = await api.get('/partners/suppliers/', {
    params: { page_size: 100 }
  })
  suppliers.value = data.results ?? data
}

  return { suppliers,  fetchSuppliers }
})