'use client'

import { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  Clock3,
  Database,
  Loader2,
  RefreshCw,
  TestTube2,
  Wrench,
} from 'lucide-react'

import { cn } from '@/lib/utils'

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://localhost:8000'

interface ServiceState {
  name: string
  status: string
  running: boolean
}

interface SystemStatusPayload {
  overall_status: string
  timestamp: string
  summary: {
    total: number
    healthy: number
    unhealthy: number
    error: number
  }
  services: ServiceState[]
}

interface EvolutionStatusPayload {
  status: string
  health: string
  issues: string[]
  components: Record<string, boolean>
  last_results: Record<string, any>
  timestamp: string
}

interface CollectionHealthPayload {
  summary?: {
    status?: string
    raw_ingest_24h?: number
    feed_items_24h?: number
    issue_types?: string[]
  }
  pending_sources_1h?: string[]
  error_sources_24h?: string[]
}

interface MvpStatusPayload {
  trial_ready: boolean
  self_test?: {
    healthy?: boolean
    failed_checks?: Array<{ name: string; detail?: string }>
  }
  pipeline?: {
    status?: string
    gathered?: number
    processed?: number
    imported?: number
  }
  open_issues?: {
    total?: number
    p0?: number
    p1?: number
    active_blockers_6h?: number
  }
}

interface TestingIssue {
  id: string
  title: string
  priority: number
  status: string
  source_type: string
  updated_at?: string
}

interface ContextSummary {
  id: string
  context_type: string
  title: string
  goal?: string | null
  owner_type?: string | null
  owner_id?: string | null
  status: string
  priority: number
  task_count: number
  open_task_count: number
  artifact_count: number
  event_count: number
  latest_event_at?: string | null
  latest_artifact_at?: string | null
  updated_at?: string | null
  latest_event?: {
    action?: string
    result?: string
    event_type?: string
    reason?: string | null
    created_at?: string | null
  } | null
  latest_artifact?: {
    artifact_type?: string
    title?: string
    summary?: string | null
    created_at?: string | null
  } | null
}

interface ContextDetail extends ContextSummary {
  tasks: Array<{
    id: string
    title: string
    status: string
    priority: number
    source_type?: string | null
    task_type?: string | null
    assigned_brain?: string | null
    updated_at?: string | null
  }>
  recent_events: Array<{
    id: string
    event_type?: string | null
    action: string
    result: string
    reason?: string | null
    created_at?: string | null
  }>
  recent_artifacts: Array<{
    id: string
    artifact_type: string
    title: string
    summary?: string | null
    created_at?: string | null
  }>
}

interface TaskMemoryItem {
  id: string
  context_id: string
  memory_kind: string
  title: string
  summary?: string | null
  created_at?: string | null
}

interface ProceduralMemoryItem {
  id: string
  memory_key: string
  name: string
  problem_type?: string | null
  method_name?: string | null
  validation_status: string
  effectiveness_score: number
  last_validated_at?: string | null
}

function tone(status?: string) {
  if (status === 'healthy' || status === 'running' || status === 'active' || status === 'ok') {
    return 'bg-emerald-50 text-emerald-700 ring-emerald-200'
  }
  if (status === 'degraded' || status === 'pending' || status === 'warning') {
    return 'bg-amber-50 text-amber-700 ring-amber-200'
  }
  return 'bg-red-50 text-red-700 ring-red-200'
}

