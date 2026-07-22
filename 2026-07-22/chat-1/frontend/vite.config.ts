import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/resume': 'http://localhost:8000',
      '/flow': 'http://localhost:8000',
      '/jobs': 'http://localhost:8000',
      '/grants': 'http://localhost:8000',
      '/upskilling': 'http://localhost:8000',
      '/apply': 'http://localhost:8000',
    },
  },
})
