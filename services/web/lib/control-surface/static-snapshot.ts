import { ControlSnapshot } from './types'

export const STATIC_SNAPSHOT: ControlSnapshot = {
  provenance: {
    sourceKind: 'manual_curated',
    sourceLabel: 'Controller curation (Anchor P0)',
    freshnessLabel: '2026-05-06',
    truthStatus: 'non_canonical',
    caveat: 'This is a controller-curated static project anchor. It is not live backend truth.'
  },
  mainline: {
    name: 'flywheel_v1_ai_entry_control_surface',
    objective: 'First usable IKE evolution loop with AI conversation entry and visible project control',
    latestAcceptedEvidence: [
      'PR #2 merged at acf922c',
      'PR #4 merged at 29d0443',
      'source-intelligence GitHub signal relation hints'
    ]
  },
  tasks: [
    {
      id: 'evolution_flywheel_v1',
      title: 'Evolution Flywheel V1',
      status: 'estimated',
      description: 'First usable inspect-only AI-assisted evolution loop.'
    },
    {
      id: 'ai_conversation_entry',
      title: 'AI Conversation Entry',
      status: 'estimated',
      description: 'AI conversation as the entry into typed candidates, controller packets, and review-gated next actions.'
    },
    {
      id: 'project_control_surface',
      title: 'Project Control Surface',
      status: 'estimated',
      description: 'Visible project/progress/capability anchor for controller, user, and delegates.'
    }
  ],
  phase: {
    current: 'Project Control Surface Anchor P0 Implementation',
    nextGate: 'Controller absorption of Antigravity UI implementation and PR promotion'
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
      maturity: 'Prototype',
      gap: 'Lacks automated loop transition and worker invocation',
      status: 'estimated'
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
    { id: 'antigravity', name: 'Antigravity UI', owner: 'Claude / Qwen / AI Delegate', status: 'Active (Implements UI)' },
    { id: 'backend-cc', name: 'Backend/CC', owner: 'Claude / OpenClaw', status: 'Standby (Assists only if adapter/build needs fix)' },
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
    'Absorb control-surface UI on a clean branch',
    'Run UI build',
    'Run local review for small UI changes',
    'Open bounded PR only when ready to publish',
    'Controller decides promotion'
  ]
}
