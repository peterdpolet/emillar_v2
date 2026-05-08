<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import NavbarComponent from '@/components/navigation/NavbarComponent.vue'
import Logo_Black from '@/assets/img/Logo_Black.png'

const auth   = useAuthStore()
const router = useRouter()

function handleLogin(): void {
  router.push('/login')
}

function handleLogout(): void {
  auth.logout()
}
</script>

<template>

    <div class="grid grid-rows-2 grid-cols-[15%_70%_15%] h-full w-full">
        <div class="row-start-1 row-span-2">
            <img class="ml-10 h-25 w-35 object-fit" :src="Logo_Black">
        </div>

        <div class="row-span-2 grid grid-rows-2">
            <div class="text-5xl font-bold row-start px-8">
                Ewan Millar Ltd (.co.uk)

            </div>
            <div class="row-start-2">
                <NavbarComponent />
            </div>

        </div>

        <div class="row-span-2">
            <button 
                v-if="!auth.isAuthenticated"
                @click="handleLogin" 
                class="m-2 bg-blue-300 ...">
                Login
                </button>
                <button 
                v-else
                @click="handleLogout"
                class="m-2 bg-blue-300 ...">
                Logout
            </button>
        </div>

    </div>
</template>