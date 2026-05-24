'use client'

import { Check, Copy } from 'lucide-react'
import { buildLoopPacket, type WorkerLane } from './flywheel-packet-builders'
import type {
  FlywheelInspectResponse,
  TaskPacketPreviewResponse,
} from '@/lib/api-client'

type LoopPacketSectionProps = {
  result: FlywheelInspectResponse
  taskPreviewResult: TaskPacketPreviewResponse
  workerLane: WorkerLane
  loopPacketCopied: boolean
  onCopyLoopPacket: () => void
}

export function LoopPacketSection({
  result,
  taskPreviewResult,
  workerLane,
  loopPacketCopied,
  onCopyLoopPacket,
}: LoopPacketSectionProps) {
  return (
    <div className="mx-3 mb-3 rounded-md border bg-background p-3 space-y-3 text-xs">
      <div className="flex items-center justify-between gap-2">
        <div>
          <div className="font-medium">完整 Loop Packet</div>
          <div className="text-[11px] text-muted-foreground">
            把前向执行包、结果回流要求、以及 provenance 要求合并成一次可重复执行的手工闭环包
          </div>
        </div>
        <button
          type="button"
          onClick={onCopyLoopPacket}
          className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs hover:bg-muted transition-colors"
        >
          {loopPacketCopied ? (
            <>
              <Check className="h-3 w-3 text-green-600" />
              <span className="text-green-600">已复制</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>复制完整闭环包</span>
            </>
          )}
        </button>
      </div>

      <div className="rounded-md border bg-muted/20 px-3 py-2 text-[11px] text-muted-foreground">
        建议把这份 packet 发给 worker。worker 完成后，按其中的 return protocol 与 provenance
        要求，把结果粘贴回 execution feedback surface。
      </div>

      <pre className="max-h-72 overflow-y-auto whitespace-pre-wrap break-words rounded-md border bg-background p-2 font-mono text-[11px] leading-relaxed text-muted-foreground">
        {buildLoopPacket(
          workerLane,
          result.topic,
          result.task_intent || '(未指定)',
          taskPreviewResult,
          result,
        )}
      </pre>
    </div>
  )
}
