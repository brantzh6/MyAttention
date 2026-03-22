'use client'

import { type FormEvent, useEffect, useState } from 'react'
import {
  AlertCircle,
  Brain,
  CheckCircle,
  Globe,
  Loader2,
  Plus,
  RefreshCw,
  Rss,
  Save,
  Shield,
  Trash2,
  XCircle,
} from 'lucide-react'

import { cn } from '@/lib/utils'

type SourceType = 'rss' | 'web' | 'api'
type SourceStatus = 'ok' | 'warning' | 'error'
type ProxyMode = 'auto' | 'always' | 'never'
type DiscoveryFocus = 'latest' | 'authoritative' | 'frontier' | 'method'

interface Source {
  id: string
  name: string
  type: SourceType
  url: string
  category: string
  tags: string[]
  enabled: boolean
  status: SourceStatus
  last_fetched: string | null
  success_rate: number
  proxy_mode: ProxyMode
  proxy_effective: boolean
  proxy_reason: string
}

interface ProxyProbe {
  configured: boolean
  reachable: boolean
  working: boolean
  supported?: boolean
  error?: string | null
}

interface ProxyStatus {
  state: 'disabled' | 'healthy' | 'degraded' | 'error'
  message: string
  checked_at: string
  http: ProxyProbe
  socks: ProxyProbe
}

interface ProxySettings {
  enabled: boolean
  http_proxy: string
  socks_proxy: string
  auto_detect_domains: boolean
  test_url: string
  status?: ProxyStatus
  status_info?: ProxyStatus
}

interface NewSourceForm {
  name: string
  type: SourceType
  url: string
  category: string
  proxy_mode: ProxyMode
}

interface SourcePlanItem {
  id: string
  item_type: string
  object_key: string
  name: string
  url: string
  authority_tier: string
  authority_score: number
  monitoring_mode: string
  execution_strategy: string
  review_cadence_days: number
  rationale: string
  status: string
  evidence: Record<string, any>
}

interface SourcePlan {
  id: string
  topic: string
  focus: DiscoveryFocus
  objective: string
  planning_brain: string
  status: string
  review_status: string
  review_cadence_days: number
  current_version: number
  latest_version: number
  last_reviewed_at: string | null
  next_review_due_at: string | null
  created_at: string | null
  updated_at: string | null
  items: SourcePlanItem[]
}

interface SourcePlanVersion {
  id: string
  version_number: number
  parent_version: number | null
  trigger_type: string
  decision_status: string
  change_reason: string
  change_summary: Record<string, any>
  evaluation: Record<string, any>
  created_by: string
  accepted_at: string | null
  created_at: string | null
}

const emptyForm: NewSourceForm = {
  name: '',
  type: 'rss',
  url: '',
  category: '',
  proxy_mode: 'auto',
}

const emptyPlanForm = {
  topic: '',
  focus: 'authoritative' as DiscoveryFocus,
  objective: '',
  review_cadence_days: 14,
}

const typeIcons = {
  rss: Rss,
  web: Globe,
  api: Globe,
}

const statusIcons = {
  ok: CheckCircle,
  warning: AlertCircle,
  error: XCircle,
}

const statusColors = {
  ok: 'text-green-500',
  warning: 'text-yellow-500',
  error: 'text-red-500',
}

const proxyStateClasses = {
  disabled: 'bg-muted text-muted-foreground',
  healthy: 'bg-green-100 text-green-700',
  degraded: 'bg-yellow-100 text-yellow-700',
  error: 'bg-red-100 text-red-700',
}

const proxyModeLabels: Record<ProxyMode, string> = {
  auto: '自动',
  always: '强制代理',
  never: '直连',
}

