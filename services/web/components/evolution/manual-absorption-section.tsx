'use client'

import { Check, Copy } from 'lucide-react'
import type { FlywheelInspectResponse } from '@/lib/api-client'

type ManualAbsorptionSectionProps = {
  result: FlywheelInspectResponse
  selectedKnowledge: Set<number>
  selectedTriggers: Set<number>
  selectedSources: Set<number>
  reviewerNote: string
  hasAnyAbsorptionSelection: boolean
  absorptionCopied: boolean
  onCopyAbsorptionPacket: () => void
  onToggleSelect: (family: 'knowledge' | 'triggers' | 'sources', index: number) => void
  onReviewerNoteChange: (value: string) => void
}

export function ManualAbsorptionSection({
  result,
  selectedKnowledge,
  selectedTriggers,
  selectedSources,
  reviewerNote,
  hasAnyAbsorptionSelection,
  absorptionCopied,
  onCopyAbsorptionPacket,
  onToggleSelect,
  onReviewerNoteChange,
}: ManualAbsorptionSectionProps) {
  return (
    <div className="mt-4 rounded-lg border border-dashed bg-muted/30">
      <div className="flex items-center justify-between border-b border-dashed px-3 py-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold">手动吸收</span>
          <span className="text-[10px] text-muted-foreground">
            Absorption - 选择候选项并生成紧凑吸收包
          </span>
        </div>
        <button
          type="button"
          onClick={onCopyAbsorptionPacket}
          disabled={!hasAnyAbsorptionSelection && !reviewerNote.trim()}
          className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs transition-colors hover:bg-muted disabled:cursor-not-allowed disabled:opacity-40"
          title="复制吸收包到剪贴板"
        >
          {absorptionCopied ? (
            <>
              <Check className="h-3 w-3 text-green-600" />
              <span className="text-green-600">已复制</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>复制吸收包</span>
            </>
          )}
        </button>
      </div>

      <div className="space-y-3 px-3 py-2">
        {result.knowledge_delta_candidates.length > 0 && (
          <div>
            <div className="mb-1 text-[11px] font-medium text-muted-foreground">
              知识增量候选
            </div>
            <div className="space-y-0.5">
              {result.knowledge_delta_candidates.map((delta, i) => (
                <label key={i} className="flex cursor-pointer items-start gap-2">
                  <input
                    type="checkbox"
                    checked={selectedKnowledge.has(i)}
                    onChange={() => onToggleSelect('knowledge', i)}
                    className="mt-0.5 h-3.5 w-3.5 rounded border-muted-foreground/30 accent-primary"
                  />
                  <span className="text-xs">
                    <span className="rounded bg-muted px-1 py-0.5 font-mono text-[10px]">
                      {delta.delta_type}
                    </span>{' '}
                    {delta.label}
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}

        {result.evolution_trigger_candidates.length > 0 && (
          <div>
            <div className="mb-1 text-[11px] font-medium text-muted-foreground">
              进化触发候选
            </div>
            <div className="space-y-0.5">
              {result.evolution_trigger_candidates.map((trigger, i) => (
                <label key={i} className="flex cursor-pointer items-start gap-2">
                  <input
                    type="checkbox"
                    checked={selectedTriggers.has(i)}
                    onChange={() => onToggleSelect('triggers', i)}
                    className="mt-0.5 h-3.5 w-3.5 rounded border-muted-foreground/30 accent-primary"
                  />
                  <span className="text-xs">
                    <span className="rounded bg-muted px-1 py-0.5 font-mono text-[10px]">
                      {trigger.trigger_type}
                    </span>{' '}
                    {trigger.label}
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}

        {result.source_candidates.length > 0 && (
          <div>
            <div className="mb-1 text-[11px] font-medium text-muted-foreground">
              来源候选
            </div>
            <div className="space-y-0.5">
              {result.source_candidates.map((source, i) => (
                <label key={i} className="flex cursor-pointer items-start gap-2">
                  <input
                    type="checkbox"
                    checked={selectedSources.has(i)}
                    onChange={() => onToggleSelect('sources', i)}
                    className="mt-0.5 h-3.5 w-3.5 rounded border-muted-foreground/30 accent-primary"
                  />
                  <span className="text-xs text-muted-foreground">
                    {source.name || source.id || '未命名'}
                    {source.type && (
                      <span className="text-[10px] text-muted-foreground/60">
                        {' '}
                        · {source.type}
                      </span>
                    )}
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}

        <div>
          <label className="mb-1 block text-[11px] font-medium text-muted-foreground">
            审查备注
          </label>
          <textarea
            value={reviewerNote}
            onChange={(e) => onReviewerNoteChange(e.target.value)}
            placeholder="简短备注（可选）..."
            rows={2}
            maxLength={500}
            className="w-full resize-none rounded-md border bg-background px-2 py-1.5 text-xs placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>
    </div>
  )
}
