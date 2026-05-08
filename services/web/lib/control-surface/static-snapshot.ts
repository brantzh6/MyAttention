import { ControlSnapshot } from './types'

export const STATIC_SNAPSHOT: ControlSnapshot = {
  provenance: {
    sourceKind: 'manual_curated',
    sourceLabel: 'Controller curation (Anchor P0 + smoke absorption)',
    freshnessLabel: '2026-05-08',
    truthStatus: 'non_canonical',
    caveat: 'This is a controller-curated static project anchor. It is not live backend truth.'
  },
  mainline: {
    name: 'flywheel_v1_ai_entry_control_surface',
    objective: 'First usable IKE evolution loop with AI conversation entry and visible project control',
    latestAcceptedEvidence: [
      'PR #10: chat-to-flywheel handoff bridge accepted',
      'PR #11: Flywheel V1 browser smoke packet accepted',
      'PR #12: /control project control surface accepted',
      '9977bd2: real chat handoff browser smoke evidence recorded',
      'full UI loop smoke: inspect -> preview -> execution feedback passed',
      'Loop Closure Summary: completed loop now has a controller-readable result surface'
    ]
  },
  tasks: [
    {
      id: 'evolution_flywheel_v1',
      title: 'Evolution Flywheel V1',
      status: 'accepted',
      description: 'First usable inspect-only AI-assisted evolution loop; route chain and chat handoff smoke are now evidenced.'
    },
    {
      id: 'ai_conversation_entry',
      title: 'AI Conversation Entry',
      status: 'accepted',
      description: 'AI conversation can hand transient, non-canonical input into the flywheel inspect surface.'
    },
    {
      id: 'project_control_surface',
      title: 'Project Control Surface',
      status: 'accepted',
      description: 'Visible project/progress/capability anchor for controller, user, and delegates.'
    }
  ],
  phase: {
    current: 'Flywheel V1 first evidence baseline accepted',
    nextGate: 'Run a real controller rehearsal through the verified loop'
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
      gap: 'Verified inspect -> preview -> execution-feedback UI loop now has a controller-readable closure summary; next gap is live rehearsal quality',
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
    { id: 'antigravity', name: 'Antigravity UI', owner: 'Claude / Qwen / AI Delegate', status: 'P0 accepted; available for next UI packet' },
    { id: 'backend-cc', name: 'Backend/CC', owner: 'Claude / OpenClaw', status: 'Standby for bounded flywheel/UI smoke hardening' },
    { id: 'code-review', name: 'Code Review', owner: 'Delegated Model', status: 'Available' },
    { id: 'test-exec', name: 'Test Execution', owner: 'Test Runner', status: 'Available' },
    { id: 'review-gate', name: 'Review Gate', owner: 'Local reviewer / Codex when needed', status: 'Local review first; GitHub/Codex only for promotion-ready versions' }
  ],
  reviewState: {
    prReviewGate: 'Local validation and local review are default; GitHub/Codex is promotion evidence only',
    promotion: 'Controller owns promotion',
    termination: 'Review gates terminate after absorbed findings when no unresolved thread remains',
    monitor: 'No standing review monitor unless an active GitHub/Codex promotion review is pending'
  },
  nextActions: [
    'Run a real controller rehearsal through the verified Flywheel V1 loop',
    'Keep /control snapshot updated after accepted evidence changes',
    'Use local review for small smoke/docs/snapshot changes',
    'Use GitHub/Codex review only for promotion-ready GitHub versions',
    'Do not reopen Codex review loops for local smoke evidence'
  ]
}
