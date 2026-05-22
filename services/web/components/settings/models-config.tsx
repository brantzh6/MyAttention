'use client'

import { useEffect, useMemo, useState } from 'react'
import {
  AlertTriangle,
  Check,
  Eye,
  EyeOff,
  KeyRound,
  Loader2,
  RefreshCw,
  X,
} from 'lucide-react'
import { apiClient, type LLMProvider } from '@/lib/api-client'
import { cn } from '@/lib/utils'

type ProviderRow = LLMProvider & {
  apiKeySet: boolean
  priority: 'high' | 'medium' | 'low'
  useCase: string[]
  base_url?: string
  api?: string
  key_env?: string | null
  reasoning?: boolean
  input?: string[]
  context_window?: number
  max_tokens?: number
  cost_input?: number
  cost_output?: number
}

type ProviderFamily = {
  provider: string
  title: string
  description: string
  baseUrl: string
  api: string
  keyEnv: string | null
  priority: 'high' | 'medium' | 'low'
  useCase: string[]
  apiKeySet: boolean
  models: ProviderRow[]
}

const PROVIDER_META: Record<string, Omit<ProviderFamily, 'provider' | 'apiKeySet' | 'models'>> = {
  'bailian-coding-plan': {
    title: 'Bailian Coding Plan',
    description: 'Routine coding, planning, and multi-model voting lane from the local OpenClaw profile.',
    baseUrl: 'https://coding.dashscope.aliyuncs.com/v1',
    api: 'openai-completions',
    keyEnv: 'BAILIAN_CODING_PLAN_API_KEY',
    priority: 'high',
    useCase: ['编码', '规划', '多模型投票'],
  },
  bailian: {
    title: 'Bailian',
    description: 'General-purpose Bailian lane for the normal automatable model surface.',
    baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    api: 'openai-completions',
    keyEnv: 'BAILIAN_API_KEY',
    priority: 'high',
    useCase: ['通用对话', '快速响应'],
  },
  qwen: {
    title: 'Qwen',
    description: 'Legacy Qwen-compatible family kept for runtime compatibility and fallback coverage.',
    baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    api: 'openai-completions',
    keyEnv: 'QWEN_API_KEY',
    priority: 'high',
    useCase: ['摘要', '对话', '创意写作'],
  },
  anthropic: {
    title: 'Anthropic',
    description: 'Claude lane for deeper reasoning and code generation.',
    baseUrl: 'https://api.anthropic.com/v1',
    api: 'anthropic',
    keyEnv: 'ANTHROPIC_API_KEY',
    priority: 'medium',
    useCase: ['深度推理', '代码生成'],
  },
  openai: {
    title: 'OpenAI',
    description: 'OpenAI general-purpose lane.',
    baseUrl: 'https://api.openai.com/v1',
    api: 'openai',
    keyEnv: 'OPENAI_API_KEY',
    priority: 'medium',
    useCase: ['综合任务'],
  },
  ollama: {
    title: 'Ollama Local',
    description: 'Local offline lane that does not require an API key.',
    baseUrl: 'http://localhost:11434',
    api: 'ollama',
    keyEnv: null,
    priority: 'low',
    useCase: ['离线使用', '隐私优先'],
  },
}

const PROVIDER_ORDER = ['bailian-coding-plan', 'bailian', 'qwen', 'anthropic', 'openai', 'ollama']

function normalizeProvider(provider: LLMProvider): ProviderRow {
  return {
    ...provider,
    apiKeySet: Boolean(provider.apiKeySet ?? provider.api_key_set),
    priority: provider.priority || 'medium',
    useCase: provider.useCase || provider.use_case || [],
  }
}

function formatNumber(value?: number) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '—'
  return value.toLocaleString('en-US')
}

