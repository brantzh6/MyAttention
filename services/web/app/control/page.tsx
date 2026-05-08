import { getSnapshot } from '@/lib/control-surface/get-snapshot'
import { ProvenanceBlock } from '@/components/control/provenance-block'
import { ScoreStatus } from '@/lib/control-surface/types'

function StatusBadge({ status }: { status: ScoreStatus }) {
  const colors: Record<ScoreStatus, string> = {
    estimated: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 border-yellow-200 dark:border-yellow-800',
    accepted: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 border-green-200 dark:border-green-800',
    blocked: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 border-red-200 dark:border-red-800',
    unknown: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300 border-gray-200 dark:border-gray-700'
  }
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider border ${colors[status]}`}>
      {status}
    </span>
  )
}

export default async function ControlAnchorPage() {
  const data = await getSnapshot()

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <ProvenanceBlock provenance={data.provenance} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mainline & Phase */}
        <div className="space-y-6">
          <section className="border rounded-lg bg-card shadow-sm p-5">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 border-b pb-2">Current Mainline</h2>
            <div className="mb-4">
              <div className="text-lg font-bold text-primary mb-1">{data.mainline.name}</div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                <span className="font-medium text-foreground">Objective: </span>
                {data.mainline.objective}
              </p>
            </div>
            <div className="bg-muted/30 p-3 rounded text-sm">
              <span className="font-semibold block mb-2 text-xs text-muted-foreground uppercase tracking-wider">Latest Accepted Evidence</span>
              <ul className="list-disc pl-4 space-y-1 text-xs">
                {data.mainline.latestAcceptedEvidence.map((ev, i) => (
                  <li key={i}>{ev}</li>
                ))}
              </ul>
            </div>
          </section>

          <section className="border rounded-lg bg-card shadow-sm p-5">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 border-b pb-2">Current Phase & Gate</h2>
            <div className="space-y-3">
              <div>
                <span className="text-xs text-muted-foreground block mb-1">Current Phase</span>
                <div className="font-medium text-sm">{data.phase.current}</div>
              </div>
              <div>
                <span className="text-xs text-muted-foreground block mb-1">Next Gate</span>
                <div className="font-medium text-sm text-primary">{data.phase.nextGate}</div>
              </div>
            </div>
          </section>
        </div>

        {/* First-Class Tasks */}
        <section className="border rounded-lg bg-card shadow-sm p-5 flex flex-col">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 border-b pb-2">First-Class Tasks</h2>
          <div className="space-y-3 flex-1">
            {data.tasks.map(task => (
              <div key={task.id} className="p-3 border rounded bg-background hover:border-primary/30 transition-colors">
                <div className="flex justify-between items-start mb-2 gap-2">
                  <h3 className="font-medium text-sm">{task.title}</h3>
                  <StatusBadge status={task.status} />
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">{task.description}</p>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Capability Maturity & Gaps */}
        <section className="border rounded-lg bg-card shadow-sm p-5">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 border-b pb-2">Capability Maturity & Gaps</h2>
          <div className="space-y-3">
            {data.capabilities.map(cap => (
              <div key={cap.id} className="p-3 border rounded bg-background">
                <div className="flex justify-between items-start mb-2 gap-2">
                  <h3 className="font-medium text-sm">{cap.title}</h3>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase tracking-wider font-semibold bg-muted px-1.5 py-0.5 rounded">
                      {cap.maturity}
                    </span>
                    <StatusBadge status={cap.status} />
                  </div>
                </div>
                <div className="text-xs">
                  <span className="text-destructive/80 font-medium">Gap: </span>
                  <span className="text-muted-foreground">{cap.gap}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        <div className="space-y-6">
          {/* Active Lanes & Owners */}
          <section className="border rounded-lg bg-card shadow-sm p-5">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 border-b pb-2">Active Lanes & Owners</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {data.lanes.map(lane => (
                <div key={lane.id} className="p-2.5 border rounded bg-background text-xs">
                  <div className="font-medium mb-1">{lane.name}</div>
                  <div className="text-muted-foreground mb-1">Owner: {lane.owner}</div>
                  <div className="text-[10px] uppercase tracking-wider text-primary/80">{lane.status}</div>
                </div>
              ))}
            </div>
          </section>

          {/* Review & Operations State */}
          <section className="border rounded-lg bg-card shadow-sm p-5">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 border-b pb-2">Review & Operations State</h2>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li className="flex gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1 flex-shrink-0" />
                <span>{data.reviewState.prReviewGate}</span>
              </li>
              <li className="flex gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1 flex-shrink-0" />
                <span><strong className="text-foreground">Promotion:</strong> {data.reviewState.promotion}</span>
              </li>
              <li className="flex gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1 flex-shrink-0" />
                <span>{data.reviewState.termination}</span>
              </li>
              <li className="flex gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1 flex-shrink-0" />
                <span>{data.reviewState.monitor}</span>
              </li>
            </ul>
          </section>
        </div>
      </div>

      {/* Next Actions */}
      <section className="border rounded-lg bg-primary/5 border-primary/20 p-5">
        <h2 className="text-sm font-semibold text-primary uppercase tracking-wider mb-4 border-b border-primary/20 pb-2">Next Actions</h2>
        <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {data.nextActions.map((action, i) => (
            <li key={i} className="flex gap-2 text-sm items-start">
              <div className="mt-0.5 w-5 h-5 rounded bg-primary/10 text-primary flex items-center justify-center flex-shrink-0 text-xs font-bold">
                {i + 1}
              </div>
              <span className="text-primary/90 font-medium">{action}</span>
            </li>
          ))}
        </ul>
      </section>

    </div>
  )
}
