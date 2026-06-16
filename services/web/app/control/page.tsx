import type { ReactNode } from 'react'
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
    estimated: 'In progress',
    accepted: 'Accepted',
    blocked: 'Blocked',
    unknown: 'Unknown'
  }

  const icons: Record<ScoreStatus, ReactNode> = {
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
      {status === 'healthy' ? 'Healthy' : status === 'caveat' ? 'Caveat' : 'Unhealthy'}
    </span>
  )
}

function SummaryTile({ label, children, tone = 'default' }: { label: string; children: ReactNode; tone?: 'default' | 'gate' }) {
  const toneClass = tone === 'gate'
    ? 'border-amber-200 dark:border-amber-900/60 bg-amber-50/70 dark:bg-amber-950/10'
    : 'bg-background/80'

  return (
    <div className={`p-3 rounded-lg border shadow-sm ${toneClass}`}>
      <span className="block text-[10px] uppercase font-bold text-muted-foreground mb-1">{label}</span>
      <div className="text-sm font-semibold leading-snug line-clamp-3">{children}</div>
    </div>
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
        <span className="text-[10px] text-muted-foreground uppercase font-medium">Status</span>
        <div className="text-xs font-semibold">
          {task.status === 'accepted' ? 'Complete' : task.status === 'blocked' ? 'Blocked' : 'Moving'}
        </div>
      </div>
    </div>
  )
}

