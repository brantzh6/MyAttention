'use client'

import { useMemo, useState } from 'react'
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
  const [candidateFilter, setCandidateFilter] = useState('')

  const normalizedFilter = candidateFilter.trim().toLowerCase()

  const knowledgeRows = useMemo(() => {
    const rows = result.knowledge_delta_candidates.map((delta, index) => ({
      index,
      delta,
      haystack: `${delta.delta_type ?? ''} ${delta.label ?? ''}`.toLowerCase(),
    }))

    if (!normalizedFilter) return rows
    return rows.filter((row) => row.haystack.includes(normalizedFilter))
  }, [normalizedFilter, result.knowledge_delta_candidates])

  const triggerRows = useMemo(() => {
    const rows = result.evolution_trigger_candidates.map((trigger, index) => ({
      index,
      trigger,
      haystack: `${trigger.trigger_type ?? ''} ${trigger.label ?? ''}`.toLowerCase(),
    }))

    if (!normalizedFilter) return rows
    return rows.filter((row) => row.haystack.includes(normalizedFilter))
  }, [normalizedFilter, result.evolution_trigger_candidates])

  const sourceRows = useMemo(() => {
    const rows = result.source_candidates.map((source, index) => ({
      index,
      source,
      haystack: `${source.name ?? ''} ${source.id ?? ''} ${source.type ?? ''}`.toLowerCase(),
    }))

    if (!normalizedFilter) return rows
    return rows.filter((row) => row.haystack.includes(normalizedFilter))
  }, [normalizedFilter, result.source_candidates])

  return (
    <div
      data-testid="manual-absorption-section"
      className="mt-4 rounded-lg border border-dashed bg-muted/30"
    >
      <div className="flex items-center justify-between border-b border-dashed px-3 py-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold">Manual Review</span>
          <span className="text-[10px] text-muted-foreground">
            Absorption - Select items to include in packet
          </span>
        </div>
        <button
          type="button"
          onClick={onCopyAbsorptionPacket}
          disabled={!hasAnyAbsorptionSelection && !reviewerNote.trim()}
          className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs transition-colors hover:bg-muted disabled:cursor-not-allowed disabled:opacity-40"
          title="Copy selection"
        >
          {absorptionCopied ? (
            <>
              <Check className="h-3 w-3 text-green-600" />
              <span className="text-green-600">Copied</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>Copy Packet</span>
            </>
          )}
        </button>
      </div>

      <div className="space-y-3 px-3 py-2">
        {(result.knowledge_delta_candidates.length > 0 ||
          result.evolution_trigger_candidates.length > 0 ||
          result.source_candidates.length > 0) && (
          <div className="flex flex-col gap-1">
            <label className="text-[11px] font-medium text-muted-foreground">
              Filter candidates
            </label>
            <input
              type="text"
              value={candidateFilter}
              onChange={(e) => setCandidateFilter(e.target.value)}
              placeholder="Type to filter by visible text..."
              className="w-full rounded-md border bg-background px-2 py-1.5 text-xs placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-primary"
            />
            {normalizedFilter && (
              <div className="text-[10px] text-muted-foreground">
                Showing {knowledgeRows.length + triggerRows.length + sourceRows.length} of{' '}
                {result.knowledge_delta_candidates.length +
                  result.evolution_trigger_candidates.length +
                  result.source_candidates.length}{' '}
                candidates
              </div>
            )}
          </div>
        )}

        {result.knowledge_delta_candidates.length > 0 && (
          <div>
            <div className="mb-1 text-[11px] font-medium text-muted-foreground">
              Knowledge{' '}
              <span className="text-[10px] text-muted-foreground/60">
                ({knowledgeRows.length}/{result.knowledge_delta_candidates.length})
              </span>
            </div>
            <div className="space-y-0.5">
              {knowledgeRows.map(({ delta, index }) => (
                <label key={index} className="flex cursor-pointer items-start gap-2">
                  <input
                    type="checkbox"
                    checked={selectedKnowledge.has(index)}
                    onChange={() => onToggleSelect('knowledge', index)}
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
              Triggers{' '}
              <span className="text-[10px] text-muted-foreground/60">
                ({triggerRows.length}/{result.evolution_trigger_candidates.length})
              </span>
            </div>
            <div className="space-y-0.5">
              {triggerRows.map(({ trigger, index }) => (
                <label key={index} className="flex cursor-pointer items-start gap-2">
                  <input
                    type="checkbox"
                    checked={selectedTriggers.has(index)}
                    onChange={() => onToggleSelect('triggers', index)}
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
              Sources{' '}
              <span className="text-[10px] text-muted-foreground/60">
                ({sourceRows.length}/{result.source_candidates.length})
              </span>
            </div>
            <div className="space-y-0.5">
              {sourceRows.map(({ source, index }) => (
                <label key={index} className="flex cursor-pointer items-start gap-2">
                  <input
                    type="checkbox"
                    checked={selectedSources.has(index)}
                    onChange={() => onToggleSelect('sources', index)}
                    className="mt-0.5 h-3.5 w-3.5 rounded border-muted-foreground/30 accent-primary"
                  />
                  <span className="text-xs text-muted-foreground">
                    {source.name || source.id || 'Unknown'}
                    {source.type && (
                      <span className="text-[10px] text-muted-foreground/60">
                        {' '}
                        / {source.type}
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
            Notes
          </label>
          <textarea
            value={reviewerNote}
            onChange={(e) => onReviewerNoteChange(e.target.value)}
            placeholder="Add a reviewer note..."
            rows={2}
            maxLength={500}
            className="w-full resize-none rounded-md border bg-background px-2 py-1.5 text-xs placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>
    </div>
  )
}
