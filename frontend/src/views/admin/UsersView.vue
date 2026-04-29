<template>
  <div class="flex-1 flex flex-col overflow-hidden">

    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white flex-shrink-0">
      <h1 class="text-lg font-bold text-slate-800">Users</h1>
      <button @click="showInvite = true"
        class="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white
               text-sm font-medium rounded-lg px-4 py-2 transition-colors">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
        </svg>
        Invite user
      </button>
    </div>

    <!-- Filters -->
    <div class="px-6 py-3 border-b border-slate-100 bg-white flex-shrink-0 flex items-center gap-4">
      <input v-model="search" type="text" placeholder="Search users…"
        class="w-full max-w-xs border border-slate-200 rounded-lg px-3 py-2 text-sm
               focus:outline-none focus:ring-2 focus:ring-brand-500" />
      <select v-model="roleFilter"
        class="border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white
               focus:outline-none focus:ring-2 focus:ring-brand-500">
        <option value="">All roles</option>
        <option value="staff">Staff</option>
        <option value="customer">Customer</option>
        <option value="supplier">Supplier</option>
      </select>
    </div>

    <!-- Table -->
    <div class="flex-1 overflow-y-auto">
      <table class="w-full table-fixed text-sm">
        <colgroup>
          <col class="w-48">
          <col class="w-56">
          <col class="w-28">
          <col class="w-28">
          <col class="w-32">
          <col class="w-24">
        </colgroup>
        <thead class="bg-slate-50 border-b border-slate-200 sticky top-0">
          <tr>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Name</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Email</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Role</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">Joined</th>
            <th class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="px-4 py-8 text-center text-slate-400 text-sm">Loading…</td>
          </tr>
          <tr v-else-if="!filteredUsers.length">
            <td colspan="6" class="px-4 py-8 text-center text-slate-400 text-sm">No users found</td>
          </tr>
          <tr v-for="user in filteredUsers" :key="user.id"
            class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
            <td class="px-4 py-3">
              <p class="font-medium text-slate-800 truncate">{{ user.name || '—' }}</p>
            </td>
            <td class="px-4 py-3 text-slate-500 text-xs truncate">{{ user.email }}</td>
            <td class="px-4 py-3">
              <span :class="roleClass(user.role)"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium capitalize">
                {{ user.role }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span :class="user.is_active
                ? 'bg-green-50 text-green-700'
                : 'bg-slate-100 text-slate-500'"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium">
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-4 py-3 text-slate-400 text-xs">
              {{ user.created_at ? new Date(user.created_at).toLocaleDateString('en-GB') : '—' }}
            </td>
            <td class="px-4 py-3 flex items-center gap-3">
              <button @click="toggleActive(user)"
                class="text-xs font-medium"
                :class="user.is_active ? 'text-red-500 hover:text-red-600' : 'text-green-600 hover:text-green-700'">
                {{ user.is_active ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/axios.js'

const loading    = ref(false)
const search     = ref('')
const roleFilter = ref('')
const showInvite = ref(false)
const users      = ref([])

const filteredUsers = computed(() => {
  let list = users.value
  if (roleFilter.value) list = list.filter(u => u.role === roleFilter.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(u =>
      u.name?.toLowerCase().includes(q) ||
      u.email?.toLowerCase().includes(q)
    )
  }
  return list
})

function roleClass(role) {
  return {
    staff:    'bg-brand-50 text-brand-700',
    customer: 'bg-green-50 text-green-700',
    supplier: 'bg-amber-50 text-amber-700',
  }[role] ?? 'bg-slate-100 text-slate-600'
}

onMounted(fetchUsers)

async function fetchUsers() {
  loading.value = true
  try {
    const { data } = await api.get('/auth/users/')
    users.value = data.results ?? data
  } catch {
    users.value = []
  } finally {
    loading.value = false
  }
}

async function toggleActive(user) {
  try {
    await api.patch(`/auth/users/${user.id}/`, { is_active: !user.is_active })
    user.is_active = !user.is_active
  } catch {
    // TODO: show error toast
  }
}
</script>
