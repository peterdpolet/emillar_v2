import api from './axios'

export const fetchGRs    = (poId) =>
  api.get('/goods-receipts/', {
    params: { purchase_order: poId, page_size: 100 }
  })
export const fetchGR     = (id)       => api.get(`/goods-receipts/${id}/`)
export const createGR    = (data)     => api.post('/goods-receipts/', data)
export const addGRLine   = (id, data) => api.post(`/goods-receipts/${id}/add-line/`, data)
export const updateGRLine = (id, lineId, data) =>
  api.patch(`/goods-receipts/${id}/update-line/${lineId}/`, data)