<script setup lang="ts">
import {computed} from 'vue'
import { Disclosure, DisclosureButton } from '@headlessui/vue'
import { Bars3Icon, XMarkIcon } from '@heroicons/vue/24/outline'
import { RouterLink } from 'vue-router'
import { navConfig } from '@/config/navigation'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'

const ui   = useUiStore()
const auth = useAuthStore()

// Filter sections by role — same pattern as sidebar

// Show all role-appropriate sections, 
// fall back to showing all if user not loaded yet
const visibleSections = computed(() => 
  navConfig.filter(section =>
    !section.roles || 
    !auth.user ||  // show all while user loading
    section.roles.includes(auth.user.role)
  )
)


</script>

<template>
  <Disclosure as="nav" 
    class="relative bg-white shadow-sm dark:bg-gray-800/50" 
    v-slot="{ open }">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-10 justify-between">
        <div class="flex">
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8 text-lg">
            <button
              v-for="section in visibleSections"
              :key="section.id"
              @click="ui.setSection(section.id)"
              :class="[
                'inline-flex items-center border-b-2 px-1 pt-1 text-xl font-medium transition-colors',
                ui.activeSection === section.id
                  ? 'border-indigo-600 text-gray-900'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              ]">
              {{ section.label }}
            </button>
          </div>
        </div>

        <!-- Mobile menu button -->
        <div class="-mr-2 flex items-center sm:hidden">
          <DisclosureButton class="relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500">
            <Bars3Icon v-if="!open" class="block size-6" />
            <XMarkIcon v-else class="block size-6" />
          </DisclosureButton>
        </div>
      </div>
    </div>
  </Disclosure>
</template>