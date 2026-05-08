'use client'

import { useEffect, useMemo, useState } from 'react'
import { AlertTriangle, Check, Eye, EyeOff, KeyRound, Loader2, RefreshCw, X } from 'lucide-react'
import { apiClient, type LLMProvider } from '@/lib/api-client'
import { cn } from '@/lib/utils'

type ProviderView = LLMProvider & {
  apiKeySet: boolean
  priority: 'high' | 'medium' | 'low'
  useCase: string[]
}

const DEFAULT_PROVIDERS: ProviderView[] = [
  {
    id: '1',
    name: '通义千问 Max',
    provider: 'qwen',
    model: 'qwen-max',
    enabled: false,
    apiKeySet: false,
    priority: 'high',
    useCase: ['摘要', '中文对话', '创意写作'],
  },
  {
    id: '2',
    name: 'Qwen 3.5 Plus',
    provider: 'qwen',
    model: 'qwen3.5-plus',
    enabled: false,
    apiKeySet: false,
    priority: 'high',
    useCase: ['通用对话', '联网搜索'],
  },
  {
    id: '3',
    name: 'MiniMax M2.5',
    provider: 'qwen',
    model: 'MiniMax-M2.5',
    enabled: false,
    apiKeySet: false,
    priority: 'high',
    useCase: ['通用对话', '长上下文'],
  },
  {
    id: '4',
    name: 'DeepSeek V3.2',
    provider: 'qwen',
    model: 'deepseek-v3.2',
    enabled: false,
    apiKeySet: false,
    priority: 'high',
    useCase: ['代码生成', '深度推理', '联网搜索'],
  },
  {
    id: '5',
    name: 'GLM-5',
    provider: 'qwen',
    model: 'glm-5',
    enabled: false,
    apiKeySet: false,
    priority: 'medium',
    useCase: ['简单问答', '快速响应'],
  },
  {
    id: '6',
    name: 'Kimi K2.5',
    provider: 'qwen',
    model: 'kimi-k2.5',
    enabled: false,
    apiKeySet: false,
    priority: 'medium',
    useCase: ['长文本处理'],
  },
  {
    id: '7',
    name: 'Claude 3.5',
    provider: 'anthropic',
    model: 'claude-3-5-sonnet',
    enabled: false,
    apiKeySet: false,
    priority: 'medium',
    useCase: ['深度推理', '代码生成'],
  },
  {
    id: '8',
    name: 'GPT-4o',
    provider: 'openai',
    model: 'gpt-4o',
    enabled: false,
    apiKeySet: false,
    priority: 'medium',
    useCase: ['综合任务'],
  },
  {
    id: '9',
    name: 'Ollama 本地',
    provider: 'ollama',
    model: 'qwen2:7b',
    enabled: true,
    apiKeySet: true,
    priority: 'low',
    useCase: ['离线使用', '隐私优先'],
  },
]

const priorityColors = {
  high: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-gray-100 text-gray-700',
}

function normalizeProvider(provider: LLMProvider): ProviderView {
  return {
    ...provider,
    apiKeySet: Boolean(provider.apiKeySet ?? provider.api_key_set),
    priority: provider.priority || 'medium',
    useCase: provider.useCase || provider.use_case || [],
  }
}

