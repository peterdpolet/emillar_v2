<template>
  <div class="h-screen flex overflow-hidden bg-slate-50">

    <!-- Sidebar -->
    <aside class="w-60 flex-shrink-0 bg-white border-r border-slate-200 flex flex-col">

      <!-- Brand -->
      <div class="px-5 py-5 border-b border-slate-100">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007z"/>
            </svg>
          </div>
          <div class="min-w-0">
            <p class="text-sm font-semibold text-slate-800 truncate">Ewan Millar Ltd</p>
            <p class="text-xs text-slate-400 truncate">{{ auth.user?.role || 'Loading…' }}</p>
          </div>
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <NavLink to="/dashboard" icon="home">Dashboard</NavLink>
        <NavLink to="/orders"    icon="orders">Orders</NavLink>
        <NavLink to="/items"     icon="items">Items</NavLink>
        <NavLink to="/settings"  icon="settings">Settings</NavLink>
      </nav>

      <!-- User pill -->
      <div class="px-3 py-3 border-t border-slate-100">
        <div class="flex items-center gap-3 px-2 py-2 rounded-lg">
          <div class="w-7 h-7 rounded-full bg-brand-100 text-brand-700
                      flex items-center justify-center text-xs font-semibold flex-shrink-0">
            {{ userInitial }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-medium text-slate-700 truncate">{{ auth.user?.name || auth.user?.email }}</p>
            <p class="text-xs text-slate-400 truncate">{{ auth.user?.email }}</p>
          </div>
          <button @click="auth.logout" title="Sign out"
            class="text-slate-400 hover:text-slate-600 transition-colors flex-shrink-0">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 flex flex-col overflow-hidden">
      <slot />
    </main>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, useLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'

const auth = useAuthStore()

const userInitial = computed(() =>
  (auth.user?.name || auth.user?.email || '?')[0].toUpperCase()
)

// ── NavLink component (inline) ─────────────────────────────
const NavLink = {
  props: ['to', 'icon'],
  setup(props, { slots }) {
    const { isActive } = useLink({ to: props.to })
    return { isActive, props, slots }
  },
  template: `
    <RouterLink :to="props.to"
      :class="[
        'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
        isActive
          ? 'bg-brand-50 text-brand-700'
          : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
      ]">
      <slot />
    </RouterLink>
  `
}
</script>
