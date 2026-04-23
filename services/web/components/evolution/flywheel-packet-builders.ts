import type {
  FlywheelExecutionFeedbackInspectResponse,
  FlywheelInspectResponse,
  TaskPacketPreviewResponse,
} from '@/lib/api-client'

export type WorkerLane = 'coding' | 'review' | 'test'

export function buildReviewPacket(r: FlywheelInspectResponse): string {
  const provider = r.provider || '(未指定)'
  const model = r.model || '(默认)'
  const reviewMode = r.controller_packet?.review_mode || '(未知)'
  const truthStatus = r.controller_packet?.truth_status || '(未知)'
  const reasonTags = r.controller_packet?.reason_tags || []
  const knowledgeDeltas = r.knowledge_delta_candidates || []
  const evolutionTriggers = r.evolution_trigger_candidates || []
  const sourceCandidates = r.source_candidates || []
  const lines: string[] = []
  lines.push('=== Flywheel 手动审查包 (Inspect-Only) ===')
  lines.push('')
  lines.push(`主题: ${r.topic}`)
  lines.push(`任务意图: ${r.task_intent || '(未指定)'}`)
  lines.push(`意图分段: ${r.segment_intent || '(未识别)'}`)
  lines.push('')

  if (r.operational_advice?.suggested_next_step && r.operational_advice.suggested_next_step !== 'no_action') {
    lines.push(`建议下一步: ${r.operational_advice.suggested_next_step}`)
  } else {
    lines.push('建议下一步: 无')
  }
  lines.push('')

  if (reasonTags.length) {
    lines.push('原因标签:')
    reasonTags.forEach((t) => lines.push(`  - ${t}`))
    lines.push('')
  }

  if (knowledgeDeltas.length) {
    lines.push('知识增量标签:')
    knowledgeDeltas.forEach((d) => lines.push(`  - [${d.delta_type}] ${d.label}`))
    lines.push('')
  }

  if (evolutionTriggers.length) {
    lines.push('进化触发标签:')
    evolutionTriggers.forEach((t) => lines.push(`  - [${t.trigger_type}] ${t.label}`))
    lines.push('')
  }

  if (sourceCandidates.length) {
    lines.push('来源候选标识:')
    sourceCandidates.forEach((s) => {
      const parts = [s.name || s.id || '未命名']
      if (s.type) parts.push(`(${s.type})`)
      if (s.url) parts.push(s.url)
      lines.push(`  - ${parts.join(' ')}`)
    })
    lines.push('')
  }

  lines.push(`Provider: ${provider} | Model: ${model}`)
  lines.push(`审查模式: ${reviewMode}`)
  lines.push(`事实状态: ${truthStatus}`)
  lines.push('')
  lines.push('--- 此包仅供手动审查参考，非规范事实，未经持久化 ---')
  return lines.join('\n')
}

export function buildDecisionPacket(params: {
  topic: string
  taskIntent: string
  selectedKnowledge: string[]
  selectedTriggers: string[]
  selectedSources: string[]
  suggestedNextStep: string
  reasonTags: string[]
  reviewerNote: string
}): string {
  const lines: string[] = []
  lines.push('=== Flywheel 手动决策桥接包 (Decision Bridge) ===')
  lines.push('')
  lines.push(`主题: ${params.topic}`)
  lines.push(`任务意图: ${params.taskIntent}`)
  lines.push('')

  if (params.selectedKnowledge.length || params.selectedTriggers.length || params.selectedSources.length) {
    lines.push('--- 已选候选项 ---')
    if (params.selectedKnowledge.length) {
      lines.push('')
      lines.push('[知识增量]')
      params.selectedKnowledge.forEach((l) => lines.push(`  - ${l}`))
    }
    if (params.selectedTriggers.length) {
      lines.push('')
      lines.push('[进化触发]')
      params.selectedTriggers.forEach((l) => lines.push(`  - ${l}`))
    }
    if (params.selectedSources.length) {
      lines.push('')
      lines.push('[来源]')
      params.selectedSources.forEach((l) => lines.push(`  - ${l}`))
    }
    lines.push('')
  }

  lines.push(`建议下一步: ${params.suggestedNextStep || '无'}`)

  if (params.reasonTags.length) {
    lines.push('')
    lines.push('原因标签:')
    params.reasonTags.forEach((t) => lines.push(`  - ${t}`))
  }

  if (params.reviewerNote.trim()) {
    lines.push('')
    lines.push('审查备注:')
    lines.push(`  ${params.reviewerNote.trim()}`)
  }

  lines.push('')
  lines.push('--- 此包仅用于手动决策/对齐讨论，非规范事实，未经持久化，不构成自动执行指令 ---')
  return lines.join('\n')
}

