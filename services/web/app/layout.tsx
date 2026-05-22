import type { Metadata } from 'next'

import './globals.css'
import { Sidebar } from '@/components/ui/sidebar'

export const metadata: Metadata = {
  title: 'IKE - 信息大脑、知识大脑、进化大脑、世界模型与思维工具',
  description: '以信息大脑、知识大脑、进化大脑、世界模型和思维工具组织的 AI 驱动系统，用于持续发现、整理、推理与进化。',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-CN">
      <body>
        <div className="flex h-screen">
          <Sidebar />
          <main className="flex-1 overflow-auto">{children}</main>
        </div>
      </body>
    </html>
  )
}
