import { SourcesManager } from '@/components/settings/sources-manager'

export default function SourcesPage() {
  return (
    <div className="p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-foreground">信息源管理</h1>
        <p className="text-muted-foreground mt-1">管理 RSS 订阅、网页监控和 API 数据源</p>
      </header>
      <SourcesManager />
    </div>
  )
}
