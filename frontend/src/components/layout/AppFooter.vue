<template>
  <!--
    AppFooter.vue
    ─────────────
    Minimal footer. Sits at the bottom of AppLayout.
    Keep it lean — most content is in the sidebar or main area.
  -->
  <footer class="h-10 flex items-center justify-between px-4 lg:px-6
                 border-t border-slate-200 bg-white text-xs text-slate-400">
    <span>Ewan Millar Ltd &copy; {{ year }}</span>
    <span>Invitation only platform</span>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()
</script>
