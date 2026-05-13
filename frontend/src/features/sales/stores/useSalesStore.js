import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/axios.js'

export const useSalesStore = defineStore('sales', () => {
  const selectedCustomer   = ref(null)
  const salesOrders        = ref([])
  const salesOrdersLoading = ref(false)
  const selectedSalesOrder = ref(null)
  const salesOrderLines    = ref([])
  const linesLoading       = ref(false)

  async function fetchSalesOrders() {
    if (!selectedCustomer.value) return
    salesOrdersLoading.value = true
    try {
      const { data } = await api.get('/sales/orders/', {
        params: { customer: selectedCustomer.value.bp_id }
      })
      salesOrders.value = data.results
    } finally {
      salesOrdersLoading.value = false
    }
  }

  async function fetchSalesOrderLines() {
    if (!selectedSalesOrder.value) return
    linesLoading.value = true
    try {
      const { data } = await api.get('/sales/lines/', {
        params: { sales_order: selectedSalesOrder.value.id }
      })
      salesOrderLines.value = data.results
    } finally {
      linesLoading.value = false
    }
  }

  function selectCustomer(customer) {
    selectedCustomer.value   = customer
    salesOrders.value        = []
    selectedSalesOrder.value = null
    salesOrderLines.value    = []
    fetchSalesOrders()
  }

  function selectSalesOrder(order) {
    selectedSalesOrder.value = order
    salesOrderLines.value    = []
    fetchSalesOrderLines()
  }

  return {
    selectedCustomer, salesOrders, salesOrdersLoading,
    selectedSalesOrder, salesOrderLines, linesLoading,
    selectCustomer, selectSalesOrder,
  }
})