export function buildAbsorptionPacket(params: {
  topic: string
  taskIntent: string
  selectedKnowledge: string[]
  selectedTriggers: string[]
  selectedSources: string[]
  suggestedNextStep: string
  reasonTags: string[]
  reviewerNote: string
}): string {
  const lines: string[] = []
  lines.push('=== Flywheel 手动吸收包 (Manual Absorption) ===')
  lines.push('')
  lines.push(`主题: ${params.topic}`)
  lines.push(`任务意图: ${params.taskIntent}`)
  lines.push('')

  lines.push('--- 选中候选项 (按族分组) ---')

  if (params.selectedKnowledge.length) {
    lines.push('')
    lines.push('[知识增量]')
    params.selectedKnowledge.forEach((label) => lines.push(`  - ${label}`))
  }

  if (params.selectedTriggers.length) {
    lines.push('')
    lines.push('[进化触发]')
    params.selectedTriggers.forEach((label) => lines.push(`  - ${label}`))
  }

  if (params.selectedSources.length) {
    lines.push('')
    lines.push('[来源]')
    params.selectedSources.forEach((label) => lines.push(`  - ${label}`))
  }

  if (!params.selectedKnowledge.length && !params.selectedTriggers.length && !params.selectedSources.length) {
    lines.push('  (无选中项)')
  }

  lines.push('')
  lines.push(`建议下一步: ${params.suggestedNextStep || '无'}`)

  if (params.reasonTags.length) {
    lines.push('')
    lines.push('原因标签:')
    params.reasonTags.forEach((t) => lines.push(`  - ${t}`))
  }

  if (params.reviewerNote.trim()) {
    lines.push('')
    lines.push('审查备注:')
    lines.push(`  ${params.reviewerNote.trim()}`)
  }

  lines.push('')
  lines.push('--- 非规范 / 仅手动吸收，未经持久化，不构成规范事实 ---')
  return lines.join('\n')
}

export function buildWorkerPacket(
  lane: WorkerLane,
  topic: string,
  taskIntent: string,
  preview: TaskPacketPreviewResponse,
  result: FlywheelInspectResponse,
): string {
  const heading = lane === 'coding'
    ? '=== Worker Packet: Coding ==='
    : lane === 'review'
    ? '=== Worker Packet: Review ==='
    : '=== Worker Packet: Test ==='

  const instruction = lane === 'coding'
    ? 'INSTRUCTION: 根据此 packet 执行编码实现。严格遵循 suggested_next_step，仅在 selected_label_groups 标注的范围内改动。'
    : lane === 'review'
    ? 'INSTRUCTION: 根据此 packet 执行代码/设计审查。重点检查 trust_boundary 标注的区域，确认变更与 topic 意图对齐。'
    : 'INSTRUCTION: 根据此 packet 编写/执行测试。覆盖 suggested_next_step 涉及的逻辑，验证 selected_label_groups 标注的行为。'

  const lines: string[] = []
  lines.push(heading)
  lines.push('')
  lines.push(`topic: ${topic}`)
  lines.push(`task_intent: ${taskIntent || '(未指定)'}`)
  lines.push(`suggested_lane: ${preview.suggested_lane}`)
  lines.push(`suggested_next_step: ${preview.suggested_next_step}`)
  lines.push('')
  lines.push(instruction)
  lines.push('')

  if (preview.selected_label_groups.length) {
    lines.push('[selected_label_groups]')
    preview.selected_label_groups.forEach((g) => {
      lines.push(`  ${g.label_type} (${g.count}):`)
      g.labels.forEach((l) => lines.push(`    - ${l}`))
    })
    lines.push('')
  }

  if (preview.truth_boundary.length) {
    lines.push('[trust_boundary]')
    preview.truth_boundary.forEach((b) => lines.push(`  - ${b}`))
    lines.push('')
  }

  if (preview.controller_packet) {
    const cp = preview.controller_packet
    lines.push(`[controller] review_mode=${cp.review_mode} truth_status=${cp.truth_status}`)
    if (cp.reason_tags.length) {
      cp.reason_tags.forEach((t) => lines.push(`  - reason: ${t}`))
    }
    lines.push('')
  }

  const trustNote = lane === 'coding'
    ? '此包为手动生成的工作指令，非自动执行。编码前请确认 trust_boundary 内约束。'
    : lane === 'review'
    ? '此包为手动生成的审查指令，非规范事实。审查请独立验证 trust_boundary 内声明。'
    : '此包为手动生成的测试指令，非规范事实。测试范围以 selected_label_groups 为界。'
  lines.push(`--- ${trustNote} ---`)
  return lines.join('\n')
}

