import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  esbuild: {
    tsconfigRaw: {
      compilerOptions: {
        baseUrl: '.',
      }
    }
  },
  resolve: {
    alias: { 
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@purchasing': '/src/features/purchasing',
      '@orders': '/src/features/orders',
      '@shared': '/src/shared',
      '@inventory': '/src/features/inventory',
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  },

})