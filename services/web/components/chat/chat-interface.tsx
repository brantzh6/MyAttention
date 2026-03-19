'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { Send, Vote, Loader2, FileText, Globe, Rss, Upload as UploadIcon, BookOpen, MessageSquare, Plus, Trash2, ChevronLeft, ChevronRight, RefreshCw, Brain, ChevronDown, Lightbulb, ChevronUp, Database, CheckCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { apiClient } from '@/lib/api-client'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const API_URL = process.env.API_URL || 'http://localhost:8000'

function MarkdownContent({ content, className }: { content: string; className?: string }) {
  return (
    <div className={cn('prose-chat', className)}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {content}
      </ReactMarkdown>
    </div>
  )
}

// Available models on Bailian platform
const AVAILABLE_MODELS = [
  { provider: 'qwen', model: 'qwen-max', name: '通义千问 Max', supportsSearch: true, supportsThinking: false },
  { provider: 'qwen', model: 'qwen3.5-plus', name: 'Qwen 3.5 Plus', supportsSearch: true, supportsThinking: true },
  { provider: 'qwen', model: 'MiniMax-M2.5', name: 'MiniMax M2.5', supportsSearch: true, supportsThinking: false },
  { provider: 'qwen', model: 'deepseek-v3.2', name: 'DeepSeek V3.2', supportsSearch: true, supportsThinking: true },
  { provider: 'qwen', model: 'glm-5', name: 'GLM-5', supportsSearch: false, supportsThinking: true },
  { provider: 'qwen', model: 'kimi-k2.5', name: 'Kimi K2.5', supportsSearch: false, supportsThinking: false },
]

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  thinking?: string  // 模型思考过程
  sources?: { title: string; url: string; source?: string; score?: number }[]
  isVoting?: boolean
  votingResults?: {
    model: string
    content: string
    success: boolean
    error?: string
  }[]
  searchEnabled?: boolean
  modelUsed?: string
}

// State for real-time voting display
interface VotingState {
  isActive: boolean
  models: string[]
  modelContents: Record<string, string>  // Real-time content from each model
  modelStatus: Record<string, 'pending' | 'streaming' | 'completed' | 'failed'>
  synthesisContent: string  // Real-time synthesis content
  isSynthesizing: boolean
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
  description: string
  document_count: number
  chunk_count: number
  status: string
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [useVoting, setUseVoting] = useState(false)
  const [enableSearch, setEnableSearch] = useState(false)  // Web search toggle
  const [enableThinking, setEnableThinking] = useState(false)  // Thinking mode toggle
  const [useRag, setUseRag] = useState(true)  // Knowledge base retrieval toggle
  const [selectedModel, setSelectedModel] = useState(AVAILABLE_MODELS[0])  // Model selection
  const [showModelDropdown, setShowModelDropdown] = useState(false)
  const [expandedThinking, setExpandedThinking] = useState<Record<string, boolean>>({})  // Track expanded thinking sections
  const [expandedVotingResults, setExpandedVotingResults] = useState<Record<string, Record<number, boolean>>>({})  // Track expanded voting cards
  const [votingState, setVotingState] = useState<VotingState>({
    isActive: false,
    models: [],
    modelContents: {},
    modelStatus: {},
    synthesisContent: '',
    isSynthesizing: false,
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const modelDropdownRef = useRef<HTMLDivElement>(null)

  // Conversation state
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [loadingConversations, setLoadingConversations] = useState(true)
  const [userProfile, setUserProfile] = useState<{ preferences: any[]; facts: any[] } | null>(null)
  const [chatStatus, setChatStatus] = useState<string>('')  // 对话状态显示

  // Knowledge base state
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKbIds, setSelectedKbIds] = useState<string[]>([])  // Selected KB IDs
  const [showKbDropdown, setShowKbDropdown] = useState(false)
  const kbDropdownRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Close model dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modelDropdownRef.current && !modelDropdownRef.current.contains(event.target as Node)) {
        setShowModelDropdown(false)
      }
      if (kbDropdownRef.current && !kbDropdownRef.current.contains(event.target as Node)) {
        setShowKbDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Load knowledge bases
  const loadKnowledgeBases = useCallback(async () => {
    try {
      const data = await apiClient.getKnowledgeBases()
      setKnowledgeBases(data.knowledge_bases)
    } catch (error) {
      console.error('Failed to load knowledge bases:', error)
    }
  }, [])

  useEffect(() => {
    loadKnowledgeBases()
  }, [loadKnowledgeBases])

  // Load conversations on mount
  const loadConversations = useCallback(async () => {
    setLoadingConversations(true)
    try {
      const res = await apiClient.listConversations(1, 50)
      setConversations(res.conversations)
    } catch (error) {
      console.error('Failed to load conversations:', error)
    } finally {
      setLoadingConversations(false)
    }
  }, [])

  // Load user profile (memories)
  const loadUserProfile = useCallback(async () => {
    try {
      const profile = await apiClient.getUserProfile()
      setUserProfile(profile)
    } catch (error) {
      console.error('Failed to load user profile:', error)
    }
  }, [])

  useEffect(() => {
    loadConversations()
    loadUserProfile()
  }, [loadConversations, loadUserProfile])

  // Load conversation messages
  const loadConversationMessages = useCallback(async (conversationId: string) => {
    try {
      const msgs = await apiClient.getMessages(conversationId, 100)
      setMessages(msgs.map((m: any) => ({
        id: m.id,
        role: m.role as 'user' | 'assistant',
        content: m.content,
        sources: m.sources || [],
        isVoting: !!m.voting_results,
        votingResults: m.voting_results?.individual_results?.map((r: any) => ({
          model: r.model,
          content: r.content || '',
          success: r.success,
          error: r.error,
        })),
        modelUsed: m.model,
      })))
      setCurrentConversationId(conversationId)
    } catch (error) {
      console.error('Failed to load messages:', error)
    }
  }, [])

  const handleSelectConversation = (id: string) => {
    loadConversationMessages(id)
  }

  const handleNewConversation = () => {
    setCurrentConversationId(null)
    setMessages([])
  }

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('确定要删除这个会话吗？')) return
    
