<script setup>
import { Disclosure, DisclosureButton, DisclosurePanel, Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { Bars3Icon, BellIcon, XMarkIcon } from '@heroicons/vue/24/outline'
</script>
<template>

  <Disclosure as="nav" class="relative bg-white shadow-sm dark:bg-gray-800/50 dark:shadow-none dark:after:pointer-events-none dark:after:absolute dark:after:inset-x-0 dark:after:bottom-0 dark:after:h-px dark:after:bg-white/10" v-slot="{ open }">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-10 justify-between">
        <div class="flex">
          <div class="flex shrink-0 items-center">
            <!-- <img class="h-8 w-auto dark:hidden" src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=600" alt="Your Company" />
            <img class="h-8 w-auto not-dark:hidden" src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=500" alt="Your Company" /> -->
          </div>
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8 text-lg">
            <!-- Current: "border-indigo-600 text-gray-900 dark:border-indigo-500 dark:text-white", Default: "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-300 dark:hover:border-white/20 dark:hover:text-white" -->
            <!-- <a href="#" class="inline-flex items-center border-b-2 border-indigo-600 px-1 pt-1 text-sm font-medium text-gray-900 dark:border-indigo-500 dark:text-white">Dashboard</a> -->
            <RouterLink class="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-xl font-medium text-gray-500 hover:border-gray-300 hover:text-blue-700 dark:text-gray-300 dark:hover:border-white/20 dark:hover:text-white" to="/home">Home</RouterLink>
            <RouterLink class="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-xl font-medium text-gray-500 hover:border-gray-300 hover:text-blue-700 dark:text-gray-300 dark:hover:border-white/20 dark:hover:text-white" to="/about">About</RouterLink>
            <RouterLink class="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-xl font-medium text-gray-500 hover:border-gray-300 hover:text-blue-700 dark:text-gray-300 dark:hover:border-white/20 dark:hover:text-white" to="/admin">Admin</RouterLink>
            <RouterLink class="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-xl font-medium text-gray-500 hover:border-gray-300 hover:text-blue-700 dark:text-gray-300 dark:hover:border-white/20 dark:hover:text-white" to="/orders">Orders</RouterLink>
            <RouterLink class="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-xl font-medium text-gray-500 hover:border-gray-300 hover:text-blue-700 dark:text-gray-300 dark:hover:border-white/20 dark:hover:text-white" to="/diamonds">Diamonds</RouterLink>
            <RouterLink class="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-xl font-medium text-gray-500 hover:border-gray-300 hover:text-blue-700 dark:text-gray-300 dark:hover:border-white/20 dark:hover:text-white" to="/gemstones">Gemstones</RouterLink>
            <RouterLink class="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-xl font-medium text-gray-500 hover:border-gray-300 hover:text-blue-700 dark:text-gray-300 dark:hover:border-white/20 dark:hover:text-white" to="/blog">Blog</RouterLink>
            <RouterLink class="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-xl font-medium text-gray-500 hover:border-gray-300 hover:text-blue-700 dark:text-gray-300 dark:hover:border-white/20 dark:hover:text-white" to="/chat">Chat</RouterLink>

          </div>
        </div>

        <div class="-mr-2 flex items-center sm:hidden">
          <!-- Mobile menu button -->
          <DisclosureButton class="relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-2 focus:-outline-offset-1 focus:outline-indigo-600 dark:hover:bg-white/5 dark:hover:text-white dark:focus:outline-indigo-500">
            <span class="absolute -inset-0.5"></span>
            <span class="sr-only">Open main menu</span>
            <Bars3Icon v-if="!open" class="block size-6" aria-hidden="true" />
            <XMarkIcon v-else class="block size-6" aria-hidden="true" />
          </DisclosureButton>
        </div>
      </div>
    </div>


  </Disclosure>
</template>

