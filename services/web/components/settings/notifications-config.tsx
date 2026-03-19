'use client'

import { useState, useEffect } from 'react'
import { Bell, Send, CheckCircle, XCircle, Loader2, Info, Server, RefreshCw, AlertTriangle, Plus, Trash2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface NotificationChannel {
  id: string
  name: string
  type: 'feishu' | 'dingtalk'
  webhook_url: string
  secret?: string
  // 飞书应用模式
  app_id?: string
  app_secret?: string
  default_target_id?: string
  enabled: boolean
  last_test: string | null
  test_status: string | null
  // 保存状态
  save_status?: 'idle' | 'saving' | 'success' | 'error'
  save_message?: string
  ws_test_result?: any
}

interface PushSettings {
  push_important: boolean
  push_daily_digest: boolean
  digest_times: string[]
  importance_threshold: number
}

// 服务状态接口
interface ServiceStatus {
  name: string
  status: string
  running: boolean
  type?: string
  details?: any
  error?: string
}

interface SystemHealth {
  timestamp: string
  overall_status: string
  summary: {
    total: number
    healthy: number
    unhealthy: number
    error: number
  }
  databases: ServiceStatus[]
  services: ServiceStatus[]
  external: ServiceStatus[]
}

export function NotificationsConfig() {
  const [channels, setChannels] = useState<NotificationChannel[]>([])
  const [pushSettings, setPushSettings] = useState<PushSettings>({
    push_important: true,
    push_daily_digest: true,
    digest_times: ['09:00', '18:00'],
    importance_threshold: 70,
  })
  const [testingId, setTestingId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [feishuMode, setFeishuMode] = useState<'webhook' | 'app'>('app')
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null)
  const [healthLoading, setHealthLoading] = useState(false)

  // Load data from API
  useEffect(() => {
    loadData()
    loadSystemHealth()
    // 定时刷新系统健康状态
    const interval = setInterval(loadSystemHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [channelsRes, settingsRes] = await Promise.all([
        fetch('/api/settings/notifications/channels'),
        fetch('/api/settings/notifications/push'),
      ])

      if (channelsRes.ok) {
        const channelsData = await channelsRes.json()
        setChannels(channelsData)
      }

      if (settingsRes.ok) {
        const settingsData = await settingsRes.json()
        setPushSettings(settingsData)
      }
    } catch (error) {
      console.error('Failed to load notification settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleEnabled = async (id: string) => {
    const channel = channels.find(c => c.id === id)
    if (!channel) return

    const updatedChannel = { ...channel, enabled: !channel.enabled }

    try {
      const res = await fetch(`/api/settings/notifications/channels/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedChannel),
      })

      if (res.ok) {
        setChannels(channels.map(c => c.id === id ? updatedChannel : c))
      }
    } catch (error) {
      console.error('Failed to update channel:', error)
    }
  }

  const testNotification = async (id: string) => {
    setTestingId(id)

    try {
      const res = await fetch(`/api/settings/notifications/channels/${id}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: '🔔 测试通知',
          message: '这是一条来自 MyAttention 的测试消息',
        }),
      })

      const data = await res.json()

      setChannels(channels.map(c =>
        c.id === id
          ? {
              ...c,
              last_test: data.timestamp || new Date().toISOString(),
              test_status: data.status === 'success' ? 'success' : 'failed',
            }
          : c
      ))
    } catch (error) {
      console.error('Failed to test notification:', error)
      setChannels(channels.map(c =>
        c.id === id
          ? { ...c, test_status: 'error' }
          : c
      ))
    } finally {
      setTestingId(null)
    }
  }

  const updateWebhook = (id: string, url: string) => {
    setChannels(channels.map(c => c.id === id ? { ...c, webhook_url: url } : c))
  }

  const updateSecret = (id: string, secret: string) => {
    setChannels(channels.map(c => c.id === id ? { ...c, secret } : c))
  }

  const updateFeishuApp = (id: string, field: 'app_id' | 'app_secret' | 'default_target_id', value: string) => {
    setChannels(channels.map(c => c.id === id ? { ...c, [field]: value } : c))
  }

  const saveChannel = async (id: string, skipTest: boolean = false) => {
    const channel = channels.find(c => c.id === id)
    if (!channel) return

    // 设置保存状态
    setChannels(channels.map(c => c.id === id ? { ...c, save_status: 'saving', save_message: '' } : c))

    try {
      const res = await fetch(`/api/settings/notifications/channels/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...channel,
          test_connection: !skipTest, // 是否测试连接
        }),
      })

      const data = await res.json()

      if (res.ok && data.status !== 'error') {
        // 保存成功
        setChannels(channels.map(c => c.id === id ? {
          ...c,
          save_status: 'success',
          save_message: '保存成功',
          ws_test_result: data.ws_test
        } : c))

        // 3秒后清除状态
        setTimeout(() => {
          setChannels(channels.map(c => c.id === id ? { ...c, save_status: 'idle', save_message: '' } : c))
        }, 3000)
      } else {
        // 保存失败（通常是WebSocket测试失败）
        const errorMsg = data.message || data.detail || '保存失败'
        const wsHint = data.hint || ''
        const step = data.step || ''

        setChannels(channels.map(c => c.id === id ? {
          ...c,
          save_status: 'error',
          save_message: `${errorMsg}${wsHint ? '\n' + wsHint : ''}`,
          ws_test_result: data.ws_test
        } : c))
      }
    } catch (error: any) {
      setChannels(channels.map(c => c.id === id ? {
        ...c,
        save_status: 'error',
        save_message: error.message || '保存失败，请检查网络'
      } : c))
    }
  }

  // 创建新渠道
  const createChannel = async (type: 'feishu' | 'dingtalk', name: string) => {
    setSaving(true)
    try {
      const res = await fetch('/api/settings/notifications/channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          type,
          test_connection: false, // 新建时不测试
        }),
      })

      const data = await res.json()

      if (res.ok && data.channel) {
        // 重新加载渠道列表
        await loadData()
      } else {
        console.error('Failed to create channel:', data)
        alert('创建失败: ' + (data.detail || data.message || '未知错误'))
      }
    } catch (error: any) {
      console.error('Failed to create channel:', error)
      alert('创建失败: ' + error.message)
    } finally {
      setSaving(false)
    }
  }

  const deleteChannel = async (id: string) => {
    if (!confirm('确定要删除这个通知渠道吗？')) return

    try {
      const res = await fetch(`/api/settings/notifications/channels/${id}`, {
        method: 'DELETE',
      })

      if (res.ok) {
        // 从列表中移除
        setChannels(channels.filter(c => c.id !== id))
      }
    } catch (error) {
      console.error('Failed to delete channel:', error)
    }
  }

  const updatePushSettings = async (key: keyof PushSettings, value: any) => {
    const newSettings = { ...pushSettings, [key]: value }
    setPushSettings(newSettings)

    try {
      await fetch('/api/settings/notifications/push', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings),
      })
    } catch (error) {
      console.error('Failed to update push settings:', error)
    }
  }

  const loadSystemHealth = async () => {
    setHealthLoading(true)
    try {
      const res = await fetch('/api/settings/system')
      if (res.ok) {
        const data = await res.json()
        setSystemHealth(data)
      }
    } catch (error) {
      console.error('Failed to load system health:', error)
    } finally {
      setHealthLoading(false)
    }
  }

  // 获取状态图标和颜色
  const getStatusIcon = (status: string, running: boolean) => {
    if (!running || status === 'error') {
      return <XCircle className="h-4 w-4 text-red-500" />
    }
    if (status === 'unhealthy' || status === 'degraded') {
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />
    }
    return <CheckCircle className="h-4 w-4 text-green-500" />
  }

  const getStatusText = (status: string, running: boolean) => {
    if (!running || status === 'error') return '离线'
    if (status === 'unhealthy') return '异常'
    if (status === 'degraded') return '降级'
    if (status === 'not_configured') return '未配置'
    return '正常'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* System Status Panel */}
      <div className="p-4 rounded-lg border bg-card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Server className="h-5 w-5 text-primary" />
            <h3 className="font-medium">系统状态</h3>
            {systemHealth && (
              <span className={cn(
                "px-2 py-0.5 rounded text-xs font-medium",
                systemHealth.overall_status === 'healthy' && "bg-green-100 text-green-700",
                systemHealth.overall_status === 'degraded' && "bg-yellow-100 text-yellow-700",
                systemHealth.overall_status === 'error' && "bg-red-100 text-red-700"
              )}>
                {systemHealth.overall_status === 'healthy' ? '全部正常' :
                 systemHealth.overall_status === 'degraded' ? '部分异常' : '服务异常'}
              </span>
            )}
          </div>
          <button
            onClick={loadSystemHealth}
            disabled={healthLoading}
            className="flex items-center gap-1 px-2 py-1 rounded text-sm hover:bg-muted disabled:opacity-50"
          >
            <RefreshCw className={cn("h-3 w-3", healthLoading && "animate-spin")} />
            刷新
          </button>
        </div>

        {healthLoading && !systemHealth ? (
          <div className="flex items-center justify-center p-4">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          </div>
        ) : systemHealth ? (
          <div className="space-y-3">
            {/* 数据库服务 */}
            <div>
              <p className="text-xs text-muted-foreground mb-2">数据库服务</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {systemHealth.databases.map((db) => (
                  <div key={db.name} className="flex items-center gap-2 p-2 rounded bg-muted/50">
                    {getStatusIcon(db.status, db.running)}
                    <div>
                      <p className="text-xs font-medium">{db.name}</p>
                      <p className="text-xs text-muted-foreground">{getStatusText(db.status, db.running)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* API 服务 */}
            <div>
              <p className="text-xs text-muted-foreground mb-2">核心服务</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {systemHealth.services.map((svc) => (
                  <div key={svc.name} className="flex items-center gap-2 p-2 rounded bg-muted/50">
                    {getStatusIcon(svc.status, svc.running)}
                    <div>
                      <p className="text-xs font-medium">{svc.name}</p>
                      <p className="text-xs text-muted-foreground">{getStatusText(svc.status, svc.running)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 外部服务 */}
            <div>
              <p className="text-xs text-muted-foreground mb-2">外部依赖</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {systemHealth.external.map((ext) => (
                  <div key={ext.name} className="flex items-center gap-2 p-2 rounded bg-muted/50">
                    {getStatusIcon(ext.status, ext.running)}
                    <div>
                      <p className="text-xs font-medium">{ext.name}</p>
                      <p className="text-xs text-muted-foreground">{getStatusText(ext.status, ext.running)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 汇总信息 */}
            <div className="pt-2 border-t text-xs text-muted-foreground">
              <span>服务状态: </span>
              <span className="text-green-600">{systemHealth.summary.healthy} 正常</span>
              {systemHealth.summary.unhealthy > 0 && (
                <span className="text-yellow-600"> / {systemHealth.summary.unhealthy} 异常</span>
              )}
              {systemHealth.summary.error > 0 && (
                <span className="text-red-600"> / {systemHealth.summary.error} 错误</span>
              )}
              <span className="ml-2">
                (最后更新: {new Date(systemHealth.timestamp).toLocaleTimeString('zh-CN')})
              </span>
            </div>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">加载中...</p>
        )}
      </div>

      {/* Push Settings */}
      <div className="p-4 rounded-lg border bg-card">
        <div className="flex items-center gap-2 mb-4">
          <Bell className="h-5 w-5 text-primary" />
          <h3 className="font-medium">推送策略</h3>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">推送触发条件</label>
            <p className="text-xs text-muted-foreground mb-2">AI 将根据信息重要性自动判断是否推送</p>
            <div className="flex gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={pushSettings.push_important}
                  onChange={(e) => updatePushSettings('push_important', e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm">重要信息即时推送</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={pushSettings.push_daily_digest}
                  onChange={(e) => updatePushSettings('push_daily_digest', e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm">每日简报定时推送</span>
              </label>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium">定时简报时间</label>
            <div className="flex gap-2 mt-2">
              {pushSettings.digest_times.map((time, index) => (
                <input
                  key={index}
                  type="time"
                  value={time}
                  onChange={(e) => {
                    const newTimes = [...pushSettings.digest_times]
                    newTimes[index] = e.target.value
                    updatePushSettings('digest_times', newTimes)
                  }}
                  className="px-3 py-1.5 rounded-md border bg-background text-sm"
                />
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              每天 {pushSettings.digest_times.join(' 和 ')} 推送简报
            </p>
          </div>

          <div>
            <label className="text-sm font-medium">重要性阈值</label>
            <p className="text-xs text-muted-foreground mb-2">只有重要性高于此阈值的信息才会即时推送</p>
            <input
              type="range"
              min="0"
              max="100"
              value={pushSettings.importance_threshold}
              onChange={(e) => updatePushSettings('importance_threshold', parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>低 (推送更多)</span>
              <span>{pushSettings.importance_threshold}%</span>
              <span>高 (只推重要)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Notification Channels */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-medium">通知渠道</h3>
          <div className="flex gap-2">
            <button
              onClick={() => {
                const name = prompt('请输入渠道名称（如：我的飞书）')
                if (name) createChannel('feishu', name)
              }}
              disabled={saving}
              className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-green-600 text-white text-sm hover:bg-green-700 disabled:opacity-50"
            >
              <Plus className="h-3 w-3" /> 添加飞书
            </button>
            <button
              onClick={() => {
                const name = prompt('请输入渠道名称（如：我的钉钉）')
                if (name) createChannel('dingtalk', name)
              }}
              disabled={saving}
              className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-blue-600 text-white text-sm hover:bg-blue-700 disabled:opacity-50"
            >
              <Plus className="h-3 w-3" /> 添加钉钉
            </button>
          </div>
        </div>

        {channels.length === 0 && (
          <div className="text-center py-8 text-muted-foreground border rounded-lg">
            <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>暂无通知渠道</p>
            <p className="text-xs mt-1">点击上方按钮添加飞书或钉钉渠道</p>
          </div>
        )}

        {channels.map((channel) => (
          <div key={channel.id} className="p-4 rounded-lg border bg-card">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="font-medium">{channel.name}</span>
                <span className="px-2 py-0.5 rounded bg-muted text-xs">
                  {channel.type === 'feishu' ? '飞书' : '钉钉'}
                </span>
              </div>

              <div className="flex items-center gap-2">
                {channel.test_status && (
                  <span className={cn(
                    'flex items-center gap-1 text-xs',
                    channel.test_status === 'success' ? 'text-green-600' : 'text-red-600'
                  )}>
                    {channel.test_status === 'success' ? (
                      <><CheckCircle className="h-3 w-3" /> 测试成功</>
                    ) : (
                      <><XCircle className="h-3 w-3" /> 测试失败</>
                    )}
                  </span>
                )}

                <button
                  onClick={() => toggleEnabled(channel.id)}
                  className={cn(
                    'px-3 py-1 rounded text-xs font-medium transition-colors',
                    channel.enabled
                      ? 'bg-green-100 text-green-700 hover:bg-green-200'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  )}
                >
                  {channel.enabled ? '启用' : '禁用'}
                </button>
              </div>
            </div>

            <div className="space-y-3">
              {channel.type === 'feishu' && (
                <>
                  {/* 飞书模式选择 */}
                  <div className="flex gap-2 mb-3">
                    <button
                      onClick={() => setFeishuMode('app')}
                      className={cn(
                        'px-3 py-1 rounded text-sm',
                        feishuMode === 'app' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                      )}
                    >
                      应用 API 模式（推荐）
                    </button>
                    <button
                      onClick={() => setFeishuMode('webhook')}
                      className={cn(
                        'px-3 py-1 rounded text-sm',
                        feishuMode === 'webhook' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                      )}
                    >
                      Webhook 模式
                    </button>
                  </div>

                  {feishuMode === 'app' ? (
                    <>
                      <div className="p-3 rounded bg-muted/50 mb-3">
                        <div className="flex items-start gap-2">
                          <Info className="h-4 w-4 text-blue-500 mt-0.5" />
                          <div className="text-xs text-muted-foreground">
                            <p className="font-medium text-foreground mb-1">应用 API 模式</p>
                            <p>1. 在飞书开发者后台创建企业自建应用</p>
                            <p>2. 开通 im:message, im:chat 权限</p>
                            <p>3. 将应用添加到目标群聊</p>
                            <p>4. 获取群聊 ID：群设置 → 群信息 → 会话 ID</p>
                          </div>
                        </div>
                      </div>

                      <div>
                        <label className="text-xs text-muted-foreground">App ID</label>
                        <input
                          type="text"
                          value={channel.app_id || ''}
                          onChange={(e) => updateFeishuApp(channel.id, 'app_id', e.target.value)}
                          placeholder="cli_xxxxxxxxxxxxxxxxx"
                          className="w-full px-3 py-1.5 rounded-md border bg-background text-sm mt-1"
                        />
                      </div>

                      <div>
                        <label className="text-xs text-muted-foreground">App Secret</label>
                        <input
                          type="password"
                          value={channel.app_secret || ''}
                          onChange={(e) => updateFeishuApp(channel.id, 'app_secret', e.target.value)}
                          placeholder="应用密钥"
                          className="w-full px-3 py-1.5 rounded-md border bg-background text-sm mt-1"
                        />
                      </div>

                      <div>
                        <label className="text-xs text-muted-foreground">默认推送目标（群聊 ID）</label>
                        <input
                          type="text"
                          value={channel.default_target_id || ''}
                          onChange={(e) => updateFeishuApp(channel.id, 'default_target_id', e.target.value)}
                          placeholder="oc_xxxxxxxxxxxxxxxxxxxxx"
                          className="w-full px-3 py-1.5 rounded-md border bg-background text-sm mt-1"
                        />
                        <p className="text-xs text-muted-foreground mt-1">
                          群聊格式: oc_xxx，用户格式: ou_xxx
                        </p>
                      </div>
                    </>
                  ) : (
                    <div>
                      <label className="text-xs text-muted-foreground">Webhook URL</label>
                      <input
                        type="url"
                        value={channel.webhook_url || ''}
                        onChange={(e) => updateWebhook(channel.id, e.target.value)}
                        placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
                        className="w-full px-3 py-1.5 rounded-md border bg-background text-sm mt-1"
                      />
                    </div>
                  )}
                </>
              )}

              {channel.type === 'dingtalk' && (
                <>
                  <div>
                    <label className="text-xs text-muted-foreground">Webhook URL</label>
                    <input
                      type="url"
                      value={channel.webhook_url || ''}
                      onChange={(e) => updateWebhook(channel.id, e.target.value)}
                      placeholder="https://oapi.dingtalk.com/robot/send?access_token=xxx"
                      className="w-full px-3 py-1.5 rounded-md border bg-background text-sm mt-1"
                    />
                  </div>

                  <div>
                    <label className="text-xs text-muted-foreground">签名密钥 (Secret)</label>
                    <input
                      type="password"
                      value={channel.secret || ''}
                      onChange={(e) => updateSecret(channel.id, e.target.value)}
                      placeholder="SECxxx..."
                      className="w-full px-3 py-1.5 rounded-md border bg-background text-sm mt-1"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      推荐使用加签方式，提高安全性
                    </p>
                  </div>
                </>
              )}

              <div className="flex gap-2 items-center">
                <button
                  onClick={() => saveChannel(channel.id)}
                  disabled={channel.save_status === 'saving'}
                  className={cn(
                    "px-3 py-1.5 rounded-md border text-sm hover:bg-muted disabled:opacity-50",
                    channel.save_status === 'success' && "border-green-500 text-green-600",
                    channel.save_status === 'error' && "border-red-500 text-red-600"
                  )}
                >
                  {channel.save_status === 'saving' ? (
                    <><Loader2 className="h-3 w-3 animate-spin inline" /> 保存中...</>
                  ) : channel.save_status === 'success' ? (
                    <><CheckCircle className="h-3 w-3 inline" /> 已保存</>
                  ) : channel.save_status === 'error' ? (
                    <><XCircle className="h-3 w-3 inline" /> 保存失败</>
                  ) : (
                    "保存并建立长链接"
                  )}
                </button>
                {/* 跳过测试直接保存 */}
                <button
                  onClick={() => saveChannel(channel.id, true)}
                  disabled={channel.save_status === 'saving'}
                  className="px-3 py-1.5 rounded-md border text-sm text-muted-foreground hover:bg-muted disabled:opacity-50"
                  title="跳过连接测试，直接保存配置"
                >
                  跳过测试保存
                </button>
                <button
                  onClick={() => testNotification(channel.id)}
                  disabled={testingId === channel.id}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-primary text-primary-foreground text-sm disabled:opacity-50"
                >
                  {testingId === channel.id ? (
                    <><Loader2 className="h-3 w-3 animate-spin" /> 发送中...</>
                  ) : (
                    <><Send className="h-3 w-3" /> 测试</>
                  )}
                </button>
                <button
                  onClick={() => deleteChannel(channel.id)}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-md border text-red-600 text-sm hover:bg-red-50"
                  title="删除渠道"
                >
                  <Trash2 className="h-3 w-3" />
                </button>
              </div>

              {/* 保存结果提示 */}
              {channel.save_message && (
                <div className={cn(
                  "p-2 rounded text-xs mt-2",
                  channel.save_status === 'success' && "bg-green-50 text-green-700",
                  channel.save_status === 'error' && "bg-red-50 text-red-700"
                )}>
                  {channel.save_message}
                </div>
              )}

              {channel.last_test && (
                <p className="text-xs text-muted-foreground">
                  上次测试: {new Date(channel.last_test).toLocaleString('zh-CN')}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Quick Test Section */}
      <div className="p-4 rounded-lg border bg-card">
        <h3 className="font-medium mb-3">快速测试</h3>
        <p className="text-xs text-muted-foreground mb-3">
          发送测试简报到已配置的渠道
        </p>
        <button
          onClick={async () => {
            const feishuChannel = channels.find(c => c.type === 'feishu' && c.enabled)
            if (feishuChannel) {
              await testNotification(feishuChannel.id)
            }
          }}
          className="px-3 py-1.5 rounded-md bg-primary text-primary-foreground text-sm"
        >
          发送测试简报
        </button>
      </div>
    </div>
  )
}