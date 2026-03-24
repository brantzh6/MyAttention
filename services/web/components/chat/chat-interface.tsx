'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import {
  BookOpen,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Database,
  FileText,
  Globe,
  Lightbulb,
  Loader2,
  MessageSquare,
  Plus,
  RefreshCw,
  Rss,
  Send,
  Trash2,
  Upload as UploadIcon,
  Vote,
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

import { apiClient } from '@/lib/api-client'
import { cn } from '@/lib/utils'

const API_URL = process.env.API_URL || 'http://localhost:8000'

const AVAILABLE_MODELS = [
  { provider: 'qwen', model: 'qwen-max', name: 'Qwen Max', supportsSearch: true, supportsThinking: false },
  { provider: 'qwen', model: 'qwen3.5-plus', name: 'Qwen 3.5 Plus', supportsSearch: true, supportsThinking: true },
  { provider: 'qwen', model: 'MiniMax-M2.5', name: 'MiniMax M2.5', supportsSearch: true, supportsThinking: false },
  { provider: 'qwen', model: 'deepseek-v3.2', name: 'DeepSeek V3.2', supportsSearch: true, supportsThinking: true },
  { provider: 'qwen', model: 'glm-5', name: 'GLM-5', supportsSearch: false, supportsThinking: true },
  { provider: 'qwen', model: 'kimi-k2.5', name: 'Kimi K2.5', supportsSearch: false, supportsThinking: false },
] as const

const DEFAULT_MODEL =
  AVAILABLE_MODELS.find((model) => model.model === 'qwen3.5-plus') ?? AVAILABLE_MODELS[0]

type AvailableModel = (typeof AVAILABLE_MODELS)[number]

type Locale = 'zh-CN' | 'en'

const TEXT: Record<Locale, Record<string, string>> = {
  'zh-CN': {
    chatHistory: '\u4f1a\u8bdd\u5386\u53f2',
    newChat: '\u65b0\u5bf9\u8bdd',
    noConversation: '\u6682\u65e0\u4f1a\u8bdd',
    startTitle: '\u5f00\u59cb\u5bf9\u8bdd',
    startDesc: '\u5411 AI \u63d0\u95ee\uff0c\u83b7\u53d6\u57fa\u4e8e\u77e5\u8bc6\u5e93\u548c\u591a\u6a21\u578b\u6295\u7968\u7684\u667a\u80fd\u56de\u7b54\u3002',
    thinking: '\u601d\u8003\u8fc7\u7a0b',
    finalVerdict: '\u6700\u7ec8\u88c1\u51b3',
    modelViews: '\u6a21\u578b\u89c2\u70b9',
    directAnswer: '\u76f4\u63a5\u56de\u7b54',
    rerunTurn: '\u91cd\u8dd1\u672c\u8f6e',
    sources: '\u5f15\u7528\u6765\u6e90',
    webSearch: '\u8054\u7f51\u641c\u7d22',
    deepThinking: '\u6df1\u5ea6\u601d\u8003',
    voting: '\u591a\u6a21\u578b\u6295\u7968',
    knowledgeBase: '\u77e5\u8bc6\u5e93',
    allKnowledgeBases: '\u5168\u90e8\u77e5\u8bc6\u5e93',
    selected: '\u5df2\u9009',
    docs: '\u6587\u6863',
    selectKnowledgeBases: '\u9009\u62e9\u8981\u641c\u7d22\u7684\u77e5\u8bc6\u5e93\uff08\u53ef\u591a\u9009\uff09',
    inputPlaceholder: '\u8f93\u5165\u4f60\u7684\u95ee\u9898...',
    deleteConversation: '\u786e\u5b9a\u8981\u5220\u9664\u8fd9\u4e2a\u4f1a\u8bdd\u5417\uff1f',
    online: '\u8054\u7f51',
    connecting: '\u8fde\u63a5\u540e\u7aef\u670d\u52a1...',
    callingApi: '\u8c03\u7528 API...',
    thinkingStatus: '\u6a21\u578b\u6b63\u5728\u601d\u8003...',
    generating: '\u6b63\u5728\u751f\u6210\u56de\u7b54...',
    voteStarted: '\u6295\u7968\u5f00\u59cb',
    voteStreaming: '\u6b63\u5728\u8f93\u51fa',
    voteCompleted: '\u5b8c\u6210',
    voteFailed: '\u5931\u8d25',
    synthesizing: '\u6b63\u5728\u7efc\u5408\u88c1\u51b3...',
    processing: '\u5904\u7406\u4e2d...',
    noContent: '\u6682\u65e0\u5185\u5bb9',
    summary: '\u6458\u8981',
    connectionFailed: '\u8fde\u63a5\u5931\u8d25',
    today: '\u4eca\u5929',
    yesterday: '\u6628\u5929',
    daysAgo: '\u5929\u524d',
    modelsUnit: '\u4e2a\u6a21\u578b',
    noAvailableModels: '\u65e0\u53ef\u7528\u6a21\u578b',
    votingModelsLabel: '\u672c\u8f6e\u53c2\u4e0e\u6a21\u578b',
    primaryDecision: '\u4e3b\u88c1',
    supportEvidence: '\u8865\u5145',
    brainRoute: '\u5927\u8111\u8def\u7531',
    primaryBrain: '\u4e3b\u8111',
    supportingBrains: '\u534f\u4f5c',
    thinkingFramework: '\u6846\u67b6',
  },
  en: {
    chatHistory: 'Conversations',
    newChat: 'New chat',
    noConversation: 'No conversations',
    startTitle: 'Start a conversation',
    startDesc: 'Ask AI and get answers grounded in knowledge bases and multi-model voting.',
    thinking: 'Thinking',
    finalVerdict: 'Final verdict',
    modelViews: 'Model viewpoints',
    directAnswer: 'Direct answer',
    rerunTurn: 'Rerun turn',
    sources: 'Sources',
    webSearch: 'Web search',
    deepThinking: 'Deep thinking',
    voting: 'Voting',
    knowledgeBase: 'Knowledge base',
    allKnowledgeBases: 'All knowledge bases',
    selected: 'Selected',
    docs: 'docs',
    selectKnowledgeBases: 'Choose knowledge bases to search',
    inputPlaceholder: 'Enter your question...',
    deleteConversation: 'Delete this conversation?',
    online: 'Online',
    connecting: 'Connecting to backend...',
    callingApi: 'Calling API...',
    thinkingStatus: 'Model is thinking...',
    generating: 'Generating response...',
    voteStarted: 'Voting started',
    voteStreaming: 'Streaming',
    voteCompleted: 'Completed',
    voteFailed: 'Failed',
    synthesizing: 'Synthesizing final answer...',
    processing: 'Processing...',
    noContent: 'No content',
    summary: 'Summary',
    connectionFailed: 'Connection failed',
    today: 'Today',
    yesterday: 'Yesterday',
    daysAgo: 'days ago',
    modelsUnit: 'models',
    noAvailableModels: 'none',
    votingModelsLabel: 'Voting models',
    primaryDecision: 'Primary',
    supportEvidence: 'Support',
    brainRoute: 'Brain route',
    primaryBrain: 'Primary brain',
    supportingBrains: 'Supporting',
    thinkingFramework: 'Framework',
  },
}

