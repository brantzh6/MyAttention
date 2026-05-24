import { ControlSnapshot } from './types'
import { STATIC_SNAPSHOT } from './static-snapshot'
import { getOpsStateSnapshot } from './ops-state-adapter'

export async function getSnapshot(): Promise<ControlSnapshot> {
  const opsSnapshot = getOpsStateSnapshot()
  if (opsSnapshot) {
    return opsSnapshot
  }
  return STATIC_SNAPSHOT
}
