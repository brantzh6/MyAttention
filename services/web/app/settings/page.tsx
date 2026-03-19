import Link from 'next/link'
import { Rss, Brain, Bell, Database, Sparkles } from 'lucide-react'

const settingsItems = [
  {
    title: '信息源管理',
    description: '管理 RSS 订阅、网页监控和 API 数据源',
    href: '/settings/sources',
    icon: Rss,
  },
  {
    title: 'LLM 配置',
    description: '配置大模型、路由策略和多模型投票',
    href: '/settings/models',
    icon: Brain,
  },
  {
    title: '知识库管理',
    description: '管理 RAG 知识库文档，上传和索引内容',
    href: '/settings/knowledge',
    icon: Database,
  },
  {
    title: '记忆管理',
    description: '管理长期记忆，查看和编辑 AI 提取的用户信息',
    href: '/settings/memory',
    icon: Sparkles,
  },
  {
    title: '通知设置',
    description: '配置飞书、钉钉推送',
    href: '/settings/notifications',
    icon: Bell,
  },
]

export default function SettingsPage() {
  return (
    <div className="p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-foreground">设置</h1>
        <p className="text-muted-foreground mt-1">系统配置和管理</p>
      </header>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {settingsItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="block p-6 bg-card rounded-lg border hover:border-primary transition-colors"
          >
            <item.icon className="h-8 w-8 text-primary mb-3" />
            <h2 className="font-medium text-card-foreground">{item.title}</h2>
            <p className="text-sm text-muted-foreground mt-1">{item.description}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