interface BrainPlan {
  route_id: string
  problem_type: string
  thinking_framework: string
  primary_brain: string
  supporting_brains: string[]
  review_brain?: string | null
  fallback_brain?: string | null
  primary_models: string[]
  supporting_models: string[]
  selected_models: string[]
  execution_mode: string
  surface?: string | null
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  thinking?: string
  sources?: { title: string; url: string; source?: string; score?: number }[]
  isVoting?: boolean
  votingResults?: { model: string; content: string; success: boolean; error?: string }[]
  searchEnabled?: boolean
  modelUsed?: string
  brainPlan?: BrainPlan
}

interface Conversation {
  id: string
  title: string | null
  message_count: number
  last_message_at: string | null
  created_at: string
}

interface KnowledgeBase {
  id: string
  name: string
  document_count: number
}

interface VotingState {
  isActive: boolean
  models: string[]
  modelContents: Record<string, string>
  modelStatus: Record<string, 'pending' | 'streaming' | 'completed' | 'failed'>
  synthesisContent: string
  isSynthesizing: boolean
}

function MarkdownContent({ content }: { content: string }) {
  return (
    <div className="prose-chat">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  )
}

function detectLocale(): Locale {
  if (typeof window === 'undefined') return 'zh-CN'

  const saved = window.localStorage.getItem('myattention.locale')
  if (saved === 'zh-CN' || saved === 'en') {
    return saved
  }

  const docLang = document.documentElement.lang?.toLowerCase()
  if (docLang?.startsWith('en')) return 'en'

  return 'zh-CN'
}

function t(locale: Locale, key: string) {
  return TEXT[locale][key] || key
}

function formatRelativeDate(locale: Locale, value: string | null) {
  if (!value) return ''
  const date = new Date(value)
  const diff = Date.now() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return t(locale, 'today')
  if (days === 1) return t(locale, 'yesterday')
  if (days < 7) return `${days}${locale === 'zh-CN' ? t(locale, 'daysAgo') : ` ${t(locale, 'daysAgo')}`}`
  return date.toLocaleDateString(locale)
}

function sourceMeta(type?: string) {
  if (type === 'rss') return { Icon: Rss, color: 'text-orange-500' }
  if (type === 'web') return { Icon: Globe, color: 'text-blue-500' }
  if (type === 'upload') return { Icon: UploadIcon, color: 'text-emerald-500' }
  if (type === 'documentation') return { Icon: BookOpen, color: 'text-cyan-500' }
  return { Icon: FileText, color: 'text-slate-500' }
}

function parseVerdictSections(content: string) {
  const sections: { title: string; body: string }[] = []
  const pattern = /\u3010([^\u3011]+)\u3011\s*([\s\S]*?)(?=\u3010[^\u3011]+\u3011|$)/g
  let match: RegExpExecArray | null

  while ((match = pattern.exec(content)) !== null) {
    const title = match[1]?.trim()
    const body = match[2]?.trim()
    if (title && body) {
      sections.push({ title, body })
    }
  }

  return sections
}

function looksCorruptedTitle(value?: string | null) {
  if (!value) return false
  const text = value.trim()
  if (!text) return false

  const questionMarks = text.split('').filter(char => char === '?').length
  return text.includes('�') || (questionMarks >= 3 && questionMarks / text.length >= 0.3)
}

