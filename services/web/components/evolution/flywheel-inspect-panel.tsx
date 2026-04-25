'use client'

import { Loader2, AlertTriangle, BrainCircuit } from 'lucide-react'
import { CollapsibleSection } from './collapsible-section'
import { ExecutionFeedbackSection } from './execution-feedback-section'
import { ManualAbsorptionSection } from './manual-absorption-section'
import { ManualDecisionSection } from './manual-decision-section'
import { ManualReviewSection } from './manual-review-section'
import { WorkerPacketBridgeSection } from './worker-packet-bridge-section'
import { TaskPreviewSection } from './task-preview-section'
import { useFlywheelRuntimeController } from './use-flywheel-runtime-controller'
export function FlywheelInspectPanel() {
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

  return (
    <div className="rounded-2xl border bg-card p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <BrainCircuit className="h-4 w-4 text-muted-foreground" />
        <h3 className="text-sm font-semibold">Flywheel 探测面板</h3>
      </div>

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
          workerCopiedMap={workerCopiedMap}
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


      {/* Results */}
      {result && (
        <div className="mt-4 space-y-3">
          {/* Extraction summary */}
          <CollapsibleSection title="提取摘要" open={isSectionOpen('extraction')} defaultOpen>
            <p className="text-sm text-muted-foreground">{result.extraction_summary || '无摘要'}</p>
            {result.segment_intent && result.segment_intent !== 'other' && (
              <p className="mt-2 text-xs">
                <span className="text-muted-foreground">意图识别：</span>
                <span className="font-medium">{result.segment_intent}</span>
              </p>
            )}
          </CollapsibleSection>

          {/* Knowledge delta candidates */}
          <CollapsibleSection title={`知识增量候选 (${result.knowledge_delta_candidates.length})`} open={isSectionOpen('knowledge')}>
            {result.knowledge_delta_candidates.length === 0 ? (
              <p className="text-xs text-muted-foreground">无候选</p>
            ) : (
              <ul className="space-y-2">
                {result.knowledge_delta_candidates.map((d, i) => (
                  <li key={i} className="rounded-md border bg-background p-2 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">{d.delta_type}</span>
                      <span className="font-medium">{d.label}</span>
                    </div>
                    <p className="mt-1 text-muted-foreground">{d.content}</p>
                  </li>
                ))}
              </ul>
            )}
          </CollapsibleSection>

          {/* Evolution trigger candidates */}
          <CollapsibleSection title={`进化触发候选 (${result.evolution_trigger_candidates.length})`} open={isSectionOpen('triggers')}>
            {result.evolution_trigger_candidates.length === 0 ? (
              <p className="text-xs text-muted-foreground">无候选</p>
            ) : (
              <ul className="space-y-2">
                {result.evolution_trigger_candidates.map((t, i) => (
                  <li key={i} className="rounded-md border bg-background p-2 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">{t.trigger_type}</span>
                      <span className="font-medium">{t.label}</span>
                    </div>
                    {t.rationale && <p className="mt-1 text-muted-foreground">{t.rationale}</p>}
                  </li>
                ))}
              </ul>
            )}
          </CollapsibleSection>

          {/* Source candidates */}
          <CollapsibleSection title={`来源候选 (${result.source_candidates.length})`} open={isSectionOpen('sources')}>
            {result.source_candidates.length === 0 ? (
              <p className="text-xs text-muted-foreground">无来源候选</p>
            ) : (
              <ul className="space-y-1">
                {result.source_candidates.map((s, i) => (
                  <li key={i} className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span className="h-1 w-1 rounded-full bg-muted-foreground" />
                    {s.name || s.id || '未命名'}
                    {s.type && <span className="text-[10px] text-muted-foreground/60">· {s.type}</span>}
                  </li>
                ))}
              </ul>
            )}
          </CollapsibleSection>

          {/* Operational advice */}
          <CollapsibleSection title="操作建议" open={isSectionOpen('advice')}>
            {result.operational_advice.suggested_next_step !== 'no_action' && (
              <p className="text-sm font-medium">{result.operational_advice.suggested_next_step}</p>
            )}
            {result.operational_advice.controller_notes.length > 0 && (
              <ul className="mt-1 space-y-1">
                {result.operational_advice.controller_notes.map((n, i) => (
                  <li key={i} className="text-xs text-muted-foreground">· {n}</li>
                ))}
              </ul>
            )}
            {result.operational_advice.suggested_next_step === 'no_action' && result.operational_advice.controller_notes.length === 0 && (
              <p className="text-xs text-muted-foreground">无操作建议</p>
            )}
          </CollapsibleSection>

          {/* Controller packet */}
          <CollapsibleSection title="控制器数据包" open={isSectionOpen('controller')}>
            <div className="space-y-1 text-xs">
              <p>
                <span className="text-muted-foreground">审查模式：</span>{result.controller_packet.review_mode}
              </p>
              <p>
                <span className="text-muted-foreground">事实状态：</span>{result.controller_packet.truth_status}
              </p>
              {result.controller_packet.reason_tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1">
                  {result.controller_packet.reason_tags.map((tag, i) => (
                    <span key={i} className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">{tag}</span>
                  ))}
                </div>
              )}
            </div>
          </CollapsibleSection>
        </div>
      )}
    </div>
  )
}
