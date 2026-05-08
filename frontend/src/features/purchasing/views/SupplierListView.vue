<script setup>
import { onMounted, computed, ref } from 'vue'
import { useSupplierListStore } from '@purchasing/stores/useSupplierListStore.js'

const store = useSupplierListStore()
const searchFilter = ref('')


onMounted(() => store.fetchSuppliers())

const filterSuppliers = computed( () => {
    let filteredSuppliers = store.suppliers;
    searchFilter.value = 'm'
    console.log("Filtered Suppliers", filteredSuppliers)

    // switch (radioFilter.value) {
    //     case 'customer':
    //         items = items.filter(item => item.bp_type === 'CUST')
    //         break;

    //     case 'supplier':
    //         items = items.filter(item => item.bp_type === 'SUPP')
    //         break;
    // }

        filteredSuppliers = filteredSuppliers.filter(filteredSuppliers => 
        filteredSuppliers.bp_name.includes(searchFilter.value))   

    return filteredSuppliers;
})


</script>

<template>
  <div v-if="store.supplierLoading">Loading…</div>

  <div v-else-if="!store.suppliers.length">No orders yet</div>

  <table v-else>
    <thead>
      <tr>
        <th>#</th>
        <th>Supplier Name</th>
        <th>Status</th>
        <th>Total</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(supplier, index) in filterSuppliers" :key="index">
        <td>{{ index }}</td>       
        <td>{{ supplier.bp_name }}</td>
        <td>{{ supplier.bp_type }}</td>
        <!-- <td>{{ order.status }}</td>
        <td>£{{ Number(order.total).toFixed(2) }}</td> -->
      </tr>
    </tbody>
  </table>
</template>