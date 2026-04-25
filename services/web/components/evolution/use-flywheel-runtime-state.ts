'use client'

import { useReducer } from 'react'
import type {
  FlywheelExecutionFeedbackInspectResponse,
  FlywheelInspectResponse,
  TaskPacketPreviewResponse,
} from '@/lib/api-client'
import type { WorkerLane } from './flywheel-packet-builders'

export type SectionKey = 'extraction' | 'knowledge' | 'triggers' | 'sources' | 'advice' | 'controller'

type CopyFlagKey =
  | 'copied'
  | 'absorptionCopied'
  | 'decisionCopied'
  | 'taskPreviewCopied'
  | 'executionFeedbackCopied'
  | 'loopPacketCopied'

export type StringFieldKey =
  | 'conversationText'
  | 'topic'
  | 'taskIntent'
  | 'provider'
  | 'model'
  | 'reviewerNote'
  | 'executionFeedbackText'
  | 'executionStatusHint'
  | 'workerRunId'
  | 'workerProvider'
  | 'workerModel'
  | 'workerArtifactRef'

export type SelectionFamily = 'knowledge' | 'triggers' | 'sources'

export type FlywheelRuntimeState = {
  conversationText: string
  topic: string
  taskIntent: string
  provider: string
  model: string
  loading: boolean
  error: string | null
  result: FlywheelInspectResponse | null
  openSections: Set<SectionKey>
  copied: boolean
  selectedKnowledge: Set<number>
  selectedTriggers: Set<number>
  selectedSources: Set<number>
  reviewerNote: string
  absorptionCopied: boolean
  decisionCopied: boolean
  taskPreviewLoading: boolean
  taskPreviewResult: TaskPacketPreviewResponse | null
  taskPreviewError: string | null
  taskPreviewCopied: boolean
  loopPacketCopied: boolean
  workerLane: WorkerLane
  workerCopiedMap: Record<WorkerLane, boolean>
  executionFeedbackText: string
  executionStatusHint: string
  executionFeedbackLoading: boolean
  executionFeedbackError: string | null
  executionFeedbackResult: FlywheelExecutionFeedbackInspectResponse | null
  executionFeedbackCopied: boolean
  workerRunId: string
  workerProvider: string
  workerModel: string
  workerArtifactRef: string
}

type Action =
  | { type: 'setStringField'; field: StringFieldKey; value: string }
  | { type: 'toggleSection'; key: SectionKey }
  | { type: 'toggleSelection'; family: SelectionFamily; index: number }
  | { type: 'startInspect' }
  | { type: 'inspectSuccess'; result: FlywheelInspectResponse }
  | { type: 'inspectError'; error: string }
  | { type: 'startTaskPreview' }
  | { type: 'taskPreviewSuccess'; result: TaskPacketPreviewResponse }
  | { type: 'taskPreviewError'; error: string }
  | { type: 'startExecutionFeedback' }
  | { type: 'executionFeedbackSuccess'; result: FlywheelExecutionFeedbackInspectResponse }
  | { type: 'executionFeedbackError'; error: string }
  | { type: 'setCopyFlag'; key: CopyFlagKey; value: boolean }
  | { type: 'setWorkerCopied'; lane: WorkerLane; value: boolean }
  | { type: 'setWorkerLane'; lane: WorkerLane }

const initialState: FlywheelRuntimeState = {
  conversationText: '',
  topic: '',
  taskIntent: '',
  provider: 'qwen',
  model: '',
  loading: false,
  error: null,
  result: null,
  openSections: new Set(),
  copied: false,
  selectedKnowledge: new Set(),
  selectedTriggers: new Set(),
  selectedSources: new Set(),
  reviewerNote: '',
  absorptionCopied: false,
  decisionCopied: false,
  taskPreviewLoading: false,
  taskPreviewResult: null,
  taskPreviewError: null,
  taskPreviewCopied: false,
  loopPacketCopied: false,
  workerLane: 'coding',
  workerCopiedMap: { coding: false, review: false, test: false },
  executionFeedbackText: '',
  executionStatusHint: 'neutral',
  executionFeedbackLoading: false,
  executionFeedbackError: null,
  executionFeedbackResult: null,
  executionFeedbackCopied: false,
  workerRunId: '',
  workerProvider: '',
  workerModel: '',
  workerArtifactRef: '',
}

