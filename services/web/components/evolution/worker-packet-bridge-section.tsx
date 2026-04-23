'use client'

import type { ReactNode } from 'react'
import { Check, Copy } from 'lucide-react'
import { buildWorkerPacket, type WorkerLane } from './flywheel-packet-builders'
import type {
  FlywheelInspectResponse,
  TaskPacketPreviewResponse,
} from '@/lib/api-client'

type WorkerPacketBridgeSectionProps = {
  result: FlywheelInspectResponse
  taskPreviewResult: TaskPacketPreviewResponse
  workerLane: WorkerLane
  onWorkerLaneChange: (lane: WorkerLane) => void
  onCopyWorkerPacket: (lane: WorkerLane) => void
  workerCopiedMap: Record<WorkerLane, boolean>
  executionFeedbackSection: ReactNode
}

export function WorkerPacketBridgeSection({
  result,
  taskPreviewResult,
  workerLane,
  onWorkerLaneChange,
  onCopyWorkerPacket,
  workerCopiedMap,
  executionFeedbackSection,
}: WorkerPacketBridgeSectionProps) {
  return (
    <div className="mt-4 rounded-lg border border-dashed bg-muted/20">
      <div className="flex items-center justify-between px-3 py-2 border-b border-dashed">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold">Worker Packet Bridge</span>
          <span className="text-[10px] text-muted-foreground">
            基于后端预览生成 coding / review / test 手动包
          </span>
        </div>
      </div>

      <div className="px-3 pt-2 flex gap-1">
        {(['coding', 'review', 'test'] as WorkerLane[]).map((lane) => (
          <button
            key={lane}
            type="button"
            onClick={() => onWorkerLaneChange(lane)}
            className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
              workerLane === lane
                ? 'bg-primary text-primary-foreground'
                : 'bg-background text-muted-foreground hover:bg-muted'
            }`}
          >
            {lane}
          </button>
        ))}
        <div className="flex-1" />
        <button
          type="button"
          onClick={() => onCopyWorkerPacket(workerLane)}
          className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs hover:bg-muted transition-colors"
          title={`复制 ${workerLane} packet`}
        >
          {workerCopiedMap[workerLane] ? (
            <>
              <Check className="h-3 w-3 text-green-600" />
              <span className="text-green-600">已复制</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>复制</span>
            </>
          )}
        </button>
      </div>

      <div className="px-3 pb-3 pt-2">
        <pre className="rounded-md border bg-background p-2 text-[11px] leading-relaxed whitespace-pre-wrap break-words font-mono text-muted-foreground max-h-64 overflow-y-auto">
          {buildWorkerPacket(
            workerLane,
            result.topic,
            result.task_intent || '(未指定)',
            taskPreviewResult,
            result,
          )}
        </pre>
      </div>

      {executionFeedbackSection}
    </div>
  )
}
