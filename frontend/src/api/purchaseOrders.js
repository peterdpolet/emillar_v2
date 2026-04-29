import api from './axios'

export function fetchPOs({
  page = 1, pageSize = 20, search = '',
  ordering = '-created_at', filters = {}, signal,
} = {}) {
  return api.get('/purchase-orders/', {
    params: {
      page, page_size: pageSize,
      ...(search   && { search }),
      ...(ordering && { ordering }),
      ...filters,
    },
    signal,
  })
}

export const fetchPO      = (id)       => api.get(`/purchase-orders/${id}/`)
export const createPO     = (data)     => api.post('/purchase-orders/', data)
export const updatePO     = (id, data) => api.patch(`/purchase-orders/${id}/`, data)
export const markPOSent   = (id)       => api.post(`/purchase-orders/${id}/mark-sent/`)
export const cancelPO     = (id)       => api.post(`/purchase-orders/${id}/cancel/`)
export const addPOLine    = (id, data) => api.post(`/purchase-orders/${id}/add-line/`, data)
export const removePOLine = (id, lineId) =>
  api.delete(`/purchase-orders/${id}/remove-line/${lineId}/`)

// Suppliers
export const fetchSuppliers = () =>
  api.get('/suppliers/', { params: { page_size: 200, ordering: 'name' } })
export const fetchSupplier  = (id)       => api.get(`/suppliers/${id}/`)
export const createSupplier = (data)     => api.post('/suppliers/', data)
export const updateSupplier = (id, data) => api.patch(`/suppliers/${id}/`, data)