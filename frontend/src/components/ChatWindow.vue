<template>
  <div class="flex flex-col h-full">

    <div class="flex items-center justify-between px-6 py-3.5 bg-white border-b border-slate-200 flex-shrink-0">
      <div class="flex items-center gap-2">
        <span class="text-slate-400 font-medium">#</span>
        <h2 class="font-semibold text-slate-800">{{ chat.activeRoom.name }}</h2>
        <span v-if="chat.activeRoom.description" class="text-sm text-slate-400">
          — {{ chat.activeRoom.description }}
        </span>
      </div>
      <div class="flex items-center gap-1.5 text-xs text-slate-500">
        <span class="w-2 h-2 rounded-full bg-emerald-400 inline-block"></span>
        {{ chat.onlineUsers.size }} online
      </div>
    </div>

    <div ref="messagesEl" class="flex-1 overflow-y-auto px-6 py-4 space-y-1">
      <div
        v-if="!chat.messages.length"
        class="flex items-center justify-center h-full"
      >
        <p class="text-sm text-slate-400">No messages yet. Say hello!</p>
      </div>
      <MessageBubble
        v-for="msg in chat.messages"
        :key="msg.id"
        :message="msg"
        :is-own="msg.sender_id === auth.user?.id"
      />
    </div>

    <div class="px-6 h-6 flex items-center flex-shrink-0">
      <div v-if="chat.typingText" class="flex items-center gap-2">
        <div class="flex gap-0.5">
          <span
            v-for="n in 3"
            :key="n"
            class="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce"
            :style="{ animationDelay: `${(n - 1) * 0.15}s` }"
          ></span>
        </div>
        <span class="text-xs text-slate-400">{{ chat.typingText }}</span>
      </div>
    </div>

    <div class="px-4 pb-4 flex-shrink-0">
      <div class="flex items-center gap-2 bg-white border border-slate-200 rounded-xl px-4 py-2.5 focus-within:ring-2 focus-within:ring-brand-500 focus-within:border-transparent transition">
        <input
          v-model="draft"
          :placeholder="`Message #${chat.activeRoom.name}`"
          class="flex-1 text-sm text-slate-800 placeholder-slate-400 bg-transparent outline-none"
          @keydown.enter.prevent="send"
          @input="onType"
        />
        <button
          @click="send"
          :disabled="!draft.trim()"
          class="flex-shrink-0 w-8 h-8 rounded-lg bg-brand-600 hover:bg-brand-700 disabled:opacity-40 disabled:cursor-not-allowed text-white flex items-center justify-center transition-colors"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat.js'
import { useAuthStore } from '@/stores/auth.js'
import MessageBubble from './MessageBubble.vue'

const chat = useChatStore()
const auth = useAuthStore()
const draft = ref('')
const messagesEl = ref(null)

function send() {
  if (!draft.value.trim()) return
  chat.sendMessage(draft.value.trim())
  chat.sendTyping(false)
  draft.value = ''
}

function onType() {
  chat.sendTyping(draft.value.length > 0)
}

watch(
  () => chat.messages.length,
  async () => {
    await nextTick()
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  }
)
</script>