import 'server-only'
import fs from 'fs'
import path from 'path'
import { ControlSnapshot, ObservedState, PmRunDigest, RuntimeProbeService, RuntimeProbeState, ScoreStatus } from './types'

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

  // 2. Try bounded local repo roots from cwd. Do not walk above cwd unless the
  // process is running from the known services/web app directory or Next standalone.
  const cwd = process.cwd()
  const candidateRoots: string[] = [
    cwd, // running from repo root
  ]

  // Local dev: running from services/web
  if (path.basename(cwd) === 'web' && path.basename(path.dirname(cwd)) === 'services') {
    candidateRoots.push(path.resolve(cwd, '..', '..'))
  }

  // Next standalone: running from services/web/.next/standalone
  if (path.basename(cwd) === 'standalone' && path.basename(path.dirname(cwd)) === '.next') {
    // standalone -> .next -> web -> services -> repo root (4 levels up)
    candidateRoots.push(path.resolve(cwd, '..', '..', '..', '..'))
  }

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
  const candidateRoots: string[] = [
    cwd,
  ]

  // Local dev: running from services/web
  if (path.basename(cwd) === 'web' && path.basename(path.dirname(cwd)) === 'services') {
    candidateRoots.push(path.resolve(cwd, '..', '..'))
  }

  // Next standalone: running from services/web/.next/standalone
  if (path.basename(cwd) === 'standalone' && path.basename(path.dirname(cwd)) === '.next') {
    // standalone -> .next -> web -> services -> repo root (4 levels up)
    candidateRoots.push(path.resolve(cwd, '..', '..', '..', '..'))
  }

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

  let state: Record<string, any>
  try {
    let rawData = fs.readFileSync(statePath, 'utf-8')
    if (rawData.charCodeAt(0) === 0xFEFF) {
      rawData = rawData.slice(1)
    }
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

  // Optional fields - degrade gracefully if missing
  const dirtyTree = state?.dirty_tree_state
  const nextAction = state?.next_action

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
        latestAcceptedEvidence: product.first_class_tasks.flatMap((t: { evidence?: string[] }) => t.evidence || [])
      },
      tasks: product.first_class_tasks.map((t: { id: string; status: string; remaining_gap: string }) => ({
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
      operationsSplit: dirtyTree ? {
        codeTruth: dirtyTree.status === 'clean' ? 'Dirty tree is clean' : 'Dirty tree is DEGRADED',
        runtimeTruth: `Reachability: ${runtime.reachability_status}`,
        runtimeDependency: `Product Runtime: ${runtime.product_runtime_status}`
      } : undefined,
      nextActions: nextAction ? [
        {
          lane: nextAction.owner,
          action: nextAction.action
        }
      ] : [],
      observed: readObservedState(),
      runtime: readRuntimeState()
    }

    return snapshot
  } catch (error) {
    console.error('OpsStateAdapter: Failed to construct snapshot from valid fields:', error instanceof Error ? error.message : error)
    return null
  }
}

function readObservedState(): ObservedState | undefined {
  const observedPath = resolveRepoPath(path.join('ops', 'state', 'observed_state.json'))
  if (!observedPath) return undefined

  try {
    let rawData = fs.readFileSync(observedPath, 'utf-8')
    if (rawData.charCodeAt(0) === 0xFEFF) {
      rawData = rawData.slice(1)
    }
    const data = JSON.parse(rawData)

    // Schema validation - fail closed
    if (typeof data.observed_at !== 'string' ||
        typeof data.reconciler_version !== 'string' ||
        typeof data.controller_attention_required !== 'boolean' ||
        !Array.isArray(data.attention_evidence) ||
        !data.attention_evidence.every((item: unknown) => typeof item === 'string')) {
      console.error('OpsStateAdapter: Observed state failed schema validation')
      return undefined
    }

    // Validate state_comparison.conflict_detected if present: it must be a boolean. Do not coerce it.
    let reachabilityConflict = false
    if (data.state_comparison !== undefined) {
      if (typeof data.state_comparison !== 'object' || data.state_comparison === null ||
          (data.state_comparison.conflict_detected !== undefined && typeof data.state_comparison.conflict_detected !== 'boolean')) {
        console.error('OpsStateAdapter: Observed state_comparison failed validation')
        return undefined
      }
      reachabilityConflict = !!data.state_comparison.conflict_detected
    }

    return {
      observedAt: data.observed_at,
      reconcilerVersion: data.reconciler_version,
      controllerAttentionRequired: data.controller_attention_required,
      attentionEvidence: data.attention_evidence,
      reachabilityConflict
    }
  } catch (error) {
    console.error('OpsStateAdapter: Failed to read observed state:', error)
    return undefined
  }
}

function readRuntimeState(): RuntimeProbeState | undefined {
  const runtimePath = resolveRepoPath(path.join('ops', 'runtime', 'latest.json'))
  if (!runtimePath) return undefined

  try {
    let rawData = fs.readFileSync(runtimePath, 'utf-8')
    if (rawData.charCodeAt(0) === 0xFEFF) {
      rawData = rawData.slice(1)
    }
    const data = JSON.parse(rawData)

    // Schema validation - fail closed
    if (typeof data.probed_at !== 'string' ||
        typeof data.overall_reachability !== 'string' ||
        typeof data.services !== 'object' ||
        data.services === null) {
      console.error('OpsStateAdapter: Runtime state failed schema validation')
      return undefined
    }

    const services: RuntimeProbeService[] = []
    for (const [id, svc] of Object.entries(data.services)) {
      if (typeof svc !== 'object' || svc === null) {
        console.error(`OpsStateAdapter: Runtime service "${id}" is not a non-null object`)
        return undefined
      }
      const s = svc as any

      // Status must be a supported string status
      if (s.status !== 'healthy' && s.status !== 'unhealthy' && s.status !== 'degraded') {
        console.error(`OpsStateAdapter: Runtime service "${id}" has invalid status: ${s.status}`)
        return undefined
      }

      // Optional url, evidence, and response must be strings
      if (s.url !== undefined && typeof s.url !== 'string') return undefined
      if (s.evidence !== undefined && typeof s.evidence !== 'string') return undefined
      if (s.response !== undefined && typeof s.response !== 'string') return undefined

      // Optional tcp_check.status must be string
      if (s.tcp_check !== undefined) {
        if (typeof s.tcp_check !== 'object' || s.tcp_check === null || typeof s.tcp_check.status !== 'string') {
          return undefined
        }
      }

      services.push({
        id: String(id),
        status: s.status,
        url: s.url,
        details: s.evidence || s.response || (s.tcp_check ? `TCP ${s.tcp_check.status}` : '') || 'No details'
      })
    }

    return {
      probedAt: data.probed_at,
      overallReachability: data.overall_reachability,
      services
    }
  } catch (error) {
    console.error('OpsStateAdapter: Failed to read runtime state:', error)
    return undefined
  }
}

function readPmRunDigest(): PmRunDigest | undefined {
  const digestPath = resolveRepoPath(path.join('ops', 'pm-runs', 'latest.json'))
  if (!digestPath) return undefined

  try {
    let rawData = fs.readFileSync(digestPath, 'utf-8')
    if (rawData.charCodeAt(0) === 0xFEFF) {
      rawData = rawData.slice(1)
    }
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

function mapServiceStatus(status: unknown): 'healthy' | 'caveat' | 'unhealthy' {
  if (typeof status !== 'string') return 'unhealthy'
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
