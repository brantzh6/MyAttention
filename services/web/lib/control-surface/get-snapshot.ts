import { ControlSnapshot } from './types'
import { STATIC_SNAPSHOT } from './static-snapshot'

export async function getSnapshot(): Promise<ControlSnapshot> {
  return STATIC_SNAPSHOT
}
