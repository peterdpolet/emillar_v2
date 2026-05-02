// src/composables/useItems.ts
import { ref, watch, onUnmounted } from 'vue'
import { fetchItems } from '@/api/items'
import { useDebounceFn } from '@vueuse/core'
import type { PaginatedResponse, Filters } from '@/types/common'

// ── Types ─────────────────────────────────────────────────
interface Item {
  id: number
  name: string
  sku: string
  description?: string
  price?: number
  [key: string]: unknown   // allows extra fields without errors
}

interface Filters {
  [key: string]: string | number | boolean | undefined
}

// DRF PageNumberPagination response shape
interface PaginatedResponse<T> {
  count:    number
  next:     string | null
  previous: string | null
  results:  T[]
}

export function useItems() {
  const items    = ref<Item[]>([])
  const total    = ref<number>(0)
  const page     = ref<number>(1)
  const pageSize = ref<number>(20)
  const search   = ref<string>('')
  const ordering = ref<string>('-created_at')
  const filters  = ref<Filters>({})
  const loading  = ref<boolean>(false)
  const error    = ref<string | null>(null)

  let controller: AbortController | null = null

  async function load(): Promise<void> {
    controller?.abort()
    controller = new AbortController()

    loading.value = true
    error.value   = null

    try {
      const { data } = await fetchItems<PaginatedResponse<Item>>({
        page:     page.value,
        pageSize: pageSize.value,
        search:   search.value,
        ordering: ordering.value,
        filters:  filters.value,
        signal:   controller.signal,
      })

      items.value = data.results
      total.value = data.count
    } catch (err: unknown) {
      const e = err as { name?: string; response?: { data?: { detail?: string } } }
      if (e.name !== 'CanceledError') {
        error.value = e.response?.data?.detail ?? 'Failed to load items.'
      }
    } finally {
      loading.value = false
    }
  }

  const debouncedLoad = useDebounceFn(load, 300)

  watch(search, () => {
    page.value = 1
    debouncedLoad()
  })

  watch([page, pageSize, ordering, filters], load, { deep: true })

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