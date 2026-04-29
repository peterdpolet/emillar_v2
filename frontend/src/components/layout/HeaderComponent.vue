<script setup>
import NavbarComponent from '@/components/layout/NavbarComponent.vue'
import Logo_Black from '@/assets/img/Logo_Black.png'


</script>

<template>
    Header
    <div class="grid grid-rows-2 grid-cols-[15%_70%_15%] h-full w-full">
        <div class="row-start-1 row-span-2">
            <img class="ml-10 h-25 w-35 object-fit" :src="Logo_Black">
        </div>

        <div class="row-span-2 grid grid-rows-2">
            <div class="text-5xl font-bold row-start px-8">
                Ewan Millar Ltd

            </div>
            <div class="row-start-2">
                <NavbarComponent />
            </div>

        </div>

        <div class="row-span-2">
            <button @click="showDialog" class="m-2 bg-blue-300 text-black bg-brand box-border border border-solid hover:bg-brand-strong focus:ring-4 focus:ring-brand-medium shadow-xs font-medium leading-5 rounded-full text-sm px-4 py-2.5 focus:outline-none">Login</button>
        </div>

    </div>
</template>