export default async function ControlDashboardPage() {
  const data = await getSnapshot()

  const firstClassTaskIds = ['evolution_flywheel_v1', 'ai_conversation_entry', 'project_control_surface']
  const dashboardTasks = data.tasks.filter(t => firstClassTaskIds.includes(t.id))
  dashboardTasks.sort((a, b) => firstClassTaskIds.indexOf(a.id) - firstClassTaskIds.indexOf(b.id))

  const currentBlocker = data.controlSummary?.currentBlocker
  const primaryAction = data.nextActions[0]
  const currentStage = data.controlSummary?.currentPhase || data.phase.current
  const mainlineGoal = data.controlSummary?.mainlineGoal || data.mainline.objective
  const decisionGate = currentBlocker?.title || data.phase.nextGate

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-20 px-4 sm:px-6">
      <header className="relative overflow-hidden border rounded-xl bg-muted/10 shadow-sm p-6">
        <div className="relative z-10 space-y-5">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-primary">
              <LayoutDashboard className="w-5 h-5" />
              <span className="text-xs font-bold uppercase tracking-[0.2em]">IKE Control Surface</span>
            </div>
            <h1 className="text-3xl font-black tracking-tight">{data.mainline.name}</h1>
            <p className="text-sm text-muted-foreground max-w-3xl">{mainlineGoal}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <SummaryTile label="Current Stage">{currentStage}</SummaryTile>
            <SummaryTile label="Decision Gate" tone="gate">{decisionGate}</SummaryTile>
            <SummaryTile label="Immediate Owner / Action">
              {primaryAction ? `${primaryAction.lane}: ${primaryAction.action}` : 'Controller: choose the next bounded action from accepted truth.'}
            </SummaryTile>
            <SummaryTile label="Snapshot">
              <span className="flex items-center gap-1.5 font-mono">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                {data.provenance.freshnessLabel}
              </span>
              <span className="block mt-1 text-[10px] text-muted-foreground font-normal uppercase">{data.provenance.sourceKind}</span>
            </SummaryTile>
          </div>
        </div>
      </header>

      <section className="border rounded-xl bg-card shadow-sm overflow-hidden">
        <div className="px-4 py-3 border-b bg-muted/20">
          <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-500" /> Mainline Lane Status
          </h2>
        </div>
        <div className="px-4">
          {dashboardTasks.map(task => (
            <TaskProgressRow key={task.id} task={task} />
          ))}
          {dashboardTasks.length === 0 && (
            <div className="py-6 text-center text-xs text-muted-foreground italic">
              No mainline lane data was found in the snapshot.
            </div>
          )}
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 space-y-6">
          {currentBlocker ? (
            <section className="border rounded-xl bg-amber-50/50 dark:bg-amber-950/10 border-amber-200 dark:border-amber-900/50 p-5 shadow-sm">
              <div className="flex items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-2 text-amber-800 dark:text-amber-300">
                  <AlertTriangle className="w-5 h-5" />
                  <h2 className="font-bold text-sm uppercase tracking-wider text-amber-900 dark:text-amber-100">Current Blocker</h2>
                </div>
                <span className="px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200 border border-amber-200 dark:border-amber-800 text-[10px] font-bold uppercase">
                  {currentBlocker.status}
                </span>
              </div>
              <div className="space-y-4 text-sm leading-relaxed">
                <div>
                  <h3 className="font-bold text-amber-900 dark:text-amber-100 mb-1">{currentBlocker.title}</h3>
                  <p className="text-muted-foreground">{currentBlocker.summary}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-bold text-muted-foreground">Why It Matters</span>
                    <p className="text-xs">{currentBlocker.whyItMatters}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] uppercase font-bold text-muted-foreground">Risk / Impact</span>
                    <p className="text-xs">
                      <span className="font-bold text-red-600 dark:text-red-400 mr-1">[{currentBlocker.riskLevel.toUpperCase()}]</span>
                      {currentBlocker.blastRadius}
                    </p>
                  </div>
                </div>
              </div>
            </section>
          ) : (
            <section className="border rounded-xl bg-muted/5 p-5 shadow-sm border-dashed">
              <div className="flex items-center gap-2 mb-2 text-muted-foreground">
                <CheckCircle2 className="w-4 h-4" />
                <h2 className="font-bold text-xs uppercase tracking-wider">No Active Blocker</h2>
              </div>
              <p className="text-[10px] text-muted-foreground italic">No critical blocker is present in the current snapshot.</p>
            </section>
          )}

          {data.controlSummary?.plan && (
            <section className="border rounded-xl bg-card shadow-sm p-5">
              <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
                <ListFilter className="w-4 h-4" /> Strategic Plan
              </h2>
              <div className="space-y-4">
                {[
                  ['Now', data.controlSummary.plan.now, 'text-primary', 'bg-primary'],
                  ['Next', data.controlSummary.plan.next, 'text-muted-foreground', 'bg-muted-foreground/30'],
                  ['Later', data.controlSummary.plan.later, 'text-muted-foreground', 'bg-muted-foreground/20']
                ].map(([label, value, textClass, dotClass], index) => (
                  <div key={label} className="flex gap-4">
                    <div className="flex flex-col items-center pt-1">
                      <div className={`w-2 h-2 rounded-full ${dotClass}`} />
                      {index < 2 && <div className="w-0.5 flex-1 bg-border my-1" />}
                    </div>
                    <div>
                      <span className={`text-[10px] uppercase font-bold block mb-0.5 ${textClass}`}>{label}</span>
                      <p className={`text-xs ${index === 0 ? 'font-medium' : 'text-muted-foreground'}`}>{value}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        <div className="lg:col-span-5 space-y-6">
          <section className="border rounded-xl bg-card shadow-sm overflow-hidden">
            <div className="px-4 py-3 border-b bg-muted/20">
              <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                <Activity className="w-4 h-4" /> Runtime Readiness
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
                    <span className="text-[9px] text-muted-foreground truncate">{svc.details || 'Online'}</span>
                  </div>
                ))
              ) : (
                <div className="col-span-2 py-4 text-center text-[10px] text-muted-foreground italic border-2 border-dashed rounded-lg">
                  No live probe data is available.
                </div>
              )}
            </div>
          </section>

          <section className="border rounded-xl bg-card shadow-sm p-4">
            <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4" /> Promotion Gate
            </h2>
            <div className="space-y-3">
              <div className="p-2.5 rounded-lg bg-muted/30 border text-xs">
                <div className="flex items-center gap-2 mb-1">
                  <Info className="w-3 h-3 text-blue-500" />
                  <span className="font-bold">Review Status</span>
                </div>
                <p className="text-muted-foreground text-[11px]">{data.reviewState.prReviewGate}</p>
              </div>
              {data.controlSummary?.qualityGate ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="p-2 rounded bg-muted/30 border text-[10px]">
                      <span className="block text-muted-foreground uppercase font-bold mb-1">Local Review</span>
                      <span className="font-semibold">{data.controlSummary.qualityGate.localReviewStatus}</span>
                    </div>
                    <div className="p-2 rounded bg-muted/30 border text-[10px]">
                      <span className="block text-muted-foreground uppercase font-bold mb-1">Cloud Review</span>
                      <span className="font-semibold">{data.controlSummary.qualityGate.cloudReviewStatus}</span>
                    </div>
                  </div>

                  {data.controlSummary.qualityGate.exceptionActive && (
                    <div className="p-2.5 rounded-lg bg-amber-500/5 border border-amber-500/20">
                      <div className="flex items-center gap-2 mb-1.5">
                        <AlertTriangle className="w-3 h-3 text-amber-500" />
                        <span className="text-[10px] font-bold text-amber-800 dark:text-amber-300 uppercase">Exception Active</span>
                      </div>
                      <div className="text-[10px] text-amber-700 dark:text-amber-400 space-y-1">
                        <p className="font-medium">Scope: {data.controlSummary.qualityGate.exceptionScope.join(', ')}</p>
                        <p className="italic">Cloud review quota is exhausted; local independent review is the active exception path.</p>
                      </div>
                    </div>
                  )}

                  <div className="p-2 rounded border flex items-center justify-between text-[10px]">
                    <span className="font-bold uppercase text-muted-foreground">Merge Auth</span>
                    {data.controlSummary.qualityGate.mergeAuthorized ? (
                      <span className="text-green-600 dark:text-green-400 font-bold">AUTHORIZED</span>
                    ) : (
                      <span className="text-red-600 dark:text-red-400 font-bold">BLOCKED</span>
                    )}
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-[10px] text-green-700 dark:text-green-400 bg-green-500/5 p-2 rounded border border-green-500/20">
                  <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
                  <p>No quality exceptions</p>
                </div>
              )}
            </div>
          </section>

          <section className="border rounded-xl bg-card shadow-sm overflow-hidden">
            <div className="px-4 py-3 border-b bg-muted/20">
              <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                <Cpu className="w-4 h-4" /> Agents
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

      <footer className="mt-12 space-y-4">
        <details className="group">
          <summary className="flex items-center gap-2 cursor-pointer text-xs font-bold text-muted-foreground uppercase tracking-widest hover:text-primary transition-colors">
            <ChevronDown className="w-4 h-4 group-open:rotate-180 transition-transform" />
            Evidence & Diagnostics
          </summary>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t">
            <section className="space-y-4">
              <div>
                <h3 className="text-[10px] font-black uppercase mb-2 text-muted-foreground flex items-center gap-1">
                  <Database className="w-3 h-3" /> Provenance
                </h3>
                <ProvenanceBlock provenance={data.provenance} />
              </div>

              <div className="p-4 rounded-xl border bg-muted/10">
                <h3 className="text-[10px] font-black uppercase mb-2 text-muted-foreground">Latest Evidence (Top 3)</h3>
                <ul className="space-y-2">
                  {data.mainline.latestAcceptedEvidence.slice(0, 3).map((ev, i) => (
                    <li key={i} className="flex gap-2 text-xs">
                      <div className="w-1 h-1 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                      <span className="text-muted-foreground">{ev}</span>
                    </li>
                  ))}
                  {data.mainline.latestAcceptedEvidence.length > 3 && (
                    <li className="text-[10px] text-muted-foreground italic pl-3">
                      ... plus {data.mainline.latestAcceptedEvidence.length - 3} more accepted evidence items
                    </li>
                  )}
                </ul>
              </div>

              {currentBlocker && (
                <div className="p-4 rounded-xl border bg-card">
                  <h3 className="text-[10px] font-black uppercase mb-3 text-muted-foreground">Blocker Detail</h3>
                  <div className="space-y-3">
                    <div>
                      <span className="text-[10px] uppercase font-bold text-muted-foreground block mb-1.5">Completed Steps</span>
                      <ul className="space-y-1">
                        {currentBlocker.completedSteps.map((step, i) => (
                          <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                            <CheckCircle2 className="w-3 h-3 mt-0.5 text-green-500 flex-shrink-0" />
                            <span>{step}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <span className="text-[10px] uppercase font-bold text-muted-foreground block mb-1.5">Proposed Steps</span>
                      <ul className="space-y-1">
                        {currentBlocker.proposedSteps.map((step, i) => (
                          <li key={i} className="flex items-start gap-2 text-xs">
                            <ArrowRight className="w-3 h-3 mt-0.5 text-amber-500 flex-shrink-0" />
                            <span>{step}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </section>

            <section className="space-y-4">
              {data.operationsSplit && (
                <div className="p-4 rounded-xl border bg-card">
                  <h3 className="text-[10px] font-black uppercase mb-3 text-muted-foreground">Truth Split (Diagnostics)</h3>
                  <div className="space-y-2 text-[10px]">
                    <div className="flex justify-between gap-3">
                      <span className="text-muted-foreground">Code Truth:</span>
                      <span className="font-mono text-right">{data.operationsSplit.codeTruth}</span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-muted-foreground">Runtime Truth:</span>
                      <span className="font-mono text-right">{data.operationsSplit.runtimeTruth}</span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-muted-foreground">Dependencies:</span>
                      <span className="font-mono text-right">{data.operationsSplit.runtimeDependency}</span>
                    </div>
                  </div>
                </div>
              )}

              {data.flywheelLoop && (
                <div className="p-4 rounded-xl border bg-card">
                  <h3 className="text-[10px] font-black uppercase mb-3 text-muted-foreground">Flywheel Status</h3>
                  <div className="space-y-2 text-[10px]">
                    <div className="flex justify-between gap-3">
                      <span className="text-muted-foreground">Loop Status:</span>
                      <span className="font-bold text-right">{data.flywheelLoop.statusLabel}</span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="text-muted-foreground">Next Gate:</span>
                      <span className="font-mono text-right">{data.flywheelLoop.nextGate}</span>
                    </div>
                    <div className="pt-1">
                      <span className="text-muted-foreground block mb-1">Truth Boundary:</span>
                      <span className="font-mono text-[9px] break-all bg-muted p-1 rounded block">{data.flywheelLoop.truthBoundary}</span>
                    </div>
                  </div>
                </div>
              )}

              <div className="p-4 rounded-xl border bg-card">
                <h3 className="text-[10px] font-black uppercase mb-3 text-muted-foreground">Capabilities</h3>
                <div className="space-y-3">
                  {data.capabilities.slice(0, 3).map(cap => (
                    <div key={cap.id} className="text-xs">
                      <div className="flex justify-between items-center gap-3 mb-1">
                        <span className="font-bold">{cap.title}</span>
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-muted font-mono">{cap.maturity}</span>
                      </div>
                      <p className="text-[10px] text-muted-foreground line-clamp-1">{cap.gap}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-4 rounded-xl border bg-card">
                <h3 className="text-[10px] font-black uppercase mb-2 text-muted-foreground">Next Actions</h3>
                <div className="space-y-2">
                  {data.nextActions.slice(0, 2).map((action, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      <ArrowRight className="w-3 h-3 text-primary flex-shrink-0" />
                      <span className="font-bold min-w-[60px] uppercase text-[9px]">{action.lane}</span>
                      <span className="text-muted-foreground truncate">{action.action}</span>
                    </div>
                  ))}
                  {data.nextActions.length === 0 && (
                    <p className="text-[10px] text-muted-foreground italic">No next actions are present in the snapshot.</p>
                  )}
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
