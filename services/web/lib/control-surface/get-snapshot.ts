import { ControlSnapshot } from './types'
import { STATIC_SNAPSHOT } from './static-snapshot'
import { getOpsStateSnapshot, readObservedState, readRuntimeState, readPmRunDigest, mapPmDigestStatus } from './ops-state-adapter'

export async function getSnapshot(): Promise<ControlSnapshot> {
  const opsSnapshot = getOpsStateSnapshot()
  const observed = readObservedState()
  const runtime = readRuntimeState()
  const pmRunDigest = readPmRunDigest()

  // 1. Determine the base snapshot (Ops State or Static Fallback)
  let snapshot: ControlSnapshot
  if (opsSnapshot) {
    // Clone to avoid mutating the source state when overlaying telemetry
    snapshot = { ...opsSnapshot }
  } else {
    // Clone to avoid mutating the shared static constant
    snapshot = { ...STATIC_SNAPSHOT }
  }

  // 2. Overlay fresh observed/runtime telemetry independently.
  // This ensures telemetry survives even if current_state.json is missing or invalid.
  if (observed) {
    snapshot.observed = observed
  }

  if (runtime) {
    snapshot.runtime = runtime
  }

  if (pmRunDigest) {
    snapshot.pmRunDigest = pmRunDigest

    // Ensure PM digest is visible in automation health if we fell back to static snapshot
    // or if the ops state didn't already include it.
    if (!snapshot.automationHealth) {
      snapshot.automationHealth = []
    } else {
      // PR24 FIX: Clone the collection to avoid mutating shared source state (STATIC_SNAPSHOT or ops-state arrays)
      snapshot.automationHealth = [...snapshot.automationHealth]
    }

    if (!snapshot.automationHealth.some(item => item.id === 'ike-pm-mainline-watch')) {
      snapshot.automationHealth.unshift({
        id: 'ike-pm-mainline-watch',
        name: 'IKE PM MAINLINE WATCH',
        status: mapPmDigestStatus(pmRunDigest),
        description: `${pmRunDigest.decision}: ${pmRunDigest.reason}`
      })
    }
  }

  return snapshot
}