function formatTime(value?: string | null) {
  if (!value) return '未记录'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function contextTypeLabel(type?: string) {
  switch (type) {
    case 'evolution':
      return '进化'
    case 'source_intelligence':
      return '来源智能'
    case 'system':
      return '系统'
    default:
      return type || '未知'
  }
}

function priorityLabel(priority: number) {
  switch (priority) {
    case 0:
      return 'P0'
    case 1:
      return 'P1'
    case 2:
      return 'P2'
    default:
      return `P${priority}`
  }
}

function artifactTypeLabel(type?: string | null) {
  switch (type) {
    case 'report':
      return '报告快照'
    case 'log':
      return '日志证据'
    case 'decision':
      return '决策产物'
    default:
      return type || '未知产物'
  }
}

function eventLabel(eventType?: string | null, action?: string | null) {
  if (eventType === 'source_plan_review') return '建源计划评审'
  if (eventType === 'collection_health') return '采集健康检查'
  if (eventType === 'self_test') return '系统自测'
  if (eventType === 'log_health') return '日志健康巡检'
  if (action === 'dedupe_update') return '重复问题归并'
  return eventType || action || '事件'
}

// Task classification for visual hierarchy
// actionable: needs immediate attention (failed, pending, confirmed with high priority)
// auto_trace: system-generated monitoring events
// historical: completed, cancelled, or low priority old tasks
function classifyTaskStatus(task: ContextDetail['tasks'][0]): 'actionable' | 'auto_trace' | 'historical' {
  const actionableStatuses = ['pending', 'confirmed', 'failed']
  const historicalStatuses = ['completed', 'cancelled']
  const autoTraceSources = ['log_analysis', 'system_health', 'auto_cleanup']

  // Historical: completed or cancelled
  if (historicalStatuses.includes(task.status)) {
    return 'historical'
  }

  // Actionable: failed, pending, confirmed with P0/P1 priority (check first)
  if (actionableStatuses.includes(task.status) && task.priority <= 1) {
    return 'actionable'
  }

  // Auto-trace: system-generated monitoring tasks (check after actionable)
  if (autoTraceSources.includes(task.source_type || '')) {
    return 'auto_trace'
  }

  // Default: auto_trace for executing or lower priority
  return 'auto_trace'
}

function classifyEventStatus(event: ContextDetail['recent_events'][0]): 'actionable' | 'auto_trace' | 'historical' {
  // Auto-trace: dedupe and routine maintenance
  if (event.action === 'dedupe_update' || event.action?.includes('cleanup')) {
    return 'auto_trace'
  }

  // Actionable: failed results or manual actions
  if (event.result === 'failed' || event.event_type === 'manual_action') {
    return 'actionable'
  }

  // Historical: older than 24h
  const eventTime = event.created_at ? new Date(event.created_at).getTime() : 0
  const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000
  if (eventTime < oneDayAgo) {
    return 'historical'
  }

  // Default: auto_trace for routine events
  return 'auto_trace'
}

function sortTasksByStatus(tasks: ContextDetail['tasks']): ContextDetail['tasks'] {
  const priority: Record<string, number> = { actionable: 0, auto_trace: 1, historical: 2 }

  return [...tasks].sort((a, b) => {
    const aClass = classifyTaskStatus(a)
    const bClass = classifyTaskStatus(b)

    // First sort by classification
    if (priority[aClass] !== priority[bClass]) {
      return priority[aClass] - priority[bClass]
    }

    // Then by priority within same class
    if (a.priority !== b.priority) {
      return a.priority - b.priority
    }

    // Finally by update time
    const aTime = new Date(a.updated_at || 0).getTime()
    const bTime = new Date(b.updated_at || 0).getTime()
    return bTime - aTime
  })
}

function sortEventsByStatus(events: ContextDetail['recent_events']): ContextDetail['recent_events'] {
  const priority: Record<string, number> = { actionable: 0, auto_trace: 1, historical: 2 }

  return [...events].sort((a, b) => {
    const aClass = classifyEventStatus(a)
    const bClass = classifyEventStatus(b)

    // First sort by classification
    if (priority[aClass] !== priority[bClass]) {
      return priority[aClass] - priority[bClass]
    }

    // Then by time (newest first)
    const aTime = new Date(a.created_at || 0).getTime()
    const bTime = new Date(b.created_at || 0).getTime()
    return bTime - aTime
  })
}

function buildContextGuidance(context?: ContextDetail | null) {
  if (!context) {
    return {
      headline: '先选择一个上下文',
      detail: '建议优先查看 source intelligence 或 evolution 上下文，确认它最近做了什么。',
    }
  }

  if (context.context_type === 'source_intelligence') {
    return {
      headline: '重点看版本变化和待复核项',
      detail: '先看最新快照，再看最近事件，最后看上下文任务。这样最容易判断这次 refresh 是变好还是变差。',
    }
  }

  if (context.context_type === 'evolution') {
    return {
      headline: '重点看失败链路和恢复建议',
      detail: '先看关键问题，再看最近事件和产物，确认它是在报错、观察，还是已经进入恢复动作。',
    }
  }

  return {
    headline: '先看目标，再看事件和产物',
    detail: '不要先盯计数。先确认这个上下文要解决什么，再看最近做了什么、留下了什么证据。',
  }
}

export function EvolutionDashboard() {
  const [systemStatus, setSystemStatus] = useState<SystemStatusPayload | null>(null)
  const [evolutionStatus, setEvolutionStatus] = useState<EvolutionStatusPayload | null>(null)
  const [collectionHealth, setCollectionHealth] = useState<CollectionHealthPayload | null>(null)
  const [mvpStatus, setMvpStatus] = useState<MvpStatusPayload | null>(null)
  const [issues, setIssues] = useState<TestingIssue[]>([])
  const [contexts, setContexts] = useState<ContextSummary[]>([])
  const [selectedContextId, setSelectedContextId] = useState<string | null>(null)
  const [selectedContext, setSelectedContext] = useState<ContextDetail | null>(null)
  const [taskMemories, setTaskMemories] = useState<TaskMemoryItem[]>([])
  const [proceduralMemories, setProceduralMemories] = useState<ProceduralMemoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [runningSelfTest, setRunningSelfTest] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async (silent = false) => {
    if (silent) {
      setRefreshing(true)
    } else {
      setLoading(true)
    }

    try {
      const [systemRes, evolutionRes, collectionRes, mvpRes, issuesRes, contextsRes, taskMemoryRes, proceduralMemoryRes] = await Promise.all([
        fetch(`${API_URL}/api/settings/system`),
        fetch(`${API_URL}/api/evolution/status`),
        fetch(`${API_URL}/api/evolution/collection-health?fresh=true`),
        fetch(`${API_URL}/api/evolution/mvp-status`),
        fetch(`${API_URL}/api/testing/issues`),
        fetch(`${API_URL}/api/evolution/contexts`),
        fetch(`${API_URL}/api/evolution/memories/task`),
        fetch(`${API_URL}/api/evolution/memories/procedural`),
      ])

      if (!systemRes.ok || !evolutionRes.ok || !collectionRes.ok || !mvpRes.ok || !issuesRes.ok || !contextsRes.ok || !taskMemoryRes.ok || !proceduralMemoryRes.ok) {
        throw new Error('进化大脑数据加载失败')
      }

      const [systemData, evolutionData, collectionData, mvpData, issuesData, contextsData, taskMemoryData, proceduralMemoryData] = await Promise.all([
        systemRes.json(),
        evolutionRes.json(),
        collectionRes.json(),
        mvpRes.json(),
        issuesRes.json(),
        contextsRes.json(),
        taskMemoryRes.json(),
        proceduralMemoryRes.json(),
      ])

      const nextContexts = Array.isArray(contextsData?.contexts) ? contextsData.contexts : []
      const nextIssues = Array.isArray(issuesData?.issues) ? issuesData.issues : Array.isArray(issuesData) ? issuesData : []

      setSystemStatus(systemData)
      setEvolutionStatus(evolutionData)
      setCollectionHealth(collectionData)
      setMvpStatus(mvpData)
      setIssues(nextIssues)
      setContexts(nextContexts)
      setTaskMemories(Array.isArray(taskMemoryData?.memories) ? taskMemoryData.memories : [])
      setProceduralMemories(Array.isArray(proceduralMemoryData?.memories) ? proceduralMemoryData.memories : [])

      setSelectedContextId((current) => {
        if (current && nextContexts.some((item: ContextSummary) => item.id === current)) {
          return current
        }
        return nextContexts[0]?.id ?? null
      })

      setError(null)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : '加载失败')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    void load()
    const timer = window.setInterval(() => {
      void load(true)
    }, 30000)
    return () => window.clearInterval(timer)
  }, [])

  useEffect(() => {
    if (!selectedContextId) {
      setSelectedContext(null)
      return
    }

    let cancelled = false

    async function fetchDetail() {
      try {
        const response = await fetch(`${API_URL}/api/evolution/contexts/${selectedContextId}`)
        if (!response.ok) {
          throw new Error('上下文详情加载失败')
        }
        const data = await response.json()
        if (!cancelled) {
          setSelectedContext(data)
        }
      } catch (detailError) {
        if (!cancelled) {
          setError(detailError instanceof Error ? detailError.message : '上下文详情加载失败')
        }
      }
    }

    void fetchDetail()
    return () => {
      cancelled = true
    }
  }, [selectedContextId])

  const runSelfTestNow = async () => {
    setRunningSelfTest(true)
    try {
      const response = await fetch(`${API_URL}/api/evolution/self-test/run`, { method: 'POST' })
      if (!response.ok) {
        throw new Error('执行自测失败')
      }
      await load(true)
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : '执行自测失败')
    } finally {
      setRunningSelfTest(false)
    }
  }

  const failedChecks = mvpStatus?.self_test?.failed_checks || []
  const criticalIssues = useMemo(() => issues.filter((item) => item.priority <= 1).slice(0, 6), [issues])
  const contextGuidance = useMemo(() => buildContextGuidance(selectedContext), [selectedContext])

  if (loading) {
    return (
      <div className="flex items-center justify-center rounded-xl border bg-card p-12">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border bg-card p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <BrainCircuit className="h-4 w-4" />
              进化大脑
            </div>
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">持续监控、自测、归因和恢复入口</h2>
            <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
              这里展示的是持续运行中的进化上下文，而不是一组手动按钮。重点看系统正在监控什么、最近产出了什么快照、出了问题会落成什么任务。
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={runSelfTestNow}
              disabled={runningSelfTest}
              className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-muted disabled:opacity-50"
            >
              <TestTube2 className={cn('h-4 w-4', runningSelfTest && 'animate-pulse')} />
              立即自测
            </button>
            <button
              onClick={() => void load(true)}
              disabled={refreshing}
              className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-muted disabled:opacity-50"
            >
              <RefreshCw className={cn('h-4 w-4', refreshing && 'animate-spin')} />
              刷新
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <div className="rounded-xl border bg-background p-4">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">试运行状态</p>
            <p className="mt-2 text-lg font-semibold">{mvpStatus?.trial_ready ? '可试运行' : '未就绪'}</p>
            <p className="mt-1 text-sm text-muted-foreground">近 6 小时阻塞 {mvpStatus?.open_issues?.active_blockers_6h ?? 0}</p>
          </div>
          <div className="rounded-xl border bg-background p-4">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">自测结果</p>
            <p className="mt-2 text-lg font-semibold">{mvpStatus?.self_test?.healthy ? '通过' : '失败'}</p>
            <p className="mt-1 text-sm text-muted-foreground">失败检查 {failedChecks.length} 项</p>
          </div>
          <div className="rounded-xl border bg-background p-4">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">采集链路</p>
            <p className="mt-2 text-lg font-semibold">{collectionHealth?.summary?.status || 'unknown'}</p>
            <p className="mt-1 text-sm text-muted-foreground">
              24h 原始写入 {collectionHealth?.summary?.raw_ingest_24h ?? 0} / 事实层 {collectionHealth?.summary?.feed_items_24h ?? 0}
            </p>
          </div>
          <div className="rounded-xl border bg-background p-4">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">持续上下文</p>
            <p className="mt-2 text-lg font-semibold">{contexts.length}</p>
            <p className="mt-1 text-sm text-muted-foreground">运行中的观察与进化任务</p>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[320px_minmax(0,1fr)]">
        <div className="rounded-2xl border bg-card p-4 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Activity className="h-4 w-4 text-muted-foreground" />
            <h3 className="text-sm font-semibold">持续上下文</h3>
          </div>
          <div className="space-y-3">
            {contexts.map((context) => {
              const active = context.id === selectedContextId
              return (
                <button
                  key={context.id}
                  type="button"
                  onClick={() => setSelectedContextId(context.id)}
                  className={cn(
                    'w-full rounded-xl border px-4 py-3 text-left transition-colors',
                    active ? 'border-primary bg-primary/5' : 'hover:bg-muted/60',
                  )}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-foreground">{context.title}</p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {contextTypeLabel(context.context_type)} · {priorityLabel(context.priority)} · {context.status}
                      </p>
                    </div>
                    <span className={cn('inline-flex items-center rounded-full px-2 py-1 text-xs ring-1', tone(context.status))}>
                      {context.open_task_count} 开放任务
                    </span>
                  </div>
                  {context.goal && <p className="mt-2 line-clamp-2 text-xs text-muted-foreground">{context.goal}</p>}
                  <div className="mt-3 grid grid-cols-3 gap-2 text-xs text-muted-foreground">
                    <span>{context.task_count} 任务</span>
                    <span>{context.event_count} 事件</span>
                    <span>{context.artifact_count} 产物</span>
                  </div>
                  <p className="mt-2 text-[11px] text-muted-foreground">最近活动 {formatTime(context.updated_at || context.latest_event_at)}</p>
                </button>
              )
            })}
          </div>
        </div>

        <div className="space-y-6">
          <section className="rounded-2xl border bg-card p-6 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold">{selectedContext?.title || '未选择上下文'}</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  {selectedContext?.goal || '这个上下文还没有记录明确目标。'}
                </p>
              </div>
              {selectedContext && (
                <div className="flex flex-wrap gap-2">
                  <span className={cn('inline-flex items-center rounded-full px-2.5 py-1 text-xs ring-1', tone(selectedContext.status))}>
                    {selectedContext.status}
                  </span>
                  <span className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-700 ring-1 ring-slate-200">
                    {contextTypeLabel(selectedContext.context_type)}
                  </span>
                </div>
              )}
            </div>

            <div className="mt-4 rounded-xl border bg-muted/30 p-4">
              <div className="text-sm font-medium">{contextGuidance.headline}</div>
              <div className="mt-1 text-sm text-muted-foreground">{contextGuidance.detail}</div>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-4">
              <div className="rounded-xl border bg-background p-4">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">任务</p>
                <p className="mt-2 text-lg font-semibold">{selectedContext?.task_count ?? 0}</p>
              </div>
              <div className="rounded-xl border bg-background p-4">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">开放任务</p>
                <p className="mt-2 text-lg font-semibold">{selectedContext?.open_task_count ?? 0}</p>
              </div>
              <div className="rounded-xl border bg-background p-4">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">事件</p>
                <p className="mt-2 text-lg font-semibold">{selectedContext?.event_count ?? 0}</p>
              </div>
              <div className="rounded-xl border bg-background p-4">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">产物</p>
                <p className="mt-2 text-lg font-semibold">{selectedContext?.artifact_count ?? 0}</p>
              </div>
            </div>

            {selectedContext?.latest_artifact && (
              <div className="mt-6 rounded-xl border bg-background p-4">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <Database className="h-4 w-4 text-muted-foreground" />
                  最新快照
                </div>
                <p className="mt-2 text-sm font-semibold">{selectedContext.latest_artifact.title}</p>
                <p className="mt-1 text-sm text-muted-foreground">{selectedContext.latest_artifact.summary || '暂无摘要。'}</p>
                <p className="mt-2 text-xs text-muted-foreground">
                  {selectedContext.latest_artifact.artifact_type} · {formatTime(selectedContext.latest_artifact.created_at)}
                </p>
              </div>
            )}
          </section>

          <section className="grid gap-6 xl:grid-cols-2">
            <div className="rounded-2xl border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Clock3 className="h-4 w-4 text-muted-foreground" />
                  <h3 className="text-sm font-semibold">最近事件</h3>
                </div>
                {selectedContext && selectedContext.recent_events && selectedContext.recent_events.length > 0 && (
                  <div className="flex gap-2 text-xs text-muted-foreground">
                    <span className="inline-flex items-center gap-1">
                      <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                      需关注 {selectedContext.recent_events.filter((e: ContextDetail['recent_events'][0]) => classifyEventStatus(e) === 'actionable').length}
                    </span>
                  </div>
                )}
              </div>
              <div className="mt-4 space-y-3">
                {selectedContext?.recent_events?.length ? (
                  (() => {
                    const sortedEvents = sortEventsByStatus(selectedContext.recent_events)
                    const actionableCount = sortedEvents.filter(e => classifyEventStatus(e) === 'actionable').length

                    return (
                      <>
                        {/* Actionable events - highlighted */}
                        {sortedEvents.filter(e => classifyEventStatus(e) === 'actionable').map((event) => (
                          <div
                            key={event.id}
                            className="rounded-xl border border-l-4 border-l-amber-500 bg-amber-50/30 p-4"
                          >
                            <div className="flex items-center justify-between gap-2">
                              <div className="flex items-center gap-2">
                                <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" />
                                <p className="text-sm font-medium">{eventLabel(event.event_type, event.action)}</p>
                              </div>
                              <span className={cn('inline-flex items-center rounded-full px-2 py-1 text-xs ring-1', tone(event.result))}>
                                {event.result}
                              </span>
                            </div>
                            <p className="mt-1 text-xs text-muted-foreground">{event.reason || event.action}</p>
                            <p className="mt-2 text-[11px] text-muted-foreground">{formatTime(event.created_at)}</p>
                          </div>
                        ))}

                        {/* Divider if there are actionable events */}
                        {actionableCount > 0 && sortedEvents.length > actionableCount && (
                          <div className="my-4 flex items-center gap-2">
                            <div className="flex-1 border-t" />
                            <span className="text-xs text-muted-foreground">以下为历史事件或系统自动痕迹</span>
                            <div className="flex-1 border-t" />
                          </div>
                        )}

                        {/* Auto-trace and historical events - de-emphasized */}
                        {sortedEvents.filter(e => classifyEventStatus(e) !== 'actionable').map((event) => (
                          <div
                            key={event.id}
                            className={cn(
                              'rounded-xl border bg-background p-4',
                              classifyEventStatus(event) === 'historical' && 'opacity-60 grayscale-[0.3]'
                            )}
                          >
                            <div className="flex items-center justify-between gap-2">
                              <p className="text-sm font-medium">{eventLabel(event.event_type, event.action)}</p>
                              <span className={cn('inline-flex items-center rounded-full px-2 py-1 text-xs ring-1', tone(event.result))}>
                                {event.result}
                              </span>
                            </div>
                            <p className="mt-1 text-xs text-muted-foreground">{event.reason || event.action}</p>
                            <p className="mt-2 text-[11px] text-muted-foreground">{formatTime(event.created_at)}</p>
                          </div>
                        ))}
                      </>
                    )
                  })()
                ) : (
                  <p className="text-sm text-muted-foreground">暂无事件。</p>
                )}
              </div>
            </div>

            <div className="rounded-2xl border bg-card p-6 shadow-sm">
              <div className="flex items-center gap-2">
                <Wrench className="h-4 w-4 text-muted-foreground" />
                <h3 className="text-sm font-semibold">最近产物</h3>
              </div>
              <div className="mt-4 space-y-3">
                {selectedContext?.recent_artifacts?.length ? (
                  selectedContext.recent_artifacts.map((artifact) => (
                    <div key={artifact.id} className="rounded-xl border bg-background p-4">
                      <p className="text-sm font-medium">{artifact.title}</p>
                      <p className="mt-1 text-xs text-muted-foreground">{artifact.summary || '暂无摘要。'}</p>
                      <p className="mt-2 text-[11px] text-muted-foreground">
                        {artifactTypeLabel(artifact.artifact_type)} · {formatTime(artifact.created_at)}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">暂无产物。</p>
                )}
              </div>
            </div>
          </section>

          <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
            <div className="rounded-2xl border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <BrainCircuit className="h-4 w-4 text-muted-foreground" />
                  <h3 className="text-sm font-semibold">上下文任务</h3>
                </div>
                {selectedContext && selectedContext.tasks && selectedContext.tasks.length > 0 && (
                  <div className="flex gap-2 text-xs text-muted-foreground">
                    <span className="inline-flex items-center gap-1">
                      <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                      需关注 {selectedContext.tasks.filter((t: ContextDetail['tasks'][0]) => classifyTaskStatus(t) === 'actionable').length}
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <span className="h-1.5 w-1.5 rounded-full bg-slate-400" />
                      自动 {selectedContext.tasks.filter((t: ContextDetail['tasks'][0]) => classifyTaskStatus(t) === 'auto_trace').length}
                    </span>
                  </div>
                )}
              </div>
              <div className="mt-4 space-y-3">
                {selectedContext?.tasks?.length ? (
                  (() => {
                    const sortedTasks = sortTasksByStatus(selectedContext.tasks)
                    const actionableCount = sortedTasks.filter(t => classifyTaskStatus(t) === 'actionable').length

                    return (
                      <>
                        {/* Actionable tasks - highlighted */}
                        {sortedTasks.filter(t => classifyTaskStatus(t) === 'actionable').map((task) => (
                          <div
                            key={task.id}
                            className="rounded-xl border border-l-4 border-l-amber-500 bg-amber-50/30 p-4"
                          >
                            <div className="flex items-center justify-between gap-3">
                              <div className="flex items-center gap-2">
                                <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" />
                                <p className="text-sm font-medium">{task.title}</p>
                              </div>
                              <span className={cn('inline-flex items-center rounded-full px-2 py-1 text-xs ring-1', tone(task.status))}>
                                {task.status}
                              </span>
                            </div>
                            <p className="mt-1 text-xs text-muted-foreground">
                              {task.task_type || 'workflow'} · {task.source_type || 'unknown'} · {task.assigned_brain || 'unassigned'}
                            </p>
                            <p className="mt-2 text-[11px] text-muted-foreground">最近更新 {formatTime(task.updated_at)}</p>
                          </div>
                        ))}

                        {/* Divider if there are actionable tasks */}
                        {actionableCount > 0 && sortedTasks.length > actionableCount && (
                          <div className="my-4 flex items-center gap-2">
                            <div className="flex-1 border-t" />
                            <span className="text-xs text-muted-foreground">以下任务已归档或为系统自动痕迹</span>
                            <div className="flex-1 border-t" />
                          </div>
                        )}

                        {/* Auto-trace and historical tasks - de-emphasized */}
                        {sortedTasks.filter(t => classifyTaskStatus(t) !== 'actionable').map((task) => (
                          <div
                            key={task.id}
                            className={cn(
                              'rounded-xl border bg-background p-4',
                              classifyTaskStatus(task) === 'historical' && 'opacity-60 grayscale-[0.3]'
                            )}
                          >
                            <div className="flex items-center justify-between gap-3">
                              <p className="text-sm font-medium">{task.title}</p>
                              <span className={cn('inline-flex items-center rounded-full px-2 py-1 text-xs ring-1', tone(task.status))}>
                                {task.status}
                              </span>
                            </div>
                            <p className="mt-1 text-xs text-muted-foreground">
                              {task.task_type || 'workflow'} · {task.source_type || 'unknown'} · {task.assigned_brain || 'unassigned'}
                            </p>
                            <p className="mt-2 text-[11px] text-muted-foreground">最近更新 {formatTime(task.updated_at)}</p>
                          </div>
                        ))}
                      </>
                    )
                  })()
                ) : (
                  <p className="text-sm text-muted-foreground">这个上下文还没有挂接任务。</p>
                )}
              </div>
            </div>

            <div className="space-y-6">
              <div className="rounded-2xl border bg-card p-6 shadow-sm">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
                  <h3 className="text-sm font-semibold">系统总览</h3>
                </div>
                <div className="mt-4 space-y-3 text-sm">
                  <p className="text-muted-foreground">整体健康：{systemStatus?.overall_status || 'unknown'}</p>
                  <p className="text-muted-foreground">进化状态：{evolutionStatus?.health || 'unknown'}</p>
                  <p className="text-muted-foreground">服务总数：{systemStatus?.summary?.total ?? 0}</p>
                </div>
              </div>

              <div className="rounded-2xl border bg-card p-6 shadow-sm">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                  <h3 className="text-sm font-semibold">关键问题</h3>
                </div>
                <div className="mt-4 space-y-3">
                  {criticalIssues.length ? (
                    criticalIssues.map((issue) => (
                      <div key={issue.id} className="rounded-xl border bg-background p-4">
                        <p className="text-sm font-medium">{issue.title}</p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          P{issue.priority} · {issue.source_type} · {issue.status}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">当前没有 P0/P1 级问题。</p>
                  )}
                </div>
              </div>

              <div className="rounded-2xl border bg-card p-6 shadow-sm">
                <div className="flex items-center gap-2">
                  <BrainCircuit className="h-4 w-4 text-muted-foreground" />
                  <h3 className="text-sm font-semibold">人工采纳建议</h3>
                </div>
                <div className="mt-4 space-y-3 text-sm text-muted-foreground">
                  <div className="rounded-xl border bg-background p-4">
                    <p className="font-medium text-foreground">界面层级建议</p>
                    <p className="mt-1">
                      如果你发现事件、产物和任务看起来像同一类信息，优先调整展示层级，而不是继续增加字段。
                    </p>
                  </div>
                  <div className="rounded-xl border bg-background p-4">
                    <p className="font-medium text-foreground">建源策略建议</p>
                    <p className="mt-1">
                      如果同主题反复出现待复核候选，先检查 plan 分类和 review cadence，而不是马上新增更多 source。
                    </p>
                  </div>
                  <div className="rounded-xl border bg-background p-4">
                    <p className="font-medium text-foreground">说明</p>
                    <p className="mt-1">
                      这些建议不一定自动执行，它们是给主控脑和人工决策参考的可采纳建议。
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="grid gap-6 xl:grid-cols-2">
            <div className="rounded-2xl border bg-card p-6 shadow-sm">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-muted-foreground" />
                <h3 className="text-sm font-semibold">任务记忆</h3>
              </div>
              <div className="mt-4 space-y-3">
                {taskMemories.length ? (
                  taskMemories.slice(0, 8).map((memory) => (
                    <div key={memory.id} className="rounded-xl border bg-background p-4">
                      <p className="text-sm font-medium">{memory.title}</p>
                      <p className="mt-1 text-xs text-muted-foreground">{memory.summary || memory.memory_kind}</p>
                      <p className="mt-2 text-[11px] text-muted-foreground">
                        {memory.memory_kind} · {formatTime(memory.created_at)}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">暂无任务记忆。</p>
                )}
              </div>
            </div>

            <div className="rounded-2xl border bg-card p-6 shadow-sm">
              <div className="flex items-center gap-2">
                <BrainCircuit className="h-4 w-4 text-muted-foreground" />
                <h3 className="text-sm font-semibold">程序性记忆</h3>
              </div>
              <div className="mt-4 space-y-3">
                {proceduralMemories.length ? (
                  proceduralMemories.slice(0, 8).map((memory) => (
                    <div key={memory.id} className="rounded-xl border bg-background p-4">
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-sm font-medium">{memory.name}</p>
                        <span className={cn('inline-flex items-center rounded-full px-2 py-1 text-xs ring-1', tone(memory.validation_status))}>
                          {memory.validation_status}
                        </span>
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {memory.problem_type || 'unknown'} · {memory.method_name || 'method'}
                      </p>
                      <p className="mt-2 text-[11px] text-muted-foreground">
                        score {memory.effectiveness_score.toFixed(2)} · {formatTime(memory.last_validated_at)}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">暂无程序性记忆。</p>
                )}
              </div>
            </div>
          </section>
        </div>
      </section>
    </div>
  )
}
