/**
 * TAILWIND CSS — STABLE LAYOUTS WITH MINIMAL CODE
 * ─────────────────────────────────────────────────
 * A practical guide for the Ewan Millar / Spadework stack
 *
 * Core principle: Build structure first, style second.
 * A class that does two things is a bug waiting to happen.
 */


// ════════════════════════════════════════════════════════════════
// 1. THE MENTAL MODEL — three layers of classes
// ════════════════════════════════════════════════════════════════

/**
 * Layer 1 — STRUCTURE (layout, sizing, position)
 *   flex, grid, w-*, h-*, p-*, m-*, overflow-*
 *   These define WHERE things are. Never mix with decoration.
 *
 * Layer 2 — DECORATION (colour, border, shadow, rounded)
 *   bg-*, text-*, border-*, rounded-*, shadow-*
 *   These define HOW things look. Never use to control layout.
 *
 * Layer 3 — STATE (hover, focus, active, responsive)
 *   hover:*, focus:*, lg:*, md:*
 *   These modify layer 1 or 2 at a given state/breakpoint.
 *
 * The rule: each class should belong to exactly one layer.
 * If you're using `p-4` to "push things apart visually" — stop.
 * That's a layout decision dressed as decoration.
 */


// ════════════════════════════════════════════════════════════════
// 2. THE STABLE BASE LAYOUT (desktop + mobile, ~8 classes)
// ════════════════════════════════════════════════════════════════

/**
 * Full-height app shell — sidebar + content
 *
 * Desktop: sidebar fixed left, content fills right
 * Mobile:  sidebar hidden, content full width
 *
 * That's it. Don't add more until you need more.
 */

// HTML structure:
//
// <div class="min-h-screen flex flex-col">           ← full height, vertical stack
//   <header class="h-14 flex-shrink-0">              ← fixed height, won't shrink
//   <div class="flex flex-1 overflow-hidden">        ← fills remaining height
//     <aside class="w-64 flex-shrink-0 lg:block hidden">  ← sidebar, hidden mobile
//     <main class="flex-1 overflow-auto p-4 lg:p-6"> ← content, scrolls independently
//   <footer class="h-10 flex-shrink-0">              ← fixed height footer


// ════════════════════════════════════════════════════════════════
// 3. THE OVER-CODING TRAP — what it looks like
// ════════════════════════════════════════════════════════════════

// BAD — too many classes, multiple concerns mixed together:
// class="flex items-center gap-3 px-4 py-2 bg-blue-600 text-white
//        rounded-lg shadow-md hover:bg-blue-700 hover:shadow-lg
//        active:scale-95 transition-all duration-200 font-medium
//        text-sm tracking-wide border border-blue-700 cursor-pointer
//        focus:outline-none focus:ring-2 focus:ring-blue-500
//        focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"

// This is a button. It has 22 classes. It's unmaintainable.
// Structure, decoration, state, and typography are all mixed.

// GOOD — extract to a component class:
// In your CSS:
// .btn-primary {
//   @apply flex items-center gap-2 px-4 py-2
//          bg-brand-600 text-white text-sm font-medium rounded-lg
//          hover:bg-brand-700 transition-colors
//          focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2
//          disabled:opacity-50 disabled:cursor-not-allowed;
// }
//
// In your template:
// <button class="btn-primary">Save</button>
//
// Now you have ONE class in the template. The component is reusable.
// When the design changes, you change it in ONE place.


// ════════════════════════════════════════════════════════════════
// 4. RESPONSIVE — mobile first, extend upward
// ════════════════════════════════════════════════════════════════

/**
 * Tailwind is mobile-first. Unprefixed classes apply everywhere.
 * Prefixed classes (sm:, md:, lg:) apply AT that size and above.
 *
 * Pattern: write mobile layout first, add lg: overrides for desktop.
 * Never write desktop layout and try to override down — it's a mess.
 */

// Mobile first example — sidebar:
// class="hidden lg:block"     ← hidden on mobile, visible on desktop
// class="block lg:hidden"     ← visible on mobile, hidden on desktop
// class="p-4 lg:p-6"          ← less padding mobile, more desktop
// class="text-sm lg:text-base" ← smaller text mobile, normal desktop

// Breakpoints (min-width):
// sm:  640px   — large phones landscape
// md:  768px   — tablets
// lg:  1024px  — laptops (most common split point)
// xl:  1280px  — desktops
// 2xl: 1536px  — large monitors


// ════════════════════════════════════════════════════════════════
// 5. SPACING — the system that keeps things consistent
// ════════════════════════════════════════════════════════════════