function formatConversationTitle(locale: Locale, value?: string | null) {
  if (!value || looksCorruptedTitle(value)) {
    return t(locale, 'newChat')
  }
  return value
}

function getVotingCandidateRole(model: AvailableModel, enableSearch: boolean, enableThinking: boolean) {
  if (enableSearch && enableThinking) {
    if (model.supportsSearch && model.supportsThinking) return 'primary'
    if (model.supportsSearch || model.supportsThinking) return 'support'
    return 'excluded'
  }
  if (enableSearch) return model.supportsSearch ? 'primary' : 'excluded'
  if (enableThinking) return model.supportsThinking ? 'primary' : 'excluded'
  return 'primary'
}

export function ChatInterface() {
  const [locale, setLocale] = useState<Locale>('zh-CN')
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [useVoting, setUseVoting] = useState(false)
  const [enableSearch, setEnableSearch] = useState(false)
  const [enableThinking, setEnableThinking] = useState(false)
  const [useRag, setUseRag] = useState(true)
  const [selectedModel, setSelectedModel] = useState<AvailableModel>(DEFAULT_MODEL)
  const [showModelDropdown, setShowModelDropdown] = useState(false)
  const [expandedThinking, setExpandedThinking] = useState<Record<string, boolean>>({})
  const [expandedVotingResults, setExpandedVotingResults] = useState<Record<string, Record<number, boolean>>>({})
  const [votingState, setVotingState] = useState<VotingState>({ isActive: false, models: [], modelContents: {}, modelStatus: {}, synthesisContent: '', isSynthesizing: false })
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [loadingConversations, setLoadingConversations] = useState(true)
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKbIds, setSelectedKbIds] = useState<string[]>([])
  const [showKbDropdown, setShowKbDropdown] = useState(false)
  const [chatStatus, setChatStatus] = useState('')

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const modelDropdownRef = useRef<HTMLDivElement>(null)
  const kbDropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => setLocale(detectLocale()), [])
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modelDropdownRef.current && !modelDropdownRef.current.contains(event.target as Node)) setShowModelDropdown(false)
      if (kbDropdownRef.current && !kbDropdownRef.current.contains(event.target as Node)) setShowKbDropdown(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const loadConversations = useCallback(async () => {
    setLoadingConversations(true)
    try {
      const res = await apiClient.listConversations(1, 50)
      setConversations(res.conversations)
    } finally {
      setLoadingConversations(false)
    }
  }, [])

  const loadKnowledgeBases = useCallback(async () => {
    try {
      const data = await apiClient.getKnowledgeBases()
      setKnowledgeBases(data.knowledge_bases.map((kb: any) => ({ id: kb.id, name: kb.name, document_count: kb.document_count })))
    } catch (error) {
      console.error('Failed to load knowledge bases:', error)
    }
  }, [])

  const loadConversationMessages = useCallback(async (conversationId: string) => {
    try {
      const msgs = await apiClient.getMessages(conversationId, 100)
      setMessages(msgs.map((m: any) => ({
        id: m.id,
        role: m.role,
        content: m.content,
        thinking: m.thinking,
        sources: m.sources || [],
        isVoting: !!m.voting_results,
        votingResults: m.voting_results?.individual_results?.map((r: any) => ({ model: r.model, content: r.content || '', success: r.success, error: r.error })),
        searchEnabled: m.search_enabled,
        modelUsed: m.model,
        brainPlan: m.metadata?.brain_plan,
      })))
      setCurrentConversationId(conversationId)
    } catch (error) {
      console.error('Failed to load messages:', error)
    }
  }, [])

  useEffect(() => {
    loadConversations()
    loadKnowledgeBases()
  }, [loadConversations, loadKnowledgeBases])

  const resetVotingState = () => {
    setVotingState({ isActive: false, models: [], modelContents: {}, modelStatus: {}, synthesisContent: '', isSynthesizing: false })
  }

  const sendMessage = useCallback(async (
    message: string,
    options?: {
      clearInput?: boolean
      useVoting?: boolean
      enableSearch?: boolean
      enableThinking?: boolean
      selectedModel?: typeof AVAILABLE_MODELS[number]
    },
  ) => {
    const trimmed = message.trim()
    if (!trimmed || isLoading) return

    const effectiveUseVoting = options?.useVoting ?? useVoting
    const effectiveEnableSearch = options?.enableSearch ?? enableSearch
    const effectiveModel = options?.selectedModel ?? selectedModel
    const requestedThinking = options?.enableThinking ?? enableThinking
    const effectiveEnableThinking = effectiveUseVoting ? requestedThinking : (requestedThinking && effectiveModel.supportsThinking)

    setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', content: trimmed }])
    if (options?.clearInput) setInput('')
    setIsLoading(true)
    setChatStatus(`${t(locale, 'connecting')} ${effectiveUseVoting ? t(locale, 'voting') : effectiveModel.name}`)

    const assistantId = `${Date.now() + 1}`
    let assistantAdded = false
    let sources: Message['sources'] = []
    let brainPlan: BrainPlan | undefined

    try {
      setChatStatus(`${t(locale, 'callingApi')} ${effectiveUseVoting ? t(locale, 'voting') : effectiveModel.name}`)
      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: trimmed,
          use_voting: effectiveUseVoting,
          use_rag: useRag,
          enable_search: effectiveEnableSearch,
          enable_thinking: effectiveEnableThinking,
          conversation_id: currentConversationId,
          provider: effectiveUseVoting ? undefined : effectiveModel.provider,
          model: effectiveUseVoting ? undefined : effectiveModel.model,
          kb_ids: useRag && selectedKbIds.length > 0 ? selectedKbIds : undefined,
        }),
      })
      if (!res.ok) throw new Error(`API error: ${res.status}`)

      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      if (reader) {
        let buffer = ''
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })
          const parts = buffer.split('\n\n')
          buffer = parts.pop() || ''
          for (const part of parts) {
            for (const line of part.split('\n')) {
              if (!line.startsWith('data: ')) continue
              const data = line.slice(6).trim()
              if (data === '[DONE]') continue
              try {
                const parsed = JSON.parse(data)
                if (parsed.status) {
                  setChatStatus(parsed.status)
                  continue
                }
                if (parsed.conversation_id && !currentConversationId) {
                  setCurrentConversationId(parsed.conversation_id)
                }
                if (parsed.sources?.length) sources = parsed.sources
                if (parsed.brain_plan) {
                  brainPlan = parsed.brain_plan
                  setChatStatus(`${t(locale, 'brainRoute')}: ${parsed.brain_plan.route_id}`)
                }
                if (parsed.type === 'voting_start') {
                  const modelStatus: VotingState['modelStatus'] = {}
                  const modelContents: VotingState['modelContents'] = {}
                  for (const model of parsed.models || []) {
                    modelStatus[model] = 'pending'
                    modelContents[model] = ''
                  }
                  setVotingState({ isActive: true, models: parsed.models || [], modelContents, modelStatus, synthesisContent: '', isSynthesizing: false })
                  if (!assistantAdded) {
                    assistantAdded = true
                    setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '', isVoting: true }])
                  }
                  setChatStatus(`${t(locale, 'voteStarted')}: ${(parsed.models || []).join(', ')}`)
                  continue
                }
                if (parsed.type === 'voting_model_content') {
                  setVotingState(prev => ({
                    ...prev,
                    modelContents: { ...prev.modelContents, [parsed.model]: `${prev.modelContents[parsed.model] || ''}${parsed.content}` },
                    modelStatus: { ...prev.modelStatus, [parsed.model]: 'streaming' },
                  }))
                  setChatStatus(`${parsed.model} ${t(locale, 'voteStreaming')}`)
                  continue
                }
                if (parsed.type === 'voting_progress') {
                  setVotingState(prev => ({
                    ...prev,
                    modelStatus: { ...prev.modelStatus, [parsed.model]: parsed.success ? 'completed' : 'failed' },
                  }))
                  continue
                }
                if (parsed.type === 'voting_synthesizing') {
                  setVotingState(prev => ({ ...prev, isSynthesizing: true }))
                  setChatStatus(t(locale, 'synthesizing'))
                  continue
                }
                if (parsed.type === 'voting_synthesis_content') {
                  setVotingState(prev => ({ ...prev, synthesisContent: `${prev.synthesisContent}${parsed.content}` }))
                  setMessages(prev => prev.map(m => (m.id === assistantId ? { ...m, content: `${m.content}${parsed.content}`, isVoting: true } : m)))
                  continue
                }
                if (parsed.type === 'voting_result' || parsed.consensus) {
                  resetVotingState()
                  const votingResults = parsed.individual_results?.map((r: any) => ({ model: r.model, content: r.content || '', success: r.success, error: r.error }))
                  const payload = {
                    id: assistantId,
                    role: 'assistant' as const,
                    content: parsed.consensus || '',
                    isVoting: true,
                    sources: parsed.sources || sources,
                    searchEnabled: parsed.search_enabled,
                    votingResults,
                    brainPlan: parsed.brain_plan || brainPlan,
                  }
                  if (!assistantAdded) {
                    assistantAdded = true
                    setMessages(prev => [...prev, payload])
                  } else {
                    setMessages(prev => prev.map(m => (m.id === assistantId ? { ...m, ...payload } : m)))
                  }
                  continue
                }
                if (parsed.error) {
                  const errorContent = `${t(locale, 'connectionFailed')}: ${parsed.error}`
                  if (!assistantAdded) {
                    assistantAdded = true
                    setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: errorContent }])
                  } else {
                    setMessages(prev => prev.map(m => (m.id === assistantId ? { ...m, content: errorContent } : m)))
                  }
                  continue
                }
                if (parsed.thinking) {
                  setChatStatus(t(locale, 'thinkingStatus'))
                  if (!assistantAdded) {
                    assistantAdded = true
                    setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '', thinking: parsed.thinking }])
                    setExpandedThinking(prev => ({ ...prev, [assistantId]: true }))
                  } else {
                    setMessages(prev => prev.map(m => (m.id === assistantId ? { ...m, thinking: `${m.thinking || ''}${parsed.thinking}` } : m)))
                  }
                  continue
                }
                if (parsed.content) {
                  setChatStatus(t(locale, 'generating'))
                  const payload = {
                    id: assistantId,
                    role: 'assistant' as const,
                    content: parsed.content,
                    sources,
                    searchEnabled: parsed.search_enabled,
                    modelUsed: parsed.model,
                    brainPlan: parsed.brain_plan || brainPlan,
                  }
                  if (!assistantAdded) {
                    assistantAdded = true
                    setMessages(prev => [...prev, payload])
                  } else {
                    setMessages(prev => prev.map(m => (
                      m.id === assistantId
                        ? {
                            ...m,
                            content: `${m.content}${parsed.content}`,
                            sources,
                            searchEnabled: parsed.search_enabled ?? m.searchEnabled,
                            modelUsed: parsed.model || m.modelUsed,
                            brainPlan: parsed.brain_plan || m.brainPlan || brainPlan,
                          }
                        : m
                    )))
                  }
                }
              } catch {
                // Ignore malformed SSE chunks.
              }
            }
          }
        }
      }
      loadConversations()
    } catch (err: any) {
      resetVotingState()
      setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: `${t(locale, 'connectionFailed')}: ${err.message}` }])
    } finally {
      setIsLoading(false)
      setChatStatus('')
    }
  }, [currentConversationId, enableSearch, enableThinking, isLoading, loadConversations, locale, selectedKbIds, selectedModel, useRag, useVoting])

  const handleRerunMessage = async (assistantIndex: number) => {
    if (isLoading) return
    const assistantMessage = messages[assistantIndex]
    const previousUserMessage = [...messages.slice(0, assistantIndex)].reverse().find(message => message.role === 'user')
    if (!assistantMessage || assistantMessage.role !== 'assistant' || !previousUserMessage) return
    const rerunModel = assistantMessage.modelUsed ? AVAILABLE_MODELS.find(model => model.model === assistantMessage.modelUsed) : undefined
    await sendMessage(previousUserMessage.content, {
      useVoting: assistantMessage.isVoting ?? false,
      enableSearch: assistantMessage.searchEnabled ?? enableSearch,
      enableThinking,
      selectedModel: rerunModel ?? selectedModel,
    })
  }

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm(t(locale, 'deleteConversation'))) return
    await apiClient.deleteConversation(id)
    loadConversations()
    if (currentConversationId === id) {
      setCurrentConversationId(null)
      setMessages([])
    }
  }

  const votingCandidates = AVAILABLE_MODELS
    .map(model => ({ model, role: getVotingCandidateRole(model, enableSearch, enableThinking) }))
    .filter(item => item.role !== 'excluded')

  const primaryVotingCandidates = votingCandidates.filter(item => item.role === 'primary')
  const supportVotingCandidates = votingCandidates.filter(item => item.role === 'support')

  return (
    <div className="flex h-full">
      {sidebarCollapsed ? (
        <div className="w-12 border-r bg-card flex flex-col items-center py-4">
          <button onClick={() => { setCurrentConversationId(null); setMessages([]) }} title={t(locale, 'newChat')} className="p-2 rounded hover:bg-muted transition-colors">
            <Plus className="h-5 w-5" />
          </button>
          <button onClick={() => setSidebarCollapsed(false)} title={t(locale, 'chatHistory')} className="p-2 rounded hover:bg-muted transition-colors mt-auto">
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      ) : (
        <div className="w-72 border-r bg-card flex flex-col">
          <div className="p-3 border-b flex items-center justify-between">
            <h3 className="font-medium text-sm">{t(locale, 'chatHistory')}</h3>
            <div className="flex gap-1">
              <button onClick={loadConversations} className="p-1.5 rounded hover:bg-muted transition-colors"><RefreshCw className={cn('h-4 w-4', loadingConversations && 'animate-spin')} /></button>
              <button onClick={() => setSidebarCollapsed(true)} className="p-1.5 rounded hover:bg-muted transition-colors"><ChevronLeft className="h-4 w-4" /></button>
            </div>
          </div>
          <div className="p-2">
            <button onClick={() => { setCurrentConversationId(null); setMessages([]) }} className="w-full flex items-center justify-start px-3 py-2 rounded-md border bg-background hover:bg-muted text-sm font-medium transition-colors">
              <Plus className="h-4 w-4 mr-2" />
              {t(locale, 'newChat')}
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {loadingConversations ? (
              <div className="flex items-center justify-center py-8"><Loader2 className="h-5 w-5 animate-spin text-muted-foreground" /></div>
            ) : conversations.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground text-sm"><MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" /><p>{t(locale, 'noConversation')}</p></div>
            ) : conversations.map(conv => (
              <div key={conv.id} className={cn('group relative rounded-lg p-2 cursor-pointer hover:bg-accent transition-colors', currentConversationId === conv.id && 'bg-accent')} onClick={() => loadConversationMessages(conv.id)}>
                <div className="flex items-start gap-2">
                  <MessageSquare className="h-4 w-4 mt-0.5 flex-shrink-0 text-muted-foreground" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate">{formatConversationTitle(locale, conv.title)}</div>
                    <div className="text-xs text-muted-foreground flex items-center gap-2">
                      <span>{conv.message_count}</span>
                      <span>{formatRelativeDate(locale, conv.last_message_at || conv.created_at)}</span>
                    </div>
                  </div>
                  <button className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-muted transition-all" onClick={(e) => handleDeleteConversation(conv.id, e)}>
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-auto p-6">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-muted-foreground max-w-lg">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">{t(locale, 'startTitle')}</p>
                <p className="text-sm mt-1">{t(locale, 'startDesc')}</p>
              </div>
            </div>
          ) : (
            <div className="space-y-6 max-w-4xl mx-auto">
              {messages.map((message, index) => (
                <div key={message.id} className={cn('flex', message.role === 'user' ? 'justify-end' : 'justify-start')}>
                  <div className={cn('max-w-[85%] rounded-2xl p-4 shadow-sm', message.role === 'user' ? 'bg-primary text-primary-foreground' : message.isVoting ? 'bg-white border border-amber-200' : 'bg-muted')}>
                    {message.role === 'assistant' && (
                      <div className="mb-3 flex items-center justify-between gap-3">
                        <div className="flex items-center gap-2 text-xs text-muted-foreground flex-wrap">
                          <span className={cn('px-2 py-1 rounded-full', message.isVoting ? 'bg-amber-100 text-amber-800' : 'bg-background/60')}>{message.isVoting ? t(locale, 'finalVerdict') : t(locale, 'directAnswer')}</span>
                          {message.searchEnabled && <span className="px-2 py-1 rounded-full bg-blue-100 text-blue-700 flex items-center gap-1"><Globe className="h-3 w-3" />{t(locale, 'online')}</span>}
                          {message.modelUsed && <span className="px-2 py-1 rounded-full bg-background/60">{message.modelUsed}</span>}
                        </div>
                        <button type="button" onClick={() => handleRerunMessage(index)} disabled={isLoading} className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full border bg-background hover:bg-muted disabled:opacity-50">
                          <RefreshCw className={cn('h-3 w-3', isLoading && 'animate-spin')} />
                          {t(locale, 'rerunTurn')}
                        </button>
                      </div>
                    )}

                    {message.brainPlan && (
                      <div className="mb-3 rounded-xl border border-sky-200 bg-sky-50/80 px-3 py-2 text-xs text-sky-900">
                        <div className="font-medium">
                          {t(locale, 'brainRoute')}: {message.brainPlan.route_id}
                        </div>
                        <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-sky-800/90">
                          <span>{t(locale, 'primaryBrain')}: {message.brainPlan.primary_brain}</span>
                          {message.brainPlan.supporting_brains.length > 0 && (
                            <span>{t(locale, 'supportingBrains')}: {message.brainPlan.supporting_brains.join(locale === 'zh-CN' ? '、' : ', ')}</span>
                          )}
                          <span>{t(locale, 'thinkingFramework')}: {message.brainPlan.thinking_framework}</span>
                        </div>
                      </div>
                    )}

                    {message.thinking && (
                      <div className="mb-3 border border-amber-200 rounded-xl overflow-hidden">
                        <button type="button" onClick={() => setExpandedThinking(prev => ({ ...prev, [message.id]: !prev[message.id] }))} className="w-full flex items-center gap-2 px-3 py-2 text-xs text-amber-800 bg-amber-50 hover:bg-amber-100 transition-colors">
                          <Lightbulb className="h-3 w-3" />
                          {t(locale, 'thinking')}
                          {expandedThinking[message.id] ? <ChevronUp className="h-3 w-3 ml-auto" /> : <ChevronDown className="h-3 w-3 ml-auto" />}
                        </button>
                        {expandedThinking[message.id] && <div className="px-3 py-2 text-xs text-muted-foreground bg-amber-50/40 max-h-64 overflow-y-auto"><MarkdownContent content={message.thinking} /></div>}
                      </div>
                    )}

                    {message.isVoting ? (
                      <div className="mb-3 rounded-xl border border-amber-300 bg-amber-50/70 p-3">
                        <div className="flex items-center gap-2 mb-3"><Vote className="h-4 w-4 text-amber-700" /><div className="text-sm font-semibold text-amber-900">{t(locale, 'finalVerdict')}</div></div>
                        {parseVerdictSections(message.content).length > 0 ? (
                          <div className="grid gap-3 md:grid-cols-2">
                            {parseVerdictSections(message.content).map((section, sectionIndex) => (
                              <div
                                key={`${message.id}-section-${sectionIndex}`}
                                className={cn(
                                  'rounded-lg border p-3 bg-white/80',
                                  sectionIndex === 0 && 'md:col-span-2 border-amber-300 bg-amber-100/70',
                                )}
                              >
                                <div className="text-xs font-semibold uppercase tracking-wide text-amber-900/80 mb-2">
                                  {section.title}
                                </div>
                                <MarkdownContent content={section.body} />
                              </div>
                            ))}
                          </div>
                        ) : (
                          <MarkdownContent content={message.content || t(locale, 'noContent')} />
                        )}
                      </div>
                    ) : (
                      <MarkdownContent content={message.content} />
                    )}

                    {message.sources && message.sources.filter(source => !source.score || source.score >= 0.5).length > 0 && (
                      <div className="mt-3 pt-3 border-t border-border/50">
                        <p className="text-xs font-medium mb-2 opacity-70">{t(locale, 'sources')}</p>
                        <div className="space-y-1.5">
                          {message.sources.filter(source => !source.score || source.score >= 0.5).map((source, i) => {
                            const { Icon, color } = sourceMeta(source.source)
                            return (
                              <div key={i} className="flex items-center gap-2 text-xs">
                                <Icon className={cn('h-3 w-3 flex-shrink-0', color)} />
                                {source.url ? <a href={source.url} target="_blank" rel="noopener noreferrer" className="underline opacity-70 hover:opacity-100 truncate">{source.title}</a> : <span className="opacity-70 truncate">{source.title}</span>}
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}

                    {message.votingResults && message.votingResults.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-border/50">
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-xs font-medium opacity-70">{t(locale, 'modelViews')}</p>
                          <span className="text-[10px] text-muted-foreground">{message.votingResults.length} {t(locale, 'modelsUnit')}</span>
                        </div>
                        <div className="space-y-2">
                          {message.votingResults.map((result, i) => {
                            const isExpanded = expandedVotingResults[message.id]?.[i] ?? false
                            return (
                              <div key={i} className="border border-border/40 rounded-xl overflow-hidden bg-background/80">
                                <button type="button" onClick={() => setExpandedVotingResults(prev => ({ ...prev, [message.id]: { ...(prev[message.id] || {}), [i]: !isExpanded } }))} className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-muted/50 transition-colors">
                                  <span className={cn('inline-flex h-2.5 w-2.5 rounded-full', result.success ? 'bg-emerald-500' : 'bg-destructive')} />
                                  <span className="text-sm font-medium">{result.model}</span>
                                  <span className="text-xs text-muted-foreground ml-auto">{result.success ? t(locale, 'summary') : t(locale, 'voteFailed')}</span>
                                  {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                                </button>
                                {!isExpanded && <div className="px-3 pb-3 text-xs text-muted-foreground">{result.success ? `${result.content.slice(0, 180)}${result.content.length > 180 ? '...' : ''}` : (result.error || t(locale, 'voteFailed'))}</div>}
                                {isExpanded && <div className="px-3 pb-3 text-sm max-h-80 overflow-y-auto">{result.success ? <MarkdownContent content={result.content} /> : <div className="text-destructive">{result.error || t(locale, 'voteFailed')}</div>}</div>}
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-2xl p-4 max-w-[85%] w-full">
                    {votingState.isActive && votingState.models.length > 0 ? (
                      <div className="space-y-3">
                        {votingState.models.map(model => (
                          <div key={model} className="border border-border/30 rounded-xl overflow-hidden bg-background/80">
                            <div className="flex items-center gap-2 px-3 py-2 bg-muted/40">
                              <span className={cn('inline-flex h-2.5 w-2.5 rounded-full', votingState.modelStatus[model] === 'completed' ? 'bg-emerald-500' : votingState.modelStatus[model] === 'failed' ? 'bg-destructive' : votingState.modelStatus[model] === 'streaming' ? 'bg-blue-500' : 'bg-slate-400')} />
                              <span className="text-sm font-medium">{model}</span>
                              <span className="text-xs ml-auto text-muted-foreground">{votingState.modelStatus[model]}</span>
                            </div>
                            {votingState.modelContents[model] && <div className="px-3 py-2 text-xs max-h-32 overflow-y-auto"><MarkdownContent content={votingState.modelContents[model]} /></div>}
                          </div>
                        ))}
                        {votingState.isSynthesizing && <div className="border border-amber-300 rounded-xl p-3 bg-amber-50/70"><div className="flex items-center gap-2 text-amber-800 text-sm font-medium mb-2"><Loader2 className="h-4 w-4 animate-spin" />{t(locale, 'synthesizing')}</div>{votingState.synthesisContent && <MarkdownContent content={votingState.synthesisContent} />}</div>}
                      </div>
                    ) : (
                      <div className="flex items-center gap-3"><Loader2 className="h-4 w-4 animate-spin flex-shrink-0" /><span className="text-sm text-muted-foreground">{chatStatus || t(locale, 'processing')}</span></div>
                    )}
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="border-t p-4">
          <form onSubmit={async (e) => { e.preventDefault(); await sendMessage(input, { clearInput: true }) }} className="max-w-4xl mx-auto">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <div className="relative" ref={modelDropdownRef}>
                <button type="button" onClick={() => setShowModelDropdown(prev => !prev)} className={cn('flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors', 'bg-muted text-muted-foreground hover:bg-muted/80', useVoting && 'opacity-50 cursor-not-allowed')} disabled={useVoting}>
                  <span className="max-w-[140px] truncate">{selectedModel.name}</span>
                  <ChevronDown className="h-3 w-3" />
                </button>
                {showModelDropdown && !useVoting && (
                  <div className="absolute bottom-full left-0 mb-1 w-56 rounded-xl border border-border bg-background shadow-2xl ring-1 ring-black/5 z-[100] py-1 max-h-64 overflow-y-auto isolate">
                    {AVAILABLE_MODELS.map(model => (
                      <button key={model.model} type="button" onClick={() => { setSelectedModel(model); setShowModelDropdown(false) }} className={cn('w-full px-3 py-2 text-left text-sm hover:bg-accent transition-colors flex items-center justify-between gap-2', selectedModel.model === model.model && 'bg-accent')}>
                        <span className="truncate">{model.name}</span>
                        <div className="flex items-center gap-1 flex-shrink-0">
                          {model.supportsSearch && <Globe className="h-3 w-3 text-blue-500" />}
                          {model.supportsThinking && <Lightbulb className="h-3 w-3 text-amber-500" />}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <button type="button" onClick={() => setEnableSearch(prev => !prev)} disabled={!selectedModel.supportsSearch && !useVoting} className={cn('flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors', enableSearch ? 'bg-blue-500 text-white' : 'bg-muted text-muted-foreground hover:bg-muted/80', !selectedModel.supportsSearch && !useVoting && 'opacity-50 cursor-not-allowed')}><Globe className="h-3 w-3" />{t(locale, 'webSearch')}</button>
              <button type="button" onClick={() => setEnableThinking(prev => !prev)} disabled={!selectedModel.supportsThinking && !useVoting} className={cn('flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors', enableThinking ? 'bg-amber-500 text-white' : 'bg-muted text-muted-foreground hover:bg-muted/80', !selectedModel.supportsThinking && !useVoting && 'opacity-50 cursor-not-allowed')}><Lightbulb className="h-3 w-3" />{t(locale, 'deepThinking')}</button>
              <button type="button" onClick={() => { const next = !useVoting; setUseVoting(next); if (next) setUseRag(false) }} className={cn('flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors', useVoting ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80')}><Vote className="h-3 w-3" />{t(locale, 'voting')}</button>
              <button type="button" onClick={() => setUseRag(prev => !prev)} className={cn('flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors', useRag ? 'bg-emerald-500 text-white' : 'bg-muted text-muted-foreground hover:bg-muted/80')}><Database className="h-3 w-3" />{t(locale, 'knowledgeBase')}</button>
              {useRag && knowledgeBases.length > 0 && (
                <div className="relative" ref={kbDropdownRef}>
                  <button type="button" onClick={() => setShowKbDropdown(prev => !prev)} className={cn('flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors border', selectedKbIds.length > 0 ? 'bg-emerald-50 border-emerald-300 text-emerald-700' : 'bg-background border-border text-muted-foreground hover:bg-muted')}>
                    {selectedKbIds.length === 0 ? t(locale, 'allKnowledgeBases') : `${t(locale, 'selected')} ${selectedKbIds.length}`}
                    <ChevronDown className="h-3 w-3" />
                  </button>
                  {showKbDropdown && (
                    <div className="absolute bottom-full left-0 mb-1 min-w-[220px] max-h-64 overflow-y-auto rounded-xl border border-border bg-background shadow-2xl ring-1 ring-black/5 z-[100] isolate">
                      <div className="p-2 border-b text-xs text-muted-foreground">{t(locale, 'selectKnowledgeBases')}</div>
                      <div className="p-1">
                        <button type="button" onClick={() => setSelectedKbIds([])} className={cn('w-full text-left px-3 py-1.5 text-xs rounded hover:bg-muted', selectedKbIds.length === 0 && 'bg-muted')}>{t(locale, 'allKnowledgeBases')}</button>
                        {knowledgeBases.map(kb => (
                          <button key={kb.id} type="button" onClick={() => setSelectedKbIds(prev => prev.includes(kb.id) ? prev.filter(id => id !== kb.id) : [...prev, kb.id])} className={cn('w-full text-left px-3 py-1.5 text-xs rounded hover:bg-muted', selectedKbIds.includes(kb.id) && 'bg-muted')}>
                            {kb.name} · {kb.document_count} {t(locale, 'docs')}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              {useVoting && (
                <span className="text-xs text-muted-foreground">
                  {locale === 'zh-CN'
                    ? `${t(locale, 'votingModelsLabel')}：${[
                        primaryVotingCandidates.length > 0
                          ? `${t(locale, 'primaryDecision')} ${primaryVotingCandidates.map(item => item.model.name).join('、')}`
                          : '',
                        supportVotingCandidates.length > 0
                          ? `${t(locale, 'supportEvidence')} ${supportVotingCandidates.map(item => item.model.name).join('、')}`
                          : '',
                      ].filter(Boolean).join(' ｜ ') || t(locale, 'noAvailableModels')}`
                    : `${t(locale, 'votingModelsLabel')}: ${[
                        primaryVotingCandidates.length > 0
                          ? `${t(locale, 'primaryDecision')} ${primaryVotingCandidates.map(item => item.model.name).join(', ')}`
                          : '',
                        supportVotingCandidates.length > 0
                          ? `${t(locale, 'supportEvidence')} ${supportVotingCandidates.map(item => item.model.name).join(', ')}`
                          : '',
                      ].filter(Boolean).join(' | ') || t(locale, 'noAvailableModels')}`}
                </span>
              )}
            </div>
            <div className="flex gap-2">
              <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder={t(locale, 'inputPlaceholder')} className="flex-1 px-4 py-3 rounded-2xl border bg-background focus:outline-none focus:ring-2 focus:ring-primary" disabled={isLoading} />
              <button type="submit" disabled={!input.trim() || isLoading} className="px-4 py-3 rounded-2xl bg-primary text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"><Send className="h-5 w-5" /></button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
