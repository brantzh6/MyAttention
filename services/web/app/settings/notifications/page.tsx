import { NotificationsConfig } from '@/components/settings/notifications-config'

export default function NotificationsPage() {
  return (
    <div className="p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-foreground">通知设置</h1>
        <p className="text-muted-foreground mt-1">配置飞书、钉钉推送</p>
      </header>
      <NotificationsConfig />
    </div>
  )
}
