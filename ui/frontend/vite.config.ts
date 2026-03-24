import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/ws': {
        target: 'wss://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io',
        ws: true,
      },
    },
  },
})
