<script setup>

const emit = defineEmits(['filter'])

const filter = (e) => {
    emit('filter', e.target.value)
}


</script>


<template>

    <label class="flex mr-4 items-center flex-nowrap">
        <input type="radio" name="show" value="all" @change="filter">
        <span class="whitespace-nowrap ml-1">All</span>
    </label>

    <label class="flex mr-4 items-center flex-nowrap">
        <input type="radio" name="show" value="customer" @change="filter">
        <span class="whitespace-nowrap ml-1">Customers</span>
    </label>

    <label class="flex mr-4 items-center flex-nowrap">
        <input type="radio" name="show" value="supplier" @change="filter">
        <span class="whitespace-nowrap ml-1">Suppliers</span>
    </label>


    
</template>