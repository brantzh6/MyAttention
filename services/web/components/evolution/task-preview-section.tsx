'use client'

import { AlertTriangle, Check, Copy, Loader2 } from 'lucide-react'
import type { TaskPacketPreviewResponse } from '@/lib/api-client'

type TaskPreviewSectionProps = {
  taskPreviewLoading: boolean
  taskPreviewError: string | null
  taskPreviewResult: TaskPacketPreviewResponse | null
  taskPreviewCopied: boolean
  selectedPreviewCount: number
  onRequestPreview: () => void
  onCopyPreview: () => void
}

export function TaskPreviewSection({
  taskPreviewLoading,
  taskPreviewError,
  taskPreviewResult,
  taskPreviewCopied,
  selectedPreviewCount,
  onRequestPreview,
  onCopyPreview,
}: TaskPreviewSectionProps) {
  return (
    <div className="mt-4 rounded-lg border bg-muted/20">
      <div className="flex items-center justify-between px-3 py-2 border-b">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold">Task Packet Preview</span>
          <span className="text-[10px] text-muted-foreground">
            Backend generated for review
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={onRequestPreview}
            disabled={taskPreviewLoading || selectedPreviewCount === 0}
            className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs hover:bg-muted transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {taskPreviewLoading && <Loader2 className="h-3 w-3 animate-spin" />}
            Request Preview
          </button>
          {taskPreviewResult && (
            <button
              type="button"
              onClick={onCopyPreview}
              className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs hover:bg-muted transition-colors"
              title="Copy handoff packet to clipboard"
            >
              {taskPreviewCopied ? (
                <>
                  <Check className="h-3 w-3 text-green-600" />
                  <span className="text-green-600">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  <span>Copy Handoff Packet</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {taskPreviewError && (
        <div className="px-3 py-2 flex items-start gap-2 text-sm text-red-700">
          <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
          {taskPreviewError}
        </div>
      )}

      {taskPreviewLoading && (
        <div className="px-3 py-2 flex items-center gap-2 text-xs text-muted-foreground">
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
          Requesting preview...
        </div>
      )}

      {taskPreviewResult && (
        <div className="px-3 py-2 space-y-1.5 text-xs">
          <div className="grid grid-cols-[90px_1fr] gap-x-2">
            <span className="text-muted-foreground shrink-0">Summary</span>
            <span className="font-medium truncate">{taskPreviewResult.task_packet_summary}</span>
          </div>
          <div className="grid grid-cols-[90px_1fr] gap-x-2">
            <span className="text-muted-foreground shrink-0">Intent</span>
            <span>{taskPreviewResult.packet_intent}</span>
          </div>
          <div className="grid grid-cols-[90px_1fr] gap-x-2">
            <span className="text-muted-foreground shrink-0">Suggested Lane</span>
            <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">{taskPreviewResult.suggested_lane}</span>
          </div>
          {taskPreviewResult.suggested_next_step && (
            <div className="grid grid-cols-[90px_1fr] gap-x-2">
              <span className="text-muted-foreground shrink-0">Next Step</span>
              <span>{taskPreviewResult.suggested_next_step}</span>
            </div>
          )}
          {taskPreviewResult.selected_label_groups.length > 0 && (
            <div className="grid grid-cols-[90px_1fr] gap-x-2">
              <span className="text-muted-foreground shrink-0">Label Groups</span>
              <div className="flex flex-wrap gap-1">
                {taskPreviewResult.selected_label_groups.map((group, index) => (
                  <span key={index} className="rounded bg-muted px-1.5 py-0.5 text-[10px]">
                    [{group.label_type}] {group.count} items
                  </span>
                ))}
              </div>
            </div>
          )}
          {taskPreviewResult.controller_packet?.reason_tags?.length > 0 && (
            <div className="grid grid-cols-[90px_1fr] gap-x-2">
              <span className="text-muted-foreground shrink-0">Reason Tags</span>
              <div className="flex flex-wrap gap-1">
                {taskPreviewResult.controller_packet.reason_tags.map((tag, index) => (
                  <span key={index} className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
          {taskPreviewResult.candidate_packet && (
            <div className="mt-2 pt-2 border-t border-dashed">
              <div className="text-xs font-semibold text-blue-600 mb-1.5">Candidate Packet</div>
              <div className="space-y-1 text-xs">
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">Task ID</span>
                  <span className="font-mono text-[10px] truncate">{taskPreviewResult.candidate_packet.candidate_task_id}</span>
                </div>
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">Lane</span>
                  <span className="rounded bg-blue-100 px-1.5 py-0.5 font-mono text-[10px]">{taskPreviewResult.candidate_packet.candidate_lane}</span>
                </div>
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">Goal</span>
                  <span className="truncate">{taskPreviewResult.candidate_packet.candidate_goal}</span>
                </div>
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">Delegation</span>
                  <span className="rounded bg-green-100 px-1.5 py-0.5 font-mono text-[10px]">{taskPreviewResult.candidate_packet.delegation_target}</span>
                </div>
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">Review Gate</span>
                  <span className="text-[10px]">{taskPreviewResult.candidate_packet.review_gate}</span>
                </div>
                {taskPreviewResult.candidate_packet.allowed_files.length > 0 && (
                  <div className="grid grid-cols-[90px_1fr] gap-x-2">
                    <span className="text-muted-foreground shrink-0">Allowed Files</span>
                    <div className="flex flex-wrap gap-1">
                      {taskPreviewResult.candidate_packet.allowed_files.slice(0, 3).map((file, index) => (
                        <span key={index} className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px] truncate max-w-[200px]">
                          {file}
                        </span>
                      ))}
                      {taskPreviewResult.candidate_packet.allowed_files.length > 3 && (
                        <span className="text-muted-foreground text-[10px]">
                          +{taskPreviewResult.candidate_packet.allowed_files.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          {taskPreviewResult.handoff_preview && (
            <div className="mt-2 pt-2 border-t border-dashed">
              <div className="text-xs font-semibold text-emerald-700 mb-1.5">Execution Handoff Preview</div>
              <div className="space-y-1 text-xs">
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">task_id</span>
                  <span className="font-mono text-[10px] truncate">{taskPreviewResult.handoff_preview.task_id}</span>
                </div>
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">owner_lane</span>
                  <span className="rounded bg-emerald-100 px-1.5 py-0.5 font-mono text-[10px]">{taskPreviewResult.handoff_preview.owner_lane}</span>
                </div>
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">objective</span>
                  <span className="truncate">{taskPreviewResult.handoff_preview.objective}</span>
                </div>
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">gate</span>
                  <span className="text-[10px]">{taskPreviewResult.handoff_preview.review_gate}</span>
                </div>
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">result</span>
                  <div className="flex flex-wrap gap-1">
                    {taskPreviewResult.handoff_preview.expected_result_format.map((field) => (
                      <span key={field} className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">
                        {field}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">state</span>
                  <span className="font-mono text-[10px]">{taskPreviewResult.handoff_preview.promotion_state}</span>
                </div>
                {/* New metadata fields */}
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">sdlc_stage</span>
                  <span className="rounded bg-amber-100 px-1.5 py-0.5 font-mono text-[10px]">{taskPreviewResult.handoff_preview.sdlc_stage}</span>
                </div>
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">risk_level</span>
                  <span className={`rounded px-1.5 py-0.5 font-mono text-[10px] ${taskPreviewResult.handoff_preview.risk_level === 'R3' ? 'bg-red-100 text-red-700' : 'bg-muted'}`}>{taskPreviewResult.handoff_preview.risk_level}</span>
                </div>
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">result_path</span>
                  <span className="font-mono text-[10px] truncate">{taskPreviewResult.handoff_preview.result_artifact_path}</span>
                </div>
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-muted-foreground shrink-0">write_policy</span>
                  <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">{taskPreviewResult.handoff_preview.write_policy}</span>
                </div>
                {/* Handoff markdown preview */}
                {taskPreviewResult.handoff_preview.handoff_markdown && (
                  <div className="mt-2 pt-2 border-t border-dashed">
                    <div className="text-[10px] font-semibold text-muted-foreground mb-1">Generated Handoff Markdown (Copy-ready)</div>
                    <pre className="bg-muted/50 rounded p-2 text-[10px] font-mono whitespace-pre-wrap max-h-[200px] overflow-auto">
                      {taskPreviewResult.handoff_preview.handoff_markdown}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          )}
          <div className="grid grid-cols-[90px_1fr] gap-x-2">
            <span className="text-muted-foreground shrink-0">Truth Status</span>
            <span className="text-muted-foreground">{taskPreviewResult.promotion_state}</span>
          </div>

          {/* Controller Next Action Panel */}
          <div
            data-testid="controller-next-action-panel"
            className="mt-3 rounded-md border border-amber-200 bg-amber-50/50 p-3"
          >
            <div className="mb-2 flex items-center gap-2">
              <AlertTriangle className="h-3.5 w-3.5 text-amber-600" />
              <span className="text-xs font-bold text-amber-900">Controller Next Action (Inspect-only)</span>
            </div>

            <div className="space-y-1.5 text-xs">
              <div className="grid grid-cols-[90px_1fr] gap-x-2">
                <span className="text-amber-800/70">Next Step</span>
                <span className="font-medium text-amber-900">{taskPreviewResult.suggested_next_step || 'none'}</span>
              </div>
              <div className="grid grid-cols-[90px_1fr] gap-x-2">
                <span className="text-amber-800/70">Owner Lane</span>
                <span className="font-mono text-[10px] text-amber-900">
                  {taskPreviewResult.handoff_preview?.owner_lane ||
                   taskPreviewResult.candidate_packet?.candidate_lane ||
                   taskPreviewResult.suggested_lane ||
                   'unknown'}
                </span>
              </div>
              <div className="grid grid-cols-[90px_1fr] gap-x-2">
                <span className="text-amber-800/70">Review Gate</span>
                <span className="text-amber-900">
                  {taskPreviewResult.handoff_preview?.review_gate ||
                   taskPreviewResult.candidate_packet?.review_gate ||
                   'manual_approval'}
                </span>
              </div>
              {taskPreviewResult.handoff_preview?.result_artifact_path && (
                <div className="grid grid-cols-[90px_1fr] gap-x-2">
                  <span className="text-amber-800/70">Result Path</span>
                  <span className="font-mono text-[10px] truncate text-amber-900">
                    {taskPreviewResult.handoff_preview.result_artifact_path}
                  </span>
                </div>
              )}
              <div className="grid grid-cols-[90px_1fr] gap-x-2">
                <span className="text-amber-800/70">Validation</span>
                <span className="text-amber-900">
                  {taskPreviewResult.handoff_preview?.validation_commands?.length ||
                   taskPreviewResult.candidate_packet?.validation_commands?.length || 0} commands suggested
                </span>
              </div>

              <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 border-t border-amber-200 pt-2 text-[10px] font-medium text-amber-800/80">
                <span className="flex items-center gap-1">
                  <div className="h-1 w-1 rounded-full bg-amber-500" />
                  Manual copy/dispatch only
                </span>
                <span className="flex items-center gap-1">
                  <div className="h-1 w-1 rounded-full bg-amber-500" />
                  Inspect-only
                </span>
                <span className="flex items-center gap-1">
                  <div className="h-1 w-1 rounded-full bg-amber-500" />
                  No automatic execution
                </span>
                <span className="flex items-center gap-1">
                  <div className="h-1 w-1 rounded-full bg-amber-500" />
                  Review before controller absorption
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {!taskPreviewResult && !taskPreviewError && !taskPreviewLoading && (
        <div className="px-3 py-2 text-xs text-muted-foreground">
          {selectedPreviewCount === 0
            ? 'Select items to request preview'
            : 'Click "Request Preview" to fetch packet'}
        </div>
      )}
    </div>
  )
}
