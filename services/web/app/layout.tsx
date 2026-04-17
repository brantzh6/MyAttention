import type { Metadata } from 'next'

import './globals.css'
import { Sidebar } from '@/components/ui/sidebar'

export const metadata: Metadata = {
  title: 'IKE - 智能决策支持系统',
  description: 'AI 驱动的信息获取、整理、知识沉淀与决策支持系统',
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
