<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
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

watch(() => route.meta.sidebarSection, (section) => {
  if (section) ui.setSection(section as string)
}, { immediate: true })

const userRole = computed<string>(() => auth.user?.role ?? '')

const topNav = computed(() => {
  if (!auth.user) return []
  return navConfig.filter(section =>
    !section.roles || section.roles.includes(userRole.value)
  )
})

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

// Replace switchSection:
function switchSection(section: any) {
  if (section.direct) {
    router.push(section.direct)
    ui.setSection(section.id)
    return
  }
  ui.setSection(section.id)
  const found = navConfig.find(s => s.id === section.id)
  if (found?.items?.length) {
    router.push(found.items[0].route)
  }
}

// Add computed to hide sidebar:
  const showSidebar = computed(() => {
    const activeSection = navConfig.find(s => s.id === ui.activeSection)
    return !activeSection?.direct
  })

</script>

<template>
  <div class="min-h-screen flex flex-col bg-slate-50">

    <!-- ── Header ── -->
    <header class="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">

      <!-- Brand bar -->
      <div class="flex items-center h-16 px-6 gap-4">
        <button class="lg:hidden p-1.5 rounded-md text-slate-500 hover:bg-slate-100"
          @click="sidebarOpen = !sidebarOpen">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path v-if="sidebarOpen" stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            <path v-else stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>

        <RouterLink to="/dashboard" class="flex items-center gap-3 flex-shrink-0">
          <div class="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-sm">
            <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M21 11.25v8.25a1.5 1.5 0 01-1.5 1.5H5.25a1.5 1.5 0 01-1.5-1.5v-8.25M12 4.875A2.625 2.625 0 1014.25 7.5H12m0-2.625V7.5m0-2.625A2.625 2.625 0 109.75 7.5H12m0 0V21m-8.625-9.75h18c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125h-18c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"/>
            </svg>
          </div>
          <div>
            <p class="font-bold text-slate-800 text-lg leading-tight tracking-tight">Ewan Millar Ltd</p>
            <p class="text-xs text-slate-400 leading-tight">ewanmillarltd.co.uk</p>
          </div>
        </RouterLink>

        <div class="flex-1" />

        <div v-if="auth.user" class="flex items-center gap-4">
          <div class="hidden sm:block text-right">
            <p class="text-xs font-medium text-slate-700 leading-none">
              {{ auth.user.name || auth.user.email }}
            </p>
            <p class="text-xs text-slate-400 mt-0.5 capitalize">{{ auth.user.role }}</p>
          </div>
          <button @click="auth.logout()"
            class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-500
                   border border-slate-200 rounded-lg hover:bg-slate-50 hover:text-slate-700 transition-colors">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75"/>
            </svg>
            Logout
          </button>
        </div>
      </div>

      <!-- Top nav tabs -->
      <nav class="flex px-6 border-t border-slate-100 overflow-x-auto">
        <button
          v-for="section in topNav"
          :key="section.id"
          @click="switchSection(section)"
          :class="[
            'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px whitespace-nowrap',
            ui.activeSection === section.id
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
          ]"
        >
          {{ section.label }}
        </button>
        <RouterLink to="/chat"
          :class="[
            'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px whitespace-nowrap',
            route.path === '/chat'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
          ]">
          Chat
        </RouterLink>
      </nav>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <Transition name="fade">
        <div v-if="sidebarOpen"
          class="fixed inset-0 bg-black/40 z-20 lg:hidden"
          @click="sidebarOpen = false" />
      </Transition>

      <Transition name="slide">
        <AppSidebar
          v-show="sidebarOpen || isDesktop && showSidebar"
          :nav="filteredNav"
          :current-section="route.meta.sidebarSection"
          class="fixed lg:static z-30 lg:z-auto h-full lg:h-auto"
          @navigate="sidebarOpen = false"
        />
      </Transition>

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