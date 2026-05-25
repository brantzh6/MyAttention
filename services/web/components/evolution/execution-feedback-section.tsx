'use client'

import { Check, Copy, Loader2 } from 'lucide-react'
import {
  ExecutionFeedbackProvenanceDisplay,
  ExecutionFeedbackProvenanceInputs,
} from './execution-feedback-provenance'
import type {
  FlywheelExecutionFeedbackInspectResponse,
  TaskPacketPreviewResponse,
} from '@/lib/api-client'

type ExecutionFeedbackSectionProps = {
  executionStatusHint: string
  onExecutionStatusHintChange: (value: string) => void
  executionFeedbackText: string
  onExecutionFeedbackTextChange: (value: string) => void
  workerRunId: string
  workerProvider: string
  workerModel: string
  workerArtifactRef: string
  onWorkerRunIdChange: (value: string) => void
  onWorkerProviderChange: (value: string) => void
  onWorkerModelChange: (value: string) => void
  onWorkerArtifactRefChange: (value: string) => void
  executionFeedbackLoading: boolean
  executionFeedbackError: string | null
  executionFeedbackResult: FlywheelExecutionFeedbackInspectResponse | null
  executionFeedbackCopied: boolean
  onRequestInspect: () => void
  onCopyPacket: () => void
  taskPreviewResult: TaskPacketPreviewResponse | null
}

export function ExecutionFeedbackSection({
  executionStatusHint,
  onExecutionStatusHintChange,
  executionFeedbackText,
  onExecutionFeedbackTextChange,
  workerRunId,
  workerProvider,
  workerModel,
  workerArtifactRef,
  onWorkerRunIdChange,
  onWorkerProviderChange,
  onWorkerModelChange,
  onWorkerArtifactRefChange,
  executionFeedbackLoading,
  executionFeedbackError,
  executionFeedbackResult,
  executionFeedbackCopied,
  onRequestInspect,
  onCopyPacket,
  taskPreviewResult,
}: ExecutionFeedbackSectionProps) {
  return (
    <div className="mx-3 mb-3 rounded-md border bg-background p-3 space-y-3 text-xs">
      <div className="flex items-center justify-between gap-2">
        <div>
          <div className="font-medium">Execution Feedback</div>
          <div className="text-[11px] text-muted-foreground">
            Paste worker results for inspect-only feedback preview
          </div>
        </div>
        {executionFeedbackResult && (
          <button
            type="button"
            onClick={onCopyPacket}
            className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs hover:bg-muted transition-colors"
          >
            {executionFeedbackCopied ? (
              <>
                <Check className="h-3 w-3 text-green-600" />
                <span className="text-green-600">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3 w-3" />
                <span>Copy Feedback Packet</span>
              </>
            )}
          </button>
        )}
      </div>

      <div className="grid gap-3 md:grid-cols-[160px_1fr]">
        <div>
          <label className="text-xs text-muted-foreground mb-1 block">Status hint</label>
          <select
            value={executionStatusHint}
            onChange={(e) => onExecutionStatusHintChange(e.target.value)}
            className="w-full rounded-lg border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="neutral">neutral</option>
            <option value="accept">accept</option>
            <option value="accept_with_changes">accept_with_changes</option>
            <option value="reject">reject</option>
            <option value="blocked">blocked</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-muted-foreground mb-1 block">Worker execution feedback *</label>
          <textarea
            value={executionFeedbackText}
            onChange={(e) => onExecutionFeedbackTextChange(e.target.value)}
            placeholder="Paste coding/review/test result summary..."
            rows={5}
            className="w-full rounded-lg border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>

      <ExecutionFeedbackProvenanceInputs
        workerRunId={workerRunId}
        workerProvider={workerProvider}
        workerModel={workerModel}
        workerArtifactRef={workerArtifactRef}
        onWorkerRunIdChange={onWorkerRunIdChange}
        onWorkerProviderChange={onWorkerProviderChange}
        onWorkerModelChange={onWorkerModelChange}
        onWorkerArtifactRefChange={onWorkerArtifactRefChange}
      />

      <button
        type="button"
        onClick={onRequestInspect}
        disabled={executionFeedbackLoading || !executionFeedbackText.trim()}
        className="inline-flex items-center gap-2 rounded-lg border bg-background px-3 py-2 text-xs font-medium hover:bg-muted disabled:opacity-50"
      >
        {executionFeedbackLoading && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
        Inspect Execution Feedback
      </button>

      {executionFeedbackError && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
          {executionFeedbackError}
        </div>
      )}

      {executionFeedbackResult && (
        <div className="space-y-2">
          <div className="rounded-md border bg-muted/30 px-3 py-2">
            <div className="font-medium">Summary</div>
            <div className="mt-1 text-muted-foreground">
              {executionFeedbackResult.feedback_summary || '(none)'}
            </div>
          </div>

          <ExecutionFeedbackProvenanceDisplay provenance={executionFeedbackResult.provenance} />

          <div className="grid gap-2 md:grid-cols-2">
            <div className="rounded-md border bg-muted/20 px-3 py-2">
              <div className="font-medium">Next step</div>
              <div className="mt-1 text-muted-foreground">
                {executionFeedbackResult.operational_advice?.suggested_next_step || 'no_action'}
              </div>
            </div>
            <div className="rounded-md border bg-muted/20 px-3 py-2">
              <div className="font-medium">Intent</div>
              <div className="mt-1 text-muted-foreground">
                {executionFeedbackResult.feedback_intent}
              </div>
            </div>
          </div>

          {executionFeedbackResult.knowledge_delta_candidates.length > 0 && (
            <div className="rounded-md border bg-background px-3 py-2">
              <div className="mb-2 font-medium">Knowledge deltas</div>
              <div className="flex flex-wrap gap-1">
                {executionFeedbackResult.knowledge_delta_candidates.map((delta, index) => (
                  <span key={index} className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-700">
                    [{delta.delta_type}] {delta.label}
                  </span>
                ))}
              </div>
            </div>
          )}

          {executionFeedbackResult.evolution_trigger_candidates.length > 0 && (
            <div className="rounded-md border bg-background px-3 py-2">
              <div className="mb-2 font-medium">Evolution triggers</div>
              <div className="flex flex-wrap gap-1">
                {executionFeedbackResult.evolution_trigger_candidates.map((trigger, index) => (
                  <span key={index} className="rounded bg-purple-50 px-1.5 py-0.5 text-[10px] text-purple-700">
                    [{trigger.trigger_type}] {trigger.label}
                  </span>
                ))}
              </div>
            </div>
          )}

          {taskPreviewResult && (
            <div className="text-[10px] text-muted-foreground">
              task preview: {taskPreviewResult.task_packet_summary}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
