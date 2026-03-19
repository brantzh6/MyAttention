'use client'

import { type FormEvent, useEffect, useState } from 'react'
import {
  AlertCircle,
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

const emptyForm: NewSourceForm = {
  name: '',
  type: 'rss',
  url: '',
  category: '',
  proxy_mode: 'auto',
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
  const [showAddForm, setShowAddForm] = useState(false)
  const [newSource, setNewSource] = useState<NewSourceForm>(emptyForm)

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

  const proxyStatus = proxySettings.status
  const proxyState = proxyStatus?.state ?? 'disabled'

  return (
    <div className="space-y-6">
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