export function SourcesManager() {
  const [sources, setSources] = useState<Source[]>([])
  const [sourcePlans, setSourcePlans] = useState<SourcePlan[]>([])
  const [proxySettings, setProxySettings] = useState<ProxySettings>({
    enabled: false,
    http_proxy: '',
    socks_proxy: '',
    auto_detect_domains: true,
    test_url: 'https://httpbin.org/ip',
  })
  const [loading, setLoading] = useState(true)
  const [savingProxy, setSavingProxy] = useState(false)
  const [testingProxy, setTestingProxy] = useState(false)
  const [refreshingId, setRefreshingId] = useState<string | null>(null)
  const [savingSourceId, setSavingSourceId] = useState<string | null>(null)
  const [subscribingPlanItemId, setSubscribingPlanItemId] = useState<string | null>(null)
  const [refreshingPlanId, setRefreshingPlanId] = useState<string | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newSource, setNewSource] = useState<NewSourceForm>(emptyForm)
  const [planForm, setPlanForm] = useState(emptyPlanForm)
  const [creatingPlan, setCreatingPlan] = useState(false)
  const [planVersions, setPlanVersions] = useState<Record<string, SourcePlanVersion[]>>({})
  const [loadingVersionsPlanId, setLoadingVersionsPlanId] = useState<string | null>(null)

  useEffect(() => {
    void loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [sourcesRes, proxyRes] = await Promise.all([
        fetch('/api/sources'),
        fetch('/api/settings/proxy'),
      ])

      if (sourcesRes.ok) {
        const sourcesData = await sourcesRes.json()
        setSources(sourcesData)
      }

      if (proxyRes.ok) {
        const proxyData = await proxyRes.json()
        setProxySettings(proxyData)
      }

      await loadSourcePlans()
    } catch (error) {
      console.error('Failed to load sources settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveProxy = async () => {
    setSavingProxy(true)
    try {
      const res = await fetch('/api/settings/proxy', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          enabled: proxySettings.enabled,
          http_proxy: proxySettings.http_proxy,
          socks_proxy: proxySettings.socks_proxy,
          auto_detect_domains: proxySettings.auto_detect_domains,
          test_url: proxySettings.test_url,
        }),
      })

      if (res.ok) {
        const data = await res.json()
        setProxySettings((prev) => ({
          ...prev,
          ...data,
          status: data.status_info,
        }))
        await loadSourcesOnly()
      }
    } catch (error) {
      console.error('Failed to save proxy settings:', error)
    } finally {
      setSavingProxy(false)
    }
  }

  const testProxy = async () => {
    setTestingProxy(true)
    try {
      const res = await fetch('/api/settings/proxy/test', {
        method: 'POST',
      })
      if (res.ok) {
        const data = await res.json()
        setProxySettings((prev) => ({
          ...prev,
          ...data.proxy,
          status: data.status_info,
        }))
      }
    } catch (error) {
      console.error('Failed to test proxy settings:', error)
    } finally {
      setTestingProxy(false)
    }
  }

  const loadSourcesOnly = async () => {
    try {
      const res = await fetch('/api/sources')
      if (res.ok) {
        const data = await res.json()
        setSources(data)
      }
    } catch (error) {
      console.error('Failed to reload sources:', error)
    }
  }

  const loadSourcePlans = async () => {
    try {
      const res = await fetch('/api/sources/plans')
      if (res.ok) {
        const data = await res.json()
        setSourcePlans(data)
      }
    } catch (error) {
      console.error('Failed to load source plans:', error)
    }
  }

  const toggleEnabled = async (id: string) => {
    try {
      const res = await fetch(`/api/sources/${id}/toggle`, { method: 'POST' })
      if (res.ok) {
        const data = await res.json()
        setSources((prev) =>
          prev.map((source) =>
            source.id === id ? { ...source, enabled: data.enabled } : source
          )
        )
      }
    } catch (error) {
      console.error('Failed to toggle source:', error)
    }
  }

  const updateSourceProxy = async (id: string, proxyMode: ProxyMode) => {
    setSavingSourceId(id)
    try {
      const res = await fetch(`/api/sources/${id}/proxy`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ proxy_mode: proxyMode }),
      })
      if (res.ok) {
        const updated = await res.json()
        setSources((prev) =>
          prev.map((source) => (source.id === id ? updated : source))
        )
      }
    } catch (error) {
      console.error('Failed to update source proxy mode:', error)
    } finally {
      setSavingSourceId(null)
    }
  }

  const refreshSource = async (id: string) => {
    setRefreshingId(id)
    try {
      await fetch(`/api/sources/${id}/refresh`, { method: 'POST' })
    } catch (error) {
      console.error('Failed to refresh source:', error)
    } finally {
      setRefreshingId(null)
    }
  }

  const deleteSource = async (id: string) => {
    if (!window.confirm('确定删除这个信息源吗？')) return

    try {
      const res = await fetch(`/api/sources/${id}`, { method: 'DELETE' })
      if (res.ok) {
        setSources((prev) => prev.filter((source) => source.id !== id))
      }
    } catch (error) {
      console.error('Failed to delete source:', error)
    }
  }

  const addSource = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    try {
      const res = await fetch('/api/sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSource),
      })
      if (res.ok) {
        const created = await res.json()
        setSources((prev) => [created, ...prev])
        setNewSource(emptyForm)
        setShowAddForm(false)
      }
    } catch (error) {
      console.error('Failed to add source:', error)
    }
  }

  const createSourcePlan = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!planForm.topic.trim() || creatingPlan) return

    setCreatingPlan(true)
    try {
      const res = await fetch('/api/sources/plans', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(planForm),
      })
      if (res.ok) {
        const created = await res.json()
        setSourcePlans((prev) => [created, ...prev.filter((item) => item.id !== created.id)])
        setPlanForm(emptyPlanForm)
      }
    } catch (error) {
      console.error('Failed to create source plan:', error)
    } finally {
      setCreatingPlan(false)
    }
  }

  const subscribePlanItem = async (plan: SourcePlan, item: SourcePlanItem) => {
    setSubscribingPlanItemId(item.id)
    try {
      const res = await fetch(`/api/sources/plans/${plan.id}/items/${item.id}/subscribe`, {
        method: 'POST',
      })
      if (res.ok) {
        const created = await res.json()
        setSources((prev) => {
          const next = [created, ...prev.filter((source) => source.id !== created.id)]
          return next
        })
        await loadSourcePlans()
      }
    } catch (error) {
      console.error('Failed to subscribe plan item:', error)
    } finally {
      setSubscribingPlanItemId(null)
    }
  }

  const refreshSourcePlan = async (planId: string) => {
    setRefreshingPlanId(planId)
    try {
      const res = await fetch(`/api/sources/plans/${planId}/refresh`, {
        method: 'POST',
      })
      if (res.ok) {
        const refreshed = await res.json()
        setSourcePlans((prev) => [refreshed, ...prev.filter((plan) => plan.id !== refreshed.id)])
      }
    } catch (error) {
      console.error('Failed to refresh source plan:', error)
    } finally {
      setRefreshingPlanId(null)
    }
  }

  const loadPlanVersions = async (planId: string) => {
    setLoadingVersionsPlanId(planId)
    try {
      const res = await fetch(`/api/sources/plans/${planId}/versions`)
      if (res.ok) {
        const data = await res.json()
        setPlanVersions((prev) => ({ ...prev, [planId]: data }))
      }
    } catch (error) {
      console.error('Failed to load source plan versions:', error)
    } finally {
      setLoadingVersionsPlanId(null)
    }
  }

  const proxyStatus = proxySettings.status
  const proxyState = proxyStatus?.state ?? 'disabled'

  return (
    <div className="space-y-6">
      <section className="rounded-xl border bg-card p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">Source Intelligence</h2>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              围绕主题生成建源计划，区分长期关注对象、低频复查对象和复杂获取策略，再将候选项订阅为真实信息源。
            </p>
          </div>
          <button
            type="button"
            onClick={() => void loadSourcePlans()}
            className="inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-muted transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            刷新计划
          </button>
        </div>

        <form onSubmit={createSourcePlan} className="mt-5 grid gap-4 md:grid-cols-2">
          <div className="md:col-span-2">
            <label className="mb-1 block text-sm font-medium">主题</label>
            <input
              type="text"
              value={planForm.topic}
              onChange={(event) => setPlanForm((prev) => ({ ...prev, topic: event.target.value }))}
              className="w-full rounded-lg border bg-background px-3 py-2"
              placeholder="例如：AI coding agents、量化投资数据源、认知架构研究"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">关注重点</label>
            <select
              value={planForm.focus}
              onChange={(event) => setPlanForm((prev) => ({ ...prev, focus: event.target.value as DiscoveryFocus }))}
              className="w-full rounded-lg border bg-background px-3 py-2"
            >
              <option value="authoritative">权威理解</option>
              <option value="latest">最新动态</option>
              <option value="frontier">前沿研究</option>
              <option value="method">方法与工具</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">复查周期（天）</label>
            <input
              type="number"
              min={1}
              max={180}
              value={planForm.review_cadence_days}
              onChange={(event) =>
                setPlanForm((prev) => ({
                  ...prev,
                  review_cadence_days: Number(event.target.value || 14),
                }))
              }
              className="w-full rounded-lg border bg-background px-3 py-2"
            />
          </div>
          <div className="md:col-span-2">
            <label className="mb-1 block text-sm font-medium">目标</label>
            <textarea
              value={planForm.objective}
              onChange={(event) => setPlanForm((prev) => ({ ...prev, objective: event.target.value }))}
              className="min-h-[84px] w-full rounded-lg border bg-background px-3 py-2"
              placeholder="例如：建立一个持续跟踪 coding agent、agent team、workflow/skill 演化的来源集合"
            />
          </div>
          <div className="md:col-span-2 flex justify-end">
            <button
              type="submit"
              disabled={creatingPlan || !planForm.topic.trim()}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {creatingPlan ? <Loader2 className="h-4 w-4 animate-spin" /> : <Brain className="h-4 w-4" />}
              生成建源计划
            </button>
          </div>
        </form>

        <div className="mt-6 space-y-4">
          {sourcePlans.length === 0 ? (
            <div className="rounded-lg border border-dashed p-6 text-sm text-muted-foreground">
              还没有 source plan。先围绕一个主题生成建源计划，再选择候选项进入真实信息源。
            </div>
          ) : (
            sourcePlans.map((plan) => (
              <div key={plan.id} className="rounded-xl border p-4">
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-base font-semibold">{plan.topic}</h3>
                      <span className="rounded-full bg-sky-100 px-2 py-0.5 text-xs text-sky-700">
                        {plan.focus}
                      </span>
                      <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                        {plan.planning_brain}
                      </span>
                    </div>
                    {plan.objective && (
                      <p className="mt-1 text-sm text-muted-foreground">{plan.objective}</p>
                    )}
                    <p className="mt-2 text-xs text-muted-foreground">
                      review cadence: {plan.review_cadence_days} days · items: {plan.items.length} · review status: {plan.review_status} · current v{plan.current_version} / latest v{plan.latest_version}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      last reviewed: {plan.last_reviewed_at ? new Date(plan.last_reviewed_at).toLocaleString() : 'never'} · next due: {plan.next_review_due_at ? new Date(plan.next_review_due_at).toLocaleString() : 'not scheduled'}
                    </p>
                    {plan.latest_version > plan.current_version && (
                      <p className="mt-1 text-xs text-amber-700">
                        newer candidate version pending review
                      </p>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={() => void loadPlanVersions(plan.id)}
                      disabled={loadingVersionsPlanId === plan.id}
                      className="inline-flex items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-muted transition-colors disabled:opacity-50"
                    >
                      {loadingVersionsPlanId === plan.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Save className="h-4 w-4" />
                      )}
                      查看版本
                    </button>
                    <button
                      type="button"
                      onClick={() => void refreshSourcePlan(plan.id)}
                      disabled={refreshingPlanId === plan.id}
                      className="inline-flex items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-muted transition-colors disabled:opacity-50"
                    >
                      {refreshingPlanId === plan.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <RefreshCw className="h-4 w-4" />
                      )}
                      重新评审
                    </button>
                  </div>
                </div>

                {planVersions[plan.id] && planVersions[plan.id].length > 0 && (
                  <div className="mt-4 rounded-lg border bg-muted/30 p-3">
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <div className="text-sm font-medium">版本记录</div>
                      <div className="text-xs text-muted-foreground">
                        latest {planVersions[plan.id][0]?.trigger_type} · {planVersions[plan.id][0]?.decision_status}
                      </div>
                    </div>
                    <div className="space-y-2">
                      {planVersions[plan.id].slice(0, 3).map((version) => (
                        <div key={version.id} className="rounded-md border bg-background p-2">
                          <div className="flex flex-wrap items-center gap-2 text-xs">
                            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-700">
                              v{version.version_number}
                            </span>
                            <span className="rounded-full bg-muted px-2 py-0.5 text-muted-foreground">
                              {version.trigger_type}
                            </span>
                            <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-emerald-700">
                              {version.decision_status}
                            </span>
                            <span className="text-muted-foreground">
                              {version.parent_version ? `from v${version.parent_version}` : 'baseline'}
                            </span>
                          </div>
                          <div className="mt-2 text-sm">{version.change_reason}</div>
                          <div className="mt-1 text-xs text-muted-foreground">
                            {version.evaluation?.reasons?.join?.(' · ') || 'No evaluation notes'}
                          </div>
                          {version.change_summary?.summary && (
                            <div className="mt-2 grid gap-1 text-xs text-muted-foreground md:grid-cols-2">
                              <div>
                                avg score delta:{' '}
                                {Number(version.change_summary.summary.average_score_delta ?? 0).toFixed(2)}
                              </div>
                              <div>
                                evidence delta:{' '}
                                {version.change_summary.summary.evidence_delta ?? 0}
                              </div>
                              <div>
                                trusted delta:{' '}
                                {version.change_summary.summary.trusted_count_delta ?? 0}
                              </div>
                              <div>
                                stale:{' '}
                                {version.change_summary.summary.stale_count ?? 0}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-4 grid gap-3">
                  {plan.items.map((item) => (
                    <div key={item.id} className="rounded-lg border bg-background p-3">
                      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-medium">{item.name}</span>
                            <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-800">
                              {item.authority_tier}
                            </span>
                            <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                              {item.execution_strategy}
                            </span>
                            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-700">
                              {item.status}
                            </span>
                          </div>
                          <div className="mt-1 text-xs text-muted-foreground break-all">{item.url}</div>
                          <div className="mt-2 text-sm text-muted-foreground">{item.rationale}</div>
                          <div className="mt-2 text-xs text-muted-foreground">
                            authority score: {item.authority_score.toFixed(2)} · review every {item.review_cadence_days} days
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => void subscribePlanItem(plan, item)}
                          disabled={subscribingPlanItemId === item.id || item.status === 'subscribed'}
                          className="inline-flex items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-muted transition-colors disabled:opacity-50"
                        >
                          {subscribingPlanItemId === item.id ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Plus className="h-4 w-4" />
                          )}
                          订阅为信息源
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      <section className="rounded-xl border bg-card p-5">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold">代理设置</h2>
              <span
                className={cn(
                  'rounded-full px-2 py-1 text-xs font-medium',
                  proxyStateClasses[proxyState]
                )}
              >
                {proxyState}
              </span>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              全局开关控制是否允许信息源走代理。单个信息源仍可设置自动、强制代理或直连。
            </p>
            {proxyStatus && (
              <p className="mt-2 text-sm text-muted-foreground">
                {proxyStatus.message}
              </p>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => void testProxy()}
              className="inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm hover:bg-muted transition-colors"
              disabled={testingProxy}
            >
              {testingProxy ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              测试代理
            </button>
            <button
              onClick={() => void saveProxy()}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 transition-colors"
              disabled={savingProxy}
            >
              {savingProxy ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              保存设置
            </button>
          </div>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <label className="rounded-lg border p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="font-medium">启用代理</div>
                <div className="text-sm text-muted-foreground">
                  关闭后所有信息源都直接连接，不再尝试代理。
                </div>
              </div>
              <input
                type="checkbox"
                className="h-4 w-4"
                checked={proxySettings.enabled}
                onChange={(event) =>
                  setProxySettings((prev) => ({
                    ...prev,
                    enabled: event.target.checked,
                  }))
                }
              />
            </div>
          </label>

          <label className="rounded-lg border p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="font-medium">自动识别需要代理的站点</div>
                <div className="text-sm text-muted-foreground">
                  仅对命中的海外域名自动走代理，其他源保持直连。
                </div>
              </div>
              <input
                type="checkbox"
                className="h-4 w-4"
                checked={proxySettings.auto_detect_domains}
                onChange={(event) =>
                  setProxySettings((prev) => ({
                    ...prev,
                    auto_detect_domains: event.target.checked,
                  }))
                }
              />
            </div>
          </label>

          <div>
            <label className="mb-1 block text-sm font-medium">HTTP Proxy</label>
            <input
              type="text"
              value={proxySettings.http_proxy}
              onChange={(event) =>
                setProxySettings((prev) => ({
                  ...prev,
                  http_proxy: event.target.value,
                }))
              }
              className="w-full rounded-lg border bg-background px-3 py-2"
              placeholder="http://127.0.0.1:10808"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">SOCKS Proxy</label>
            <input
              type="text"
              value={proxySettings.socks_proxy}
              onChange={(event) =>
                setProxySettings((prev) => ({
                  ...prev,
                  socks_proxy: event.target.value,
                }))
              }
              className="w-full rounded-lg border bg-background px-3 py-2"
              placeholder="socks5://127.0.0.1:10808"
            />
          </div>
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <ProxyProbeCard title="HTTP" probe={proxyStatus?.http} />
          <ProxyProbeCard title="SOCKS" probe={proxyStatus?.socks} />
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">共 {sources.length} 个信息源</div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => void loadData()}
              className="inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm hover:bg-muted transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              刷新
            </button>
            <button
              onClick={() => setShowAddForm((prev) => !prev)}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              <Plus className="h-4 w-4" />
              添加信息源
            </button>
          </div>
        </div>

        {showAddForm && (
          <form onSubmit={addSource} className="rounded-xl border bg-card p-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-1 block text-sm font-medium">名称</label>
                <input
                  type="text"
                  value={newSource.name}
                  onChange={(event) =>
                    setNewSource((prev) => ({ ...prev, name: event.target.value }))
                  }
                  className="w-full rounded-lg border bg-background px-3 py-2"
                  required
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium">类型</label>
                <select
                  value={newSource.type}
                  onChange={(event) =>
                    setNewSource((prev) => ({
                      ...prev,
                      type: event.target.value as SourceType,
                    }))
                  }
                  className="w-full rounded-lg border bg-background px-3 py-2"
                >
                  <option value="rss">RSS</option>
                  <option value="web">网页</option>
                  <option value="api">API</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="mb-1 block text-sm font-medium">URL</label>
                <input
                  type="url"
                  value={newSource.url}
                  onChange={(event) =>
                    setNewSource((prev) => ({ ...prev, url: event.target.value }))
                  }
                  className="w-full rounded-lg border bg-background px-3 py-2"
                  required
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium">分类</label>
                <input
                  type="text"
                  value={newSource.category}
                  onChange={(event) =>
                    setNewSource((prev) => ({
                      ...prev,
                      category: event.target.value,
                    }))
                  }
                  className="w-full rounded-lg border bg-background px-3 py-2"
                  required
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium">代理策略</label>
                <select
                  value={newSource.proxy_mode}
                  onChange={(event) =>
                    setNewSource((prev) => ({
                      ...prev,
                      proxy_mode: event.target.value as ProxyMode,
                    }))
                  }
                  className="w-full rounded-lg border bg-background px-3 py-2"
                >
                  <option value="auto">自动</option>
                  <option value="always">强制代理</option>
                  <option value="never">直连</option>
                </select>
              </div>
            </div>

            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="rounded-lg border px-4 py-2 text-sm hover:bg-muted transition-colors"
              >
                取消
              </button>
              <button
                type="submit"
                className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                创建
              </button>
            </div>
          </form>
        )}

        <div className="rounded-xl border overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center gap-2 p-8 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              正在加载信息源配置...
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">名称</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">状态</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">代理策略</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">当前路由</th>
                  <th className="px-4 py-3 text-right text-sm font-medium">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {sources.map((source) => {
                  const TypeIcon = typeIcons[source.type]
                  const StatusIcon = statusIcons[source.status]

                  return (
                    <tr key={source.id} className={cn(!source.enabled && 'opacity-50')}>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <TypeIcon className="h-4 w-4 text-muted-foreground" />
                          <div>
                            <div className="font-medium">{source.name}</div>
                            <div className="text-xs text-muted-foreground">
                              {source.category}
                            </div>
                            <div className="mt-1 text-xs text-muted-foreground">
                              {source.url}
                            </div>
                          </div>
                        </div>
                      </td>

                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2 text-sm">
                          <StatusIcon className={cn('h-4 w-4', statusColors[source.status])} />
                          <span>{source.enabled ? '已启用' : '已禁用'}</span>
                        </div>
                      </td>

                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <select
                            value={source.proxy_mode}
                            onChange={(event) =>
                              void updateSourceProxy(
                                source.id,
                                event.target.value as ProxyMode
                              )
                            }
                            className="rounded-lg border bg-background px-3 py-2 text-sm"
                            disabled={savingSourceId === source.id}
                          >
                            <option value="auto">自动</option>
                            <option value="always">强制代理</option>
                            <option value="never">直连</option>
                          </select>
                          {savingSourceId === source.id && (
                            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                          )}
                        </div>
                      </td>

                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        <div>{source.proxy_effective ? '代理' : '直连'}</div>
                        <div className="text-xs">{formatProxyReason(source.proxy_reason)}</div>
                      </td>

                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => void toggleEnabled(source.id)}
                            className={cn(
                              'rounded px-2 py-1 text-xs font-medium transition-colors',
                              source.enabled
                                ? 'bg-green-100 text-green-700 hover:bg-green-200'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            )}
                          >
                            {source.enabled ? '停用' : '启用'}
                          </button>
                          <button
                            onClick={() => void refreshSource(source.id)}
                            className="rounded p-1 hover:bg-muted transition-colors"
                            title="刷新"
                          >
                            {refreshingId === source.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <RefreshCw className="h-4 w-4" />
                            )}
                          </button>
                          <button
                            onClick={() => void deleteSource(source.id)}
                            className="rounded p-1 text-destructive hover:bg-muted transition-colors"
                            title="删除"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  )
}

function ProxyProbeCard({
  title,
  probe,
}: {
  title: string
  probe?: ProxyProbe
}) {
  if (!probe) {
    return (
      <div className="rounded-lg border p-4 text-sm text-muted-foreground">
        {title}: 暂无检测结果
      </div>
    )
  }

  return (
    <div className="rounded-lg border p-4">
      <div className="font-medium">{title}</div>
      <div className="mt-2 text-sm text-muted-foreground">
        配置: {probe.configured ? '已配置' : '未配置'}
      </div>
      <div className="text-sm text-muted-foreground">
        端口: {probe.reachable ? '可连接' : '不可连接'}
      </div>
      <div className="text-sm text-muted-foreground">
        可用: {probe.working ? '正常' : '不可用'}
      </div>
      {probe.supported === false && (
        <div className="mt-1 text-sm text-yellow-600">当前环境缺少 SOCKS 支持</div>
      )}
      {probe.error && (
        <div className="mt-1 text-sm text-red-600 break-all">{probe.error}</div>
      )}
    </div>
  )
}

function formatProxyReason(reason: string) {
  if (reason === 'global_disabled') return '全局关闭'
  if (reason === 'source_never') return '单源直连'
  if (reason === 'source_forced') return '单源强制代理'
  if (reason === 'auto_detection_disabled') return '关闭自动识别'
  if (reason === 'direct') return '未命中代理规则'
  if (reason.startsWith('domain:')) return `命中 ${reason.replace('domain:', '')}`
  return reason
}
