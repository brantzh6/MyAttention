import { getSnapshot } from '@/lib/control-surface/get-snapshot'
import { ProvenanceBlock } from '@/components/control/provenance-block'
import { ScoreStatus, MainlineTask } from '@/lib/control-surface/types'
import { mapPmDigestStatus } from '@/lib/control-surface/ops-state-adapter'
import {
  CheckCircle2,
  Clock,
  AlertTriangle,
  Activity,
  ShieldCheck,
  Zap,
  Info,
  ChevronDown,
  ListFilter,
  Cpu,
  LayoutDashboard,
  Database,
  ArrowRight
} from 'lucide-react'

export const dynamic = 'force-dynamic'

function StatusBadge({ status }: { status: ScoreStatus }) {
  const colors: Record<ScoreStatus, string> = {
    estimated: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 border-blue-200 dark:border-blue-800',
    accepted: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 border-green-200 dark:border-green-800',
    blocked: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 border-red-200 dark:border-red-800',
    unknown: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-700'
  }

  const labels: Record<ScoreStatus, string> = {
    estimated: '部分/进行中',
    accepted: '已接受',
    blocked: '已阻塞',
    unknown: '未知'
  }

  const icons: Record<ScoreStatus, React.ReactNode> = {
    estimated: <Activity className="w-3 h-3" />,
    accepted: <CheckCircle2 className="w-3 h-3" />,
    blocked: <AlertTriangle className="w-3 h-3" />,
    unknown: <Clock className="w-3 h-3" />
  }

  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider border flex items-center gap-1.5 ${colors[status]}`}>
      {icons[status]}
      {labels[status]}
    </span>
  )
}

function AutomationStatusBadge({ status }: { status: 'healthy' | 'caveat' | 'unhealthy' }) {
  const colors = {
    healthy: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 border-green-200 dark:border-green-800',
    caveat: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200 border-amber-200 dark:border-amber-800',
    unhealthy: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 border-red-200 dark:border-red-800'
  }
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider border ${colors[status]}`}>
      {status === 'healthy' ? '健康' : status === 'caveat' ? '风险' : '异常'}
    </span>
  )
}

function TaskProgressRow({ task }: { task: MainlineTask }) {
  return (
    <div className="flex items-center gap-4 py-3 border-b last:border-0">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h3 className="font-bold text-sm truncate">{task.title}</h3>
          <StatusBadge status={task.status} />
        </div>
        <p className="text-xs text-muted-foreground line-clamp-1">{task.description}</p>
      </div>
      <div className="hidden sm:block text-right whitespace-nowrap">
        <span className="text-[10px] text-muted-foreground uppercase font-medium">状态 / Status</span>
        <div className="text-xs font-semibold">{task.status === 'accepted' ? '完成' : '推进中'}</div>
      </div>
    </div>
  )
}