/**
 * Tailwind's spacing scale is 4px per unit.
 * p-1 = 4px, p-2 = 8px, p-4 = 16px, p-6 = 24px, p-8 = 32px
 *
 * Pick 3-4 values and stick to them throughout the app.
 * For Ewan Millar we use:
 *   Component internal padding:  p-3 (12px) or p-4 (16px)
 *   Section gaps:                gap-4 (16px) or gap-6 (24px)
 *   Page padding:                p-4 mobile, p-6 desktop
 *   Tight UI (buttons, badges):  px-3 py-1.5
 *
 * If you find yourself using p-5, p-7, p-9 — stop and reconsider.
 * Consistency beats precision.
 */


// ════════════════════════════════════════════════════════════════
// 6. COLOUR — use semantic CSS variables, not hardcoded values
// ════════════════════════════════════════════════════════════════

/**
 * Define brand colours in tailwind.config.js, not inline.
 * This means ONE change updates the whole app.
 */

// tailwind.config.js:
// theme: {
//   extend: {
//     colors: {
//       brand: {
//         50:  '#eff6ff',
//         100: '#dbeafe',
//         500: '#3b82f6',
//         600: '#2563eb',   ← primary action colour
//         700: '#1d4ed8',   ← hover state
//       }
//     }
//   }
// }

// Then use: bg-brand-600, text-brand-700, ring-brand-500
// Not:       bg-blue-600 (hardcoded, changes require find/replace)


// ════════════════════════════════════════════════════════════════
// 7. WHEN TO USE @apply vs inline classes
// ════════════════════════════════════════════════════════════════

/**
 * Inline Tailwind classes — use when:
 *   • The style is unique to this element
 *   • It won't be reused
 *   • It's structural (layout, spacing)
 *   • Max ~6-8 classes
 *
 * @apply in CSS — use when:
 *   • The same combination appears 3+ times
 *   • It's a UI primitive (button, badge, input, card)
 *   • The class list exceeds ~8 classes
 *   • You want one place to update the design
 *
 * Vue component — use when:
 *   • The element has behaviour (not just style)
 *   • It's used across multiple views
 *   • It needs props to vary its appearance
 *
 * The ladder:
 *   inline classes → @apply → Vue component
 *   Move up when complexity increases.
 */


// ════════════════════════════════════════════════════════════════
// 8. THE "FANCY BITS" — add on top of the stable base
// ════════════════════════════════════════════════════════════════

/**
 * Once your layout is stable, enhance with:
 *
 * Transitions:     transition-colors, transition-transform, duration-200
 * Shadows:         shadow-sm (subtle), shadow-md (cards), shadow-lg (modals)
 * Ring focus:      focus:ring-2 focus:ring-brand-500 focus:ring-offset-2
 * Hover lift:      hover:-translate-y-0.5 hover:shadow-md
 * Active press:    active:scale-95
 * Skeleton load:   animate-pulse bg-slate-200
 *
 * Rule: add ONE enhancement at a time. Test it. Keep it if it helps.
 * Don't add hover + shadow + transition + ring + scale all at once
 * and wonder why it looks wrong.
 */


// ════════════════════════════════════════════════════════════════
// 9. COMMON PATTERNS FOR THIS STACK
// ════════════════════════════════════════════════════════════════

// ── Page wrapper (consistent page padding) ────────────────────
// <div class="space-y-6">   ← vertical rhythm between sections

// ── Section card ──────────────────────────────────────────────
// <div class="bg-white rounded-xl border border-slate-200 p-4 lg:p-6">

// ── Page heading ──────────────────────────────────────────────
// <h1 class="text-xl font-semibold text-slate-800">

// ── Muted subtext ─────────────────────────────────────────────
// <p class="text-sm text-slate-500">

// ── Data table wrapper (horizontal scroll on mobile) ──────────
// <div class="overflow-x-auto">
//   <table class="w-full text-sm">

// ── Status badge ──────────────────────────────────────────────
// .badge-green { @apply inline-flex px-2 py-0.5 rounded-full text-xs
//                       font-medium bg-green-50 text-green-700 }
// .badge-amber { @apply inline-flex px-2 py-0.5 rounded-full text-xs
//                       font-medium bg-amber-50 text-amber-700 }
// .badge-red   { @apply inline-flex px-2 py-0.5 rounded-full text-xs
//                       font-medium bg-red-50 text-red-700 }

// ── Form input (the .input class from your components) ────────
// .input { @apply w-full border border-slate-200 rounded-lg px-3 py-2
//                 text-sm bg-white focus:outline-none
//                 focus:ring-2 focus:ring-brand-500 focus:border-transparent }
