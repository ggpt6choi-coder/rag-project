import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/v1/upload-file': 'http://localhost:8000',
      '/api/v1/collections': 'http://localhost:8000',
      '/api/v1/documents': 'http://localhost:8000',
      '/api/v1/qa': 'http://localhost:8000',
      '/api/v1/search': 'http://localhost:8000',
      '/api/v1/health': 'http://localhost:8000',
    },
  },
});
