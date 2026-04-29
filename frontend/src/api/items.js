import api from './axios'

/**
 * Fetch a paginated, filtered range of items from DRF.
 *
 * @param {Object} params
 * @param {number} params.page         - Page number (DRF PageNumberPagination)
 * @param {number} params.pageSize     - Results per page
 * @param {string} [params.search]     - Search query (?search=)
 * @param {string} [params.ordering]   - Field to order by (?ordering=-created_at)
 * @param {Object} [params.filters]    - Any extra filter params (?status=active&category=3)
 * @param {AbortSignal} [params.signal] - For request cancellation
 */
export function fetchItems({
  page = 1,
  pageSize = 20,
  search = '',
  ordering = '-created_at',
  filters = {},
  signal,
} = {}) {
  return api.get('/items/', {
    params: {
      page,
      page_size: pageSize,
      ...(search && { search }),
      ...(ordering && { ordering }),
      ...filters,
    },
    signal,
  })
}

export function fetchItem(id) {
  return api.get(`/items/${id}/`)
}

export function createItem(data) {
  return api.post('/items/', data)
}

export function updateItem(id, data) {
  return api.patch(`/items/${id}/`, data)
}

export function deleteItem(id) {
  return api.delete(`/items/${id}/`)
}