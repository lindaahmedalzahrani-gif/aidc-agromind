import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// During local development the frontend calls its own backend proxy at /api.
// The proxy target below only matters for `npm run dev`; production builds
// use VITE_API_BASE_URL (see .env.example) or same-origin /api.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8787',
        changeOrigin: true,
      },
    },
  },
});
