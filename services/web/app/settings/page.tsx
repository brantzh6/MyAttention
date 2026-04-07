import Link from 'next/link'
import { Bell, Brain, Database, FlaskConical, Rss, Sparkles } from 'lucide-react'

const settingsItems = [
  {
    title: '信息源管理',
    description: '管理 RSS 订阅、网页监控和 API 数据源。',
    href: '/settings/sources',
    icon: Rss,
  },
  {
    title: '模型配置',
    description: '配置大模型、路由策略和多模型投票能力。',
    href: '/settings/models',
    icon: Brain,
  },
  {
    title: '知识库管理',
    description: '管理 RAG 知识库文档、上传内容和索引状态。',
    href: '/settings/knowledge',
    icon: Database,
  },
  {
    title: '记忆管理',
    description: '查看和编辑长期记忆与用户事实。',
    href: '/settings/memory',
    icon: Sparkles,
  },
  {
    title: '通知设置',
    description: '配置飞书、钉钉等通知通道。',
    href: '/settings/notifications',
    icon: Bell,
  },
  {
    title: 'IKE Workspace',
    description: 'Experimental workspace for inspecting IKE v0.1 loop objects.',
    href: '/settings/ike',
    icon: FlaskConical,
  },
]

export default function SettingsPage() {
  return (
    <div className="p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-foreground">设置</h1>
        <p className="mt-1 text-muted-foreground">系统配置、模型管理和知识能力维护。</p>
      </header>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {settingsItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="block rounded-lg border bg-card p-6 transition-colors hover:border-primary"
          >
            <item.icon className="mb-3 h-8 w-8 text-primary" />
            <h2 className="font-medium text-card-foreground">{item.title}</h2>
            <p className="mt-1 text-sm text-muted-foreground">{item.description}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
