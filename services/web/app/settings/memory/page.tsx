import { MemoryManager } from '@/components/settings/memory-manager'

export default function MemoryPage() {
  return (
    <div className="p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-foreground">记忆管理</h1>
        <p className="text-muted-foreground mt-1">管理长期记忆，系统会自动从对话中提取重要信息</p>
      </header>
      <MemoryManager />
    </div>
  )
}