export function ModelsConfig() {
  const [providers, setProviders] = useState<ProviderView[]>(DEFAULT_PROVIDERS)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showApiKey, setShowApiKey] = useState<string | null>(null)
  const [draftKeys, setDraftKeys] = useState<Record<string, string>>({})
  const [savingProviderId, setSavingProviderId] = useState<string | null>(null)
  const [savedProviderId, setSavedProviderId] = useState<string | null>(null)

  const configuredCount = useMemo(
    () => providers.filter((provider) => provider.apiKeySet).length,
    [providers],
  )

  const loadProviders = async () => {
    setSyncing(true)
    setError(null)
    try {
      const data = await apiClient.getLLMProviders()
      setProviders(data.map(normalizeProvider))
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load live provider status')
    } finally {
      setSyncing(false)
    }
  }

  useEffect(() => {
    void loadProviders()
  }, [])

  const saveApiKey = async (provider: ProviderView) => {
    const apiKey = (draftKeys[provider.id] || '').trim()
    if (!apiKey) {
      setError('API key cannot be empty.')
      return
    }

    setSavingProviderId(provider.id)
    setSavedProviderId(null)
    setError(null)
    try {
      await apiClient.updateLLMProviderApiKey(provider.id, apiKey)
      setDraftKeys((current) => ({ ...current, [provider.id]: '' }))
      setSavedProviderId(provider.id)
      await loadProviders()
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : 'Failed to save API key')
    } finally {
      setSavingProviderId(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border bg-card p-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 className="font-medium">LLM Provider Keys</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              This page renders even when no keys are configured. Keys are saved to a gitignored
              local runtime secret file, and environment variables still take precedence.
            </p>
          </div>
          <button
            type="button"
            onClick={loadProviders}
            disabled={syncing}
            className="inline-flex items-center gap-2 rounded-md border bg-background px-3 py-2 text-sm hover:bg-muted disabled:opacity-50"
          >
            {syncing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            Sync live status
          </button>
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <div className="rounded-md border bg-muted/30 px-3 py-2">
            <div className="text-xs text-muted-foreground">Configured providers</div>
            <div className="mt-1 text-lg font-semibold">
              {configuredCount} / {providers.length}
            </div>
          </div>
          <div className="rounded-md border bg-muted/30 px-3 py-2 md:col-span-2">
            <div className="text-xs text-muted-foreground">Main UI rule</div>
            <div className="mt-1 text-sm">
              Provider cards stay visible without keys. Keys only affect runtime activation.
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-4 flex items-start gap-2 rounded-md border border-yellow-200 bg-yellow-50 px-3 py-2 text-sm text-yellow-800">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            {error}
          </div>
        )}
      </div>

      <div className="space-y-3">
        {providers.map((provider) => {
          const draft = draftKeys[provider.id] || ''
          const canSave = draft.trim().length > 0 && savingProviderId !== provider.id
          const canStoreKey = provider.provider !== 'ollama'
          const configured = provider.apiKeySet

          return (
            <div
              key={provider.id}
              className={cn('rounded-lg border bg-card p-4', !provider.enabled && 'opacity-80')}
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-medium">{provider.name}</span>
                    <span className={cn('rounded px-2 py-0.5 text-xs font-medium', priorityColors[provider.priority])}>
                      {provider.priority}
                    </span>
                    <span className="rounded bg-muted px-2 py-0.5 font-mono text-xs">
                      {provider.provider}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">{provider.model}</p>
                  {provider.useCase.length > 0 && (
                    <p className="mt-1 text-xs text-muted-foreground">{provider.useCase.join(' / ')}</p>
                  )}
                </div>

                {configured ? (
                  <span className="inline-flex items-center gap-1 rounded bg-green-50 px-2 py-1 text-xs text-green-700">
                    <Check className="h-3.5 w-3.5" />
                    configured
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 rounded bg-yellow-50 px-2 py-1 text-xs text-yellow-700">
                    <X className="h-3.5 w-3.5" />
                    not configured
                  </span>
                )}
              </div>

              <div className="mt-4 flex flex-col gap-2 md:flex-row md:items-center">
                <div className="flex min-w-0 flex-1 items-center gap-2">
                  <KeyRound className="h-4 w-4 shrink-0 text-muted-foreground" />
                  <input
                    type={showApiKey === provider.id ? 'text' : 'password'}
                    value={draft}
                    disabled={!canStoreKey}
                    onChange={(event) =>
                      setDraftKeys((current) => ({
                        ...current,
                        [provider.id]: event.target.value,
                      }))
                    }
                    placeholder={canStoreKey ? 'Paste API key to save locally' : 'No API key needed'}
                    className="min-w-0 flex-1 rounded-md border bg-background px-3 py-2 text-sm disabled:opacity-50"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKey(showApiKey === provider.id ? null : provider.id)}
                    disabled={!canStoreKey}
                    className="rounded-md border bg-background p-2 hover:bg-muted disabled:opacity-50"
                    title={showApiKey === provider.id ? 'Hide key' : 'Show key'}
                  >
                    {showApiKey === provider.id ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>

                <button
                  type="button"
                  onClick={() => saveApiKey(provider)}
                  disabled={!canSave || !canStoreKey}
                  className="inline-flex items-center justify-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                >
                  {savingProviderId === provider.id && <Loader2 className="h-4 w-4 animate-spin" />}
                  Save locally
                </button>
              </div>

              {savedProviderId === provider.id && (
                <div className="mt-2 text-xs text-green-700">
                  Saved to local runtime secret store.
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
