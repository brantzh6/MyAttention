export type SnapshotSourceKind = 'static_estimate' | 'manual_curated' | 'file_derived' | 'live_backend' | 'planned'

export interface SnapshotProvenance {
  sourceKind: SnapshotSourceKind
  sourceLabel: string
  freshnessLabel: string
  truthStatus: 'non_canonical' | 'derived' | 'live_runtime'
  caveat: string
}

export type ScoreStatus = 'estimated' | 'accepted' | 'blocked' | 'unknown'

export interface MainlineTask {
  id: string
  title: string
  status: ScoreStatus
  description: string
}

export interface CapabilityGap {
  id: string
  title: string
  maturity: string
  gap: string
  status: ScoreStatus
}

export interface ActiveLane {
  id: string
  name: string
  owner: string
  status: string
}

export interface AutomationHealth {
  id: string
  name: string
  status: 'healthy' | 'caveat' | 'unhealthy'
  description: string
}

export interface PmRunDigest {
  runId: string
  checkedAt: string
  cronJobId: string
  decision: string
  status: 'ok' | 'warning' | 'error'
  reason: string
  lastRealProgressAt?: string
  stalenessMinutes?: number
  controllerActionNeeded: boolean
  triggerPath?: string
  bridgeResultPath?: string
  evidence: string[]
  nextExpectedRun?: string
}

export interface NextAction {
  lane: string
  action: string
}

export interface OperationsSplit {
  codeTruth: string
  runtimeTruth: string
  runtimeDependency: string
}

export interface FlywheelLoopStatus {
  statusLabel: string
  acceptedEvidence: string[]
  reusableCommand: string
  latestRealPacket: string
  nextGate: string
  truthBoundary: string
}

export interface ObservedState {
  observedAt: string
  reconcilerVersion: string
  controllerAttentionRequired: boolean
  attentionEvidence: string[]
  reachabilityConflict: boolean
}

export interface RuntimeProbeService {
  id: string
  status: 'healthy' | 'unhealthy' | 'degraded'
  url?: string
  details?: string
}

export interface RuntimeProbeState {
  probedAt: string
  overallReachability: string
  services: RuntimeProbeService[]
}

export interface ControlBlocker {
  title: string
  status: string
  summary: string
  whyItMatters: string
  riskLevel: string
  blastRadius: string
  completedSteps: string[]
  proposedSteps: string[]
}

export interface StrategicPlan {
  now: string
  next: string
  later: string
}

export interface QualityGate {
  localReviewStatus: string
  cloudReviewStatus: string
  exceptionActive: boolean
  exceptionScope: string[]
  mergeAuthorized: boolean
}

export interface ControlSurfaceSummary {
  overallStatus: string
  mainlineGoal: string
  currentPhase: string
  currentBlocker?: ControlBlocker
  plan?: StrategicPlan
  qualityGate?: QualityGate
}

export interface ControlSnapshot {
  provenance: SnapshotProvenance
  mainline: {
    name: string
    objective: string
    latestAcceptedEvidence: string[]
  }
  tasks: MainlineTask[]
  phase: {
    current: string
    nextGate: string
  }
  capabilities: CapabilityGap[]
  lanes: ActiveLane[]
  automationHealth?: AutomationHealth[]
  pmRunDigest?: PmRunDigest
  reviewState: {
    prReviewGate: string
    promotion: string
    termination: string
    monitor: string
  }
  operationsSplit?: OperationsSplit
  flywheelLoop?: FlywheelLoopStatus
  controlSummary?: ControlSurfaceSummary
  nextActions: NextAction[]
  observed?: ObservedState
  runtime?: RuntimeProbeState
}
