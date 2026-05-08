'use client'

import { CheckCircle2, ShieldAlert } from 'lucide-react'
import type {
  FlywheelExecutionFeedbackInspectResponse,
  FlywheelInspectResponse,
  TaskPacketPreviewResponse,
} from '@/lib/api-client'
import type { WorkerLane } from './flywheel-packet-builders'

type LoopClosureSummarySectionProps = {
  result: FlywheelInspectResponse
  taskPreviewResult: TaskPacketPreviewResponse
  executionFeedbackResult: FlywheelExecutionFeedbackInspectResponse
  workerLane: WorkerLane
  executionStatusHint: string
}

export function LoopClosureSummarySection({
  result,
  taskPreviewResult,
  executionFeedbackResult,
  workerLane,
  executionStatusHint,
}: LoopClosureSummarySectionProps) {
  const nextStep =
    executionFeedbackResult.operational_advice?.suggested_next_step ||
    taskPreviewResult.suggested_next_step ||
    result.operational_advice?.suggested_next_step ||
    'controller_review'

  return (
    <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50/60">
      <div className="flex items-start justify-between gap-3 border-b border-emerald-200 px-3 py-2">
        <div className="flex items-start gap-2">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-700" />
          <div>
            <div className="text-xs font-semibold text-emerald-950">
              Loop Closure Summary
            </div>
            <div className="text-[11px] text-emerald-800">
              Controller-readable summary of this inspect-only loop.
            </div>
          </div>
        </div>
        <span className="rounded bg-emerald-100 px-2 py-1 text-[10px] font-medium text-emerald-800">
          non-canonical
        </span>
      </div>

      <div className="grid gap-2 px-3 py-3 text-xs md:grid-cols-2">
        <div className="rounded-md border border-emerald-100 bg-background/80 px-3 py-2">
          <div className="text-[10px] uppercase tracking-wide text-muted-foreground">
            Inspect topic
          </div>
          <div className="mt-1 font-medium">{result.topic}</div>
          <div className="mt-1 text-muted-foreground">{result.task_intent || 'unspecified'}</div>
        </div>

        <div className="rounded-md border border-emerald-100 bg-background/80 px-3 py-2">
          <div className="text-[10px] uppercase tracking-wide text-muted-foreground">
            Worker lane
          </div>
          <div className="mt-1 font-medium">{workerLane}</div>
          <div className="mt-1 text-muted-foreground">
            status hint: {executionStatusHint}
          </div>
        </div>

        <div className="rounded-md border border-emerald-100 bg-background/80 px-3 py-2 md:col-span-2">
          <div className="text-[10px] uppercase tracking-wide text-muted-foreground">
            Task preview
          </div>
          <div className="mt-1">{taskPreviewResult.task_packet_summary}</div>
        </div>

        <div className="rounded-md border border-emerald-100 bg-background/80 px-3 py-2 md:col-span-2">
          <div className="text-[10px] uppercase tracking-wide text-muted-foreground">
            Execution feedback
          </div>
          <div className="mt-1">
            {executionFeedbackResult.feedback_summary || 'No feedback summary returned.'}
          </div>
        </div>

        <div className="rounded-md border border-emerald-100 bg-background/80 px-3 py-2 md:col-span-2">
          <div className="text-[10px] uppercase tracking-wide text-muted-foreground">
            Next controller action
          </div>
          <div className="mt-1 font-medium">{nextStep}</div>
          <div className="mt-2 flex items-start gap-2 text-[11px] text-muted-foreground">
            <ShieldAlert className="mt-0.5 h-3.5 w-3.5 shrink-0" />
            This summary is inspect-only evidence. It does not promote candidates, write memory,
            launch workers, or create runtime truth.
          </div>
        </div>
      </div>
    </div>
  )
}
