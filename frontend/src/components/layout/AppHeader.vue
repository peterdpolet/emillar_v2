<template>
  <!--
    AppHeader.vue
    Uses @heroicons/vue/24/outline for icons.
  -->
  <header class="sticky top-0 z-40 flex items-center h-14 px-4
                 bg-white border-b border-slate-200 shadow-sm">

    <!-- Hamburger (mobile only) -->
    <button
      class="lg:hidden mr-3 p-1.5 rounded-md text-slate-500
             hover:bg-slate-100 transition-colors"
      aria-label="Toggle sidebar"
      @click="$emit('toggle-sidebar')"
    >
      <XMarkIcon v-if="sidebarOpen" class="w-5 h-5" />
      <Bars3Icon v-else             class="w-5 h-5" />
    </button>

    <!-- Brand -->
    <div class="flex items-center gap-2 flex-1">
      <div class="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center">
        <!-- <GemIcon class="w-4 h-4 text-white" /> -->
      </div>
      <span class="font-semibold text-slate-800 text-sm tracking-tight">
        Ewan MillarLtd (.co.uk)
      </span>
    </div>

    <!-- User / logout -->
    <div v-if="user" class="flex items-center gap-3">
      <div class="hidden sm:block text-right">
        <p class="text-xs font-medium text-slate-700 leading-none">
          {{ user.name || user.email }}
        </p>
        <p class="text-xs text-slate-400 mt-0.5 capitalize">{{ user.role }}</p>
      </div>
      <button
        class="p-1.5 rounded-md text-slate-400 hover:text-slate-600
               hover:bg-slate-100 transition-colors"
        title="Sign out"
        @click="$emit('logout')"
      >
        <ArrowRightOnRectangleIcon class="w-4 h-4" />
      </button>
    </div>

  </header>
</template>

<script setup>
import {
  Bars3Icon,
  XMarkIcon,
  // GemIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/vue/24/outline'

defineProps({
  user:        { type: Object,  default: null },
  sidebarOpen: { type: Boolean, default: false },
})

defineEmits(['toggle-sidebar', 'logout'])
</script>
