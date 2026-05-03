/**
 * src/router/index.ts
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Layout
import AppLayout from '@/components/layout/AppLayout.vue'

// Auth views
import LoginView    from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'

// App views
import DashboardView   from '@/views/DashboardView.vue'
import OrdersView      from '@/views/OrdersView.vue'
import OrderDetailView from '@/views/OrderDetailView.vue'
import CreateOrderView from '@/views/CreateOrderView.vue'
import ProductsView    from '@/views/ProductsView.vue'
import SuppliersView   from '@/views/SuppliersView.vue'
import InvoicesView    from '@/views/InvoicesView.vue'
import SkuMappingView  from '@/views/SkuMappingView.vue'
import UsersView       from '@/views/admin/UsersView.vue'
import SettingsView    from '@/views/admin/SettingsView.vue'
import HomeView        from '@/views/HomeView.vue'
import ChatView        from '@/views/ChatView.vue'

// ── Extend Vue Router meta types ──────────────────────────
// This is the key pattern — tells TypeScript what fields
// are valid on route.meta throughout the entire app

const routes: RouteRecordRaw[] = [

  // ── Public routes ─────────────────────────────────────────
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guestOnly: true },
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { guestOnly: true },
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView,
    meta: { guestOnly: true },
  },
  {
    path: '/chat',
    name: 'chat',
    component: ChatView,
    meta: { requiresAuth: true },
  },

  // ── Authenticated routes (inside AppLayout) ───────────────
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },

      {
        path: 'dashboard',
        name: 'dashboard',
        component: DashboardView,
        meta: { requiresAuth: true, sidebarSection: 'dashboard' },
      },
      {
        path: 'home',
        name: 'home-auth',
        component: HomeView,
        meta: { requiresAuth: true, sidebarSection: 'purchasing' },
      },
      {
        path: 'orders',
        name: 'orders',
        component: OrdersView,
        meta: { requiresAuth: true, sidebarSection: 'purchasing' },
      },
      {
        path: 'orders/create',
        name: 'orders-create',
        component: CreateOrderView,
        meta: { requiresAuth: true, sidebarSection: 'purchasing' },
      },
      {
        path: 'orders/:id',
        name: 'order-detail',
        component: OrderDetailView,
        meta: { requiresAuth: true, sidebarSection: 'purchasing' },
      },
      {
        path: '/purchase-orders',
        name: 'purchase_orders',
        component: CreateOrderView,
        meta: { requiresAuth: true, sidebarSection: 'purchasing' },
      },
      {
        path: 'products',
        name: 'products',
        component: ProductsView,
        meta: { requiresAuth: true, sidebarSection: 'catalogue' },
      },
      {
        path: 'suppliers',
        name: 'suppliers',
        component: SuppliersView,
        meta: { requiresAuth: true, sidebarSection: 'suppliers', roles: ['staff'] },
      },
      {
        path: 'invoices',
        name: 'invoices',
        component: InvoicesView,
        meta: { requiresAuth: true, sidebarSection: 'suppliers', roles: ['staff'] },
      },
      {
        path: 'sku-mapping',
        name: 'sku-mapping',
        component: SkuMappingView,
        meta: { requiresAuth: true, sidebarSection: 'suppliers', roles: ['staff'] },
      },
      {
        path: 'admin/users',
        name: 'admin-users',
        component: UsersView,
        meta: { requiresAuth: true, sidebarSection: 'admin', roles: ['staff'] },
      },
      {
        path: 'admin/settings',
        name: 'admin-settings',
        component: SettingsView,
        meta: { requiresAuth: true, sidebarSection: 'admin', roles: ['staff'] },
      },
    ],
  },

  // ── Catch-all ─────────────────────────────────────────────
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ── Navigation guard ──────────────────────────────────────
router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  if (to.meta.guestOnly && auth.isAuthenticated) {
    return next({ name: 'dashboard' })
  }

  if (to.meta.roles && !to.meta.roles.includes(auth.user?.role ?? '')) {
    return next({ name: 'dashboard' })
  }

  next()
})

export default router