import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // 只在生产环境使用base前缀，开发环境使用根路径
  base: "/newMetrograph",
  server: {
    fs: {
      // 允许访问项目根目录以外的文件
      allow: ['..']
    }
  }
})
