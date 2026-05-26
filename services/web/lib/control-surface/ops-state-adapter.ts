import 'server-only'
import fs from 'fs'
import path from 'path'
import { ControlSnapshot, PmRunDigest, ScoreStatus } from './types'

/**
 * Resolve the path to ops/state/current_state.json.
 * Priority:
 * 1. IKE_OPS_STATE_PATH env var (absolute path)
 * 2. Reasonable local repo roots from cwd
 * 3. Return null if no path exists
 */
function resolveOpsStatePath(): string | null {
  // 1. Prefer explicit env var
  const envPath = process.env.IKE_OPS_STATE_PATH
  if (envPath && fs.existsSync(envPath)) {
    return envPath
  }

  // 2. Try reasonable local repo roots from cwd
  const cwd = process.cwd()
  const candidateRoots = [
    cwd,                                    // running from repo root
    path.join(cwd, '..', '..'),            // running from services/web
    path.join(cwd, 'services', 'web'),     // running from repo root (alt)
  ]

  for (const root of candidateRoots) {
    const candidate = path.join(root, 'ops', 'state', 'current_state.json')
    if (fs.existsSync(candidate)) {
      return candidate
    }
  }

  // 3. No path found
  return null
}

function resolveRepoRootFromStatePath(statePath: string): string | null {
  const resolved = path.resolve(statePath)
  const normalized = resolved.split(path.sep)
  const suffix = ['ops', 'state', 'current_state.json']

  for (let i = normalized.length - suffix.length; i >= 0; i--) {
    const matches = suffix.every((part, offset) => normalized[i + offset] === part)
    if (matches) {
      return normalized.slice(0, i).join(path.sep) || path.sep
    }
  }

  return null
}

function resolveRepoPath(relativePath: string): string | null {
  const explicitStatePath = process.env.IKE_OPS_STATE_PATH
  if (explicitStatePath) {
    const root = resolveRepoRootFromStatePath(explicitStatePath)
    if (root) {
      const candidate = path.join(root, relativePath)
      if (fs.existsSync(candidate)) return candidate
    }
  }

  const cwd = process.cwd()
  const candidateRoots = [
    cwd,
    path.join(cwd, '..', '..'),
  ]

  for (const root of candidateRoots) {
    const candidate = path.join(root, relativePath)
    if (fs.existsSync(candidate)) return candidate
  }

  return null
}

/**
 * Log a concise field-specific error and return null.
 */
function logFieldError(field: string, error: unknown): null {
  console.error(`OpsStateAdapter: Missing or invalid field "${field}":`, error instanceof Error ? error.message : error)
  return null
}

export function getOpsStateSnapshot(): ControlSnapshot | null {
  // Resolve path with robust fallback
  const statePath = resolveOpsStatePath()
  if (!statePath) {
    return null
  }

  let state: any
  try {
    const rawData = fs.readFileSync(statePath, 'utf-8')
    state = JSON.parse(rawData)
  } catch (error) {
    console.error('OpsStateAdapter: Failed to read or parse ops state file:', error instanceof Error ? error.message : error)
    return null
  }

  // Field guards with optional chaining - fail fast with specific logging
  const product = state?.product_state
  if (!product) {
    return logFieldError('product_state', 'undefined')
  }
  if (!Array.isArray(product.first_class_tasks)) {
    return logFieldError('product_state.first_class_tasks', 'not an array')
  }

  const runtime = state?.runtime_state
  if (!runtime) {
    return logFieldError('runtime_state', 'undefined')
  }
  if (!Array.isArray(runtime.required_before_next_product_validation)) {
    return logFieldError('runtime_state.required_before_next_product_validation', 'not an array')
  }
  if (typeof runtime.services !== 'object' || runtime.services === null) {
    return logFieldError('runtime_state.services', 'not an object')
  }

  const validation = state?.validation_state
  if (!validation) {
    return logFieldError('validation_state', 'undefined')
  }

  const runner = state?.runner_state
  if (!runner) {
    return logFieldError('runner_state', 'undefined')
  }

  const governance = state?.governance_state
  if (!governance || !Array.isArray(governance.mandatory_gates)) {
    return logFieldError('governance_state.mandatory_gates', 'undefined or not an array')
  }

  const review = state?.review_state
  if (!review) {
    return logFieldError('review_state', 'undefined')
  }

  const dirtyTree = state?.dirty_tree_state
  if (!dirtyTree) {
    return logFieldError('dirty_tree_state', 'undefined')
  }

  const nextAction = state?.next_action
  if (!nextAction) {
    return logFieldError('next_action', 'undefined')
  }

  try {
    const pmRunDigest = readPmRunDigest()
    const automationHealth = Object.entries(runtime.services).map(([id, svc]: [string, any]) => ({
      id,
      name: id.toUpperCase(),
      status: mapServiceStatus(svc.status),
      description: svc.evidence || 'No evidence provided'
    }))

    if (pmRunDigest && !automationHealth.some(item => item.id === 'ike-pm-mainline-watch')) {
      automationHealth.unshift({
        id: 'ike-pm-mainline-watch',
        name: 'IKE PM MAINLINE WATCH',
        status: mapPmDigestStatus(pmRunDigest),
        description: `${pmRunDigest.decision}: ${pmRunDigest.reason}`
      })
    }

    const snapshot: ControlSnapshot = {
      provenance: {
        sourceKind: 'file_derived',
        sourceLabel: `Ops State Sync (from ${state.updated_by})`,
        freshnessLabel: state.updated_at.split('T')[0],
        truthStatus: 'derived',
        caveat: 'Derived from ops/state/current_state.json. Status is accepted_project_truth but UI presentation is derived.'
      },
      mainline: {
        name: product.mainline,
        objective: product.current_priority,
        latestAcceptedEvidence: product.first_class_tasks.flatMap((t: any) => t.evidence || [])
      },
      tasks: product.first_class_tasks.map((t: any) => ({
        id: t.id,
        title: t.id.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
        status: mapStatus(t.status),
        description: `Gap: ${t.remaining_gap}`
      })),
      phase: {
        current: product.phase,
        nextGate: state.governance_state.mandatory_gates[0] || 'Unknown'
      },
      capabilities: [
        {
          id: 'runtime',
          title: 'Runtime Status',
          maturity: runtime.reachability_status,
          gap: runtime.required_before_next_product_validation.join('; '),
          status: runtime.product_runtime_status === 'healthy' ? 'accepted' : 'blocked'
        }
      ],
      lanes: runner.health_summary ? Object.entries(runner.health_summary).map(([id, status]) => ({
        id,
        name: id.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
        owner: 'Runner',
        status: status as string
      })) : [],
      automationHealth,
      pmRunDigest,
      reviewState: {
        prReviewGate: state.review_state.current_package,
        promotion: state.governance_state.sdlc.join(' -> '),
        termination: 'Review gates terminate after absorbed findings',
        monitor: state.review_state.status
      },
      operationsSplit: {
        codeTruth: state.dirty_tree_state.status === 'clean' ? 'Dirty tree is clean' : 'Dirty tree is DEGRADED',
        runtimeTruth: `Reachability: ${runtime.reachability_status}`,
        runtimeDependency: `Product Runtime: ${runtime.product_runtime_status}`
      },
      nextActions: [
        {
          lane: state.next_action.owner,
          action: state.next_action.action
        }
      ]
    }

    return snapshot
  } catch (error) {
    console.error('OpsStateAdapter: Failed to construct snapshot from valid fields:', error instanceof Error ? error.message : error)
    return null
  }
}

