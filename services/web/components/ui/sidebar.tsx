'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Activity, Brain, Home, MessageSquare, Settings } from 'lucide-react'

import { cn } from '@/lib/utils'

const navItems = [
  { href: '/', label: '信息流', icon: Home },
  { href: '/chat', label: '智能对话', icon: MessageSquare },
  { href: '/evolution', label: '进化大脑', icon: Activity },
  { href: '/settings', label: '设置', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="flex w-64 flex-col border-r bg-card">
      <div className="border-b p-4">
        <Link href="/" className="flex items-center gap-2">
          <Brain className="h-8 w-8 text-primary" />
          <span className="text-lg font-semibold">MyAttention</span>
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
        <p>MyAttention v0.1.0</p>
      </div>
    </aside>
  )
}
