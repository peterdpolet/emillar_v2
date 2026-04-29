import { ref, watch, onUnmounted } from 'vue'
import { fetchItems } from '@/api/items'
import { useDebounceFn } from '@vueuse/core' // or implement manually

export function useItems() {
  const items = ref([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const search = ref('')
  const ordering = ref('-created_at')
  const filters = ref({})
  const loading = ref(false)
  const error = ref(null)

  let controller = null

  async function load() {
    // Cancel any in-flight request
    controller?.abort()
    controller = new AbortController()

    loading.value = true
    error.value = null

    try {
      const { data } = await fetchItems({
        page: page.value,
        pageSize: pageSize.value,
        search: search.value,
        ordering: ordering.value,
        filters: filters.value,
        signal: controller.signal,
      })

      // Matches DRF PageNumberPagination response shape:
      // { count, next, previous, results }
      items.value = data.results
      total.value = data.count
    } catch (err) {
      if (err.name !== 'CanceledError') {
        error.value = err.response?.data?.detail ?? 'Failed to load items.'
      }
    } finally {
      loading.value = false
    }
  }

  // Debounce search so it doesn't fire on every keystroke
  const debouncedLoad = useDebounceFn(load, 300)

  // Reset to page 1 when search/filters change
  watch(search, () => {
    page.value = 1
    debouncedLoad()
  })

  watch([page, pageSize, ordering, filters], load, { deep: true })

  // Clean up on component unmount
  onUnmounted(() => controller?.abort())

  return {
    items,
    total,
    page,
    pageSize,
    search,
    ordering,
    filters,
    loading,
    error,
    load,
  }
}