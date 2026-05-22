import type {
  FlywheelExecutionFeedbackInspectResponse,
  FlywheelInspectResponse,
  TaskPacketPreviewResponse,
} from '@/lib/api-client'

export type WorkerLane = 'coding' | 'review' | 'test'

export function buildReviewPacket(r: FlywheelInspectResponse): string {
  const provider = r.provider || '(none)'
  const model = r.model || '(default)'
  const reviewMode = r.controller_packet?.review_mode || '(unknown)'
  const truthStatus = r.controller_packet?.truth_status || '(unknown)'
  const reasonTags = r.controller_packet?.reason_tags || []
  const knowledgeDeltas = r.knowledge_delta_candidates || []
  const evolutionTriggers = r.evolution_trigger_candidates || []
  const sourceCandidates = r.source_candidates || []
  const lines: string[] = []
  lines.push('=== Flywheel Manual Review Packet (Inspect-Only) ===')
  lines.push('')
  lines.push(`topic: ${r.topic}`)
  lines.push(`task_intent: ${r.task_intent || '(none)'}`)
  lines.push(`segment_intent: ${r.segment_intent || '(none)'}`)
  lines.push('')

  if (r.operational_advice?.suggested_next_step && r.operational_advice.suggested_next_step !== 'no_action') {
    lines.push(`suggested_next_step: ${r.operational_advice.suggested_next_step}`)
  } else {
    lines.push('suggested_next_step: none')
  }
  lines.push('')

  if (reasonTags.length) {
    lines.push('reason_tags:')
    reasonTags.forEach((t) => lines.push(`  - ${t}`))
    lines.push('')
  }

  if (knowledgeDeltas.length) {
    lines.push('knowledge_delta_labels:')
    knowledgeDeltas.forEach((d) => lines.push(`  - [${d.delta_type}] ${d.label}`))
    lines.push('')
  }

  if (evolutionTriggers.length) {
    lines.push('evolution_trigger_labels:')
    evolutionTriggers.forEach((t) => lines.push(`  - [${t.trigger_type}] ${t.label}`))
    lines.push('')
  }

  if (sourceCandidates.length) {
    lines.push('source_candidate_labels:')
    sourceCandidates.forEach((s) => {
      const parts = [s.name || s.id || 'unnamed']
      if (s.type) parts.push(`(${s.type})`)
      if (s.url) parts.push(s.url)
      lines.push(`  - ${parts.join(' ')}`)
    })
    lines.push('')
  }

  lines.push(`provider: ${provider} | model: ${model}`)
  lines.push(`review_mode: ${reviewMode}`)
  lines.push(`truth_status: ${truthStatus}`)
  lines.push('')
  lines.push('--- This packet is for manual review reference only, non-canonical, not persisted ---')
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
  lines.push('=== Flywheel Manual Decision Bridge Packet ===')
  lines.push('')
  lines.push(`topic: ${params.topic}`)
  lines.push(`task_intent: ${params.taskIntent}`)
  lines.push('')

  if (params.selectedKnowledge.length || params.selectedTriggers.length || params.selectedSources.length) {
    lines.push('--- Selected Candidates ---')
    if (params.selectedKnowledge.length) {
      lines.push('')
      lines.push('[knowledge_delta]')
      params.selectedKnowledge.forEach((l) => lines.push(`  - ${l}`))
    }
    if (params.selectedTriggers.length) {
      lines.push('')
      lines.push('[evolution_trigger]')
      params.selectedTriggers.forEach((l) => lines.push(`  - ${l}`))
    }
    if (params.selectedSources.length) {
      lines.push('')
      lines.push('[source]')
      params.selectedSources.forEach((l) => lines.push(`  - ${l}`))
    }
    lines.push('')
  }

  lines.push(`suggested_next_step: ${params.suggestedNextStep || 'none'}`)

  if (params.reasonTags.length) {
    lines.push('')
    lines.push('reason_tags:')
    params.reasonTags.forEach((t) => lines.push(`  - ${t}`))
  }

  if (params.reviewerNote.trim()) {
    lines.push('')
    lines.push('reviewer_note:')
    lines.push(`  ${params.reviewerNote.trim()}`)
  }

  lines.push('')
  lines.push('--- This packet is for manual decision/alignment discussion only, non-canonical, not persisted, does not constitute automatic execution instructions ---')
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
  lines.push('=== Flywheel Manual Absorption Packet ===')
  lines.push('')
  lines.push(`topic: ${params.topic}`)
  lines.push(`task_intent: ${params.taskIntent}`)
  lines.push('')

  lines.push('--- Selected Candidates (grouped by family) ---')

  if (params.selectedKnowledge.length) {
    lines.push('')
    lines.push('[knowledge_delta]')
    params.selectedKnowledge.forEach((label) => lines.push(`  - ${label}`))
  }

  if (params.selectedTriggers.length) {
    lines.push('')
    lines.push('[evolution_trigger]')
    params.selectedTriggers.forEach((label) => lines.push(`  - ${label}`))
  }

  if (params.selectedSources.length) {
    lines.push('')
    lines.push('[source]')
    params.selectedSources.forEach((label) => lines.push(`  - ${label}`))
  }

  if (!params.selectedKnowledge.length && !params.selectedTriggers.length && !params.selectedSources.length) {
    lines.push('  (none selected)')
  }

  lines.push('')
  lines.push(`suggested_next_step: ${params.suggestedNextStep || 'none'}`)

  if (params.reasonTags.length) {
    lines.push('')
    lines.push('reason_tags:')
    params.reasonTags.forEach((t) => lines.push(`  - ${t}`))
  }

  if (params.reviewerNote.trim()) {
    lines.push('')
    lines.push('reviewer_note:')
    lines.push(`  ${params.reviewerNote.trim()}`)
  }

  lines.push('')
  lines.push('--- Non-canonical / manual absorption only, not persisted, does not constitute canonical truth ---')
  return lines.join('\n')
}

