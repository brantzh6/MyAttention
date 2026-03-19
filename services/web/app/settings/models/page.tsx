import { ModelsConfig } from '@/components/settings/models-config'

export default function ModelsPage() {
  return (
    <div className="p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-foreground">LLM 配置</h1>
        <p className="text-muted-foreground mt-1">配置大模型、路由策略和多模型投票</p>
      </header>
      <ModelsConfig />
    </div>
  )
}
