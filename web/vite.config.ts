import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy /api to FastAPI so dev calls look like /api/...
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''), // /api/applications -> /applications
      },
    },
  },
})
