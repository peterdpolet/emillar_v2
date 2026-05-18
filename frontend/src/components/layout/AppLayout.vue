<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { navConfig } from '@/config/navigation'
import AppSidebar from './AppSidebar.vue'
import AppFooter from './AppFooter.vue'
import { useUiStore } from '@/stores/ui'
import { watch } from 'vue'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()
const ui     = useUiStore()

// ── Sidebar open/close state ──────────────────────────────────────────────────
const sidebarOpen = ref(false)
const isDesktop   = ref(false)

function checkDesktop() {
  isDesktop.value = window.innerWidth >= 1024
}

onMounted(() => {
  checkDesktop()
  window.addEventListener('resize', checkDesktop)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkDesktop)
})

// Auto-set active section based on current route meta
watch(() => route.meta.sidebarSection, (section) => {
  if (section) ui.setSection(section as string)
}, { immediate: true })

// ── Role-filtered navigation ──────────────────────────────────────────────────
const userRole = computed<string>(() => auth.user?.role ?? '')

// Top nav sections (role filtered)
const topNav = computed(() => {
  if (!auth.user) return []
  return navConfig.filter(section =>
    !section.roles || section.roles.includes(userRole.value)
  )
})

// Sidebar items for active section
const filteredNav = computed(() => {
  if (!auth.user) return []
  return navConfig
    .filter(section =>
      section.id === ui.activeSection &&
      (!section.roles || section.roles.includes(userRole.value))
    )
    .map(section => ({
      ...section,
      items: section.items.filter(item =>
        !item.roles || item.roles.includes(userRole.value)
      ),
    }))
    .filter(section => section.items.length > 0)
})

function switchSection(sectionId: string) {
  ui.setSection(sectionId)
  // Navigate to the first item in the section
  const section = navConfig.find(s => s.id === sectionId)
  if (section?.items?.length) {
    router.push(section.items[0].route)
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-slate-50">

    <!-- ── Header ── -->
    <header class="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">

      <!-- Top bar -->
      <div class="flex items-center h-14 px-4 gap-4">

        <!-- Mobile hamburger -->
        <button class="lg:hidden p-1.5 rounded-md text-slate-500 hover:bg-slate-100"
          @click="sidebarOpen = !sidebarOpen">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path v-if="sidebarOpen" stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            <path v-else stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>

        <!-- Brand -->
        <div class="flex items-center gap-2 flex-1">
          <div class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M21 11.25v8.25a1.5 1.5 0 01-1.5 1.5H5.25a1.5 1.5 0 01-1.5-1.5v-8.25M12 4.875A2.625 2.625 0 1014.25 7.5H12m0-2.625V7.5m0-2.625A2.625 2.625 0 109.75 7.5H12m0 0V21m-8.625-9.75h18c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125h-18c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"/>
            </svg>
          </div>
          <span class="font-bold text-slate-800 text-base tracking-tight">
            Ewan Millar Ltd
          </span>
          <span class="hidden sm:inline text-xs text-slate-400 font-normal">(.co.uk)</span>
        </div>

        <!-- User info + logout -->
        <div v-if="auth.user" class="flex items-center gap-3">
          <div class="hidden sm:block text-right">
            <p class="text-xs font-medium text-slate-700 leading-none">
              {{ auth.user.name || auth.user.email }}
            </p>
            <p class="text-xs text-slate-400 mt-0.5 capitalize">{{ auth.user.role }}</p>
          </div>
          <button @click="auth.logout()"
            class="p-1.5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            title="Sign out">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Top nav tabs -->
      <nav class="flex px-4 border-t border-slate-100">
        <button
          v-for="section in topNav"
          :key="section.id"
          @click="switchSection(section.id)"
          :class="[
            'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px',
            ui.activeSection === section.id
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
          ]"
        >
          {{ section.label }}
        </button>
      </nav>
    </header>

    <div class="flex flex-1 overflow-hidden">

      <!-- Sidebar overlay (mobile) -->
      <Transition name="fade">
        <div v-if="sidebarOpen"
          class="fixed inset-0 bg-black/40 z-20 lg:hidden"
          @click="sidebarOpen = false" />
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
.slide-enter-active,
.slide-leave-active { transition: transform 0.25s ease; }
.slide-enter-from,
.slide-leave-to { transform: translateX(-100%); }

.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }
</style>