function groupProviders(rows: ProviderRow[]): ProviderFamily[] {
  const grouped = new Map<string, ProviderRow[]>()
  for (const row of rows) {
    const list = grouped.get(row.provider) || []
    list.push(row)
    grouped.set(row.provider, list)
  }

  const families: ProviderFamily[] = []
  for (const provider of PROVIDER_ORDER) {
    const models = grouped.get(provider)
    if (!models || models.length === 0) continue
    const meta = PROVIDER_META[provider] || {
      title: provider,
      description: 'Model family configuration.',
      baseUrl: models[0].base_url || '',
      api: models[0].api || 'openai-completions',
      keyEnv: models[0].key_env || null,
      priority: models[0].priority,
      useCase: models[0].useCase,
    }
    families.push({
      provider,
      title: meta.title,
      description: meta.description,
      baseUrl: meta.baseUrl,
      api: meta.api,
      keyEnv: meta.keyEnv,
      priority: meta.priority,
      useCase: meta.useCase,
      apiKeySet: models.some((model) => model.apiKeySet),
      models,
    })
  }
  return families
}

export function ModelsConfig() {
  const [providers, setProviders] = useState<ProviderRow[]>([])
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showApiKey, setShowApiKey] = useState<string | null>(null)
  const [draftKeys, setDraftKeys] = useState<Record<string, string>>({})
  const [savingProviderId, setSavingProviderId] = useState<string | null>(null)
  const [savedProviderId, setSavedProviderId] = useState<string | null>(null)

  const families = useMemo(() => groupProviders(providers), [providers])
  const configuredFamilies = useMemo(
    () => families.filter((family) => family.apiKeySet).length,
    [families],
  )
  const configuredModels = useMemo(
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

  const saveApiKey = async (provider: string) => {
    const apiKey = (draftKeys[provider] || '').trim()
    const family = families.find((item) => item.provider === provider)
    const canStoreKey = family?.keyEnv !== null

    if (!canStoreKey) {
      setError('This provider does not use a local API key.')
      return
    }

    if (!apiKey) {
      setError('API key cannot be empty.')
      return
    }

    setSavingProviderId(provider)
    setSavedProviderId(null)
    setError(null)
    try {
      await apiClient.updateLLMProviderApiKey(provider, apiKey)
      setDraftKeys((current) => ({ ...current, [provider]: '' }))
      setSavedProviderId(provider)
      await loadProviders()
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : 'Failed to save API key')
    } finally {
      setSavingProviderId(null)
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-xl border bg-card p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-3xl">
            <h2 className="text-xl font-semibold text-foreground">LLM 模型配置</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              这个页面现在按 provider family 展示。`bailian-coding-plan` 和 `bailian` 已按本地
              OpenClaw 配置接入，family 级 API key 只影响运行时激活，不影响页面渲染。
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

        <div className="mt-5 grid gap-3 lg:grid-cols-4">
          <div className="rounded-md border bg-muted/30 px-3 py-3">
            <div className="text-xs text-muted-foreground">Configured families</div>
            <div className="mt-1 text-lg font-semibold">
              {configuredFamilies} / {families.length}
            </div>
          </div>
          <div className="rounded-md border bg-muted/30 px-3 py-3">
            <div className="text-xs text-muted-foreground">Configured models</div>
            <div className="mt-1 text-lg font-semibold">
              {configuredModels} / {providers.length}
            </div>
          </div>
          <div className="rounded-md border bg-muted/30 px-3 py-3 lg:col-span-2">
            <div className="text-xs text-muted-foreground">Main UI rule</div>
            <div className="mt-1 text-sm">
              Families stay visible without keys. Keys only affect runtime activation and local secret
              persistence.
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-4 flex items-start gap-2 rounded-md border border-yellow-200 bg-yellow-50 px-3 py-2 text-sm text-yellow-800">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            {error}
          </div>
        )}
      </section>

      <div className="space-y-4">
        {families.map((family) => {
          const draft = draftKeys[family.provider] || ''
          const canStoreKey = family.keyEnv !== null
          const canSave = draft.trim().length > 0 && savingProviderId !== family.provider && canStoreKey

          return (
            <section key={family.provider} className="rounded-xl border bg-card p-5">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-base font-semibold text-foreground">{family.title}</h3>
                    <span className={cn('rounded px-2 py-0.5 text-xs font-medium', family.priority === 'high' ? 'bg-green-100 text-green-700' : family.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700')}>
                      {family.priority}
                    </span>
                    <span className="rounded bg-muted px-2 py-0.5 font-mono text-xs">{family.provider}</span>
                    <span className="rounded bg-muted px-2 py-0.5 text-xs">{family.models.length} models</span>
                    {family.apiKeySet ? (
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
                  <p className="mt-2 text-sm text-muted-foreground">{family.description}</p>
                  <div className="mt-2 flex flex-wrap gap-2 text-xs text-muted-foreground">
                    <span className="rounded border bg-background px-2 py-1">Base URL: {family.baseUrl}</span>
                    <span className="rounded border bg-background px-2 py-1">API: {family.api}</span>
                    <span className="rounded border bg-background px-2 py-1">
                      Key: {family.keyEnv || 'not required'}
                    </span>
                  </div>
                  {family.useCase.length > 0 && (
                    <div className="mt-2 text-xs text-muted-foreground">
                      {family.useCase.join(' / ')}
                    </div>
                  )}
                </div>

                <div className="min-w-[320px] max-w-xl flex-1">
                  <div className="flex min-w-0 items-center gap-2">
                    <KeyRound className="h-4 w-4 shrink-0 text-muted-foreground" />
                    <input
                      type={showApiKey === family.provider ? 'text' : 'password'}
                      value={draft}
                      disabled={!canStoreKey}
                      onChange={(event) =>
                        setDraftKeys((current) => ({
                          ...current,
                          [family.provider]: event.target.value,
                        }))
                      }
                      placeholder={canStoreKey ? 'Paste API key to save locally' : 'No API key needed'}
                      className="min-w-0 flex-1 rounded-md border bg-background px-3 py-2 text-sm disabled:opacity-50"
                    />
                    <button
                      type="button"
                      onClick={() =>
                        setShowApiKey(showApiKey === family.provider ? null : family.provider)
                      }
                      disabled={!canStoreKey}
                      className="rounded-md border bg-background p-2 hover:bg-muted disabled:opacity-50"
                      title={showApiKey === family.provider ? 'Hide key' : 'Show key'}
                    >
                      {showApiKey === family.provider ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                    <button
                      type="button"
                      onClick={() => saveApiKey(family.provider)}
                      disabled={!canSave}
                      className="inline-flex items-center justify-center gap-2 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                    >
                      {savingProviderId === family.provider && <Loader2 className="h-4 w-4 animate-spin" />}
                      Save locally
                    </button>
                  </div>
                  {savedProviderId === family.provider && (
                    <div className="mt-2 text-xs text-green-700">Saved to local runtime secret store.</div>
                  )}
                </div>
              </div>

              <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {family.models.map((model) => (
                  <article key={model.id} className="rounded-lg border bg-muted/20 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <h4 className="font-medium text-foreground">{model.name}</h4>
                        <p className="mt-1 text-xs font-mono text-muted-foreground">{model.model}</p>
                      </div>
                      <span className={cn('rounded px-2 py-0.5 text-[11px] font-medium', model.reasoning ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700')}>
                        {model.reasoning ? 'reasoning' : 'standard'}
                      </span>
                    </div>

                    {model.useCase.length > 0 && (
                      <p className="mt-2 text-xs text-muted-foreground">{model.useCase.join(' / ')}</p>
                    )}

                    <div className="mt-3 flex flex-wrap gap-2 text-[11px] text-muted-foreground">
                      {model.input?.map((item) => (
                        <span key={item} className="rounded bg-background px-2 py-1">
                          {item}
                        </span>
                      ))}
                    </div>

                    <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                      <div className="rounded border bg-background px-2 py-1">
                        Context {formatNumber(model.context_window)}
                      </div>
                      <div className="rounded border bg-background px-2 py-1">
                        Max {formatNumber(model.max_tokens)}
                      </div>
                      <div className="rounded border bg-background px-2 py-1">
                        Input {formatNumber(model.cost_input)}
                      </div>
                      <div className="rounded border bg-background px-2 py-1">
                        Output {formatNumber(model.cost_output)}
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          )
        })}
      </div>
    </div>
  )
}
