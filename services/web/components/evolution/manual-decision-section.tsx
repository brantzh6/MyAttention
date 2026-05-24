'use client'

import { Check, Copy } from 'lucide-react'
import type { FlywheelInspectResponse } from '@/lib/api-client'

type ManualDecisionSectionProps = {
  result: FlywheelInspectResponse
  selectedKnowledge: Set<number>
  selectedTriggers: Set<number>
  selectedSources: Set<number>
  reviewerNote: string
  decisionCopied: boolean
  onCopyDecisionPacket: () => void
}

export function ManualDecisionSection({
  result,
  selectedKnowledge,
  selectedTriggers,
  selectedSources,
  reviewerNote,
  decisionCopied,
  onCopyDecisionPacket,
}: ManualDecisionSectionProps) {
  const hasSelections =
    selectedKnowledge.size > 0 || selectedTriggers.size > 0 || selectedSources.size > 0

  return (
    <div className="mt-4 rounded-lg border border-dashed bg-muted/20">
      <div className="flex items-center justify-between border-b border-dashed px-3 py-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold">手动决策桥接</span>
          <span className="text-[10px] text-muted-foreground">
            Decision Bridge - 生成紧凑决策包供对齐讨论
          </span>
        </div>
        <button
          type="button"
          onClick={onCopyDecisionPacket}
          className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs transition-colors hover:bg-muted"
          title="复制决策包到剪贴板"
        >
          {decisionCopied ? (
            <>
              <Check className="h-3 w-3 text-green-600" />
              <span className="text-green-600">已复制</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>复制决策包</span>
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
        {hasSelections && (
          <div className="grid grid-cols-[80px_1fr] gap-x-2">
            <span className="shrink-0 text-muted-foreground">已选项</span>
            <div className="flex flex-wrap gap-1">
              {Array.from(selectedKnowledge).map((i) => {
                const delta = result.knowledge_delta_candidates[i]
                return delta ? (
                  <span
                    key={`k${i}`}
                    className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-700"
                  >
                    [{delta.delta_type}] {delta.label}
                  </span>
                ) : null
              })}
              {Array.from(selectedTriggers).map((i) => {
                const trigger = result.evolution_trigger_candidates[i]
                return trigger ? (
                  <span
                    key={`t${i}`}
                    className="rounded bg-purple-50 px-1.5 py-0.5 text-[10px] text-purple-700"
                  >
                    [{trigger.trigger_type}] {trigger.label}
                  </span>
                ) : null
              })}
              {Array.from(selectedSources).map((i) => {
                const source = result.source_candidates[i]
                return source ? (
                  <span
                    key={`s${i}`}
                    className="rounded bg-muted px-1.5 py-0.5 text-[10px]"
                  >
                    {source.name || source.id || '未命名'}
                  </span>
                ) : null
              })}
            </div>
          </div>
        )}
        {reviewerNote.trim() && (
          <div className="grid grid-cols-[80px_1fr] gap-x-2">
            <span className="shrink-0 text-muted-foreground">审查备注</span>
            <span className="truncate text-muted-foreground">{reviewerNote.trim()}</span>
          </div>
        )}
      </div>
    </div>
  )
}
