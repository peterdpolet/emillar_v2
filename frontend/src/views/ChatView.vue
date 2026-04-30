<template>
  <div class="flex h-screen bg-slate-50 overflow-hidden">

    <aside class="w-64 flex-shrink-0 flex flex-col bg-white border-r border-slate-200">

      <div class="flex items-center justify-between px-4 py-4 border-b border-slate-100">
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 bg-brand-600 rounded-md flex items-center justify-center">
            <svg class="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
            </svg>
          </div>
          <span class="font-semibold text-slate-800 text-sm">Relay</span>
        </div>
        <button @click="auth.logout" class="btn-ghost p-1.5" title="Sign out">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
        </button>
      </div>

      <div class="flex items-center gap-3 px-4 py-3 border-b border-slate-100">
        <div class="w-8 h-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-xs font-semibold flex-shrink-0">
          {{ userInitial }}
        </div>
        <div class="min-w-0">
          <p class="text-sm font-medium text-slate-800 truncate">
            {{ auth.user?.name }}
          </p>
          <p class="text-xs text-slate-400 truncate">
            {{ auth.user?.email }}
          </p>
        </div>
      </div>

      <RoomList />

    </aside>

    <main class="flex-1 flex flex-col overflow-hidden">
      <ChatWindow v-if="chat.activeRoom" />
      <div
        v-else
        class="flex-1 flex flex-col items-center justify-center gap-3 text-slate-400"
      >
        <div class="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center">
          <svg class="w-8 h-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
          </svg>
        </div>
        <p class="text-sm font-medium">Select a room to start chatting</p>
        <p class="text-xs text-slate-300">Choose from the sidebar on the left</p>
      </div>
    </main>

  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useChatStore } from '@/stores/chat.js'
import RoomList from '@/components/RoomList.vue'
import ChatWindow from '@/components/ChatWindow.vue'

const auth = useAuthStore()
const chat = useChatStore()

const userInitial = computed(() =>
  auth.user?.name?.[0]?.toUpperCase() || '?'
)

onMounted(() => chat.fetchRooms())
</script>