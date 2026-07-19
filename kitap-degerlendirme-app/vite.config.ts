import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    {
      name: 'serve-root-index',
      configureServer(server) {
        server.middlewares.use((req, _res, next) => {
          const request = req as { url?: string };
          if (request.url === '/') {
            request.url = '/index.html';
          }
          next();
        });
      }
    },
    react()
  ],
  resolve: {
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json']
  },
  root: './',
  server: {
    port: 3000,
    open: false,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true
      },
      '/health': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true
      }
    },
    fs: {
      strict: false,
      allow: ['.']
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
});
