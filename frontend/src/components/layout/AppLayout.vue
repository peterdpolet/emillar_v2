<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { navConfig } from '@/config/navigation'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import AppFooter from './AppFooter.vue'
import HeaderComponent from '../layout/HeaderComponent.vue'

const route    = useRoute()
const auth     = useAuthStore()

// ── Sidebar open/close state ──────────────────────────────────────────────────
const sidebarOpen = ref(false)
const isDesktop   = ref(false)

function checkDesktop() {
  isDesktop.value = window.innerWidth >= 1024  // lg breakpoint
}

onMounted(() => {
  checkDesktop()
  window.addEventListener('resize', checkDesktop)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkDesktop)
})

// ── Role-filtered navigation ──────────────────────────────────────────────────
const userRole = computed(() => auth.user?.role)

const filteredNav = computed(() =>
  navConfig
    .filter(section =>
      !section.roles || section.roles.includes(userRole.value)
    )
    .map(section => ({
      ...section,
      items: section.items.filter(item =>
        !item.roles || item.roles.includes(userRole.value)
      ),
    }))
    .filter(section => section.items.length > 0)
)

const userRole = computed(() => {
  console.log('userRole:', auth.user?.role)
  return auth.user?.role
})

</script>



<template>
  <!--
    AppLayout.vue
    ─────────────
    Single layout wrapper for all authenticated views.
    Structure:
      ┌─────────────────────────────┐
      │         AppHeader           │
      ├──────────┬──────────────────┤
      │          │                  │
      │ Sidebar  │   <router-view>  │
      │          │                  │
      ├──────────┴──────────────────┤
      │         AppFooter           │
      └─────────────────────────────┘

    On mobile the sidebar collapses to an off-canvas drawer
    toggled by the header hamburger button.
  -->
  <div class="min-h-screen flex flex-col bg-slate-50">

    <!-- Header -->
    <!-- <AppHeader
      :user="auth.user"
      :sidebar-open="sidebarOpen"
      @toggle-sidebar="sidebarOpen = !sidebarOpen"
      @logout="auth.logout"
    /> -->
    <HeaderComponent />

    <div class="flex flex-1 overflow-hidden">

      <!-- Sidebar overlay (mobile only) -->
      <Transition name="fade">
        <div
          v-if="sidebarOpen"
          class="fixed inset-0 bg-black/40 z-20 lg:hidden"
          @click="sidebarOpen = false"
        />
      </Transition>

      <!-- Sidebar -->
      <Transition name="slide">
        <AppSidebar
          v-show="sidebarOpen || isDesktop"
          :nav="filteredNav"
          :current-section="route.meta.sidebarSection"
          class="fixed lg:static z-30 lg:z-auto h-full lg:h-auto"
          @navigate="sidebarOpen = false"
        />
      </Transition>

      <!-- Main content -->
      <main class="flex-1 overflow-auto p-4 lg:p-6">
        <router-view />
      </main>

    </div>

    <AppFooter />
  </div>
</template>



<style scoped>
/* Sidebar slide-in on mobile */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}

/* Overlay fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
