/**
 * src/config/navigation.js
 *
 * Single source of truth for the sidebar navigation.
 * Each section maps to an accordion panel.
 * Each item has an optional `roles` array — if omitted, all roles can see it.
 *
 * Roles: 'staff' | 'customer' | 'supplier'
 */

export const navConfig = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'grid',
    roles: ['staff', 'customer', 'supplier'],
    items: [
      { label: 'Overview',        route: '/dashboard',            roles: ['staff', 'customer', 'supplier'] },
    ],
  },
  {
    id: 'purchasing',
    label: 'Purchasing',
    icon: 'shopping-bag',
    roles: ['staff', 'customer'],
    items: [
      { label: 'Orders',          route: '/orders',               roles: ['staff', 'customer'] },
      { label: 'Create Order',    route: '/orders/create',        roles: ['staff'] },
      { label: 'Purchase Orders', route: '/purchase-orders',      roles: ['staff'] },
    ],
  },
  {
    id: 'catalogue',
    label: 'Catalogue',
    icon: 'gem',
    roles: ['staff', 'customer'],
    items: [
      { label: 'Products',        route: '/products',             roles: ['staff', 'customer'] },
      { label: 'Categories',      route: '/categories',           roles: ['staff'] },
      { label: 'Certifications',  route: '/certifications',       roles: ['staff'] },
    ],
  },
  {
    id: 'suppliers',
    label: 'Suppliers',
    icon: 'truck',
    roles: ['staff'],
    items: [
      { label: 'Supplier List',   route: '/suppliers',            roles: ['staff'] },
      { label: 'Invoices',        route: '/invoices',             roles: ['staff'] },
      { label: 'SKU Mapping',     route: '/sku-mapping',          roles: ['staff'] },
    ],
  },
  {
    id: 'supply',
    label: 'My Supply',
    icon: 'package',
    roles: ['supplier'],
    items: [
      { label: 'My Invoices',     route: '/my-invoices',          roles: ['supplier'] },
      { label: 'My Products',     route: '/my-products',          roles: ['supplier'] },
    ],
  },
  {
    id: 'admin',
    label: 'Administration',
    icon: 'settings',
    roles: ['staff'],
    items: [
      { label: 'Users',           route: '/admin/users',          roles: ['staff'] },
      { label: 'Invitations',     route: '/admin/invitations',    roles: ['staff'] },
      { label: 'Settings',        route: '/admin/settings',       roles: ['staff'] },
    ],
  },
]