export function buildWorkerPacket(
  lane: WorkerLane,
  topic: string,
  taskIntent: string,
  preview: TaskPacketPreviewResponse,
  result: FlywheelInspectResponse,
): string {
  if (preview.handoff_preview) {
    return buildExecutionHandoffPreviewPacket(preview)
  }

  const heading = lane === 'coding'
    ? '=== Worker Packet: Coding ==='
    : lane === 'review'
    ? '=== Worker Packet: Review ==='
    : '=== Worker Packet: Test ==='

  const instruction = lane === 'coding'
    ? 'INSTRUCTION: Execute coding implementation based on this packet. Strictly follow suggested_next_step, only modify within the scope marked by selected_label_groups.'
    : lane === 'review'
    ? 'INSTRUCTION: Execute code/design review based on this packet. Focus on checking areas marked by trust_boundary, confirm changes align with topic intent.'
    : 'INSTRUCTION: Write/execute tests based on this packet. Cover logic involved in suggested_next_step, verify behavior marked by selected_label_groups.'

  const lines: string[] = []
  lines.push(heading)
  lines.push('')
  lines.push(`topic: ${topic}`)
  lines.push(`task_intent: ${taskIntent || '(none)'}`)
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
    ? 'This packet is a manually generated work instruction, not automatic execution. Please confirm constraints within trust_boundary before coding.'
    : lane === 'review'
    ? 'This packet is a manually generated review instruction, non-canonical. Please independently verify declarations within trust_boundary during review.'
    : 'This packet is a manually generated test instruction, non-canonical. Test scope is bounded by selected_label_groups.'
  lines.push(`--- ${trustNote} ---`)
  return lines.join('\n')
}

