'use client'

import { Loader2, AlertTriangle, BrainCircuit, Copy, Check } from 'lucide-react'
import { CollapsibleSection } from './collapsible-section'
import { ExecutionFeedbackSection } from './execution-feedback-section'
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
        <div className="mt-4 rounded-lg border bg-card/80">
          <div className="flex items-center justify-between px-3 py-2 border-b">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold">手动审查包</span>
              <span className="text-[10px] text-muted-foreground">Review Packet — 仅供手动审查</span>
            </div>
            <button
              type="button"
              onClick={copyReviewPacket}
              className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs hover:bg-muted transition-colors"
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
          <div className="px-3 py-2 space-y-1.5 text-xs">
            <div className="grid grid-cols-[80px_1fr] gap-x-2">
              <span className="text-muted-foreground shrink-0">主题</span>
              <span className="font-medium truncate">{result.topic}</span>
            </div>
            <div className="grid grid-cols-[80px_1fr] gap-x-2">
              <span className="text-muted-foreground shrink-0">任务意图</span>
              <span>{result.task_intent || '(未指定)'}</span>
            </div>
            <div className="grid grid-cols-[80px_1fr] gap-x-2">
              <span className="text-muted-foreground shrink-0">意图分段</span>
              <span>{result.segment_intent || '(未识别)'}</span>
            </div>
            {result.operational_advice?.suggested_next_step && result.operational_advice.suggested_next_step !== 'no_action' && (
              <div className="grid grid-cols-[80px_1fr] gap-x-2">
                <span className="text-muted-foreground shrink-0">建议下一步</span>
                <span className="font-medium">{result.operational_advice.suggested_next_step}</span>
              </div>
            )}
            {result.controller_packet?.reason_tags?.length > 0 && (
              <div className="grid grid-cols-[80px_1fr] gap-x-2">
                <span className="text-muted-foreground shrink-0">原因标签</span>
                <div className="flex flex-wrap gap-1">
                  {result.controller_packet.reason_tags.map((tag, i) => (
                    <span key={i} className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">{tag}</span>
                  ))}
                </div>
              </div>
            )}
            {result.knowledge_delta_candidates?.length > 0 && (
              <div className="grid grid-cols-[80px_1fr] gap-x-2">
                <span className="text-muted-foreground shrink-0">知识增量</span>
                <div className="flex flex-wrap gap-1">
                  {result.knowledge_delta_candidates.map((d, i) => (
                    <span key={i} className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-700">[{d.delta_type}] {d.label}</span>
                  ))}
                </div>
              </div>
            )}
            {result.evolution_trigger_candidates?.length > 0 && (
              <div className="grid grid-cols-[80px_1fr] gap-x-2">
                <span className="text-muted-foreground shrink-0">进化触发</span>
                <div className="flex flex-wrap gap-1">
                  {result.evolution_trigger_candidates.map((t, i) => (
                    <span key={i} className="rounded bg-purple-50 px-1.5 py-0.5 text-[10px] text-purple-700">[{t.trigger_type}] {t.label}</span>
                  ))}
                </div>
              </div>
            )}
            {result.source_candidates?.length > 0 && (
              <div className="grid grid-cols-[80px_1fr] gap-x-2">
                <span className="text-muted-foreground shrink-0">来源候选</span>
                <div className="space-y-0.5">
                  {result.source_candidates.map((s, i) => (
                    <div key={i} className="text-muted-foreground">
                      <span className="h-1 w-1 rounded-full bg-muted-foreground inline-block mr-1" />
                      {s.name || s.id || '未命名'}
                      {s.type && <span className="text-[10px] text-muted-foreground/60"> · {s.type}</span>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Manual absorption surface */}
      {result && (
        <div className="mt-4 rounded-lg border border-dashed bg-muted/30">
          <div className="flex items-center justify-between px-3 py-2 border-b border-dashed">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold">手动吸收</span>
              <span className="text-[10px] text-muted-foreground">Absorption — 选择候选项并生成紧凑吸收包</span>
            </div>
            <button
              type="button"
              onClick={copyAbsorptionPacket}
              disabled={!hasAnyAbsorptionSelection && !reviewerNote.trim()}
              className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs hover:bg-muted transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
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

          <div className="px-3 py-2 space-y-3">
            {/* Knowledge delta checkboxes */}
            {result.knowledge_delta_candidates.length > 0 && (
              <div>
                <div className="text-[11px] font-medium text-muted-foreground mb-1">知识增量候选</div>
                <div className="space-y-0.5">
                  {result.knowledge_delta_candidates.map((d, i) => (
                    <label key={i} className="flex items-start gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedKnowledge.has(i)}
                        onChange={() => toggleSelect('knowledge', i)}
                        className="mt-0.5 h-3.5 w-3.5 rounded border-muted-foreground/30 accent-primary"
                      />
                      <span className="text-xs">
                        <span className="rounded bg-muted px-1 py-0.5 font-mono text-[10px]">{d.delta_type}</span>
                        {' '}{d.label}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Evolution trigger checkboxes */}
            {result.evolution_trigger_candidates.length > 0 && (
              <div>
                <div className="text-[11px] font-medium text-muted-foreground mb-1">进化触发候选</div>
                <div className="space-y-0.5">
                  {result.evolution_trigger_candidates.map((t, i) => (
                    <label key={i} className="flex items-start gap-2 cursor-pointer">
                      <input
                      type="checkbox"
                      checked={selectedTriggers.has(i)}
                      onChange={() => toggleSelect('triggers', i)}
                      className="mt-0.5 h-3.5 w-3.5 rounded border-muted-foreground/30 accent-primary"
                    />
                    <span className="text-xs">
                      <span className="rounded bg-muted px-1 py-0.5 font-mono text-[10px]">{t.trigger_type}</span>
                      {' '}{t.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Source checkboxes */}
          {result.source_candidates.length > 0 && (
            <div>
              <div className="text-[11px] font-medium text-muted-foreground mb-1">来源候选</div>
              <div className="space-y-0.5">
                {result.source_candidates.map((s, i) => (
                  <label key={i} className="flex items-start gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedSources.has(i)}
                      onChange={() => toggleSelect('sources', i)}
                      className="mt-0.5 h-3.5 w-3.5 rounded border-muted-foreground/30 accent-primary"
                    />
                    <span className="text-xs text-muted-foreground">
                      {s.name || s.id || '未命名'}
                      {s.type && <span className="text-[10px] text-muted-foreground/60"> · {s.type}</span>}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Reviewer note */}
          <div>
            <label className="text-[11px] font-medium text-muted-foreground mb-1 block">审查备注</label>
            <textarea
              value={reviewerNote}
              onChange={e => setField('reviewerNote', e.target.value)}
              placeholder="简短备注（可选）..."
              rows={2}
              maxLength={500}
              className="w-full rounded-md border bg-background px-2 py-1.5 text-xs placeholder:text-muted-foreground/60 focus:outline-none focus:ring-1 focus:ring-primary resize-none"
            />
          </div>
        </div>
      </div>
    )}

      {/* Manual decision bridge */}
      {result && (
        <div className="mt-4 rounded-lg border border-dashed bg-muted/20">
          <div className="flex items-center justify-between px-3 py-2 border-b border-dashed">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold">手动决策桥接</span>
              <span className="text-[10px] text-muted-foreground">Decision Bridge — 生成紧凑决策包供对齐讨论</span>
            </div>
            <button
              type="button"
              onClick={copyDecisionPacket}
              className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs hover:bg-muted transition-colors"
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

          <div className="px-3 py-2 space-y-1.5 text-xs">
            <div className="grid grid-cols-[80px_1fr] gap-x-2">
              <span className="text-muted-foreground shrink-0">主题</span>
              <span className="font-medium truncate">{result.topic}</span>
            </div>
            <div className="grid grid-cols-[80px_1fr] gap-x-2">
              <span className="text-muted-foreground shrink-0">任务意图</span>
              <span>{result.task_intent || '(未指定)'}</span>
            </div>
            {result.operational_advice?.suggested_next_step && result.operational_advice.suggested_next_step !== 'no_action' && (
              <div className="grid grid-cols-[80px_1fr] gap-x-2">
                <span className="text-muted-foreground shrink-0">建议下一步</span>
                <span className="font-medium">{result.operational_advice.suggested_next_step}</span>
              </div>
            )}
            {result.controller_packet?.reason_tags?.length > 0 && (
              <div className="grid grid-cols-[80px_1fr] gap-x-2">
                <span className="text-muted-foreground shrink-0">原因标签</span>
                <div className="flex flex-wrap gap-1">
                  {result.controller_packet.reason_tags.map((tag, i) => (
                    <span key={i} className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">{tag}</span>
                  ))}
                </div>
              </div>
            )}
            {(selectedKnowledge.size > 0 || selectedTriggers.size > 0 || selectedSources.size > 0) && (
              <div className="grid grid-cols-[80px_1fr] gap-x-2">
                <span className="text-muted-foreground shrink-0">已选项</span>
                <div className="flex flex-wrap gap-1">
                  {Array.from(selectedKnowledge).map((i) => {
                    const d = result.knowledge_delta_candidates[i]
                    return d ? <span key={`k${i}`} className="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-700">[{d.delta_type}] {d.label}</span> : null
                  })}
                  {Array.from(selectedTriggers).map((i) => {
                    const t = result.evolution_trigger_candidates[i]
                    return t ? <span key={`t${i}`} className="rounded bg-purple-50 px-1.5 py-0.5 text-[10px] text-purple-700">[{t.trigger_type}] {t.label}</span> : null
                  })}
                  {Array.from(selectedSources).map((i) => {
                    const s = result.source_candidates[i]
                    return s ? <span key={`s${i}`} className="rounded bg-muted px-1.5 py-0.5 text-[10px]">{s.name || s.id || '未命名'}</span> : null
                  })}
                </div>
              </div>
            )}
            {reviewerNote.trim() && (
              <div className="grid grid-cols-[80px_1fr] gap-x-2">
                <span className="text-muted-foreground shrink-0">审查备注</span>
                <span className="text-muted-foreground truncate">{reviewerNote.trim()}</span>
              </div>
            )}
          </div>
        </div>
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
