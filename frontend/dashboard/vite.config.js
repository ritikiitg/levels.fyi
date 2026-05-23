import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    proxy: {
      '/api': 'http://localhost:8000',
      '/_defender': { target: 'ws://localhost:8000', ws: true, changeOrigin: true },
    },
  },
});