function toggleIndexSet(source: Set<number>, index: number) {
  const next = new Set(source)
  if (next.has(index)) next.delete(index)
  else next.add(index)
  return next
}

function reducer(state: FlywheelRuntimeState, action: Action): FlywheelRuntimeState {
  switch (action.type) {
    case 'setStringField':
      return { ...state, [action.field]: action.value }
    case 'toggleSection':
      return {
        ...state,
        openSections: (() => {
          const next = new Set(state.openSections)
          if (next.has(action.key)) next.delete(action.key)
          else next.add(action.key)
          return next
        })(),
      }
    case 'toggleSelection':
      if (action.family === 'knowledge') {
        return { ...state, selectedKnowledge: toggleIndexSet(state.selectedKnowledge, action.index) }
      }
      if (action.family === 'triggers') {
        return { ...state, selectedTriggers: toggleIndexSet(state.selectedTriggers, action.index) }
      }
      return { ...state, selectedSources: toggleIndexSet(state.selectedSources, action.index) }
    case 'startInspect':
      return {
        ...state,
        loading: true,
        error: null,
        result: null,
        openSections: new Set(),
        copied: false,
        selectedKnowledge: new Set(),
        selectedTriggers: new Set(),
        selectedSources: new Set(),
        reviewerNote: '',
        absorptionCopied: false,
        decisionCopied: false,
        taskPreviewLoading: false,
        taskPreviewResult: null,
        taskPreviewError: null,
        taskPreviewCopied: false,
        loopPacketCopied: false,
        workerLane: 'coding',
        workerCopiedMap: { coding: false, review: false, test: false },
        executionFeedbackText: '',
        executionStatusHint: 'neutral',
        executionFeedbackLoading: false,
        executionFeedbackError: null,
        executionFeedbackResult: null,
        executionFeedbackCopied: false,
        workerRunId: '',
        workerProvider: '',
        workerModel: '',
        workerArtifactRef: '',
      }
    case 'inspectSuccess':
      return {
        ...state,
        loading: false,
        result: action.result,
        openSections: new Set<SectionKey>(['extraction', 'knowledge', 'sources']),
      }
    case 'inspectError':
      return { ...state, loading: false, error: action.error }
    case 'startTaskPreview':
      return {
        ...state,
        taskPreviewLoading: true,
        taskPreviewError: null,
        taskPreviewResult: null,
        taskPreviewCopied: false,
      }
    case 'taskPreviewSuccess':
      return {
        ...state,
        taskPreviewLoading: false,
        taskPreviewResult: action.result,
      }
    case 'taskPreviewError':
      return {
        ...state,
        taskPreviewLoading: false,
        taskPreviewError: action.error,
      }
    case 'startExecutionFeedback':
      return {
        ...state,
        executionFeedbackLoading: true,
        executionFeedbackError: null,
        executionFeedbackResult: null,
        executionFeedbackCopied: false,
      }
    case 'executionFeedbackSuccess':
      return {
        ...state,
        executionFeedbackLoading: false,
        executionFeedbackResult: action.result,
      }
    case 'executionFeedbackError':
      return {
        ...state,
        executionFeedbackLoading: false,
        executionFeedbackError: action.error,
      }
    case 'setCopyFlag':
      return { ...state, [action.key]: action.value }
    case 'setWorkerCopied':
      return {
        ...state,
        workerCopiedMap: { ...state.workerCopiedMap, [action.lane]: action.value },
      }
    case 'setWorkerLane':
      return { ...state, workerLane: action.lane }
    default:
      return state
  }
}

export function useFlywheelRuntimeState() {
  const [state, dispatch] = useReducer(reducer, initialState)
  return { state, dispatch }
}
