import { ref, watch, onUnmounted } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { fetchPOs } from '@/api/purchaseOrders'

export function usePurchaseOrders() {
  const pos      = ref([])
  const total    = ref(0)
  const page     = ref(1)
  const pageSize = ref(20)
  const search   = ref('')
  const ordering = ref('-created_at')
  const filters  = ref({})
  const loading  = ref(false)
  const error    = ref(null)

  let controller = null

  async function load() {
    controller?.abort()
    controller    = new AbortController()
    loading.value = true
    error.value   = null
    try {
      const { data } = await fetchPOs({
        page: page.value, pageSize: pageSize.value,
        search: search.value, ordering: ordering.value,
        filters: filters.value, signal: controller.signal,
      })
      pos.value   = data.results
      total.value = data.count
    } catch (err) {
      if (err.name !== 'CanceledError')
        error.value = err.response?.data?.detail ?? 'Failed to load.'
    } finally {
      loading.value = false
    }
  }

  const debouncedLoad = useDebounceFn(load, 300)
  watch(search, () => { page.value = 1; debouncedLoad() })
  watch([page, pageSize, ordering, filters], load, { deep: true })
  onUnmounted(() => controller?.abort())

  return { pos, total, page, pageSize, search,
           ordering, filters, loading, error, load }
}