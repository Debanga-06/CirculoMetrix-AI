import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Enable Fast Refresh
      fastRefresh: true,
      // Babel configuration
      babel: {
        plugins: [
          // Add any Babel plugins here if needed
        ],
      },
    }),
  ],

  // Path resolution
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@assets': path.resolve(__dirname, './src/assets'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@store': path.resolve(__dirname, './src/store'),
      '@services': path.resolve(__dirname, './src/services'),
    },
  },

  // Server configuration
  server: {
    port: 5173,
    host: true, // Listen on all addresses
    strictPort: true, // Exit if port is already in use
    open: true, // Open browser on server start
    cors: true,
    
    // Proxy API requests to backend
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'https://circulometrix-ai.onrender.com',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },

    // HMR configuration
    hmr: {
      overlay: true,
    },
  },

  // Preview server configuration (for production build)
  preview: {
    port: 4173,
    host: true,
    strictPort: true,
    open: true,
  },

  // Build configuration
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: process.env.NODE_ENV === 'development',
    
    // Minification
    minify: 'esbuild',
    
    // Target browsers
    target: 'es2015',
    
    // Rollup options
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor chunks for better caching
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'chart-vendor': ['recharts', 'd3'],
          'utils-vendor': ['axios', 'zustand', 'react-hook-form'],
        },
        // Naming convention for chunks
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },

    // Chunk size warning limit (in KB)
    chunkSizeWarningLimit: 1000,

    // CSS code splitting
    cssCodeSplit: true,

    // Report compressed size
    reportCompressedSize: true,

    // Clear output directory before build
    emptyOutDir: true,
  },

  // Optimization
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'axios',
      'recharts',
      'd3',
      'lucide-react',
      'framer-motion',
      'zustand',
    ],
    exclude: [],
  },

  // CSS configuration
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`,
      },
    },
    modules: {
      localsConvention: 'camelCase',
    },
    devSourcemap: true,
  },

  // Define global constants
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },

  // Environment variables prefix
  envPrefix: 'VITE_',

  // JSON handling
  json: {
    namedExports: true,
    stringify: false,
  },

  // ESBuild options
  esbuild: {
    logOverride: { 'this-is-undefined-in-esm': 'silent' },
    jsxInject: `import React from 'react'`,
  },

  // Test configuration (Vitest)
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.test.{js,jsx}',
        '**/*.spec.{js,jsx}',
      ],
    },
  },
});
