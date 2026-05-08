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
  reviewState: {
    prReviewGate: string
    promotion: string
    termination: string
    monitor: string
  }
  nextActions: string[]
}
