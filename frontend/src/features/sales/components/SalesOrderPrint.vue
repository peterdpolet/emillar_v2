<script setup lang="ts">
import { useSalesStore } from '@/features/sales/stores/useSalesStore.js'

const salesStore = useSalesStore()

function printOrder() {
  window.print()
}
</script>

<template>
  <div>
    <!-- Print button — hidden when printing -->
    <button
      @click="printOrder"
      class="px-4 py-1.5 bg-gray-700 text-white text-xs rounded hover:bg-gray-800 no-print">
      🖨 Print Order
    </button>

    <!-- Print view — only visible when printing -->
    <div class="print-only">
      <div class="print-page">

        <!-- Header -->
        <div class="print-header">
          <div>
            <h1 class="company-name">Ewan Millar Ltd</h1>
            <p class="company-sub">Precious Stones Trading</p>
          </div>
          <div class="text-right">
            <h2 class="doc-title">Sales Order</h2>
            <p class="doc-ref">{{ salesStore.selectedSalesOrder?.reference }}</p>
          </div>
        </div>

        <hr class="divider" />

        <!-- Order info grid -->
        <div class="info-grid">
          <div class="info-block">
            <p class="info-label">Customer</p>
            <p class="info-value">{{ salesStore.selectedSalesOrder?.customer_name }}</p>
          </div>
          <div class="info-block">
            <p class="info-label">Customer PO Ref</p>
            <p class="info-value">{{ salesStore.selectedSalesOrder?.customer_po_ref || '—' }}</p>
          </div>
          <div class="info-block">
            <p class="info-label">Date Raised</p>
            <p class="info-value">{{ salesStore.selectedSalesOrder?.raised_date }}</p>
          </div>
          <div class="info-block">
            <p class="info-label">Required By</p>
            <p class="info-value">{{ salesStore.selectedSalesOrder?.required_by || '—' }}</p>
          </div>
          <div class="info-block">
            <p class="info-label">Currency</p>
            <p class="info-value">{{ salesStore.selectedSalesOrder?.currency }}</p>
          </div>
          <div class="info-block">
            <p class="info-label">Status</p>
            <p class="info-value capitalize">{{ salesStore.selectedSalesOrder?.status }}</p>
          </div>
          <div class="info-block col-span-2">
            <p class="info-label">Raised By</p>
            <p class="info-value">{{ salesStore.selectedSalesOrder?.raised_by_name }}</p>
          </div>
          <div class="info-block col-span-2" v-if="salesStore.selectedSalesOrder?.notes">
            <p class="info-label">Notes</p>
            <p class="info-value">{{ salesStore.selectedSalesOrder?.notes }}</p>
          </div>
        </div>

        <!-- Lines table -->
        <table class="lines-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Qty</th>
              <th>Stone</th>
              <th>Type</th>
              <th>Carat Range</th>
              <th>Size mm</th>
              <th>Colour</th>
              <th>Clarity</th>
              <th>Price Range</th>
              <th>Cert</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="line in salesStore.salesOrderLines" :key="line.sol_id">
              <td>{{ line.line_number }}</td>
              <td>{{ line.quantity }}</td>
              <td class="capitalize">{{ line.stone_type }}</td>
              <td class="capitalize">{{ line.item_type }}</td>
              <td>
                <span v-if="line.min_carat || line.max_carat">
                  {{ line.min_carat || '—' }}–{{ line.max_carat || '—' }}
                </span>
                <span v-else>—</span>
              </td>
              <td>
                <span v-if="line.min_size || line.max_size">
                  {{ line.min_size || '—' }}–{{ line.max_size || '—' }}
                </span>
                <span v-else>—</span>
              </td>
              <td>{{ line.colour_spec || '—' }}</td>
              <td>{{ line.clarity_spec || '—' }}</td>
              <td>
                <span v-if="line.min_price || line.max_price">
                  {{ line.min_price || '—' }}–{{ line.max_price || '—' }}
                </span>
                <span v-else>—</span>
              </td>
              <td>{{ line.certificate_type }} {{ line.certificate_number }}</td>
              <td>{{ line.notes || '' }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Footer -->
        <div class="print-footer">
          <p>Ewan Millar Ltd — Confidential</p>
          <p>Printed: {{ new Date().toLocaleDateString('en-GB') }}</p>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
/* Screen: hide print view */
.print-only { display: none; }

/* Print: show only print view, hide button */
@media print {
  .no-print { display: none !important; }
  .print-only { display: block !important; }
}

.print-page {
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  color: #111;
  padding: 20mm;
}

.print-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.company-name { font-size: 20px; font-weight: 700; margin: 0; }
.company-sub  { font-size: 11px; color: #666; margin: 2px 0 0; }
.doc-title    { font-size: 16px; font-weight: 600; margin: 0; }
.doc-ref      { font-size: 13px; color: #444; margin: 2px 0 0; }

.divider { border: none; border-top: 1px solid #ccc; margin: 10px 0; }

.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px 16px;
  margin-bottom: 16px;
}
.col-span-2 { grid-column: span 2; }
.info-label { font-size: 9px; text-transform: uppercase; color: #888; margin: 0 0 2px; }
.info-value { font-size: 11px; font-weight: 500; margin: 0; }

.lines-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
  margin-bottom: 16px;
}
.lines-table th {
  background: #f3f4f6;
  text-align: left;
  padding: 4px 6px;
  font-size: 9px;
  text-transform: uppercase;
  border-bottom: 1px solid #ddd;
}
.lines-table td {
  padding: 4px 6px;
  border-bottom: 1px solid #eee;
  vertical-align: top;
}
.lines-table tr:last-child td { border-bottom: none; }

.print-footer {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: #999;
  border-top: 1px solid #eee;
  padding-top: 6px;
  margin-top: 8px;
}
</style>