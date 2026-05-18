<template>
  <div class="max-w-3xl space-y-6">

    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-slate-800">About Ewan Millar Ltd</h1>
      <p class="text-slate-400 text-sm mt-1">Precious Stones Trading Platform</p>
    </div>

    <!-- Company -->
    <div class="bg-white rounded-xl border border-slate-200 p-6">
      <h2 class="text-sm font-semibold text-slate-700 uppercase tracking-wide mb-4">The Company</h2>
      <div class="prose prose-sm text-slate-600 max-w-none space-y-3">
        <p>
          Ewan Millar Ltd is a specialist B2B precious stones trading company operating in the global
          gemstone market. We work with a curated network of trusted suppliers worldwide to source
          certified and uncertified diamonds, rubies, sapphires, emeralds and pearls for our customers.
        </p>
        <p>
          Our expertise spans the full trading cycle — from customer enquiry and supplier sourcing,
          through approval stock management, to final sale and invoice matching. We operate with
          transparency, precision and deep domain knowledge built over years in the industry.
        </p>
      </div>
    </div>

    <!-- Platform -->
    <div class="bg-white rounded-xl border border-slate-200 p-6">
      <h2 class="text-sm font-semibold text-slate-700 uppercase tracking-wide mb-4">The Platform</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

        <div class="flex gap-3">
          <div class="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z"/>
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium text-slate-700">Sales Order Management</p>
            <p class="text-xs text-slate-400 mt-0.5">Customer RFQs, multi-supplier quotes, order tracking</p>
          </div>
        </div>

        <div class="flex gap-3">
          <div class="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 00-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 00-16.536-1.84M7.5 14.25L5.106 5.272M6 20.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm12.75 0a.75.75 0 11-1.5 0 .75.75 0 011.5 0z"/>
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium text-slate-700">Purchase Order Management</p>
            <p class="text-xs text-slate-400 mt-0.5">PO creation, GRN tracking, three-way invoice matching</p>
          </div>
        </div>

        <div class="flex gap-3">
          <div class="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z"/>
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium text-slate-700">Appro Stock Control</p>
            <p class="text-xs text-slate-400 mt-0.5">Full approval cycle tracking with reference system</p>
          </div>
        </div>

        <div class="flex gap-3">
          <div class="w-8 h-8 rounded-lg bg-violet-50 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z"/>
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium text-slate-700">Real-time Chat</p>
            <p class="text-xs text-slate-400 mt-0.5">Internal messaging with WebSocket support</p>
          </div>
        </div>

        <div class="flex gap-3">
          <div class="w-8 h-8 rounded-lg bg-rose-50 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/>
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium text-slate-700">Secure & Invitation Only</p>
            <p class="text-xs text-slate-400 mt-0.5">2FA authentication, role-based access control</p>
          </div>
        </div>

        <div class="flex gap-3">
          <div class="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6.72 13.829c-.24.03-.48.062-.72.096m.72-.096a42.415 42.415 0 0110.56 0m-10.56 0L6.34 18m10.94-4.171c.24.03.48.062.72.096m-.72-.096L17.66 18m0 0l.229 2.523a1.125 1.125 0 01-1.12 1.227H7.231c-.662 0-1.18-.568-1.12-1.227L6.34 18m11.318 0h1.091A2.25 2.25 0 0021 15.75V9.456c0-1.081-.768-2.015-1.837-2.175a48.055 48.055 0 00-1.913-.247M6.34 18H5.25A2.25 2.25 0 013 15.75V9.456c0-1.081.768-2.015 1.837-2.175a48.041 48.041 0 011.913-.247m10.5 0a48.536 48.536 0 00-10.5 0m10.5 0V3.375c0-.621-.504-1.125-1.125-1.125h-8.25c-.621 0-1.125.504-1.125 1.125v3.659M18 10.5h.008v.008H18V10.5zm-3 0h.008v.008H15V10.5z"/>
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium text-slate-700">PDF Documents</p>
            <p class="text-xs text-slate-400 mt-0.5">Print-ready Sales Orders and Purchase Orders</p>
          </div>
        </div>

      </div>
    </div>

    <!-- Tech stack -->
    <div class="bg-white rounded-xl border border-slate-200 p-6">
      <h2 class="text-sm font-semibold text-slate-700 uppercase tracking-wide mb-4">Technology</h2>
      <div class="flex flex-wrap gap-2">
        <span v-for="tech in stack" :key="tech"
          class="px-2.5 py-1 text-xs font-medium bg-slate-100 text-slate-600 rounded-full">
          {{ tech }}
        </span>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
const stack = [
  'Vue 3', 'TypeScript', 'Pinia', 'Vue Router', 'Tailwind CSS',
  'Django 6', 'Django REST Framework', 'PostgreSQL', 'Redis',
  'Django Channels', 'WebSockets', 'Docker', 'Nginx', 'DigitalOcean',
  'JWT Auth', 'TOTP 2FA', 'WeasyPrint',
]
</script>