export default async function ControlDashboardPage() {
  const data = await getSnapshot()

  const firstClassTaskIds = ['evolution_flywheel_v1', 'ai_conversation_entry', 'project_control_surface']
  const dashboardTasks = data.tasks.filter(t => firstClassTaskIds.includes(t.id))
  // Sort to match requested order
  dashboardTasks.sort((a, b) => firstClassTaskIds.indexOf(a.id) - firstClassTaskIds.indexOf(b.id))

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-20 px-4 sm:px-6">
      {/* 1. IKE Mainline Header */}
      <header className="relative overflow-hidden border rounded-xl bg-muted/10 shadow-sm p-6">
        <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-primary">
              <LayoutDashboard className="w-5 h-5" />
              <span className="text-xs font-bold uppercase tracking-[0.2em]">IKE Mainline</span>
            </div>
            <h1 className="text-3xl font-black tracking-tight">{data.mainline.name}</h1>
            <p className="text-sm text-muted-foreground max-w-2xl">
              目标：{data.controlSummary?.mainlineGoal || (<span>第一阶段可用 AI 对话 {"->"} 进化飞轮 (Evolution Flywheel) {"->"} 控制平面闭环</span>)}
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <div className="px-3 py-1.5 rounded-lg bg-background/80 backdrop-blur-sm border shadow-sm">
              <span className="block text-[10px] uppercase font-bold text-muted-foreground mb-0.5">当前阶段 / Phase</span>
              <span className="text-xs font-bold text-primary truncate block max-w-[200px]">{data.controlSummary?.currentPhase || data.phase.current}</span>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-background/80 backdrop-blur-sm border shadow-sm flex flex-col justify-center">
              <span className="block text-[10px] uppercase font-bold text-muted-foreground mb-1">同步状态 / Sync</span>
              <div className="flex items-center gap-1.5 text-[10px] font-mono">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                {data.provenance.freshnessLabel}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 2. Three First-Class Task Progress Rows */}
      <section className="border rounded-xl bg-card shadow-sm overflow-hidden">
        <div className="px-4 py-3 border-b bg-muted/20 flex items-center justify-between">
          <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-500" /> 核心任务进度 / Task Progress
          </h2>
        </div>
        <div className="px-4">
          {dashboardTasks.map(task => (
            <TaskProgressRow key={task.id} task={task} />
          ))}
          {dashboardTasks.length === 0 && (
            <div className="py-6 text-center text-xs text-muted-foreground italic">
              未找到核心任务数据，请检查状态适配器。
            </div>
          )}
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 3. Current Blocker / Decision */}
        <div className="lg:col-span-7 space-y-6">
          {data.controlSummary?.currentBlocker ? (
            <section className="border rounded-xl bg-amber-50/50 dark:bg-amber-950/10 border-amber-200 dark:border-amber-900/50 p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2 text-amber-800 dark:text-amber-300">
                  <AlertTriangle className="w-5 h-5" />
                  <h2 className="font-bold text-sm uppercase tracking-wider text-amber-900 dark:text-amber-100">当前阻塞 / Current Blocker</h2>
                </div>
                <span className="px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200 border border-amber-200 dark:border-amber-800 text-[10px] font-bold uppercase">
                  {data.controlSummary.currentBlocker.status}
                </span>
              </div>
              <div className="space-y-4 text-sm leading-relaxed">
                <div>
                  <h3 className="font-bold text-amber-900 dark:text-amber-100 mb-1">{data.controlSummary.currentBlocker.title}</h3>
                  <p className="text-muted-foreground">{data.controlSummary.currentBlocker.summary}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-bold text-muted-foreground">关键原因 / Why it matters</span>
                    <p className="text-xs">{data.controlSummary.currentBlocker.whyItMatters}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-bold text-muted-foreground">风险与影响 / Risk & Radius</span>
                    <p className="text-xs">
                      <span className="font-bold text-red-600 dark:text-red-400 mr-1">[{data.controlSummary.currentBlocker.riskLevel.toUpperCase()}]</span>
                      {data.controlSummary.currentBlocker.blastRadius}
                    </p>
                  </div>
                </div>

                <div className="pt-2 space-y-3">
                  <div>
                    <span className="text-[10px] uppercase font-bold text-muted-foreground block mb-1.5">已完成步骤 / Completed</span>
                    <ul className="space-y-1">
                      {data.controlSummary.currentBlocker.completedSteps.map((step, i) => (
                        <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                          <CheckCircle2 className="w-3 h-3 mt-0.5 text-green-500 flex-shrink-0" />
                          <span>{step}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-muted-foreground block mb-1.5">建议后续步骤 / Proposed Steps</span>
                    <ul className="space-y-1">
                      {data.controlSummary.currentBlocker.proposedSteps.map((step, i) => (
                        <li key={i} className="flex items-start gap-2 text-xs">
                          <ArrowRight className="w-3 h-3 mt-0.5 text-amber-500 flex-shrink-0" />
                          <span>{step}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </section>
          ) : (
             <section className="border rounded-xl bg-muted/5 p-5 shadow-sm border-dashed">
              <div className="flex items-center gap-2 mb-2 text-muted-foreground">
                <CheckCircle2 className="w-4 h-4" />
                <h2 className="font-bold text-xs uppercase tracking-wider">无活动阻塞 / No Active Blocker</h2>
              </div>
              <p className="text-[10px] text-muted-foreground italic">目前未探测到关键阻塞项。</p>
            </section>
          )}

          {data.controlSummary?.plan && (
            <section className="border rounded-xl bg-card shadow-sm p-5">
              <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
                <ListFilter className="w-4 h-4" /> 推进计划 / Strategic Plan
              </h2>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex flex-col items-center pt-1">
                    <div className="w-2 h-2 rounded-full bg-primary" />
                    <div className="w-0.5 flex-1 bg-border my-1" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-primary block mb-0.5">当前 / Now</span>
                    <p className="text-xs font-medium">{data.controlSummary.plan.now}</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex flex-col items-center pt-1">
                    <div className="w-2 h-2 rounded-full bg-muted-foreground/30" />
                    <div className="w-0.5 flex-1 bg-border my-1" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-muted-foreground block mb-0.5">后续 / Next</span>
                    <p className="text-xs text-muted-foreground">{data.controlSummary.plan.next}</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex flex-col items-center pt-1">
                    <div className="w-2 h-2 rounded-full bg-muted-foreground/20" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-muted-foreground block mb-0.5">未来 / Later</span>
                    <p className="text-xs text-muted-foreground/70">{data.controlSummary.plan.later}</p>
                  </div>
                </div>
              </div>
            </section>
          )}
        </div>

        <div className="lg:col-span-5 space-y-6">
          {/* 5. Runtime Readiness */}
          <section className="border rounded-xl bg-card shadow-sm overflow-hidden">
            <div className="px-4 py-3 border-b bg-muted/20">
              <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                <Activity className="w-4 h-4" /> 运行时就绪 / Runtime Readiness
              </h2>
            </div>
            <div className="p-4 grid grid-cols-2 gap-3">
              {data.runtime ? (
                data.runtime.services.map(svc => (
                  <div key={svc.id} className="p-2 border rounded-lg bg-background flex flex-col gap-1">
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-bold uppercase">{svc.id}</span>
                      <div className={`w-2 h-2 rounded-full ${svc.status === 'healthy' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-red-500'}`} />
                    </div>
                    <span className="text-[9px] text-muted-foreground truncate">{svc.details || '在线'}</span>
                  </div>
                ))
              ) : (
                <div className="col-span-2 py-4 text-center text-[10px] text-muted-foreground italic border-2 border-dashed rounded-lg">
                  无实时探测数据
                </div>
              )}
            </div>
          </section>

          {/* 6. Quality / Promotion Gate */}
          <section className="border rounded-xl bg-card shadow-sm p-4">
            <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4" /> 质量准入门槛 / Promotion Gate
            </h2>
            <div className="space-y-3">
              <div className="p-2.5 rounded-lg bg-muted/30 border text-xs">
                <div className="flex items-center gap-2 mb-1">
                  <Info className="w-3 h-3 text-blue-500" />
                  <span className="font-bold">L1 审查状态</span>
                </div>
                <p className="text-muted-foreground text-[11px]">{data.reviewState.prReviewGate}</p>
              </div>
              {data.controlSummary?.qualityGate ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="p-2 rounded bg-muted/30 border text-[10px]">
                      <span className="block text-muted-foreground uppercase font-bold mb-1">本地审查 / Local</span>
                      <span className="font-semibold">{data.controlSummary.qualityGate.localReviewStatus}</span>
                    </div>
                    <div className="p-2 rounded bg-muted/30 border text-[10px]">
                      <span className="block text-muted-foreground uppercase font-bold mb-1">云端审查 / Cloud</span>
                      <span className="font-semibold">{data.controlSummary.qualityGate.cloudReviewStatus}</span>
                    </div>
                  </div>

                  {data.controlSummary.qualityGate.exceptionActive && (
                    <div className="p-2.5 rounded-lg bg-amber-500/5 border border-amber-500/20">
                      <div className="flex items-center gap-2 mb-1.5">
                        <AlertTriangle className="w-3 h-3 text-amber-500" />
                        <span className="text-[10px] font-bold text-amber-800 dark:text-amber-300 uppercase">质量例外激活 / Exception Active</span>
                      </div>
                      <div className="text-[10px] text-amber-700 dark:text-amber-400 space-y-1">
                        <p className="font-medium">范围 / Scope: {data.controlSummary.qualityGate.exceptionScope.join(', ')}</p>
                        <p className="italic">由于云端审查配额耗尽，PR 已通过本地独立审查授权，不受云端状态阻塞。</p>
                      </div>
                    </div>
                  )}

                  <div className="p-2 rounded border flex items-center justify-between text-[10px]">
                    <span className="font-bold uppercase text-muted-foreground">合并授权 / Merge Auth</span>
                    {data.controlSummary.qualityGate.mergeAuthorized ? (
                      <span className="text-green-600 dark:text-green-400 font-bold">已授权 / AUTHORIZED</span>
                    ) : (
                      <span className="text-red-600 dark:text-red-400 font-bold">未授权 / BLOCKED</span>
                    )}
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-[10px] text-green-700 dark:text-green-400 bg-green-500/5 p-2 rounded border border-green-500/20">
                  <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
                  <p>无质量例外项 / No quality exceptions</p>
                </div>
              )}
            </div>
          </section>

          {/* 7. Automation & Agents */}
          <section className="border rounded-xl bg-card shadow-sm overflow-hidden">
            <div className="px-4 py-3 border-b bg-muted/20">
              <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                <Cpu className="w-4 h-4" /> 自动化与代理 / Agents
              </h2>
            </div>
            <div className="p-4 space-y-3">
              <div className="grid grid-cols-2 gap-2">
                {data.lanes.slice(0, 4).map(lane => (
                  <div key={lane.id} className="p-2 border rounded bg-background">
                    <span className="text-[9px] font-bold text-muted-foreground uppercase block">{lane.name}</span>
                    <span className="text-[10px] font-medium truncate block">{lane.owner}</span>
                  </div>
                ))}
              </div>
              {data.pmRunDigest && (
                <div className="p-2.5 rounded-lg bg-blue-500/5 border border-blue-500/20">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[9px] font-bold text-blue-600 uppercase">PM Watch Digest / IKE PM Mainline Watch</span>
                    <AutomationStatusBadge status={mapPmDigestStatus(data.pmRunDigest)} />
                  </div>
                  <p className="text-[10px] text-muted-foreground leading-tight italic line-clamp-2">
                    {data.pmRunDigest.decision}: {data.pmRunDigest.reason}
                  </p>
                </div>
              )}
            </div>
          </section>
        </div>
      </div>

      {/* 8. Evidence / Diagnostics (Secondary Section) */}
      <footer className="mt-12 space-y-4">
        <details className="group">
          <summary className="flex items-center gap-2 cursor-pointer text-xs font-bold text-muted-foreground uppercase tracking-widest hover:text-primary transition-colors">
            <ChevronDown className="w-4 h-4 group-open:rotate-180 transition-transform" />
            详细证据与诊断 / Evidence & Diagnostics
          </summary>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t">
            <section className="space-y-4">
              <div>
                <h3 className="text-[10px] font-black uppercase mb-2 text-muted-foreground flex items-center gap-1">
                  <Database className="w-3 h-3" /> 事实来源 / Provenance
                </h3>
                <ProvenanceBlock provenance={data.provenance} />
              </div>

              <div className="p-4 rounded-xl border bg-muted/10">
                <h3 className="text-[10px] font-black uppercase mb-2 text-muted-foreground">最新接受的证据 / Latest Evidence (Top 3)</h3>
                <ul className="space-y-2">
                  {data.mainline.latestAcceptedEvidence.slice(0, 3).map((ev, i) => (
                    <li key={i} className="flex gap-2 text-xs">
                      <div className="w-1 h-1 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                      <span className="text-muted-foreground">{ev}</span>
                    </li>
                  ))}
                  {data.mainline.latestAcceptedEvidence.length > 3 && (
                    <li className="text-[10px] text-muted-foreground italic pl-3">
                      ... 以及另外 {data.mainline.latestAcceptedEvidence.length - 3} 项已验证证据
                    </li>
                  )}
                </ul>
              </div>
            </section>

            <section className="space-y-4">
              {data.operationsSplit && (
                <div className="p-4 rounded-xl border bg-card">
                  <h3 className="text-[10px] font-black uppercase mb-3 text-muted-foreground">Truth Split (Diagnostics)</h3>
                  <div className="space-y-2 text-[10px]">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Code Truth:</span>
                      <span className="font-mono">{data.operationsSplit.codeTruth}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Runtime Truth:</span>
                      <span className="font-mono">{data.operationsSplit.runtimeTruth}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Dependencies:</span>
                      <span className="font-mono">{data.operationsSplit.runtimeDependency}</span>
                    </div>
                  </div>
                </div>
              )}

              {data.flywheelLoop && (
                <div className="p-4 rounded-xl border bg-card">
                  <h3 className="text-[10px] font-black uppercase mb-3 text-muted-foreground">Flywheel Status</h3>
                  <div className="space-y-2 text-[10px]">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Loop Status:</span>
                      <span className="font-bold">{data.flywheelLoop.statusLabel}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Next Gate:</span>
                      <span className="font-mono">{data.flywheelLoop.nextGate}</span>
                    </div>
                    <div className="pt-1">
                      <span className="text-muted-foreground block mb-1">Truth Boundary:</span>
                      <span className="font-mono text-[9px] break-all bg-muted p-1 rounded block">{data.flywheelLoop.truthBoundary}</span>
                    </div>
                  </div>
                </div>
              )}

              <div className="p-4 rounded-xl border bg-card">
                <h3 className="text-[10px] font-black uppercase mb-3 text-muted-foreground">能力矩阵 / Capabilities</h3>
                <div className="space-y-3">
                  {data.capabilities.slice(0, 3).map(cap => (
                    <div key={cap.id} className="text-xs">
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-bold">{cap.title}</span>
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-muted font-mono">{cap.maturity}</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground line-clamp-1">{cap.gap}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-4 rounded-xl border bg-card">
                <h3 className="text-[10px] font-black uppercase mb-2 text-muted-foreground">后续动作 / Next Actions</h3>
                <div className="space-y-2">
                  {data.nextActions.slice(0, 2).map((action, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      <ArrowRight className="w-3 h-3 text-primary" />
                      <span className="font-bold min-w-[60px] uppercase text-[9px]">{action.lane}</span>
                      <span className="text-muted-foreground truncate">{action.action}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </div>
        </details>

        <div className="text-center pt-8 border-t text-[10px] text-muted-foreground font-mono">
          &copy; 2026 MyAttention IKE Control Surface
        </div>
      </footer>
    </div>
  )
}
