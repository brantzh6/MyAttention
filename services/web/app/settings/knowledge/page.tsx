import { KnowledgeBaseManager } from '@/components/settings/knowledge-base-manager'

export default function KnowledgePage() {
  return (
    <div className="p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-foreground">知识库管理</h1>
        <p className="text-muted-foreground mt-1">管理多个知识库，支持文件上传、网页索引和网络搜索</p>
      </header>
      <KnowledgeBaseManager />
    </div>
  )
}
