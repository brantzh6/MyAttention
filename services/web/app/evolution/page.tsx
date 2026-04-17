import { EvolutionDashboard } from '@/components/evolution/evolution-dashboard'

export default function EvolutionPage() {
  return (
    <div className="p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-foreground">进化大脑</h1>
        <p className="mt-1 text-muted-foreground">系统自检、持续监控、问题归因和方法迭代的统一入口。</p>
      </header>
      <EvolutionDashboard />
    </div>
  )
}
