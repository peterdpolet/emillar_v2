<template>
  <div class="space-y-8">

    <!-- Hero -->
    <div class="bg-gradient-to-br from-indigo-600 to-indigo-800 rounded-2xl p-8 text-white">
      <div class="max-w-2xl">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
            <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M21 11.25v8.25a1.5 1.5 0 01-1.5 1.5H5.25a1.5 1.5 0 01-1.5-1.5v-8.25M12 4.875A2.625 2.625 0 1014.25 7.5H12m0-2.625V7.5m0-2.625A2.625 2.625 0 109.75 7.5H12m0 0V21m-8.625-9.75h18c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125h-18c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"/>
            </svg>
          </div>
          <div>
            <h1 class="text-2xl font-bold leading-tight">Ewan Millar Ltd</h1>
            <p class="text-indigo-200 text-sm">Precious Stones Trading Platform</p>
          </div>
        </div>
        <p class="text-indigo-100 text-base leading-relaxed max-w-xl">
          A specialist B2B trading platform for the global precious stones industry.
          Manage your sales orders, purchase orders, supplier relationships and stock
          on approval — all in one place.
        </p>
        <div class="flex gap-3 mt-6">
          <RouterLink to="/sales-orders-v2"
            class="px-4 py-2 bg-white text-indigo-700 font-medium text-sm rounded-lg hover:bg-indigo-50 transition-colors">
            Sales Orders →
          </RouterLink>
          <RouterLink to="/purchase-orders"
            class="px-4 py-2 bg-indigo-500 text-white font-medium text-sm rounded-lg hover:bg-indigo-400 transition-colors">
            Purchase Orders →
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Quick stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl border border-slate-200 p-5">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">Sales Orders</p>
        <p class="text-2xl font-bold text-slate-800">—</p>
        <p class="text-xs text-slate-400 mt-1">Active orders</p>
      </div>
      <div class="bg-white rounded-xl border border-slate-200 p-5">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">Purchase Orders</p>
        <p class="text-2xl font-bold text-slate-800">—</p>
        <p class="text-xs text-slate-400 mt-1">Open POs</p>
      </div>
      <div class="bg-white rounded-xl border border-slate-200 p-5">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">On Appro</p>
        <p class="text-2xl font-bold text-slate-800">—</p>
        <p class="text-xs text-slate-400 mt-1">Items on approval</p>
      </div>
      <div class="bg-white rounded-xl border border-slate-200 p-5">
        <p class="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">Suppliers</p>
        <p class="text-2xl font-bold text-slate-800">—</p>
        <p class="text-xs text-slate-400 mt-1">Active suppliers</p>
      </div>
    </div>

    <!-- Quick access -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

      <div class="bg-white rounded-xl border border-slate-200 p-6">
        <div class="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center mb-3">
          <svg class="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z"/>
          </svg>
        </div>
        <h3 class="font-semibold text-slate-800 text-sm mb-1">Sales Orders</h3>
        <p class="text-xs text-slate-400 mb-4">Manage customer RFQs, quotes and sales orders</p>
        <RouterLink to="/sales-orders-v2"
          class="text-xs font-medium text-indigo-600 hover:text-indigo-800">
          View Sales Orders →
        </RouterLink>
      </div>

      <div class="bg-white rounded-xl border border-slate-200 p-6">
        <div class="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center mb-3">
          <svg class="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 00-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 00-16.536-1.84M7.5 14.25L5.106 5.272M6 20.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm12.75 0a.75.75 0 11-1.5 0 .75.75 0 011.5 0z"/>
          </svg>
        </div>
        <h3 class="font-semibold text-slate-800 text-sm mb-1">Purchase Orders</h3>
        <p class="text-xs text-slate-400 mb-4">Raise POs, track deliveries and match invoices</p>
        <RouterLink to="/purchase-orders"
          class="text-xs font-medium text-indigo-600 hover:text-indigo-800">
          View Purchase Orders →
        </RouterLink>
      </div>

      <div class="bg-white rounded-xl border border-slate-200 p-6">
        <div class="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center mb-3">
          <svg class="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"/>
          </svg>
        </div>
        <h3 class="font-semibold text-slate-800 text-sm mb-1">Appro Dashboard</h3>
        <p class="text-xs text-slate-400 mb-4">Track items on approval from suppliers and with customers</p>
        <RouterLink to="/appro"
          class="text-xs font-medium text-indigo-600 hover:text-indigo-800">
          View Appro Dashboard →
        </RouterLink>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>