export function buildExecutionHandoffPreviewPacket(preview: TaskPacketPreviewResponse): string {
  const handoff = preview.handoff_preview
  if (!handoff) return buildTaskPreviewPacket(preview)

  // If backend provided handoff_markdown, use it directly
  if (handoff.handoff_markdown) {
    return handoff.handoff_markdown
  }

  const lines: string[] = []
  lines.push('=== Flywheel Execution Handoff Preview (Inspect-Only) ===')
  lines.push('')
  lines.push(`task_id: ${handoff.task_id}`)
  lines.push(`owner_lane: ${handoff.owner_lane}`)
  lines.push(`delegation_target: ${handoff.delegation_target}`)
  lines.push(`review_gate: ${handoff.review_gate}`)
  lines.push(`truth_status: ${handoff.truth_status}`)
  lines.push(`promotion_state: ${handoff.promotion_state}`)
  lines.push('')
  // New metadata fields
  lines.push(`sdlc_stage: ${handoff.sdlc_stage}`)
  lines.push(`risk_level: ${handoff.risk_level}`)
  lines.push(`result_artifact_path: ${handoff.result_artifact_path}`)
  lines.push(`write_policy: ${handoff.write_policy}`)
  lines.push('')
  lines.push('[objective]')
  lines.push(handoff.objective)
  lines.push('')

  if (handoff.current_evidence.length) {
    lines.push('[current_evidence]')
    handoff.current_evidence.forEach((item) => lines.push(`  - ${item}`))
    lines.push('')
  }

  if (handoff.allowed_files.length) {
    lines.push('[allowed_files]')
    handoff.allowed_files.forEach((file) => lines.push(`  - ${file}`))
    lines.push('')
  }

  if (handoff.non_goals.length) {
    lines.push('[non_goals]')
    handoff.non_goals.forEach((item) => lines.push(`  - ${item}`))
    lines.push('')
  }

  if (handoff.validation_commands.length) {
    lines.push('[validation_commands]')
    handoff.validation_commands.forEach((command) => lines.push(`  - ${command}`))
    lines.push('')
  }

  if (handoff.expected_result_format.length) {
    lines.push('[expected_result_format]')
    handoff.expected_result_format.forEach((field) => lines.push(`  - ${field}`))
    lines.push('')
  }

  if (handoff.stop_conditions.length) {
    lines.push('[stop_conditions]')
    handoff.stop_conditions.forEach((condition) => lines.push(`  - ${condition}`))
    lines.push('')
  }

  lines.push('[handoff_boundary]')
  lines.push('  - inspect-only advisory preview')
  lines.push('  - does not trigger worker execution')
  lines.push('  - does not persist or promote project truth')
  lines.push('  - controller owns absorption and promotion decision')
  return lines.join('\n')
}

export function buildExecutionFeedbackPacket(
  feedback: FlywheelExecutionFeedbackInspectResponse,
  packetSummary: string,
): string {
  const lines: string[] = []
  lines.push('# Execution Feedback Packet')
  lines.push('')
  lines.push('[summary]')
  lines.push(feedback.feedback_summary || '(none)')
  lines.push('')
  lines.push(`worker_lane: ${feedback.worker_lane}`)
  lines.push(`execution_status_hint: ${feedback.execution_status_hint}`)
  lines.push('')
  lines.push('[feedback_summary]')
  lines.push(feedback.feedback_summary || '(none)')
  lines.push('')
  lines.push('[task_packet_summary]')
  lines.push(packetSummary)
  lines.push('')
  lines.push(`suggested_next_step: ${feedback.operational_advice?.suggested_next_step || 'no_action'}`)

  if (feedback.knowledge_delta_candidates.length) {
    lines.push('')
    lines.push('[knowledge_delta_candidates]')
    feedback.knowledge_delta_candidates.forEach((d) => {
      lines.push(`  - [${d.delta_type}] ${d.label}: ${d.content}`)
    })
  }

  if (feedback.evolution_trigger_candidates.length) {
    lines.push('')
    lines.push('[evolution_trigger_candidates]')
    feedback.evolution_trigger_candidates.forEach((t) => {
      lines.push(`  - [${t.trigger_type}] ${t.label}: ${t.rationale}`)
    })
  }

  if (feedback.provenance) {
    lines.push('')
    lines.push('[provenance]')
    lines.push(`  worker_run_id: ${feedback.provenance.worker_run_id || '(none)'}`)
    lines.push(`  worker_provider: ${feedback.provenance.worker_provider || '(none)'}`)
    lines.push(`  worker_model: ${feedback.provenance.worker_model || '(none)'}`)
    lines.push(`  worker_artifact_ref: ${feedback.provenance.worker_artifact_ref || '(none)'}`)
    lines.push(`  completeness_status: ${feedback.provenance.completeness_status || '(none)'}`)
  }

  if (feedback.truth_boundary?.length) {
    lines.push('')
    lines.push('[truth_boundary]')
    feedback.truth_boundary.forEach((b) => lines.push(`  - ${b}`))
  }

  if (feedback.operational_advice?.controller_notes?.length) {
    lines.push('')
    lines.push('[recommendation]')
    feedback.operational_advice.controller_notes.forEach((n) => lines.push(`  - ${n}`))
  }

  if (feedback.controller_packet?.reason_tags?.length) {
    lines.push('')
    lines.push('[reason_tags]')
    feedback.controller_packet.reason_tags.forEach((tag) => lines.push(`  - ${tag}`))
  }

  if (feedback.notes?.length) {
    lines.push('')
    lines.push('[notes]')
    feedback.notes.forEach((n) => lines.push(`  - ${n}`))
  }

  lines.push('')
  lines.push('[stop_condition]')
  lines.push('  - Execution feedback packet is copy-ready for controller absorption.')
  lines.push('  - Do not auto-absorb or auto-redispatch.')
  lines.push('')
  lines.push('[handoff_boundary]')
  lines.push('  - inspect-only advisory reflection')
  lines.push('  - non-canonical (does not establish project truth)')
  lines.push('  - not persisted')
  lines.push('  - not auto-absorbed')
  lines.push('  - not auto-redispatched')
  lines.push('  - controller owns absorption and promotion decision')
  return lines.join('\n')
}