    try {
      await apiClient.deleteConversation(id)
      loadConversations()
      if (currentConversationId === id) {
        handleNewConversation()
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    }
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    
    if (days === 0) return '今天'
    if (days === 1) return '昨天'
    if (days < 7) return `${days}天前`
    return date.toLocaleDateString()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    }

    setMessages(prev => [...prev, userMessage])
    const currentInput = input.trim()
    setInput('')
    setIsLoading(true)
    
    // Show detailed initial status immediately - no waiting
    const modelInfo = useVoting ? '多模型投票' : selectedModel.name
    const searchInfo = enableSearch ? ' | 联网搜索' : ''
    const thinkingInfo = enableThinking && selectedModel.supportsThinking ? ' | 深度思考' : ''
    setChatStatus(`连接后端服务... 模型: ${modelInfo}${searchInfo}${thinkingInfo}`)

    const assistantId = (Date.now() + 1).toString()
    // Don't add empty assistant message yet, add it when content arrives
    let assistantMessageAdded = false

    try {
      setChatStatus(`调用 API 接口... 模型: ${modelInfo}${searchInfo}${thinkingInfo}`)
      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: currentInput,
          use_voting: useVoting,
          use_rag: useRag,
          enable_search: enableSearch,
          enable_thinking: useVoting ? enableThinking : (enableThinking && selectedModel.supportsThinking),
          conversation_id: currentConversationId,
          provider: useVoting ? undefined : selectedModel.provider,
          model: useVoting ? undefined : selectedModel.model,
          kb_ids: useRag && selectedKbIds.length > 0 ? selectedKbIds : undefined,
        }),
      })

      if (!res.ok) throw new Error(`API error: ${res.status}`)

      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      let sources: Message['sources'] = []
      let newConversationId: string | null = null

      if (reader) {
        let sseBuffer = ''
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          sseBuffer += decoder.decode(value, { stream: true })
          // Split on double-newline (SSE event boundary)
          const parts = sseBuffer.split('\n\n')
          sseBuffer = parts.pop() || ''  // Keep incomplete trailing part

          for (const part of parts) {
            const lines = part.split('\n')
            for (const line of lines) {
            if (!line.startsWith('data: ')) continue
            const data = line.slice(6).trim()
            if (data === '[DONE]') continue

            try {
              const parsed = JSON.parse(data)

              // Handle status updates from backend
              if (parsed.status) {
                setChatStatus(parsed.status)
                continue
              }

              // Handle voting events
              if (parsed.type === 'voting_start') {
                const modelList = parsed.models?.join(', ') || ''
                setChatStatus(`多模型投票开始: ${modelList}`)
                // Initialize voting state
                const initialStatus: Record<string, 'pending' | 'streaming' | 'completed' | 'failed'> = {}
                const initialContents: Record<string, string> = {}
                for (const model of (parsed.models || [])) {
                  initialStatus[model] = 'pending'
                  initialContents[model] = ''
                }
                setVotingState({
                  isActive: true,
                  models: parsed.models || [],
                  modelContents: initialContents,
                  modelStatus: initialStatus,
                  synthesisContent: '',
                  isSynthesizing: false,
                })
                // Add assistant message placeholder for voting
                if (!assistantMessageAdded) {
                  assistantMessageAdded = true
                  setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: '' }])
                }
                continue
              }

              // Handle real-time content from individual models
              if (parsed.type === 'voting_model_content') {
                setVotingState(prev => ({
                  ...prev,
                  modelContents: {
                    ...prev.modelContents,
                    [parsed.model]: (prev.modelContents[parsed.model] || '') + parsed.content,
                  },
                  modelStatus: {
                    ...prev.modelStatus,
                    [parsed.model]: 'streaming',
                  },
                }))
                setChatStatus(`${parsed.model} 正在输出...`)
                continue
              }
              
              if (parsed.type === 'voting_progress') {
                const statusText = parsed.success ? '完成' : '失败'
                const errorInfo = !parsed.success && parsed.error ? `: ${parsed.error}` : ''
                setChatStatus(`${parsed.model} ${statusText}${errorInfo} (${parsed.completed}/${parsed.total})`)
                // Update model status
                setVotingState(prev => ({
                  ...prev,
                  modelStatus: {
                    ...prev.modelStatus,
                    [parsed.model]: parsed.success ? 'completed' : 'failed',
                  },
                }))
                continue
              }
              
              if (parsed.type === 'voting_synthesizing') {
                setChatStatus('正在综合各模型观点...')
                setVotingState(prev => ({
                  ...prev,
                  isSynthesizing: true,
                }))
                continue
              }

              // Handle real-time synthesis content
              if (parsed.type === 'voting_synthesis_content') {
                setVotingState(prev => ({
                  ...prev,
                  synthesisContent: prev.synthesisContent + parsed.content,
                }))
                // Update message content in real-time
                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? { ...m, content: m.content + parsed.content }
                    : m
                ))
                continue
              }
              
              if (parsed.type === 'voting_result') {
                setChatStatus('')
                // Reset voting state
                setVotingState({
                  isActive: false,
                  models: [],
                  modelContents: {},
                  modelStatus: {},
                  synthesisContent: '',
                  isSynthesizing: false,
                })
                setMessages(prev => prev.map(m =>
                  m.id === assistantId
                    ? {
                        ...m,
                        content: parsed.consensus,
                        isVoting: true,
                        sources: parsed.sources || sources,
                        searchEnabled: parsed.search_enabled,
                        votingResults: parsed.individual_results?.map((r: any) => ({
                          model: r.model,
                          content: r.content || '',
                          success: r.success,
                          error: r.error,
                        })),
                      }
                    : m
                ))
                continue
              }

              // Capture conversation_id from response
              if (parsed.conversation_id && !newConversationId) {
                newConversationId = parsed.conversation_id
                setCurrentConversationId(newConversationId)
              }

              if (parsed.error) {
                setChatStatus('')
                if (!assistantMessageAdded) {
                  assistantMessageAdded = true
                  setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: `Error: ${parsed.error}` }])
                } else {
                  setMessages(prev => prev.map(m =>
                    m.id === assistantId ? { ...m, content: `Error: ${parsed.error}` } : m
                  ))
                }
                break
              }

              if (parsed.sources && parsed.sources.length > 0) {
                sources = parsed.sources
              }

              // Capture search status and model info
              const searchEnabled = parsed.search_enabled
              const modelUsed = parsed.model

              // Handle thinking content from backend
              if (parsed.thinking) {
                setChatStatus('模型正在思考...')
                if (!assistantMessageAdded) {
                  assistantMessageAdded = true
                  setMessages(prev => [...prev, {
                    id: assistantId,
                    role: 'assistant',
                    content: '',
                    thinking: parsed.thinking,
                  }])
                  // Auto-expand thinking for this message
                  setExpandedThinking(prev => ({ ...prev, [assistantId]: true }))
                } else {
                  setMessages(prev => prev.map(m =>
                    m.id === assistantId
                      ? { ...m, thinking: (m.thinking || '') + parsed.thinking }
                      : m
                  ))
                }
                continue
              }

              if (parsed.content) {
                setChatStatus('正在生成回复...')
                // Add assistant message on first content
                if (!assistantMessageAdded) {
                  assistantMessageAdded = true
                  setMessages(prev => [...prev, {
                    id: assistantId,
                    role: 'assistant',
                    content: parsed.content,
                    sources,
                    searchEnabled: searchEnabled,
                    modelUsed: modelUsed,
                  }])
                } else {
                  setMessages(prev => prev.map(m =>
                    m.id === assistantId
                      ? { 
                          ...m, 
                          content: m.content + parsed.content,
                          sources,
                          searchEnabled: searchEnabled !== undefined ? searchEnabled : m.searchEnabled,
                          modelUsed: modelUsed || m.modelUsed,
                        }
                      : m
                  ))
                }
              }

              if (parsed.consensus) {
                setChatStatus('')
                if (!assistantMessageAdded) {
                  assistantMessageAdded = true
                  setMessages(prev => [...prev, {
                    id: assistantId,
                    role: 'assistant',
                    content: parsed.consensus,
                    isVoting: true,
                    sources: parsed.sources || sources,
                    searchEnabled: parsed.search_enabled,
                    votingResults: parsed.individual_results?.map((r: any) => ({
                      model: r.model,
                      content: r.content || '',
                      success: r.success,
                      error: r.error,
                    })),
                  }])
                } else {
                  setMessages(prev => prev.map(m =>
                    m.id === assistantId
                      ? {
                          ...m,
                          content: parsed.consensus,
                          isVoting: true,
                          sources: parsed.sources || sources,
                          searchEnabled: parsed.search_enabled,
                          votingResults: parsed.individual_results?.map((r: any) => ({
                            model: r.model,
                            content: r.content || '',
                            success: r.success,
                            error: r.error,
                          })),
                        }
                      : m
                  ))
                }
              }
            } catch {
              // skip unparseable lines
            }
          }
          }  // end parts loop
        }
      }

      // Refresh conversations list to show new/updated conversation
      loadConversations()
    } catch (err: any) {
      setChatStatus('')
      const errorContent = `连接失败: ${err.message}`
      if (!assistantMessageAdded) {
        setMessages(prev => [...prev, { id: assistantId, role: 'assistant', content: errorContent }])
      } else {
        setMessages(prev => prev.map(m =>
          m.id === assistantId ? { ...m, content: errorContent } : m
        ))
      }
    } finally {
      setIsLoading(false)
      setChatStatus('')
    }
  }

  return (
    <div className="flex h-full">
      {/* Sidebar - Conversation List */}
      {sidebarCollapsed ? (
        <div className="w-12 border-r bg-card flex flex-col items-center py-4">
          <button
            onClick={handleNewConversation}
            title="新对话"
            className="p-2 rounded hover:bg-muted transition-colors"
          >
            <Plus className="h-5 w-5" />
          </button>
          <button
            onClick={() => setSidebarCollapsed(false)}
            title="展开侧边栏"
            className="p-2 rounded hover:bg-muted transition-colors mt-auto"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      ) : (
        <div className="w-64 border-r bg-card flex flex-col">
          {/* Sidebar Header */}
          <div className="p-3 border-b flex items-center justify-between">
            <h3 className="font-medium text-sm">会话历史</h3>
            <div className="flex gap-1">
              <button
                onClick={loadConversations}
                className="p-1.5 rounded hover:bg-muted transition-colors"
              >
                <RefreshCw className={cn('h-4 w-4', loadingConversations && 'animate-spin')} />
              </button>
              <button
                onClick={() => setSidebarCollapsed(true)}
                className="p-1.5 rounded hover:bg-muted transition-colors"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* New Chat Button */}
          <div className="p-2">
            <button
              onClick={handleNewConversation}
              className="w-full flex items-center justify-start px-3 py-2 rounded-md border bg-background hover:bg-muted text-sm font-medium transition-colors"
            >
              <Plus className="h-4 w-4 mr-2" />
              新对话
            </button>
          </div>

          {/* User Memory Summary */}
          {userProfile && (userProfile.preferences.length > 0 || userProfile.facts.length > 0) && (
            <div className="px-2 pb-2">
              <div className="p-2 rounded-md bg-muted/50 border border-dashed">
                <div className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground mb-1">
                  <Brain className="h-3 w-3" />
                  已记住的偏好
                </div>
                <div className="text-xs text-muted-foreground space-y-0.5">
                  {userProfile.preferences.slice(0, 2).map((p, i) => (
                    <div key={i} className="truncate">{p.content}</div>
                  ))}
                  {userProfile.preferences.length > 2 && (
                    <div className="opacity-60">+{userProfile.preferences.length - 2} 条更多...</div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Conversation List */}
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {loadingConversations ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            ) : conversations.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground text-sm">
                <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>暂无会话</p>
              </div>
            ) : (
              conversations.map(conv => (
                <div
                  key={conv.id}
                  className={cn(
                    'group relative rounded-lg p-2 cursor-pointer hover:bg-accent transition-colors',
                    currentConversationId === conv.id && 'bg-accent'
                  )}
                  onClick={() => handleSelectConversation(conv.id)}
                >
                  <div className="flex items-start gap-2">
                    <MessageSquare className="h-4 w-4 mt-0.5 flex-shrink-0 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">
                        {conv.title || '新对话'}
                      </div>
                      <div className="text-xs text-muted-foreground flex items-center gap-2">
                        <span>{conv.message_count} 条消息</span>
                        <span>{formatDate(conv.last_message_at || conv.created_at)}</span>
                      </div>
                    </div>
                    <button
                      className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-muted transition-all"
                      onClick={(e) => handleDeleteConversation(conv.id, e)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages area */}
        <div className="flex-1 overflow-auto p-6">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">开始对话</p>
                <p className="text-sm mt-1">向 AI 提问，获取基于知识库的智能回答</p>
                {userProfile && userProfile.preferences.length > 0 && (
                  <p className="text-xs mt-3 text-primary/70">
                    系统已加载 {userProfile.preferences.length} 条用户偏好
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="space-y-6 max-w-3xl mx-auto">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  <div
                    className={cn(
                      'max-w-[80%] rounded-lg p-4',
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    )}
                  >
                    {/* Thinking process (collapsible) - shown ABOVE content */}
                    {message.thinking && (
                      <div className="mb-2 border border-amber-200/50 rounded-md overflow-hidden">
                        <button
                          type="button"
                          onClick={() => setExpandedThinking(prev => ({ ...prev, [message.id]: !prev[message.id] }))}
                          className="w-full flex items-center gap-1.5 px-3 py-1.5 text-xs text-amber-700 bg-amber-50/50 hover:bg-amber-50 transition-colors"
                        >
                          <Lightbulb className="h-3 w-3" />
                          <span>思考过程</span>
                          {expandedThinking[message.id] ? <ChevronUp className="h-3 w-3 ml-auto" /> : <ChevronDown className="h-3 w-3 ml-auto" />}
                        </button>
                        {expandedThinking[message.id] && (
                          <div className="px-3 py-2 text-xs text-muted-foreground bg-amber-50/20 max-h-64 overflow-y-auto">
                            <MarkdownContent content={message.thinking} />
                          </div>
                        )}
                      </div>
                    )}

                    {/* Main content with Markdown rendering */}
                    <MarkdownContent content={message.content} />
                    
                    {/* Model and search status indicator */}
                    {message.role === 'assistant' && (message.modelUsed || message.searchEnabled !== undefined) && (
                      <div className="mt-2 flex items-center gap-2 text-[10px] text-muted-foreground">
                        {message.modelUsed && (
                          <span className="px-1.5 py-0.5 rounded bg-background/50">
                            {message.modelUsed}
                          </span>
                        )}
                        {message.searchEnabled && (
                          <span className="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-600 flex items-center gap-1">
                            <Globe className="h-2.5 w-2.5" />
                            联网
                          </span>
                        )}
                      </div>
                    )}
                    
                    {message.sources && message.sources.filter(s => !s.score || s.score >= 0.5).length > 0 && (
                      <div className="mt-3 pt-3 border-t border-border/50">
                        <p className="text-xs font-medium mb-2 opacity-70">引用来源:</p>
                        <div className="space-y-1.5">
                          {message.sources.filter(s => !s.score || s.score >= 0.5).map((source, i) => {
                            const sourceType = source.source || 'manual'
                            const SourceIcon = sourceType === 'rss' ? Rss
                              : sourceType === 'web' ? Globe
                              : sourceType === 'upload' ? UploadIcon
                              : sourceType === 'documentation' ? BookOpen
                              : FileText
                            const typeColor = sourceType === 'rss' ? 'text-orange-500'
                              : sourceType === 'web' ? 'text-purple-500'
                              : sourceType === 'upload' ? 'text-green-500'
                              : sourceType === 'documentation' ? 'text-cyan-500'
                              : 'text-blue-500'
                            return (
                              <div key={i} className="flex items-center gap-2 text-xs">
                                <SourceIcon className={cn('h-3 w-3 flex-shrink-0', typeColor)} />
                                {source.url ? (
                                  <a
                                    href={source.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="underline opacity-70 hover:opacity-100 truncate"
                                  >
                                    {source.title}
                                  </a>
                                ) : (
                                  <span className="opacity-70 truncate">{source.title}</span>
                                )}
                                {source.score != null && (
                                  <span className="flex-shrink-0 px-1.5 py-0.5 rounded bg-background/50 text-[10px] font-mono opacity-60">
                                    {(source.score * 100).toFixed(0)}%
                                  </span>
                                )}
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}

                    {/* Voting results - expandable cards */}
                    {message.votingResults && message.votingResults.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-border/50">
                        <p className="text-xs font-medium mb-2 opacity-70">各模型观点:</p>
                        <div className="space-y-2">
                          {message.votingResults.map((result, i) => {
                            const isExpanded = expandedVotingResults[message.id]?.[i] ?? false
                            const toggleExpand = () => {
                              setExpandedVotingResults(prev => ({
                                ...prev,
                                [message.id]: {
                                  ...(prev[message.id] || {}),
                                  [i]: !isExpanded,
                                },
                              }))
                            }
                            return (
                              <div key={i} className="border border-border/30 rounded-md overflow-hidden">
                                <button
                                  type="button"
                                  onClick={toggleExpand}
                                  className="w-full flex items-center gap-2 px-3 py-1.5 text-xs bg-muted/30 hover:bg-muted/50 transition-colors"
                                >
                                  <span className="font-medium">{result.model}</span>
                                  {!result.success && (
                                    <span className="text-destructive">(失败)</span>
                                  )}
                                  {isExpanded ? <ChevronUp className="h-3 w-3 ml-auto" /> : <ChevronDown className="h-3 w-3 ml-auto" />}
                                </button>
                                {!isExpanded && result.content && (
                                  <div className="px-3 py-1.5 text-xs text-muted-foreground line-clamp-2">
                                    {result.content.slice(0, 150)}{result.content.length > 150 ? '...' : ''}
                                  </div>
                                )}
                                {isExpanded && (
                                  <div className="px-3 py-2 text-xs max-h-80 overflow-y-auto">
                                    {result.success ? (
                                      <MarkdownContent content={result.content} />
                                    ) : (
                                      <span className="text-destructive">{result.error || '模型调用失败'}</span>
                                    )}
                                  </div>
                                )}
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
                  <div className="bg-muted rounded-lg p-4 max-w-[80%] w-full">
                    {/* Voting progress display */}
                    {votingState.isActive && votingState.models.length > 0 && (
                      <div className="space-y-3 mb-3">
                        <div className="text-xs font-medium text-muted-foreground">
                          多模型并行查询中...
                        </div>
                        {votingState.models.map((model) => {
                          const status = votingState.modelStatus[model]
                          const content = votingState.modelContents[model] || ''
                          const statusColor = status === 'completed' ? 'text-green-500' 
                            : status === 'failed' ? 'text-red-500'
                            : status === 'streaming' ? 'text-blue-500'
                            : 'text-muted-foreground'
                          const statusIcon = status === 'completed' ? '✓' 
                            : status === 'failed' ? '✗'
                            : status === 'streaming' ? '●'
                            : '○'
                          return (
                            <div key={model} className="border border-border/30 rounded-md overflow-hidden">
                              <div className="flex items-center gap-2 px-3 py-1.5 bg-muted/50">
                                <span className={cn('text-xs', statusColor)}>{statusIcon}</span>
                                <span className="text-xs font-medium">{model}</span>
                                <span className={cn('text-xs ml-auto', statusColor)}>
                                  {status === 'pending' && '等待中'}
                                  {status === 'streaming' && '输出中...'}
                                  {status === 'completed' && '已完成'}
                                  {status === 'failed' && '失败'}
                                </span>
                              </div>
                              {content && (
                                <div className="px-3 py-2 text-xs max-h-32 overflow-y-auto">
                                  <MarkdownContent content={content.length > 500 ? content.slice(-500) + '...' : content} />
                                </div>
                              )}
                            </div>
                          )
                        })}
                        {votingState.isSynthesizing && (
                          <div className="border border-primary/30 rounded-md overflow-hidden">
                            <div className="flex items-center gap-2 px-3 py-1.5 bg-primary/10">
                              <Loader2 className="h-3 w-3 animate-spin text-primary" />
                              <span className="text-xs font-medium text-primary">综合分析中...</span>
                            </div>
                            {votingState.synthesisContent && (
                              <div className="px-3 py-2 text-xs max-h-48 overflow-y-auto">
                                <MarkdownContent content={votingState.synthesisContent} />
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                    {/* Default loading indicator */}
                    {!votingState.isActive && (
                      <div className="flex items-center gap-3">
                        <Loader2 className="h-4 w-4 animate-spin flex-shrink-0" />
                        <span className="text-sm text-muted-foreground">{chatStatus || '处理中...'}</span>
                      </div>
                    )}
                    {/* Simple status when voting but not showing cards */}
                    {votingState.isActive && (
                      <div className="flex items-center gap-3 mt-2 pt-2 border-t border-border/30">
                        <Loader2 className="h-4 w-4 animate-spin flex-shrink-0" />
                        <span className="text-sm text-muted-foreground">{chatStatus || '处理中...'}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input area */}
        <div className="border-t p-4">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              {/* Model selector */}
              <div className="relative" ref={modelDropdownRef}>
                <button
                  type="button"
                  onClick={() => setShowModelDropdown(!showModelDropdown)}
                  className={cn(
                    'flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors',
                    'bg-muted text-muted-foreground hover:bg-muted/80',
                    useVoting && 'opacity-50 cursor-not-allowed'
                  )}
                  disabled={useVoting}
                  title={useVoting ? '投票模式下自动选择多个模型' : '选择模型'}
                >
                  <span className="max-w-[120px] truncate">{selectedModel.name}</span>
                  <ChevronDown className="h-3 w-3" />
                </button>
                {showModelDropdown && !useVoting && (
                  <div className="absolute bottom-full left-0 mb-1 w-52 bg-popover border rounded-lg shadow-lg z-[100] py-1 max-h-64 overflow-y-auto">
                    {AVAILABLE_MODELS.map((model, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => {
                          setSelectedModel(model)
                          setShowModelDropdown(false)
                        }}
                        className={cn(
                          'w-full px-3 py-2 text-left text-sm hover:bg-accent transition-colors flex items-center justify-between gap-2',
                          selectedModel.model === model.model && 'bg-accent'
                        )}
                      >
                        <span className="truncate">{model.name}</span>
                        <div className="flex items-center gap-1 flex-shrink-0">
                          {model.supportsSearch && (
                            <span title="支持联网搜索"><Globe className="h-3 w-3 text-blue-500" /></span>
                          )}
                          {model.supportsThinking && (
                            <span title="支持深度思考"><Lightbulb className="h-3 w-3 text-amber-500" /></span>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <button
                type="button"
                onClick={() => setEnableSearch(!enableSearch)}
                className={cn(
                  'flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors',
                  enableSearch
                    ? 'bg-blue-500 text-white'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80',
                  !selectedModel.supportsSearch && !useVoting && 'opacity-50 cursor-not-allowed'
                )}
                disabled={!selectedModel.supportsSearch && !useVoting}
                title={!selectedModel.supportsSearch && !useVoting ? '当前模型不支持联网搜索' : ''}
              >
                <Globe className="h-3 w-3" />
                联网搜索
              </button>
              <button
                type="button"
                onClick={() => setEnableThinking(!enableThinking)}
                className={cn(
                  'flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors',
                  enableThinking
                    ? 'bg-amber-500 text-white'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80',
                  !selectedModel.supportsThinking && !useVoting && 'opacity-50 cursor-not-allowed'
                )}
                disabled={!selectedModel.supportsThinking && !useVoting}
                title={!selectedModel.supportsThinking && !useVoting ? '当前模型不支持深度思考' : ''}
              >
                <Lightbulb className="h-3 w-3" />
                深度思考
              </button>
              <button
                type="button"
                onClick={() => {
                  const newVoting = !useVoting
                  setUseVoting(newVoting)
                  // Default: turn off RAG when entering voting mode
                  if (newVoting) {
                    setUseRag(false)
                  }
                }}
                className={cn(
                  'flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors',
                  useVoting
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                )}
              >
                <Vote className="h-3 w-3" />
                多模型投票
              </button>
              <button
                type="button"
                onClick={() => setUseRag(!useRag)}
                className={cn(
                  'flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors',
                  useRag
                    ? 'bg-emerald-500 text-white'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                )}
              >
                <Database className="h-3 w-3" />
                知识库
              </button>
              {/* Knowledge base selector dropdown */}
              {useRag && knowledgeBases.length > 0 && (
                <div className="relative" ref={kbDropdownRef}>
                  <button
                    type="button"
                    onClick={() => setShowKbDropdown(!showKbDropdown)}
                    className={cn(
                      'flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition-colors border',
                      selectedKbIds.length > 0
                        ? 'bg-emerald-50 border-emerald-300 text-emerald-700'
                        : 'bg-background border-border text-muted-foreground hover:bg-muted'
                    )}
                  >
                    {selectedKbIds.length === 0 ? '全部知识库' : `已选 ${selectedKbIds.length} 个`}
                    <ChevronDown className="h-3 w-3" />
                  </button>
                  {showKbDropdown && (
                    <div className="absolute bottom-full left-0 mb-1 bg-background border rounded-lg shadow-lg min-w-[200px] max-h-64 overflow-y-auto z-10">
                      <div className="p-2 border-b text-xs text-muted-foreground">
                        选择要搜索的知识库（可多选）
                      </div>
                      <div className="p-1">
                        <button
                          type="button"
                          onClick={() => setSelectedKbIds([])}
                          className={cn(
                            'w-full text-left px-3 py-1.5 text-xs rounded hover:bg-muted flex items-center gap-2',
                            selectedKbIds.length === 0 && 'bg-muted'
                          )}
                        >
                          <div className={cn(
                            'w-4 h-4 border rounded flex items-center justify-center',
                            selectedKbIds.length === 0 && 'bg-emerald-500 border-emerald-500'
                          )}>
                            {selectedKbIds.length === 0 && <CheckCircle className="h-3 w-3 text-white" />}
                          </div>
                          全部知识库
                        </button>
                        {knowledgeBases.map(kb => (
                          <button
                            key={kb.id}
                            type="button"
                            onClick={() => {
                              setSelectedKbIds(prev =>
                                prev.includes(kb.id)
                                  ? prev.filter(id => id !== kb.id)
                                  : [...prev, kb.id]
                              )
                            }}
                            className={cn(
                              'w-full text-left px-3 py-1.5 text-xs rounded hover:bg-muted flex items-center gap-2',
                              selectedKbIds.includes(kb.id) && 'bg-muted'
                            )}
                          >
                            <div className={cn(
                              'w-4 h-4 border rounded flex items-center justify-center',
                              selectedKbIds.includes(kb.id) && 'bg-emerald-500 border-emerald-500'
                            )}>
                              {selectedKbIds.includes(kb.id) && <CheckCircle className="h-3 w-3 text-white" />}
                            </div>
                            <div className="flex-1 truncate">
                              <div className="font-medium truncate">{kb.name}</div>
                              <div className="text-muted-foreground">{kb.document_count} 文档</div>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              {enableSearch && (
                <span className="text-xs text-muted-foreground">
                  {useVoting ? '将使用支持搜索的模型进行投票' : '将使用模型内置联网搜索获取实时信息'}
                </span>
              )}
              {useVoting && !enableSearch && (
                <span className="text-xs text-muted-foreground">
                  将使用多个模型对比分析
                </span>
              )}
            </div>
            
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="输入您的问题..."
                className="flex-1 px-4 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="px-4 py-2 rounded-lg bg-primary text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
