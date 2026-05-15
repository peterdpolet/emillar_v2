// inventory/stores/useInventory.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/axios'

export const useInventoryStore = defineStore('inventory', () => {
  const items     = ref([])
  const colours   = ref([])
  const clarities = ref([])
  const cuts      = ref([])

  async function fetchLookups() {
    const [c, cl, cu] = await Promise.all([
      api.get('/inventory/colours/'),
      api.get('/inventory/clarities/'),
      api.get('/inventory/cuts/'),
    ])
    colours.value   = c.data.results
    clarities.value = cl.data.results
    cuts.value      = cu.data.results
  }

  async function createItem(payload) {
    const { data } = await api.post('/inventory/items/', payload)
    items.value.unshift(data)
    return data
  }

  async function updateItem(id, payload) {
    const { data } = await api.patch(`/inventory/items/${id}/`, payload)
    const idx = items.value.findIndex(i => i.id === id)
    if (idx !== -1) items.value[idx] = data
    return data
  }

  async function fetchItem(id) {
    const { data } = await api.get(`/inventory/items/${id}/`)
    return data
  }

  async function printLabel(itemId, soNumber) {
    const { data } = await api.post('/inventory/print-label/', {
      item_id:   itemId,
      so_number: soNumber,
    })
    return data
  }

return {
  items, colours, clarities, cuts,
  fetchLookups, createItem, updateItem, fetchItem, printLabel,
}
})