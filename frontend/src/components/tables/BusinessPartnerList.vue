<!-- SupplierList.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/axios'          // ← the shared instance, nothing else needed

const suppliers = ref([])
const loading   = ref(false)
const error     = ref(null)

onMounted(async () => {
  console.log("Mounted - getting data")
  loading.value = true
  try {
    const res = await api.get('/partners/suppliers/')
    suppliers.value = res.data          // ← interceptors are invisible to this code
  } catch (err) {
    error.value = 'Could not load suppliers'
  } finally {
    loading.value = false
    console.log("Business PartnerList = ", suppliers.value)
  }
})
</script>

<template>
  <div v-for="(supplier, index) in suppliers" :key="index">
    {{ index}}
  </div></template>