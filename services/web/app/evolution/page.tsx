import { EvolutionDashboard } from '@/components/evolution/evolution-dashboard'

export default function EvolutionPage() {
  return (
    <div className="p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-foreground">进化大脑</h1>
        <p className="mt-1 text-muted-foreground">
          面向系统诊断、优先级调整、方法论迭代与持续改进的控制面。
          它建立在信息大脑与知识大脑之上，并持续吸收世界模型与思维工具。
        </p>
      </header>
      <EvolutionDashboard />
    </div>
  )
}
