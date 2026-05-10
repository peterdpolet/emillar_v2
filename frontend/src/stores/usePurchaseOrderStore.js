import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/axios.js'

export const usePurchaseOrderStore = defineStore('purchaseOrders', () => {
  const pos         = ref([])
  const po          = ref(null)
  const loading     = ref(false)
  const error       = ref(null)
  const total       = ref(0)
  const page        = ref(1)
  const pageSize    = ref(20)

  async function fetchList(params = {}) {
    loading.value = true
    error.value   = null
    try {
      const { data } = await api.get('/purchasing/purchase-orders/', {
        params: { page: page.value, page_size: pageSize.value, ...params }
      })
      pos.value   = data.results ?? data
      total.value = data.count   ?? data.length
    } catch (e) {
      error.value = e?.response?.data?.detail ?? 'Failed to load purchase orders'
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    loading.value = true
    error.value   = null
    po.value      = null
    try {
      const { data } = await api.get(`/purchasing/purchase-orders/${id}/`)
      po.value = data
    } catch (e) {
      error.value = e?.response?.data?.detail ?? 'Failed to load purchase order'
    } finally {
      loading.value = false
    }
  }

  async function createPO(payload) {
    const { data } = await api.post('/purchasing/purchase-orders/', payload)
    return data
  }

  async function updatePO(id, payload) {
    const { data } = await api.patch(`/purchasing/purchase-orders/${id}/`, payload)
    po.value = data
    return data
  }

  async function addLine(poId, linePayload) {
    const { data } = await api.post(`/purchasing/purchase-orders/${poId}/add-line/`, linePayload)
    po.value = data
    return data
  }

  async function removeLine(poId, lineId) {
    const { data } = await api.delete(`/purchasing/purchase-orders/${poId}/remove-line/${lineId}/`)
    po.value = data
    return data
  }

  async function markSent(poId) {
    const { data } = await api.post(`/purchasing/purchase-orders/${poId}/mark-sent/`)
    po.value = data
    return data
  }

  async function cancelPO(poId) {
    const { data } = await api.post(`/purchasing/purchase-orders/${poId}/cancel/`)
    po.value = data
    return data
  }

  return {
    pos, po, loading, error, total, page, pageSize,
    fetchList, fetchOne, createPO, updatePO,
    addLine, removeLine, markSent, cancelPO,
  }
})