export function buildLoopPacket(
  lane: WorkerLane,
  topic: string,
  taskIntent: string,
  preview: TaskPacketPreviewResponse,
  result: FlywheelInspectResponse,
): string {
  const lines: string[] = []
  lines.push('=== Flywheel End-to-End Loop Packet (Manual, Inspect-Only) ===')
  lines.push('')
  lines.push('[loop_context]')
  lines.push(`topic: ${topic}`)
  lines.push(`task_intent: ${taskIntent || '(none)'}`)
  lines.push(`worker_lane: ${lane}`)
  lines.push(`task_packet_summary: ${preview.task_packet_summary}`)
  lines.push(`packet_intent: ${preview.packet_intent}`)
  lines.push(`suggested_next_step: ${preview.suggested_next_step}`)
  lines.push('')
  lines.push('[forward_packet]')
  lines.push(buildWorkerPacket(lane, topic, taskIntent, preview, result))
  lines.push('')
  lines.push('[return_protocol]')
  lines.push('After the worker completes, return one bounded result packet with these fields:')
  lines.push('  - summary')
  lines.push('  - files_changed')
  lines.push('  - why_this_solution')
  lines.push('  - validation_run')
  lines.push('  - known_risks')
  lines.push('  - recommendation')
  lines.push('')
  lines.push('[required_provenance_fields_for_feedback_return]')
  lines.push('  - worker_run_id')
  lines.push('  - worker_provider')
  lines.push('  - worker_model')
  lines.push('  - worker_artifact_ref')
  lines.push('')
  lines.push('[feedback_return_instructions]')
  lines.push('1. Paste the worker result into the execution feedback surface.')
  lines.push('2. Fill the provenance fields above if available.')
  lines.push('3. Choose execution_status_hint based on the worker conclusion.')
  lines.push('4. Run inspect-only execution feedback reflection; do not auto-promote.')
  lines.push('')
  lines.push('[truth_boundary]')
  lines.push('  - this loop packet is manual and inspect-only')
  lines.push('  - it does not create canonical truth by itself')
  lines.push('  - worker provenance remains caller-provided unless verified elsewhere')
  lines.push('  - execution feedback does not auto-absorb or auto-redelegate')
  return lines.join('\n')
}

export function buildTaskPreviewPacket(preview: TaskPacketPreviewResponse): string {
  if (preview.handoff_preview) {
    return buildExecutionHandoffPreviewPacket(preview)
  }

  const lines: string[] = []
  lines.push('=== Task Packet Preview (Backend, Inspect-Only) ===')
  lines.push('')
  lines.push(`summary: ${preview.task_packet_summary}`)
  lines.push(`intent: ${preview.packet_intent}`)
  lines.push(`suggested_lane: ${preview.suggested_lane}`)
  lines.push(`suggested_next_step: ${preview.suggested_next_step}`)
  lines.push('')

  if (preview.selected_label_groups.length) {
    lines.push('--- Selected Label Groups ---')
    preview.selected_label_groups.forEach((group) => {
      lines.push(`[${group.label_type}] (${group.count})`)
      group.labels.forEach((label) => lines.push(`  - ${label}`))
    })
    lines.push('')
  }

  if (preview.controller_packet) {
    lines.push(`review_mode: ${preview.controller_packet.review_mode}`)
    lines.push(`truth_status: ${preview.controller_packet.truth_status}`)
    lines.push(`advisory_scope: ${preview.controller_packet.advisory_scope}`)
    if (preview.controller_packet.reason_tags.length) {
      lines.push('reason_tags:')
      preview.controller_packet.reason_tags.forEach((tag) => lines.push(`  - ${tag}`))
    }
  }

  lines.push('')
  lines.push('--- This packet is backend-generated, for manual review reference only, non-canonical, not persisted ---')
  return lines.join('\n')
}
