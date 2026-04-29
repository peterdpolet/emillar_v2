<template>
  <!--
    AppSidebar.vue
    Uses @headlessui/vue Disclosure for accordion — no manual state needed.
    Uses @heroicons/vue/24/outline for icons.

    Disclosure gives you for free:
      - open/close state
      - keyboard navigation  
      - aria-expanded / aria-controls
  -->
  <aside class="w-64 flex-shrink-0 bg-white border-r border-slate-200
                flex flex-col overflow-y-auto">

    <nav class="flex-1 py-3 px-2 space-y-0.5">

      <Disclosure
        v-for="section in nav"
        :key="section.id"
        v-slot="{ open }"
        as="div"
        :default-open="section.id === currentSection"
      >
        <!-- Accordion button -->
        <DisclosureButton
          class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg
                 text-sm font-medium transition-colors"
          :class="open
            ? 'bg-brand-50 text-brand-700'
            : 'text-slate-600 hover:bg-slate-50 hover:text-slate-800'"
        >
          <component
            :is="iconMap[section.icon]"
            class="w-4 h-4 flex-shrink-0"
            :class="open ? 'text-brand-600' : 'text-slate-400'"
          />
          <span class="flex-1 text-left">{{ section.label }}</span>
          <ChevronDownIcon
            class="w-3.5 h-3.5 text-slate-400 transition-transform duration-200"
            :class="open ? 'rotate-180' : ''"
          />
        </DisclosureButton>

        <!-- Accordion panel -->
        <DisclosurePanel class="pl-4 pr-2 pb-1 space-y-0.5">
          <RouterLink
            v-for="item in section.items"
            :key="item.route"
            :to="item.route"
            class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm
                   text-slate-500 hover:text-slate-800 hover:bg-slate-50
                   transition-colors"
            active-class="!text-brand-700 !bg-brand-50 font-medium"
            @click="$emit('navigate')"
          >
            <span class="w-1 h-1 rounded-full bg-current opacity-50 flex-shrink-0" />
            {{ item.label }}
          </RouterLink>
        </DisclosurePanel>

      </Disclosure>

    </nav>

    <div class="px-4 py-3 border-t border-slate-100">
      <p class="text-xs text-slate-400">Ewan Millar Ltd &copy; {{ year }}</p>
    </div>

  </aside>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import {
  ChevronDownIcon,
  Squares2X2Icon,
  ShoppingBagIcon,
  // GemIcon,
  TruckIcon,
  ArchiveBoxIcon,
  Cog6ToothIcon,
} from '@heroicons/vue/24/outline'

defineProps({
  nav:            { type: Array,  required: true },
  currentSection: { type: String, default: '' },
})

defineEmits(['navigate'])

const iconMap = {
  'grid':         Squares2X2Icon,
  'shopping-bag': ShoppingBagIcon,
  // 'gem':          GemIcon,
  'truck':        TruckIcon,
  'package':      ArchiveBoxIcon,
  'settings':     Cog6ToothIcon,
}

const year = new Date().getFullYear()
</script>
