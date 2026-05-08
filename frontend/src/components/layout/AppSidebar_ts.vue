<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import {
  ChevronDownIcon,
  Squares2X2Icon,
  ShoppingBagIcon,
  TruckIcon,
  ArchiveBoxIcon,
  Cog6ToothIcon,
  type FunctionalComponent,
} from '@heroicons/vue/24/outline'
import type { NavSection } from '@/config/navigation'

// ── Types ─────────────────────────────────────────────────
type IconName = 'grid' | 'shopping-bag' | 'truck' | 'package' | 'settings'

// ── Props ─────────────────────────────────────────────────
interface Props {
  nav:            NavSection[]
  currentSection: string
}

withDefaults(defineProps<Props>(), {
  currentSection: '',
})

// ── Emits ─────────────────────────────────────────────────
defineEmits<{
  'navigate': []
}>()

// ── Icon map ──────────────────────────────────────────────
const iconMap: Record<IconName, FunctionalComponent> = {
  'grid':         Squares2X2Icon,
  'shopping-bag': ShoppingBagIcon,
  'truck':        TruckIcon,
  'package':      ArchiveBoxIcon,
  'settings':     Cog6ToothIcon,
}

const year: number = new Date().getFullYear()
</script>