export function buildExecutionFeedbackPacket(
  feedback: FlywheelExecutionFeedbackInspectResponse,
  packetSummary: string,
): string {
  const lines: string[] = []
  lines.push('=== Flywheel Execution Feedback Packet (Inspect-Only) ===')
  lines.push('')
  lines.push(`topic: ${feedback.topic}`)
  lines.push(`task_intent: ${feedback.task_intent || '(未指定)'}`)
  lines.push(`worker_lane: ${feedback.worker_lane}`)
  lines.push(`execution_status_hint: ${feedback.execution_status_hint}`)
  lines.push(`feedback_intent: ${feedback.feedback_intent}`)
  lines.push(`task_packet_summary: ${packetSummary}`)
  lines.push(`feedback_summary: ${feedback.feedback_summary || '(无)'}`)
  lines.push('')

  if (feedback.knowledge_delta_candidates.length) {
    lines.push('[knowledge_delta_candidates]')
    feedback.knowledge_delta_candidates.forEach((d) => {
      lines.push(`  - [${d.delta_type}] ${d.label}: ${d.content}`)
    })
    lines.push('')
  }

  if (feedback.evolution_trigger_candidates.length) {
    lines.push('[evolution_trigger_candidates]')
    feedback.evolution_trigger_candidates.forEach((t) => {
      lines.push(`  - [${t.trigger_type}] ${t.label}: ${t.rationale}`)
    })
    lines.push('')
  }

  lines.push(`suggested_next_step: ${feedback.operational_advice?.suggested_next_step || 'no_action'}`)
  if (feedback.controller_packet?.reason_tags?.length) {
    lines.push('reason_tags:')
    feedback.controller_packet.reason_tags.forEach((tag) => lines.push(`  - ${tag}`))
  }
  lines.push('')
  lines.push('--- 此包为执行结果的 inspect-only 反思压缩，非规范事实，未自动吸收，未自动重新派发 ---')
  return lines.join('\n')
}

export function buildTaskPreviewPacket(preview: TaskPacketPreviewResponse): string {
  const lines: string[] = []
  lines.push('=== Task Packet Preview (Backend, Inspect-Only) ===')
  lines.push('')
  lines.push(`摘要: ${preview.task_packet_summary}`)
  lines.push(`意图: ${preview.packet_intent}`)
  lines.push(`建议处理通道: ${preview.suggested_lane}`)
  lines.push(`建议下一步: ${preview.suggested_next_step}`)
  lines.push('')

  if (preview.selected_label_groups.length) {
    lines.push('--- 已选标签组 ---')
    preview.selected_label_groups.forEach((group) => {
      lines.push(`[${group.label_type}] (${group.count})`)
      group.labels.forEach((label) => lines.push(`  - ${label}`))
    })
    lines.push('')
  }

  if (preview.controller_packet) {
    lines.push(`审查模式: ${preview.controller_packet.review_mode}`)
    lines.push(`事实状态: ${preview.controller_packet.truth_status}`)
    lines.push(`建议范围: ${preview.controller_packet.advisory_scope}`)
    if (preview.controller_packet.reason_tags.length) {
      lines.push('原因标签:')
      preview.controller_packet.reason_tags.forEach((tag) => lines.push(`  - ${tag}`))
    }
  }

  lines.push('')
  lines.push('--- 此包为后端生成，仅供手动审查参考，非规范事实，未经持久化 ---')
  return lines.join('\n')
}
