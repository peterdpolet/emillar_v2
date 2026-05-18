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

  // ── PO List ───────────────────────────────────────────────
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

  // ── Single PO ─────────────────────────────────────────────
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

  // ── Create / Update ───────────────────────────────────────
  async function createPO(payload) {
    const { data } = await api.post('/purchasing/purchase-orders/', payload)
    return data
  }

  async function updatePO(id, payload) {
    const { data } = await api.patch(`/purchasing/purchase-orders/${id}/`, payload)
    po.value = data
    return data
  }

  // ── Lines ─────────────────────────────────────────────────
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

  // ── Status actions ────────────────────────────────────────
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

  // ── Open SO lines (for PO creation) ──────────────────────
  const openSOLines  = ref([])
  const soLinesLoading = ref(false)

  async function fetchOpenSOLines() {
    soLinesLoading.value = true
    try {
      const { data } = await api.get('/purchasing/purchase-orders/open-so-lines/')
      openSOLines.value = data
    } catch (e) {
      console.error('Failed to load open SO lines', e)
    } finally {
      soLinesLoading.value = false
    }
  }

  // ── Link sales orders to a PO ─────────────────────────────
  async function linkSalesOrders(poId, soIds) {
    const { data } = await api.post(
      `/purchasing/purchase-orders/${poId}/link-sales-orders/`,
      { sales_order_ids: soIds }
    )
    po.value = data
    return data
  }

  // ── Suppliers dropdown ────────────────────────────────────
  const suppliers        = ref([])
  const suppliersLoading = ref(false)

  async function fetchSuppliers() {
    if (suppliers.value.length) return   // already loaded
    suppliersLoading.value = true
    try {
      const { data } = await api.get('/partners/suppliers/')
      suppliers.value = data.results ?? data
    } catch (e) {
      console.error('Failed to load suppliers', e)
    } finally {
      suppliersLoading.value = false
    }
  }

  return {
    // state
    pos, po, loading, error, total, page, pageSize,
    openSOLines, soLinesLoading,
    suppliers, suppliersLoading,
    // actions
    fetchList, fetchOne,
    createPO, updatePO,
    addLine, removeLine,
    markSent, cancelPO,
    fetchOpenSOLines, linkSalesOrders,
    fetchSuppliers,
  }
})