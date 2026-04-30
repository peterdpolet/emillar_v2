<template>
  <div class="flex-1 overflow-y-auto py-3">

    <p class="px-4 mb-1 text-xs font-semibold text-slate-400 uppercase tracking-wider">
      Channels
    </p>

    <div
      v-for="room in chat.rooms"
      :key="room.id"
      @click="chat.joinRoom(room)"
      :class="[
        'flex items-center gap-2.5 px-3 py-2 mx-2 rounded-lg cursor-pointer transition-colors duration-100 group',
        isActive(room)
          ? 'bg-brand-50 text-brand-700'
          : 'text-slate-600 hover:bg-slate-50'
      ]"
    >
      <span class="text-slate-400 group-hover:text-slate-500 text-sm font-medium">
        #
      </span>
      <div class="flex-1 min-w-0">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium truncate">{{ room.name }}</span>
          <span
            v-if="room.unread_count"
            class="ml-2 flex-shrink-0 bg-brand-600 text-white text-xs font-semibold rounded-full px-1.5 py-0.5 leading-none"
          >
            {{ room.unread_count }}
          </span>
        </div>
        <p
          v-if="room.last_message"
          class="text-xs text-slate-400 truncate mt-0.5"
        >
          {{ room.last_message.content }}
        </p>
      </div>
    </div>

    <div v-if="!chat.rooms.length" class="px-4 py-3 text-xs text-slate-400">
      No rooms yet.
    </div>

  </div>
</template>

<script setup>
import { useChatStore } from '@/stores/chat.js'

const chat = useChatStore()

function isActive(room) {
  return chat.activeRoom?.id === room.id
}
</script>