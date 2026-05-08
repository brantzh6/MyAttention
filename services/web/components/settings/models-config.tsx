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
  const [providers, setProviders] = useState<ProviderView[]>([])
  const [loading, setLoading] = useState(true)
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
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.getLLMProviders()
      setProviders(data.map(normalizeProvider))
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load providers')
    } finally {
      setLoading(false)
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
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="font-medium">LLM Provider Keys</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Keys are saved to a gitignored local runtime secret file. Environment variables still
              take precedence.
            </p>
          </div>
          <button
            type="button"
            onClick={loadProviders}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-md border bg-background px-3 py-2 text-sm hover:bg-muted disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            Refresh
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
            <div className="text-xs text-muted-foreground">Storage boundary</div>
            <div className="mt-1 text-sm">
              Local runtime secret only; no git commit, no project truth, no key echo.
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-4 flex items-start gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            {error}
          </div>
        )}
      </div>

      <div className="space-y-3">
        {loading && providers.length === 0 && (
          <div className="flex items-center gap-2 rounded-lg border bg-card p-4 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading providers...
          </div>
        )}

        {providers.map((provider) => {
          const draft = draftKeys[provider.id] || ''
          const canSave = draft.trim().length > 0 && savingProviderId !== provider.id
          const canStoreKey = provider.provider !== 'ollama'

          return (
            <div
              key={provider.id}
              className={cn('rounded-lg border bg-card p-4', !provider.enabled && 'opacity-70')}
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
                    <p className="mt-1 text-xs text-muted-foreground">
                      {provider.useCase.join(' / ')}
                    </p>
                  )}
                </div>

                {provider.apiKeySet ? (
                  <span className="inline-flex items-center gap-1 rounded bg-green-50 px-2 py-1 text-xs text-green-700">
                    <Check className="h-3.5 w-3.5" />
                    configured
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 rounded bg-yellow-50 px-2 py-1 text-xs text-yellow-700">
                    <X className="h-3.5 w-3.5" />
                    missing key
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
                  Saved to local runtime secret store. Restart is not required for new requests.
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