function readPmRunDigest(): PmRunDigest | undefined {
  const digestPath = resolveRepoPath(path.join('ops', 'pm-runs', 'latest.json'))
  if (!digestPath) return undefined

  try {
    const rawData = fs.readFileSync(digestPath, 'utf-8')
    const digest = JSON.parse(rawData)
    if (digest?.schema_version !== 1 || digest?.source !== 'openclaw-ike-pm') {
      return undefined
    }

    return {
      runId: String(digest.run_id || ''),
      checkedAt: String(digest.checked_at || ''),
      cronJobId: String(digest.cron_job_id || ''),
      decision: String(digest.decision || 'unknown'),
      status: mapPmStatus(digest.status),
      reason: String(digest.reason || 'No reason provided'),
      lastRealProgressAt: digest.last_real_progress_at ? String(digest.last_real_progress_at) : undefined,
      stalenessMinutes: typeof digest.staleness_minutes === 'number' ? digest.staleness_minutes : undefined,
      controllerActionNeeded: Boolean(digest.controller_action_needed),
      triggerPath: digest.trigger_path ? String(digest.trigger_path) : undefined,
      bridgeResultPath: digest.bridge_result_path ? String(digest.bridge_result_path) : undefined,
      evidence: Array.isArray(digest.evidence) ? digest.evidence.map((item: unknown) => String(item)) : [],
      nextExpectedRun: digest.next_expected_run ? String(digest.next_expected_run) : undefined
    }
  } catch (error) {
    console.error('OpsStateAdapter: Failed to read PM run digest:', error instanceof Error ? error.message : error)
    return undefined
  }
}

function mapStatus(status: string): ScoreStatus {
  switch (status) {
    case 'passed':
    case 'accepted':
    case 'complete':
      return 'accepted'
    case 'partial':
    case 'estimated':
      return 'estimated'
    case 'failed':
    case 'blocked':
      return 'blocked'
    default:
      return 'unknown'
  }
}

function mapServiceStatus(status: string): 'healthy' | 'caveat' | 'unhealthy' {
  if (status === 'healthy') return 'healthy'
  if (status === 'degraded' || status.includes('contradictory')) return 'caveat'
  return 'unhealthy'
}

function mapPmStatus(status: unknown): 'ok' | 'warning' | 'error' {
  if (status === 'ok' || status === 'warning' || status === 'error') return status
  return 'warning'
}

function mapPmDigestStatus(digest: PmRunDigest): 'healthy' | 'caveat' | 'unhealthy' {
  if (digest.status === 'error') return 'unhealthy'
  if (digest.controllerActionNeeded || digest.status === 'warning') return 'caveat'
  return 'healthy'
}
