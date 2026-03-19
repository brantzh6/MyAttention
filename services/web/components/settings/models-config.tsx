'use client'

import { useState } from 'react'
import { Check, X, Eye, EyeOff, Vote, Zap, Brain } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LLMProvider {
  id: string
  name: string
  provider: string
  model: string
  enabled: boolean
  apiKeySet: boolean
  priority: 'high' | 'medium' | 'low'
  useCase: string[]
}

const mockProviders: LLMProvider[] = [
  {
    id: '1',
    name: '通义千问',
    provider: 'qwen',
    model: 'qwen-max',
    enabled: true,
    apiKeySet: true,
    priority: 'high',
    useCase: ['摘要', '中文对话', '创意写作'],
  },
  {
    id: '2',
    name: '智谱 GLM',
    provider: 'glm',
    model: 'glm-4',
    enabled: true,
    apiKeySet: true,
    priority: 'high',
    useCase: ['简单问答', '快速响应'],
  },
  {
    id: '3',
    name: 'Kimi',
    provider: 'kimi',
    model: 'moonshot-v1-128k',
    enabled: true,
    apiKeySet: false,
    priority: 'high',
    useCase: ['长文本处理'],
  },
  {
    id: '4',
    name: 'Claude 3.5',
    provider: 'anthropic',
    model: 'claude-3-5-sonnet',
    enabled: true,
    apiKeySet: true,
    priority: 'medium',
    useCase: ['深度推理', '代码生成'],
  },
  {
    id: '5',
    name: 'GPT-4o',
    provider: 'openai',
    model: 'gpt-4o',
    enabled: false,
    apiKeySet: false,
    priority: 'medium',
    useCase: ['综合任务'],
  },
  {
    id: '6',
    name: 'Ollama 本地',
    provider: 'ollama',
    model: 'qwen2:7b',
    enabled: false,
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

const priorityLabels = {
  high: '高优先级',
  medium: '中优先级',
  low: '低优先级',
}

export function ModelsConfig() {
  const [providers, setProviders] = useState(mockProviders)
  const [showApiKey, setShowApiKey] = useState<string | null>(null)
  const [votingEnabled, setVotingEnabled] = useState(true)
  const [votingModels, setVotingModels] = useState(['1', '4', '5'])

  const toggleEnabled = (id: string) => {
    setProviders(providers.map(p => p.id === id ? { ...p, enabled: !p.enabled } : p))
  }

  const toggleVotingModel = (id: string) => {
    if (votingModels.includes(id)) {
      setVotingModels(votingModels.filter(m => m !== id))
    } else {
      setVotingModels([...votingModels, id])
    }
  }

  return (
    <div className="space-y-6">
      {/* Voting Configuration */}
      <div className="p-4 rounded-lg border bg-card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Vote className="h-5 w-5 text-primary" />
            <h3 className="font-medium">多模型投票配置</h3>
          </div>
          <button
            onClick={() => setVotingEnabled(!votingEnabled)}
            className={cn(
              'px-3 py-1 rounded-full text-sm font-medium transition-colors',
              votingEnabled
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground'
            )}
          >
            {votingEnabled ? '已启用' : '已禁用'}
          </button>
        </div>
        
        <p className="text-sm text-muted-foreground mb-4">
          对于重大决策，系统将同时调用多个模型进行分析，并综合各方观点给出结论。
        </p>

        <div className="space-y-2">
          <p className="text-sm font-medium">参与投票的模型:</p>
          <div className="flex flex-wrap gap-2">
            {providers.filter(p => p.apiKeySet).map((provider) => (
              <button
                key={provider.id}
                onClick={() => toggleVotingModel(provider.id)}
                className={cn(
                  'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                  votingModels.includes(provider.id)
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                )}
              >
                {provider.name}
              </button>
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            已选择 {votingModels.length} 个模型，共识阈值: 2/3
          </p>
        </div>
      </div>

      {/* Smart Routing */}
      <div className="p-4 rounded-lg border bg-card">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="h-5 w-5 text-primary" />
          <h3 className="font-medium">智能路由策略</h3>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
          <div className="p-3 rounded-md bg-muted/50">
            <p className="font-medium">简单问答</p>
            <p className="text-muted-foreground">Qwen-Turbo</p>
          </div>
          <div className="p-3 rounded-md bg-muted/50">
            <p className="font-medium">信息摘要</p>
            <p className="text-muted-foreground">Qwen-Max</p>
          </div>
          <div className="p-3 rounded-md bg-muted/50">
            <p className="font-medium">深度推理</p>
            <p className="text-muted-foreground">Claude 3.5</p>
          </div>
          <div className="p-3 rounded-md bg-muted/50">
            <p className="font-medium">长文本处理</p>
            <p className="text-muted-foreground">Kimi</p>
          </div>
          <div className="p-3 rounded-md bg-muted/50">
            <p className="font-medium">代码生成</p>
            <p className="text-muted-foreground">Claude 3.5</p>
          </div>
          <div className="p-3 rounded-md bg-primary/10">
            <p className="font-medium text-primary">重大决策</p>
            <p className="text-primary">多模型投票</p>
          </div>
        </div>
      </div>

      {/* Provider List */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" />
          <h3 className="font-medium">模型配置</h3>
        </div>
        
        {providers.map((provider) => (
          <div
            key={provider.id}
            className={cn(
              'p-4 rounded-lg border bg-card',
              !provider.enabled && 'opacity-60'
            )}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{provider.name}</span>
                    <span className={cn('px-2 py-0.5 rounded text-xs font-medium', priorityColors[provider.priority])}>
                      {priorityLabels[provider.priority]}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">{provider.model}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                {provider.apiKeySet ? (
                  <span className="flex items-center gap-1 text-xs text-green-600">
                    <Check className="h-3 w-3" /> API Key 已配置
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-xs text-yellow-600">
                    <X className="h-3 w-3" /> 未配置
                  </span>
                )}
                
                <button
                  onClick={() => toggleEnabled(provider.id)}
                  className={cn(
                    'px-3 py-1 rounded text-xs font-medium transition-colors',
                    provider.enabled
                      ? 'bg-green-100 text-green-700 hover:bg-green-200'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  )}
                >
                  {provider.enabled ? '启用' : '禁用'}
                </button>
              </div>
            </div>
            
            <div className="mt-3 flex items-center gap-4">
              <div className="flex-1">
                <label className="text-xs text-muted-foreground">API Key</label>
                <div className="flex items-center gap-2 mt-1">
                  <input
                    type={showApiKey === provider.id ? 'text' : 'password'}
                    placeholder="sk-..."
                    className="flex-1 px-3 py-1.5 rounded-md border bg-background text-sm"
                    defaultValue={provider.apiKeySet ? '••••••••••••••••' : ''}
                  />
                  <button
                    onClick={() => setShowApiKey(showApiKey === provider.id ? null : provider.id)}
                    className="p-1.5 rounded hover:bg-muted"
                  >
                    {showApiKey === provider.id ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
              
              <div className="text-xs text-muted-foreground">
                <p>适用场景:</p>
                <p>{provider.useCase.join('、')}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
