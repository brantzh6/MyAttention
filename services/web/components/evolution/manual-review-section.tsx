'use client'

import { Check, Copy } from 'lucide-react'
import type { FlywheelInspectResponse } from '@/lib/api-client'

type ManualReviewSectionProps = {
  result: FlywheelInspectResponse
  copied: boolean
  onCopyReviewPacket: () => void
}

export function ManualReviewSection({
  result,
  copied,
  onCopyReviewPacket,
}: ManualReviewSectionProps) {
  return (
    <div className="mt-4 rounded-lg border bg-card/80">
      <div className="flex items-center justify-between border-b px-3 py-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold">手动审查包</span>
          <span className="text-[10px] text-muted-foreground">
            Review Packet - 仅供手动审查
          </span>
        </div>
        <button
          type="button"
          onClick={onCopyReviewPacket}
          className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs transition-colors hover:bg-muted"
          title="复制审查包到剪贴板"
        >
          {copied ? (
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
      <div className="space-y-1.5 px-3 py-2 text-xs">
        <div className="grid grid-cols-[80px_1fr] gap-x-2">
          <span className="shrink-0 text-muted-foreground">主题</span>
          <span className="truncate font-medium">{result.topic}</span>
        </div>
        <div className="grid grid-cols-[80px_1fr] gap-x-2">
          <span className="shrink-0 text-muted-foreground">任务意图</span>
          <span>{result.task_intent || '(未指定)'}</span>
        </div>
        <div className="grid grid-cols-[80px_1fr] gap-x-2">
          <span className="shrink-0 text-muted-foreground">意图分段</span>
          <span>{result.segment_intent || '(未识别)'}</span>
        </div>
        {result.operational_advice?.suggested_next_step &&
          result.operational_advice.suggested_next_step !== 'no_action' && (
            <div className="grid grid-cols-[80px_1fr] gap-x-2">
              <span className="shrink-0 text-muted-foreground">建议下一步</span>
              <span className="font-medium">
                {result.operational_advice.suggested_next_step}
              </span>
            </div>
          )}
        {result.controller_packet?.reason_tags?.length > 0 && (
          <div className="grid grid-cols-[80px_1fr] gap-x-2">
            <span className="shrink-0 text-muted-foreground">原因标签</span>
            <div className="flex flex-wrap gap-1">
              {result.controller_packet.reason_tags.map((tag, i) => (
                <span
                  key={i}
                  className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
        {result.knowledge_delta_candidates.length > 0 && (
          <div className="grid grid-cols-[80px_1fr] gap-x-2">
            <span className="shrink-0 text-muted-foreground">知识增量</span>
            <div className="flex flex-wrap gap-1">
              {result.knowledge_delta_candidates.map((delta, i) => (
                <span
                  key={i}
                  className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-700"
                >
                  [{delta.delta_type}] {delta.label}
                </span>
              ))}
            </div>
          </div>
        )}
        {result.evolution_trigger_candidates.length > 0 && (
          <div className="grid grid-cols-[80px_1fr] gap-x-2">
            <span className="shrink-0 text-muted-foreground">进化触发</span>
            <div className="flex flex-wrap gap-1">
              {result.evolution_trigger_candidates.map((trigger, i) => (
                <span
                  key={i}
                  className="rounded bg-purple-50 px-1.5 py-0.5 text-[10px] text-purple-700"
                >
                  [{trigger.trigger_type}] {trigger.label}
                </span>
              ))}
            </div>
          </div>
        )}
        {result.source_candidates.length > 0 && (
          <div className="grid grid-cols-[80px_1fr] gap-x-2">
            <span className="shrink-0 text-muted-foreground">来源候选</span>
            <div className="space-y-0.5">
              {result.source_candidates.map((source, i) => (
                <div key={i} className="text-muted-foreground">
                  <span className="mr-1 inline-block h-1 w-1 rounded-full bg-muted-foreground" />
                  {source.name || source.id || '未命名'}
                  {source.type && (
                    <span className="text-[10px] text-muted-foreground/60">
                      {' '}
                      · {source.type}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
