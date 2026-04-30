<template>
  <div
    class="flex items-end gap-2.5 group"
    :class="isOwn ? 'flex-row-reverse' : 'flex-row'"
  >

    <div
      v-if="!isOwn"
      class="w-7 h-7 rounded-full bg-slate-200 text-slate-600 flex items-center justify-center text-xs font-semibold flex-shrink-0 mb-1"
    >
      {{ senderInitial }}
    </div>

    <div
      class="max-w-xs lg:max-w-md xl:max-w-lg flex flex-col"
      :class="isOwn ? 'items-end' : 'items-start'"
    >
      <div
        class="flex items-baseline gap-2 mb-1 px-1"
        :class="isOwn ? 'flex-row-reverse' : 'flex-row'"
      >
        <span
          class="text-xs font-semibold"
          :class="isOwn ? 'text-brand-600' : 'text-slate-700'"
        >
          {{ senderName }}
        </span>
        <span class="text-xs text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
          {{ formattedTime }}
        </span>
      </div>

      <div
        class="px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed break-words"
        :class="isOwn
          ? 'bg-brand-600 text-white rounded-br-sm'
          : 'bg-white border border-slate-200 text-slate-800 rounded-bl-sm shadow-sm'"
      >
        {{ message.content }}
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  isOwn: {
    type: Boolean,
    default: false
  }
})

const senderName = computed(() =>
  props.message.sender_name || props.message.sender?.name || 'Unknown'
)

const senderInitial = computed(() =>
  senderName.value[0]?.toUpperCase() || '?'
)

const formattedTime = computed(() =>
  new Date(props.message.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  })
)
</script>