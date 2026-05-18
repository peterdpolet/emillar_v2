/**
 * src/config/navigation.js
 */
export const navConfig = [
  {
    id: 'home',
    label: 'Home',
    icon: 'home',
    direct: '/home',                          // ← new flag
    roles: ['staff', 'customer', 'supplier'],
    items: [],
  },
  {
    id: 'about',
    label: 'About',
    icon: 'info',
    direct: '/about',
    roles: ['staff', 'customer', 'supplier'],
    items: [],
  },

  {
    id: 'sales',
    label: 'Sales',
    icon: 'truck',
    roles: ['staff'],
    items: [
      { label: 'Sales Orders',    route: '/sales-orders-v2', roles: ['staff'] },
      { label: 'Appro Dashboard', route: '/appro',           roles: ['staff'] },
      { label: 'Invoices',        route: '/invoices',        roles: ['staff'] },
      { label: 'Customers',       route: '/suppliers',       roles: ['staff'] },
      { label: 'Inventory',       route: '/inventory',       roles: ['staff'] },
    ],
  },
  {
    id: 'purchasing',
    label: 'Purchasing',
    icon: 'shopping-bag',
    roles: ['staff'],
    items: [
      { label: 'Purchase Orders', route: '/purchase-orders', roles: ['staff'] },
      { label: 'Appro Dashboard', route: '/appro',           roles: ['staff'] },
      { label: 'Supplier List',   route: '/suppliers',       roles: ['staff'] },
    ],
  },
  {
    id: 'catalogue',
    label: 'Catalogue',
    icon: 'gem',
    roles: ['staff', 'customer'],
    items: [
      { label: 'Products', route: '/products', roles: ['staff', 'customer'] },
    ],
  },
  {
    id: 'supply',
    label: 'My Supply',
    icon: 'package',
    roles: ['supplier'],
    items: [
      { label: 'My Invoices', route: '/my-invoices', roles: ['supplier'] },
      { label: 'My Products', route: '/my-products', roles: ['supplier'] },
    ],
  },
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'grid',
    roles: ['staff', 'customer', 'supplier'],
    items: [

    ],
  },
  {
    id: 'admin',
    label: 'Administration',
    icon: 'settings',
    roles: ['staff'],
    items: [
      { label: 'Users',    route: '/admin/users',    roles: ['staff'] },
      { label: 'Settings', route: '/admin/settings', roles: ['staff'] },
    ],
  },
]
