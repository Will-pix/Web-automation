import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import WindiCSS from 'vite-plugin-windicss'

// https://vite.dev/config/

export default defineConfig({
  resolve:{
    alias:{
      "~":path.resolve(__dirname,"src")
    }
  },
  plugins: [vue(),WindiCSS()],
  server: {
    proxy: {
      '^/api': { // 匹配axios的baseURL
          target: 'http://127.0.0.1:5000',
          changeOrigin: true,
          // rewrite: (path) => path.replace(/^\/proxy/, '') // 移除代理前缀
          rewrite: (path) => path // 不修改路径
      }
  }
  }
})
