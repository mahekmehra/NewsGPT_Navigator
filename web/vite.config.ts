import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  server: {
    port: 5173,
    proxy: {
      '/health': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/analyze': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/compare': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/languages': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/personas': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/audio': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/video': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})
