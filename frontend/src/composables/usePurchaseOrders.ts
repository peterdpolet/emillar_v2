// src/composables/usePurchaseOrders.ts
import { ref, watch, onUnmounted } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { fetchPOs } from '@/api/purchaseOrders'
import type { PaginatedResponse, Filters } from '@/types/common'


// ── PO-specific type ──────────────────────────────────────
interface PurchaseOrder {
  id:          number
  reference:   string
  supplier:    number
  status:      'draft' | 'sent' | 'partial' | 'received' | 'cancelled'
  currency:    string
  total:       number
  created_at:  string
  [key: string]: unknown
}

export function usePurchaseOrders() {
  const pos      = ref<PurchaseOrder[]>([])
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
    controller    = new AbortController()
    loading.value = true
    error.value   = null

    try {
      const { data } = await fetchPOs<PaginatedResponse<PurchaseOrder>>({
        page:     page.value,
        pageSize: pageSize.value,
        search:   search.value,
        ordering: ordering.value,
        filters:  filters.value,
        signal:   controller.signal,
      })
      pos.value   = data.results
      total.value = data.count
    } catch (err: unknown) {
      const e = err as { name?: string; response?: { data?: { detail?: string } } }
      if (e.name !== 'CanceledError') {
        error.value = e.response?.data?.detail ?? 'Failed to load.'
      }
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