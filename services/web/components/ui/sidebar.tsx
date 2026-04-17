'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Activity, Brain, Home, MessageSquare, Settings } from 'lucide-react'

import { cn } from '@/lib/utils'

const navItems = [
  { href: '/', label: '信息大脑', icon: Home },
  { href: '/chat', label: '知识大脑', icon: MessageSquare },
  { href: '/evolution', label: '进化大脑', icon: Activity },
  { href: '/settings', label: '设置', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="flex w-64 flex-col border-r bg-card">
      <div className="border-b p-4">
        <Link href="/" className="flex items-center gap-3">
          <Brain className="h-8 w-8 text-primary" />
          <div className="leading-tight">
            <p className="text-lg font-semibold">IKE</p>
            <p className="text-xs text-muted-foreground">信息 / 知识 / 进化 / 世界模型 / 思维工具</p>
          </div>
        </Link>
      </div>

      <nav className="flex-1 p-4">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      <div className="border-t p-4 text-xs text-muted-foreground">
        <p>IKE v0.1.0</p>
        <p className="mt-1">代码仓库仍是 MyAttention，迁移到 IKE 后再统一改名。</p>
      </div>
    </aside>
  )
}
