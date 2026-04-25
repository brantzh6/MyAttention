'use client'

import { apiClient } from '@/lib/api-client'
import { copyTextToClipboard } from './clipboard'
import {
  buildAbsorptionPacket,
  buildDecisionPacket,
  buildExecutionFeedbackPacket,
  buildLoopPacket,
  buildReviewPacket,
  buildTaskPreviewPacket,
  buildWorkerPacket,
  type WorkerLane,
} from './flywheel-packet-builders'
import {
  useFlywheelRuntimeState,
  type SectionKey,
  type SelectionFamily,
  type StringFieldKey,
} from './use-flywheel-runtime-state'

const COPY_RESET_DELAY_MS = 1500

export function useFlywheelRuntimeController() {
  const { state, dispatch } = useFlywheelRuntimeState()

  const selectedPreviewCount =
    state.selectedKnowledge.size + state.selectedTriggers.size + state.selectedSources.size

  const hasAnyAbsorptionSelection =
    state.selectedKnowledge.size > 0 ||
    state.selectedTriggers.size > 0 ||
    state.selectedSources.size > 0

  const isSectionOpen = (key: SectionKey) => state.openSections.has(key)

  const resetCopyFlag = (
    key:
      | 'copied'
      | 'absorptionCopied'
      | 'decisionCopied'
      | 'taskPreviewCopied'
      | 'executionFeedbackCopied'
      | 'loopPacketCopied',
  ) => {
    setTimeout(() => dispatch({ type: 'setCopyFlag', key, value: false }), COPY_RESET_DELAY_MS)
  }

  const resetWorkerCopied = (lane: WorkerLane) => {
    setTimeout(() => dispatch({ type: 'setWorkerCopied', lane, value: false }), COPY_RESET_DELAY_MS)
  }

  const handleSubmit = async () => {
    if (!state.conversationText.trim() || !state.topic.trim()) return
    dispatch({ type: 'startInspect' })
    try {
      const data = await apiClient.inspectFlywheel({
        conversation_text: state.conversationText.trim(),
        topic: state.topic.trim(),
        task_intent: state.taskIntent.trim() || undefined,
        provider: state.provider.trim() || 'qwen',
        model: state.model.trim() || undefined,
      })
      dispatch({ type: 'inspectSuccess', result: data })
    } catch (e) {
      dispatch({
        type: 'inspectError',
        error: e instanceof Error ? e.message : 'Inspect request failed.',
      })
    }
  }

  const toggleSelect = (family: SelectionFamily, index: number) => {
    dispatch({ type: 'toggleSelection', family, index })
  }

  const setField = (field: StringFieldKey, value: string) => {
    dispatch({ type: 'setStringField', field, value })
  }

  const setWorkerLane = (lane: WorkerLane) => {
    dispatch({ type: 'setWorkerLane', lane })
  }

  const copyReviewPacket = async () => {
    if (!state.result) return
    await copyTextToClipboard(buildReviewPacket(state.result))
    dispatch({ type: 'setCopyFlag', key: 'copied', value: true })
    resetCopyFlag('copied')
  }

  const getSafeSelections = () => {
    if (!state.result) {
      return {
        knowledge: [] as number[],
        triggers: [] as number[],
        sources: [] as number[],
      }
    }
    return {
      knowledge: Array.from(state.selectedKnowledge).filter(
        (i) => i >= 0 && i < state.result!.knowledge_delta_candidates.length,
      ),
      triggers: Array.from(state.selectedTriggers).filter(
        (i) => i >= 0 && i < state.result!.evolution_trigger_candidates.length,
      ),
      sources: Array.from(state.selectedSources).filter(
        (i) => i >= 0 && i < state.result!.source_candidates.length,
      ),
    }
  }

  const copyAbsorptionPacket = async () => {
    if (!state.result) return
    const safe = getSafeSelections()
    const text = buildAbsorptionPacket({
      topic: state.result.topic,
      taskIntent: state.result.task_intent || '(未指定)',
      selectedKnowledge: safe.knowledge.map((i) => {
        const d = state.result!.knowledge_delta_candidates[i]
        return `[${d.delta_type}] ${d.label}`
      }),
      selectedTriggers: safe.triggers.map((i) => {
        const t = state.result!.evolution_trigger_candidates[i]
        return `[${t.trigger_type}] ${t.label}`
      }),
      selectedSources: safe.sources.map((i) => {
        const s = state.result!.source_candidates[i]
        return s.name || s.id || '未命名'
      }),
      suggestedNextStep:
        state.result.operational_advice?.suggested_next_step !== 'no_action'
          ? state.result.operational_advice?.suggested_next_step || '无'
          : '无',
      reasonTags: state.result.controller_packet?.reason_tags || [],
      reviewerNote: state.reviewerNote,
    })
    await copyTextToClipboard(text)
    dispatch({ type: 'setCopyFlag', key: 'absorptionCopied', value: true })
    resetCopyFlag('absorptionCopied')
  }

  const copyDecisionPacket = async () => {
    if (!state.result) return
    const safe = getSafeSelections()
    const text = buildDecisionPacket({
      topic: state.result.topic,
      taskIntent: state.result.task_intent || '(未指定)',
      selectedKnowledge: safe.knowledge
        .map((i) => {
          const d = state.result!.knowledge_delta_candidates[i]
          return d ? `[${d.delta_type}] ${d.label}` : ''
        })
        .filter(Boolean),
      selectedTriggers: safe.triggers
        .map((i) => {
          const t = state.result!.evolution_trigger_candidates[i]
          return t ? `[${t.trigger_type}] ${t.label}` : ''
        })
        .filter(Boolean),
      selectedSources: safe.sources
        .map((i) => {
          const s = state.result!.source_candidates[i]
          return s ? s.name || s.id || '未命名' : ''
        })
        .filter(Boolean),
      suggestedNextStep:
        state.result.operational_advice?.suggested_next_step !== 'no_action'
          ? state.result.operational_advice?.suggested_next_step || '无'
          : '无',
      reasonTags: state.result.controller_packet?.reason_tags || [],
      reviewerNote: state.reviewerNote,
    })
    await copyTextToClipboard(text)
    dispatch({ type: 'setCopyFlag', key: 'decisionCopied', value: true })
    resetCopyFlag('decisionCopied')
  }

  const requestTaskPreview = async () => {
    if (!state.result) return
    dispatch({ type: 'startTaskPreview' })
    try {
      const safe = getSafeSelections()
      const data = await apiClient.previewTaskPacket({
        topic: state.result.topic.trim(),
        task_intent: (state.result.task_intent || '').trim() || 'manual decision preview',
        selected_knowledge_labels: safe.knowledge
          .map((i) => {
            const d = state.result!.knowledge_delta_candidates[i]
            return d ? `[${d.delta_type}] ${d.label}` : ''
          })
          .filter(Boolean),
        selected_evolution_labels: safe.triggers
          .map((i) => {
            const t = state.result!.evolution_trigger_candidates[i]
            return t ? `[${t.trigger_type}] ${t.label}` : ''
          })
          .filter(Boolean),
        selected_source_labels: safe.sources
          .map((i) => {
            const s = state.result!.source_candidates[i]
            return s ? s.name || s.id || 'Unnamed source' : ''
          })
          .filter(Boolean),
        reviewer_note: state.reviewerNote.trim() || undefined,
        explicit_non_canonical: true,
      })
      dispatch({ type: 'taskPreviewSuccess', result: data })
    } catch (e) {
      dispatch({
        type: 'taskPreviewError',
        error: e instanceof Error ? e.message : 'Task preview request failed.',
      })
    }
  }

  const copyTaskPreviewPacket = async () => {
    if (!state.taskPreviewResult) return
    await copyTextToClipboard(buildTaskPreviewPacket(state.taskPreviewResult))
    dispatch({ type: 'setCopyFlag', key: 'taskPreviewCopied', value: true })
    resetCopyFlag('taskPreviewCopied')
  }

  const copyWorkerPacket = async (lane: WorkerLane) => {
    if (!state.taskPreviewResult || !state.result) return
    const text = buildWorkerPacket(
      lane,
      state.result.topic,
      state.result.task_intent || '(未指定)',
      state.taskPreviewResult,
      state.result,
    )
    await copyTextToClipboard(text)
    dispatch({ type: 'setWorkerCopied', lane, value: true })
    resetWorkerCopied(lane)
  }

  const copyLoopPacket = async () => {
    if (!state.taskPreviewResult || !state.result) return
    await copyTextToClipboard(
      buildLoopPacket(
        state.workerLane,
        state.result.topic,
        state.result.task_intent || '(未指定)',
        state.taskPreviewResult,
        state.result,
      ),
    )
    dispatch({ type: 'setCopyFlag', key: 'loopPacketCopied', value: true })
    resetCopyFlag('loopPacketCopied')
  }

  const requestExecutionFeedbackInspect = async () => {
    if (!state.taskPreviewResult || !state.result || !state.executionFeedbackText.trim()) return
    dispatch({ type: 'startExecutionFeedback' })
    try {
      const data = await apiClient.inspectExecutionFeedback({
        topic: state.result.topic.trim(),
        task_intent: (state.result.task_intent || '').trim() || 'manual execution feedback',
        worker_lane: state.workerLane,
        task_packet_summary: state.taskPreviewResult.task_packet_summary,
        execution_feedback_text: state.executionFeedbackText.trim(),
        execution_status_hint: state.executionStatusHint,
        provider: state.provider.trim() || 'qwen',
        model: state.model.trim() || undefined,
        worker_run_id: state.workerRunId.trim() || undefined,
        worker_provider: state.workerProvider.trim() || undefined,
        worker_model: state.workerModel.trim() || undefined,
        worker_artifact_ref: state.workerArtifactRef.trim() || undefined,
      })
      dispatch({ type: 'executionFeedbackSuccess', result: data })
    } catch (e) {
      dispatch({
        type: 'executionFeedbackError',
        error: e instanceof Error ? e.message : 'Execution feedback inspect failed.',
      })
    }
  }

  const copyExecutionFeedbackPacket = async () => {
    if (!state.executionFeedbackResult || !state.taskPreviewResult) return
    await copyTextToClipboard(
      buildExecutionFeedbackPacket(
        state.executionFeedbackResult,
        state.taskPreviewResult.task_packet_summary,
      ),
    )
    dispatch({ type: 'setCopyFlag', key: 'executionFeedbackCopied', value: true })
    resetCopyFlag('executionFeedbackCopied')
  }

  return {
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
  }
}
