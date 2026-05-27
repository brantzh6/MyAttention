import { ControlSnapshot } from './types'

export const STATIC_SNAPSHOT: ControlSnapshot = {
  provenance: {
    sourceKind: 'manual_curated',
    sourceLabel: 'Controller curation (real worker execution-feedback inspect absorption)',
    freshnessLabel: '2026-05-18',
    truthStatus: 'non_canonical',
    caveat: 'This is a controller-curated static project anchor. It is not live backend truth.'
  },
  mainline: {
    name: 'flywheel_v1_ai_entry_control_surface',
    objective: 'First usable IKE evolution loop with AI conversation entry and visible project control',
    latestAcceptedEvidence: [
      'flywheel browser smoke closed',
      'loop closure summary accepted',
      'runtime operator loop established',
      'flywheel preview now emits copy-ready delegate handoff markdown',
      'first bounded handoff UI packet accepted after local review',
      'chat handoff provenance now enters typed Flywheel reviewer note',
      'chat-to-Flywheel bridge browser smoke partially passed',
      'typed preview request smoke preserves chat provenance and explicit non-canonical flag',
      'execution-feedback closure smoke validates the first inspect-only loop',
      'first real bounded delegate packet accepted: reusable Flywheel smoke npm commands',
      '/control now shows Flywheel loop status and next product-facing gate',
      'worker bridge and execution-feedback labels cleaned for real handoff use',
      'Flywheel inspect entry labels cleaned for real product use',
      'copy-ready delegate handoff packet export accepted after local L1 review',
      'first real bounded smoke worker result validated Copy Handoff Packet clipboard export',
      'execution-feedback return packet is now copy-ready for controller absorption',
      'runtime operator restored API readiness on port 8000; watchdog remains non-blocking P2',
      'live task-packet preview route validation accepted after runtime repair',
      'chat-origin guided path accepted after build and full browser smoke',
      'runtime cleanup removed stale May 13 Next/smoke Node processes',
      'manual candidate-selection filter accepted after local review and full browser smoke',
      'post-preview controller next action panel accepted after local review and full browser smoke',
      'ASCII-safe copied packet builders accepted after local review and full browser smoke',
      'real delegated worker result consumed through execution-feedback inspect after local L1 review',
      'AI-entry next packet selected and dirty-tree containment accepted before implementation'
    ]
  },
  tasks: [
    {
      id: 'evolution_flywheel_v1',
      title: 'Evolution Flywheel V1',
      status: 'accepted',
      description: 'Chat handoff, typed preview, manual candidate filtering, explicit post-preview next action, ASCII-safe copied packets, worker bridge, execution feedback, and one real worker-result feedback loop are reviewed.'
    },
    {
      id: 'ai_conversation_entry',
      title: 'AI Conversation Entry',
      status: 'accepted',
      description: 'Accepted `/chat -> /evolution` handoff now carries provenance into reviewer note; next selected packet is AI Entry Task Packet Composer P0, blocked on dirty-tree package boundary.'
    },
    {
      id: 'project_control_surface',
      title: 'Project Control Surface',
      status: 'accepted',
      description: '`/control` static anchor accepted. Current snapshot now tracks delegate-readiness state and automation caveats.'
    }
  ],
  phase: {
    current: 'flywheel_v1_ai_entry_control_surface (Mainline)',
    nextGate: 'Stage/park the scoped Flywheel latest feedback-loop package before AI Entry Composer implementation'
  },
  capabilities: [
    {
      id: 'info-brain',
      title: 'Information Brain',
      maturity: 'Usable',
      gap: 'Source-plan active surface too noisy without manual grooming',
      status: 'accepted'
    },
    {
      id: 'knowledge-brain',
      title: 'Knowledge Brain',
      maturity: 'Prototype',
      gap: 'Entity resolution across distinct source families is weak',
      status: 'estimated'
    },
    {
      id: 'evolution-brain',
      title: 'Evolution Brain',
      maturity: 'Prototype+',
      gap: 'Forward/return packets, live preview route, chat-origin guided path, manual candidate filtering, post-preview next action, ASCII-safe copied packets, and real worker-result feedback are accepted; active gate is dirty-tree scoped packaging before AI-entry implementation',
      status: 'accepted'
    },
    {
      id: 'world-model',
      title: 'World Model',
      maturity: 'Concept',
      gap: 'No persistent background context beyond chat/doc embeddings',
      status: 'unknown'
    },
    {
      id: 'thinking-methods',
      title: 'Thinking Methods / Method Arsenal',
      maturity: 'Concept',
      gap: 'Methodology application requires explicit human prompting',
      status: 'estimated'
    }
  ],
  lanes: [
    { id: 'controller', name: 'Controller', owner: 'User / GPT / Codex', status: 'Active (Scopes, accepts, promotes)' },
    { id: 'backend-coding', name: 'Backend Coding', owner: 'Claude / OpenClaw', status: 'Ready for next bounded Flywheel V1 packet' },
    { id: 'code-review', name: 'Code Review', owner: 'Delegated Model', status: 'Local L1 first; GitHub/Codex for promotion-ready PRs' },
    { id: 'runtime-operator', name: 'Runtime Operator', owner: 'Claude Code', status: 'Active through bounded packets only' },
    { id: 'runtime-review', name: 'Runtime Review', owner: 'Controller / Human', status: 'Reviews raw runtime reports before absorption' },
    { id: 'test-agent', name: 'Test Agent', owner: 'Test Runner', status: 'Deterministic smoke helper accepted; free-form selector smoke remains discouraged' },
    { id: 'gemini-ui', name: 'Gemini UI Delegate', owner: 'Gemini CLI', status: 'Active (Current UI implementation branch)' }
  ],
  automationHealth: [
    {
      id: 'mainline-stall-watch',
      name: 'mainline-stall-watch',
      status: 'caveat',
      description: 'ACTIVE 4-hour thread heartbeat. Wake-up only; it does not run tools, create packets, operate runtime, or make implementation decisions.'
    },
    {
      id: 'mainline-stall-watch-local-executor',
      name: 'mainline-stall-watch-local-executor',
      status: 'caveat',
      description: 'ACTIVE 2-hour local fallback. Progress detection is git-first plus explicit non-automation artifacts; workspace-wide mtime scans are forbidden.'
    }
  ],
  reviewState: {
    prReviewGate: 'Local validation and local review are default; GitHub/Codex is promotion evidence only',
    promotion: 'Controller owns promotion',
    termination: 'Review gates terminate after absorbed findings when no unresolved thread remains',
    monitor: 'No standing review monitor unless an active GitHub/Codex promotion review is pending'
  },
  operationsSplit: {
    codeTruth: 'Static branch truth; validates compilation, types, and logic independent of external services.',
    runtimeTruth: 'Live execution state; inherently bound to environment, tokens, and active connections.',
    runtimeDependency: 'Separate signal; failures here are operational availability issues, not code regressions.'
  },
  flywheelLoop: {
    statusLabel: 'Inspect-only loop accepted',
    acceptedEvidence: [
      'Browser smoke passed',
      'L1 review completed',
      'Loop closure summary accepted'
    ],
    reusableCommand: 'npm run smoke:flywheel-loop',
    latestRealPacket: 'Real worker result consumed through execution-feedback inspect after local review',
    nextGate: 'Accept staging conditions for flywheel_latest_feedback_loop_closure_2026-05-18, then implement AI Entry Composer',
    truthBoundary: 'Inspect-only, non-canonical, no automatic promotion'
  },
  nextActions: [
    { lane: 'controller', action: 'Resolve staging conditions for flywheel_latest_feedback_loop_closure_2026-05-18' },
    { lane: 'AI entry', action: 'Dispatch AI Entry Task Packet Composer P0 after dirty-tree package boundary is accepted' },
    { lane: 'flywheel/backend', action: 'Keep preview and feedback inspect-only; do not canonicalize chat input' },
    { lane: 'runtime operator', action: 'Keep dev/smoke servers bounded and stopped after validation' },
    { lane: 'Gemini UI delegate', action: 'Control surface P1 accepted-with-changes; next UI work should sync live mainline state only through a new bounded packet' },
    { lane: 'test adapter repair', action: 'Repair test adapter dispatch for partial failures' }
  ]
}
