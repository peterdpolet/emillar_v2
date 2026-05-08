// src/stores/ui.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const activeSection = ref<string>('dashboard')

  function setSection(id: string): void {
    activeSection.value = id
  }

  return { activeSection, setSection }
})