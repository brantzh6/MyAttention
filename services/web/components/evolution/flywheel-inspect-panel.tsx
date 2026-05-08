'use client'

import { useEffect, useState } from 'react'
import { Loader2, AlertTriangle, BrainCircuit } from 'lucide-react'
import { FLYWHEEL_HANDOFF_STORAGE_KEY, parseFlywheelHandoffPayload } from '@/lib/flywheel-handoff'
import { ExecutionFeedbackSection } from './execution-feedback-section'
import { FlywheelResultsSection } from './flywheel-results-section'
import { LoopClosureSummarySection } from './loop-closure-summary-section'
import { ManualAbsorptionSection } from './manual-absorption-section'
import { ManualDecisionSection } from './manual-decision-section'
import { ManualReviewSection } from './manual-review-section'
import { WorkerPacketBridgeSection } from './worker-packet-bridge-section'
import { TaskPreviewSection } from './task-preview-section'
import { useFlywheelRuntimeController } from './use-flywheel-runtime-controller'
export function FlywheelInspectPanel() {
  const [handoffNotice, setHandoffNotice] = useState<string | null>(null)
  const {
    state,
    selectedPreviewCount,
    hasAnyAbsorptionSelection,
    isSectionOpen,
    handleSubmit,
    toggleSelect,
    setField,
    setWorkerLane,
    copyReviewPacket,
    copyAbsorptionPacket,
    copyDecisionPacket,
    requestTaskPreview,
    copyTaskPreviewPacket,
    copyWorkerPacket,
    copyLoopPacket,
    requestExecutionFeedbackInspect,
    copyExecutionFeedbackPacket,
  } = useFlywheelRuntimeController()
  const {
    conversationText,
    topic,
    taskIntent,
    provider,
    model,
    loading,
    error,
    result,
    copied,
    selectedKnowledge,
    selectedTriggers,
    selectedSources,
    reviewerNote,
    absorptionCopied,
    decisionCopied,
    taskPreviewLoading,
    taskPreviewResult,
    taskPreviewError,
    taskPreviewCopied,
    loopPacketCopied,
    workerLane,
    workerCopiedMap,
    executionFeedbackText,
    executionStatusHint,
    executionFeedbackLoading,
    executionFeedbackError,
    executionFeedbackResult,
    executionFeedbackCopied,
    workerRunId,
    workerProvider,
    workerModel,
    workerArtifactRef,
  } = state

  useEffect(() => {
    if (typeof window === 'undefined') return

    const params = new URLSearchParams(window.location.search)
    if (params.get('handoff') !== 'chat') return

    const payload = parseFlywheelHandoffPayload(
      window.sessionStorage.getItem(FLYWHEEL_HANDOFF_STORAGE_KEY),
    )
    window.sessionStorage.removeItem(FLYWHEEL_HANDOFF_STORAGE_KEY)

    if (!payload) return

    setField('conversationText', payload.text)
    setField('topic', payload.topic || 'chat conversation')
    setField(
      'taskIntent',
      payload.taskIntent || 'inspect chat turn for IKE flywheel candidate extraction',
    )
    setHandoffNotice('Imported transient chat input. It is inspect-only, non-canonical, and will not be submitted automatically.')
  }, [setField])

  return (
    <div className="rounded-2xl border bg-card p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <BrainCircuit className="h-4 w-4 text-muted-foreground" />
        <h3 className="text-sm font-semibold">Flywheel 探测面板</h3>
      </div>

      {handoffNotice && (
        <div className="mb-4 rounded-lg border border-sky-200 bg-sky-50 px-3 py-2 text-xs text-sky-800">
          {handoffNotice}
        </div>
      )}

      {/* Input form */}
      <div className="space-y-3">
        <div>
          <label className="text-xs text-muted-foreground mb-1 block">对话内容 *</label>
          <textarea
            value={conversationText}
            onChange={e => setField('conversationText', e.target.value)}
            placeholder="粘贴一段对话文本..."
            rows={4}
            className="w-full rounded-lg border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <div>
            <label className="text-xs text-muted-foreground mb-1 block">主题 *</label>
            <input
              value={topic}
              onChange={e => setField('topic', e.target.value)}
              placeholder="如：source intelligence"
              className="w-full rounded-lg border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <div>
            <label className="text-xs text-muted-foreground mb-1 block">任务意图</label>
            <input
              value={taskIntent}
              onChange={e => setField('taskIntent', e.target.value)}
              placeholder="如：研究新来源"
              className="w-full rounded-lg border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <div>
            <label className="text-xs text-muted-foreground mb-1 block">Provider</label>
            <input
              value={provider}
              onChange={e => setField('provider', e.target.value)}
              placeholder="qwen"
              className="w-full rounded-lg border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <div>
            <label className="text-xs text-muted-foreground mb-1 block">Model</label>
            <input
              value={model}
              onChange={e => setField('model', e.target.value)}
              placeholder="留空使用默认模型"
              className="w-full rounded-lg border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading || !conversationText.trim() || !topic.trim()}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {loading && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
          提交探测
        </button>
      </div>

      {/* Error state */}
      {error && (
        <div className="mt-4 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
          {error}
        </div>
      )}

      {/* Truth boundary banner */}
      {result && (
        <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          此结果为探测模式（inspect-only），不会持久化任何数据，不构成规范事实。
        </div>
      )}

      {/* Manual review bridge */}
      {result && (
        <ManualReviewSection
          result={result}
          copied={copied}
          onCopyReviewPacket={copyReviewPacket}
        />
      )}

      {/* Manual absorption surface */}
      {result && (
        <ManualAbsorptionSection
          result={result}
          selectedKnowledge={selectedKnowledge}
          selectedTriggers={selectedTriggers}
          selectedSources={selectedSources}
          reviewerNote={reviewerNote}
          hasAnyAbsorptionSelection={hasAnyAbsorptionSelection}
          absorptionCopied={absorptionCopied}
          onCopyAbsorptionPacket={copyAbsorptionPacket}
          onToggleSelect={toggleSelect}
          onReviewerNoteChange={(value) => setField('reviewerNote', value)}
        />
      )}

      {/* Manual decision bridge */}
      {result && (
        <ManualDecisionSection
          result={result}
          selectedKnowledge={selectedKnowledge}
          selectedTriggers={selectedTriggers}
          selectedSources={selectedSources}
          reviewerNote={reviewerNote}
          decisionCopied={decisionCopied}
          onCopyDecisionPacket={copyDecisionPacket}
        />
      )}
      {/* Backend task-packet preview */}
      {result && (
        <TaskPreviewSection
          taskPreviewLoading={taskPreviewLoading}
          taskPreviewError={taskPreviewError}
          taskPreviewResult={taskPreviewResult}
          taskPreviewCopied={taskPreviewCopied}
          selectedPreviewCount={selectedPreviewCount}
          onRequestPreview={requestTaskPreview}
          onCopyPreview={copyTaskPreviewPacket}
        />
      )}

      {/* Worker-ready packet bridge (requires taskPreviewResult) */}
      {result && taskPreviewResult && (
        <WorkerPacketBridgeSection
          result={result}
          taskPreviewResult={taskPreviewResult}
          workerLane={workerLane}
          onWorkerLaneChange={setWorkerLane}
          onCopyWorkerPacket={copyWorkerPacket}
          onCopyLoopPacket={copyLoopPacket}
          workerCopiedMap={workerCopiedMap}
          loopPacketCopied={loopPacketCopied}
          executionFeedbackSection={
            <ExecutionFeedbackSection
              executionStatusHint={executionStatusHint}
              onExecutionStatusHintChange={(value) => setField('executionStatusHint', value)}
              executionFeedbackText={executionFeedbackText}
              onExecutionFeedbackTextChange={(value) => setField('executionFeedbackText', value)}
              workerRunId={workerRunId}
              workerProvider={workerProvider}
              workerModel={workerModel}
              workerArtifactRef={workerArtifactRef}
              onWorkerRunIdChange={(value) => setField('workerRunId', value)}
              onWorkerProviderChange={(value) => setField('workerProvider', value)}
              onWorkerModelChange={(value) => setField('workerModel', value)}
              onWorkerArtifactRefChange={(value) => setField('workerArtifactRef', value)}
              executionFeedbackLoading={executionFeedbackLoading}
              executionFeedbackError={executionFeedbackError}
              executionFeedbackResult={executionFeedbackResult}
              executionFeedbackCopied={executionFeedbackCopied}
              onRequestInspect={requestExecutionFeedbackInspect}
              onCopyPacket={copyExecutionFeedbackPacket}
              taskPreviewResult={taskPreviewResult}
            />
          }
        />
      )}

      {result && taskPreviewResult && executionFeedbackResult && (
        <LoopClosureSummarySection
          result={result}
          taskPreviewResult={taskPreviewResult}
          executionFeedbackResult={executionFeedbackResult}
          workerLane={workerLane}
          executionStatusHint={executionStatusHint}
        />
      )}


      {/* Results */}
      {result && (
        <FlywheelResultsSection result={result} isSectionOpen={isSectionOpen} />
      )}
    </div>
  )
}
