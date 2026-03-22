import { NotificationsConfig } from '@/components/settings/notifications-config'

export default function NotificationsPage() {
  return (
    <div className="p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-foreground">通知设置</h1>
        <p className="mt-1 text-muted-foreground">配置飞书、钉钉和摘要推送策略。</p>
      </header>
      <NotificationsConfig showSystemStatus={false} />
    </div>
  )
}
