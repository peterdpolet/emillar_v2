<template>
  <div class="flex-1 overflow-y-auto p-6">
    <h1 class="text-xl font-bold text-slate-800 mb-6">Dashboard</h1>
    <div class="bg-white rounded-xl border border-slate-200 p-5">
      <p class="text-sm text-slate-400">
        Navigate to 
        <RouterLink to="/sales-orders-v2" class="text-brand-600 hover:underline">Sales Orders</RouterLink>
        or
        <RouterLink to="/purchase-orders-v2" class="text-brand-600 hover:underline">Purchase Orders</RouterLink>
        to get started.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>