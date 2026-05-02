<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchGR, createGR, addGRLine } from '@/api/goodsReceipts'
import { fetchPO } from '@/api/purchaseOrders'

// ── Types ─────────────────────────────────────────────────
type DiscrepancyType = 'none' | 'short' | 'over' | 'damaged' | 'wrong'
type MatchStatus     = 'not_received' | 'short' | 'matched' | 'over'

interface POLine {
  id:                number
  item_name:         string
  quantity:          number
  quantity_received: number
  outstanding:       number
}

interface PurchaseOrder {
  id:            number
  reference:     string
  supplier_name: string
  lines:         POLine[]
}

interface GRLine {
  id:                  number
  item_name:           string
  quantity_expected:   number
  quantity_received:   number
  discrepancy:         DiscrepancyType
  discrepancy_display: string
  discrepancy_note:    string | null
}

interface GoodsReceipt {
  id:               number
  supplier_name:    string
  purchase_order:   number
  delivery_ref:     string | null
  received_date:    string
  received_by_email: string
  notes:            string | null
  lines:            GRLine[]
}

interface GRForm {
  delivery_ref:  string
  received_date: string
  notes:         string
}

interface LineInput {
  quantity_received: number
  discrepancy:       DiscrepancyType
  discrepancy_note:  string
}

// ── Constants ─────────────────────────────────────────────
const DISCREPANCY_OPTIONS: { value: DiscrepancyType; label: string }[] = [
  { value: 'none',    label: 'None' },
  { value: 'short',   label: 'Short delivery' },
  { value: 'over',    label: 'Over delivery' },
  { value: 'damaged', label: 'Damaged' },
  { value: 'wrong',   label: 'Wrong item' },
]

const MATCH_COLOURS: Record<MatchStatus, string> = {
  not_received: 'bg-slate-100 text-slate-500',
  short:        'bg-amber-50 text-amber-700',
  matched:      'bg-emerald-50 text-emerald-700',
  over:         'bg-rose-50 text-rose-700',
}

const MATCH_LABELS: Record<MatchStatus, string> = {
  not_received: 'Not received',
  short:        '⚠ Short',
  matched:      '✓ Matched',
  over:         '↑ Over',
}

// ── Setup ─────────────────────────────────────────────────
const route  = useRoute()
const router = useRouter()

const poId  = computed<string | null>(() =>
  (route.query.po as string) || (route.params.poId as string) || null
)
const isNew = computed<boolean>(() => !route.params.id)

const gr      = ref<GoodsReceipt | null>(null)
const po      = ref<PurchaseOrder | null>(null)
const loading = ref<boolean>(false)
const saving  = ref<boolean>(false)
const error   = ref<string | null>(null)
const success = ref<string | null>(null)

const form = ref<GRForm>({
  delivery_ref:  '',
  received_date: new Date().toISOString().split('T')[0],
  notes:         '',
})

const lineInputs = ref<Record<number, LineInput>>({})

// ── Lifecycle ─────────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  try {
    if (!isNew.value) {
      const { data } = await fetchGR(route.params.id as string)
      gr.value = data
    } else if (poId.value) {
      const { data } = await fetchPO(poId.value)
      po.value = data
      po.value.lines.forEach((line: POLine) => {
        lineInputs.value[line.id] = {
          quantity_received: line.outstanding,
          discrepancy:       'none',
          discrepancy_note:  '',
        }
      })
    }
  } catch {
    error.value = 'Could not load data.'
  } finally {
    loading.value = false
  }
})

// ── Methods ───────────────────────────────────────────────
function onQuantityChange(lineId: number, line: POLine): void {
  const input = lineInputs.value[lineId]
  const qty   = Number(input.quantity_received) || 0
  const exp   = line.outstanding
  if (qty === exp)    input.discrepancy = 'none'
  else if (qty < exp) input.discrepancy = 'short'
  else                input.discrepancy = 'over'
}

function lineStatus(lineId: number, line: POLine): MatchStatus {
  const input = lineInputs.value[lineId]
  if (!input) return 'not_received'
  const qty = Number(input.quantity_received) || 0
  if (qty === 0)               return 'not_received'
  if (qty < line.outstanding)  return 'short'
  if (qty === line.outstanding) return 'matched'
  return 'over'
}

const allMatched = computed<boolean>(() => {
  if (!po.value) return false
  return po.value.lines.every(line => {
    const input = lineInputs.value[line.id]
    return input && Number(input.quantity_received) === line.outstanding
  })
})

const hasDiscrepancies = computed<boolean>(() => {
  if (!po.value) return false
  return po.value.lines.some(line => {
    const input = lineInputs.value[line.id]
    return input && input.discrepancy !== 'none'
  })
})

async function handleCreateAndSave(): Promise<void> {
  if (!po.value || !poId.value) return
  saving.value = true
  error.value  = null

  try {
    const { data: grData } = await createGR({
      purchase_order: parseInt(poId.value),
      delivery_ref:   form.value.delivery_ref,
      received_date:  form.value.received_date,
      notes:          form.value.notes,
    })

    for (const line of po.value.lines) {
      const input = lineInputs.value[line.id]
      if (!input) continue
      await addGRLine(grData.id, {
        po_line:           line.id,
        quantity_received: Number(input.quantity_received) || 0,
        discrepancy:       input.discrepancy,
        discrepancy_note:  input.discrepancy_note,
      })
    }

    gr.value      = grData
    success.value = 'Goods receipt saved. PO lines updated.'
    router.replace(`/admin/goods-receipts/${grData.id}`)
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    error.valu