/**
 * src/stores/orders.js
 * Manages items catalogue and orders.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/axios.js'

export const useOrdersStore = defineStore('orders', () => {

  // ── Items ────────────────────────────────────────────────
  const items       = ref([])
  const itemsTotal  = ref(0)
  const itemsLoading = ref(false)

  async function fetchItems({ page = 1, search = '', ordering = 'sku' } = {}) {
    itemsLoading.value = true
    try {
      const { data } = await api.get('/orders/items/', {
        params: { page, search, ordering }
      })
      items.value      = data.results
      itemsTotal.value = data.count
    } finally {
      itemsLoading.value = false
    }
  }

  async function createItem(payload) {
    const { data } = await api.post('/orders/items/', payload)
    items.value.unshift(data)
    return data
  }

  async function updateItem(id, payload) {
    const { data } = await api.patch(`/orders/items/${id}/`, payload)
    const idx = items.value.findIndex(i => i.id === id)
    if (idx !== -1) items.value[idx] = data
    return data
  }

  async function archiveItem(id) {
    await api.delete(`/orders/items/${id}/`)
    const idx = items.value.findIndex(i => i.id === id)
    if (idx !== -1) items.value[idx].status = 'archived'
  }

  // ── Orders ───────────────────────────────────────────────
  const orders       = ref([])
  const ordersTotal  = ref(0)
  const ordersLoading = ref(false)
  const activeOrder  = ref(null)

  async function fetchOrders({ page = 1, search = '' } = {}) {
    ordersLoading.value = true
    try {
      // const { data } = await api.get('/orders/', {
      const { data } = await api.get('/partners/suppliers/', {
        params: { page, search }
      })
      orders.value      = data.results
      ordersTotal.value = data.count
    } finally {
      ordersLoading.value = false
      console.log("Ordesrs = ", orders.value)
    }
  }

  async function fetchOrder(id) {
    const { data } = await api.get(`/orders/${id}/`)
    activeOrder.value = data
    return data
  }

  async function createOrder(payload) {
    const { data } = await api.post('/orders/', payload)
    orders.value.unshift(data)
    activeOrder.value = data
    return data
  }

  async function setOrderStatus(id, status, note = '') {
    const { data } = await api.post(`/orders/${id}/set-status/`, { status, note })
    activeOrder.value = data
    // Update in list if present
    const idx = orders.value.findIndex(o => o.id === id)
    if (idx !== -1) orders.value[idx].status = status
    return data
  }

  async function addLine(orderId, payload) {
    const { data } = await api.post(`/orders/${orderId}/lines/`, payload)
    activeOrder.value = data
    return data
  }

  async function removeLine(orderId, lineId) {
    const { data } = await api.delete(`/orders/${orderId}/lines/${lineId}/`)
    activeOrder.value = data
    return data
  }

  return {
    items, itemsTotal, itemsLoading,
    fetchItems, createItem, updateItem, archiveItem,
    orders, ordersTotal, ordersLoading, activeOrder,
    fetchOrders, fetchOrder, createOrder,
    setOrderStatus, addLine, removeLine,
  }
})
