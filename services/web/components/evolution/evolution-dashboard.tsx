'use client'

import { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  Loader2,
  RefreshCw,
  ShieldAlert,
  TestTube2,
  Wrench,
} from 'lucide-react'

import { cn } from '@/lib/utils'

const API_URL = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://localhost:8000'

interface ServiceState {
  name: string
  status: string
  running: boolean
  details?: Record<string, unknown>
  error?: string
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
  databases: ServiceState[]
  services: ServiceState[]
  external: ServiceState[]
}

interface EvolutionStatusPayload {
  status: string
  health: string
  issues: string[]
  components: Record<string, boolean>
  intervals: Record<string, number>
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

function statusTone(status?: string) {
  if (status === 'healthy' || status === 'running') return 'bg-emerald-50 text-emerald-700 ring-emerald-200'
  if (status === 'degraded') return 'bg-amber-50 text-amber-700 ring-amber-200'
  if (status === 'not_configured') return 'bg-slate-100 text-slate-600 ring-slate-200'
  return 'bg-red-50 text-red-700 ring-red-200'
}

function statusIcon(status?: string) {
  if (status === 'healthy' || status === 'running') return <CheckCircle2 className="h-4 w-4" />
  if (status === 'degraded') return <AlertTriangle className="h-4 w-4" />
  return <ShieldAlert className="h-4 w-4" />
}

export function EvolutionDashboard() {
  const [systemStatus, setSystemStatus] = useState<SystemStatusPayload | null>(null)
  const [evolutionStatus, setEvolutionStatus] = useState<EvolutionStatusPayload | null>(null)
  const [collectionHealth, setCollectionHealth] = useState<CollectionHealthPayload | null>(null)
  const [mvpStatus, setMvpStatus] = useState<MvpStatusPayload | null>(null)
  const [issues, setIssues] = useState<TestingIssue[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [runningSelfTest, setRunningSelfTest] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async (silent = false) => {
    if (!silent) {
      setLoading(true)
    } else {
      setRefreshing(true)
    }

    try {
      const [systemRes, evolutionRes, collectionRes, mvpRes, issuesRes] = await Promise.all([
        fetch(`${API_URL}/api/settings/system`),
        fetch(`${API_URL}/api/evolution/status`),
        fetch(`${API_URL}/api/evolution/collection-health?fresh=true`),
        fetch(`${API_URL}/api/evolution/mvp-status`),
        fetch(`${API_URL}/api/testing/issues`),
      ])

      if (!systemRes.ok || !evolutionRes.ok || !collectionRes.ok || !mvpRes.ok || !issuesRes.ok) {
        throw new Error('进化大脑数据加载失败')
      }

      const [systemData, evolutionData, collectionData, mvpData, issuesData] = await Promise.all([
        systemRes.json(),
        evolutionRes.json(),
        collectionRes.json(),
        mvpRes.json(),
        issuesRes.json(),
      ])

      setSystemStatus(systemData)
      setEvolutionStatus(evolutionData)
      setCollectionHealth(collectionData)
      setMvpStatus(mvpData)
      setIssues(Array.isArray(issuesData?.issues) ? issuesData.issues : Array.isArray(issuesData) ? issuesData : [])
      setError(null)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : '加载失败')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    load()
    const timer = window.setInterval(() => {
      void load(true)
    }, 30000)

    return () => window.clearInterval(timer)
  }, [])

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

  const criticalIssues = useMemo(() => issues.filter((item) => item.priority <= 1).slice(0, 6), [issues])
  const failedChecks = mvpStatus?.self_test?.failed_checks || []

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
            <h2 className="text-2xl font-semibold tracking-tight text-foreground">自测、监控、问题归并和恢复入口</h2>
            <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
              这里应该是系统主动看自己、测自己、发现问题和驱动修复的主页面，而不是藏在通知设置里的附属面板。
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
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <div className="rounded-xl border bg-background p-4">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">试运行状态</p>
            <p className="mt-2 text-lg font-semibold">{mvpStatus?.trial_ready ? '可试运行' : '未就绪'}</p>
            <p className="mt-1 text-sm text-muted-foreground">
              阻塞问题 {mvpStatus?.open_issues?.active_blockers_6h ?? 0} 个
            </p>
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
              24h 原始写入 {collectionHealth?.summary?.raw_ingest_24h ?? 0}
            </p>
          </div>
          <div className="rounded-xl border bg-background p-4">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">问题中心</p>
            <p className="mt-2 text-lg font-semibold">{mvpStatus?.open_issues?.total ?? 0} 个问题</p>
            <p className="mt-1 text-sm text-muted-foreground">
              P0 {mvpStatus?.open_issues?.p0 ?? 0} / P1 {mvpStatus?.open_issues?.p1 ?? 0}
            </p>
          </div>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
        <section className="space-y-6">
          <div className="rounded-2xl border bg-card p-6 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <TestTube2 className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-semibold">当前自测覆盖</h3>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {failedChecks.length === 0 ? (
                <div className="rounded-lg border bg-background p-4 text-sm text-muted-foreground md:col-span-2">
                  当前没有失败自测。
                </div>
              ) : (
                failedChecks.map((item, index) => (
                  <div key={`${item.name}-${index}`} className="rounded-lg border border-amber-200 bg-amber-50 p-4">
                    <p className="font-medium text-amber-900">{item.name}</p>
                    <p className="mt-1 text-sm text-amber-700">{item.detail || '未返回更多细节'}</p>
                  </div>
                ))
              )}
            </div>
            <div className="mt-4 rounded-lg border bg-background p-4 text-sm text-muted-foreground">
              当前进化大脑已经覆盖日志、自测、投票 canary、采集健康，但真实 UI 巡检还需要继续升级到浏览器级操作。
            </div>
          </div>

          <div className="rounded-2xl border bg-card p-6 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-semibold">服务与基础设施</h3>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {[...(systemStatus?.services || []), ...(systemStatus?.databases || [])].map((service) => (
                <div key={service.name} className="rounded-lg border bg-background p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-medium text-foreground">{service.name}</p>
                      <p className="mt-1 text-sm text-muted-foreground">
                        {service.error || (service.running ? '运行中' : '未运行')}
                      </p>
                    </div>
                    <span className={cn('inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs ring-1', statusTone(service.status))}>
                      {statusIcon(service.status)}
                      {service.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="space-y-6">
          <div className="rounded-2xl border bg-card p-6 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <Wrench className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-semibold">收集链路诊断</h3>
            </div>
            <div className="space-y-3 text-sm">
              <div className="rounded-lg border bg-background p-4">
                <p className="font-medium">待处理来源</p>
                <p className="mt-2 text-muted-foreground">
                  {(collectionHealth?.pending_sources_1h || []).join('，') || '无'}
                </p>
              </div>
              <div className="rounded-lg border bg-background p-4">
                <p className="font-medium">24 小时报错来源</p>
                <p className="mt-2 text-muted-foreground">
                  {(collectionHealth?.error_sources_24h || []).join('，') || '无'}
                </p>
              </div>
              <div className="rounded-lg border bg-background p-4">
                <p className="font-medium">Pipeline 状态</p>
                <p className="mt-2 text-muted-foreground">
                  {mvpStatus?.pipeline?.status || 'unknown'} / gathered {mvpStatus?.pipeline?.gathered ?? 0} / imported{' '}
                  {mvpStatus?.pipeline?.imported ?? 0}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border bg-card p-6 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-semibold">高优先级问题</h3>
            </div>
            <div className="space-y-3">
              {criticalIssues.length === 0 ? (
                <div className="rounded-lg border bg-background p-4 text-sm text-muted-foreground">
                  当前没有 P0 / P1 问题。
                </div>
              ) : (
                criticalIssues.map((issue) => (
                  <div key={issue.id} className="rounded-lg border bg-background p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-medium text-foreground">{issue.title}</p>
                        <p className="mt-1 text-sm text-muted-foreground">
                          {issue.source_type} / {issue.status}
                        </p>
                      </div>
                      <span className="rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700 ring-1 ring-red-200">
                        P{issue.priority}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="rounded-2xl border bg-card p-6 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-semibold">当前边界</h3>
            </div>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li>日志分析、接口自测和采集健康已经接入，但浏览器级 UI 巡检仍需继续强化。</li>
              <li>新存储结构只完成了对象存储原始层和部分事实层，知识大脑的结构化层还没落完。</li>
              <li>这个页面现在是进化大脑的正式入口，后续 UI 巡检和自动恢复记录也应收口到这里。</li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  )
}
