'use client'

import { CollapsibleSection } from './collapsible-section'
import type { FlywheelInspectResponse } from '@/lib/api-client'
import type { SectionKey } from './use-flywheel-runtime-state'

type FlywheelResultsSectionProps = {
  result: FlywheelInspectResponse
  isSectionOpen: (key: SectionKey) => boolean
}

export function FlywheelResultsSection({
  result,
  isSectionOpen,
}: FlywheelResultsSectionProps) {
  return (
    <div className="mt-4 space-y-3">
      <CollapsibleSection title="提取摘要" open={isSectionOpen('extraction')} defaultOpen>
        <p className="text-sm text-muted-foreground">
          {result.extraction_summary || '无摘要'}
        </p>
        {result.segment_intent && result.segment_intent !== 'other' && (
          <p className="mt-2 text-xs">
            <span className="text-muted-foreground">意图识别：</span>
            <span className="font-medium">{result.segment_intent}</span>
          </p>
        )}
      </CollapsibleSection>

      <CollapsibleSection
        title={`知识增量候选 (${result.knowledge_delta_candidates.length})`}
        open={isSectionOpen('knowledge')}
      >
        {result.knowledge_delta_candidates.length === 0 ? (
          <p className="text-xs text-muted-foreground">无候选</p>
        ) : (
          <ul className="space-y-2">
            {result.knowledge_delta_candidates.map((delta, i) => (
              <li key={i} className="rounded-md border bg-background p-2 text-xs">
                <div className="flex items-center gap-2">
                  <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">
                    {delta.delta_type}
                  </span>
                  <span className="font-medium">{delta.label}</span>
                </div>
                <p className="mt-1 text-muted-foreground">{delta.content}</p>
              </li>
            ))}
          </ul>
        )}
      </CollapsibleSection>

      <CollapsibleSection
        title={`进化触发候选 (${result.evolution_trigger_candidates.length})`}
        open={isSectionOpen('triggers')}
      >
        {result.evolution_trigger_candidates.length === 0 ? (
          <p className="text-xs text-muted-foreground">无候选</p>
        ) : (
          <ul className="space-y-2">
            {result.evolution_trigger_candidates.map((trigger, i) => (
              <li key={i} className="rounded-md border bg-background p-2 text-xs">
                <div className="flex items-center gap-2">
                  <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">
                    {trigger.trigger_type}
                  </span>
                  <span className="font-medium">{trigger.label}</span>
                </div>
                {trigger.rationale && (
                  <p className="mt-1 text-muted-foreground">{trigger.rationale}</p>
                )}
              </li>
            ))}
          </ul>
        )}
      </CollapsibleSection>

      <CollapsibleSection
        title={`来源候选 (${result.source_candidates.length})`}
        open={isSectionOpen('sources')}
      >
        {result.source_candidates.length === 0 ? (
          <p className="text-xs text-muted-foreground">无来源候选</p>
        ) : (
          <ul className="space-y-1">
            {result.source_candidates.map((source, i) => (
              <li key={i} className="flex items-center gap-2 text-xs text-muted-foreground">
                <span className="h-1 w-1 rounded-full bg-muted-foreground" />
                {source.name || source.id || '未命名'}
                {source.type && (
                  <span className="text-[10px] text-muted-foreground/60">· {source.type}</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="操作建议" open={isSectionOpen('advice')}>
        {result.operational_advice.suggested_next_step !== 'no_action' && (
          <p className="text-sm font-medium">
            {result.operational_advice.suggested_next_step}
          </p>
        )}
        {result.operational_advice.controller_notes.length > 0 && (
          <ul className="mt-1 space-y-1">
            {result.operational_advice.controller_notes.map((note, i) => (
              <li key={i} className="text-xs text-muted-foreground">
                · {note}
              </li>
            ))}
          </ul>
        )}
        {result.operational_advice.suggested_next_step === 'no_action' &&
          result.operational_advice.controller_notes.length === 0 && (
            <p className="text-xs text-muted-foreground">无操作建议</p>
          )}
      </CollapsibleSection>

      <CollapsibleSection title="控制器数据包" open={isSectionOpen('controller')}>
        <div className="space-y-1 text-xs">
          <p>
            <span className="text-muted-foreground">审查模式：</span>
            {result.controller_packet.review_mode}
          </p>
          <p>
            <span className="text-muted-foreground">事实状态：</span>
            {result.controller_packet.truth_status}
          </p>
          {result.controller_packet.reason_tags.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-1">
              {result.controller_packet.reason_tags.map((tag, i) => (
                <span
                  key={i}
                  className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </CollapsibleSection>
    </div>
  )
}
