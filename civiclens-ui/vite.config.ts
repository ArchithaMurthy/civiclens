import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Serve data files from project root's data/processed/
  server: {
    fs: { allow: ['..'] },
  },
})
