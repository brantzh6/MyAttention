const API_URL = process.env.API_URL || 'http://localhost:8000'

export interface FeedItem {
  id: string
  title: string
  summary: string
  source: string
  source_id: string
  source_type: 'rss' | 'web' | 'api'
  url: string
  published_at: string
  category: string
  importance: number
  is_read: boolean
  is_favorite: boolean
}

export interface Source {
  id: string
  name: string
  type: 'rss' | 'web' | 'api'
  url: string
  category: string
  tags: string[]
  enabled: boolean
  lastFetched: string | null
  successRate: number
  status: 'ok' | 'warning' | 'error'
}

export interface LLMProvider {
  id: string
  name: string
  provider: string
  model: string
  enabled: boolean
  apiKeySet: boolean
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: { title: string; url: string }[]
  createdAt: string
}

export interface RAGDocument {
  doc_id: string
  title: string
  source: string
  source_type: string
  url: string
  file_type?: string
  chunk_count: number
  preview: string
  created_at?: string
}

export interface FeedHealthSnapshot {
  timestamp: string
  storage: {
    object_store_backend: string
    feeds_read_backend: string
    cache_layers?: string[]
  }
  counts: {
    raw_ingest_total: number
    feed_items_total: number
    raw_ingest_1h: number
    raw_ingest_24h: number
    feed_items_1h: number
    feed_items_24h: number
    raw_errors_24h: number
    raw_durable_24h: number
    raw_duplicate_24h: number
    raw_pending_1h: number
    raw_pending_24h: number
    active_sources_24h: number
  }
  freshness: {
    last_raw_ingest_at: string | null
    last_feed_item_at: string | null
    last_raw_ingest_age_hours: number | null
    last_feed_item_age_hours: number | null
  }
  ratios: {
    durable_ratio_24h: number
    persist_ratio_24h: number
  }
  summary: {
    status: string
    state: string
    message: string
  }
}

export interface RAGSource {
  name: string
  count: number
}

// Memory types
export interface Memory {
  memory_id: string
  content: string
  fact_type: 'preference' | 'fact' | 'decision' | 'insight'
  category: string | null
  tags: string[]
  confidence: number
  access_count: number
  created_at: string
  source_conversation_id?: string
}

export interface MemoryStats {
  total_memories: number
  type_distribution: Record<string, number>
  collection_status: string
}

// Conversation types
export interface Conversation {
  id: string
  title: string | null
  model: string | null
  use_voting: boolean
  summary: string | null
  message_count: number
  context_window: number
  last_message_at: string | null
  created_at: string
  updated_at: string
}

export interface ConversationMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  model: string | null
  tokens_used: number | null
  sources: { title: string; url: string; source?: string; score?: number }[]
  metadata?: Record<string, any>
  created_at: string
}

export const apiClient = {
  async getFeeds(sourceId?: string, category?: string): Promise<FeedItem[]> {
    const params = new URLSearchParams()
    if (sourceId) params.set('source_id', sourceId)
    if (category) params.set('category', category)
    const qs = params.toString()
    const res = await fetch(`${API_URL}/api/feeds${qs ? '?' + qs : ''}`)
    if (!res.ok) throw new Error('Failed to fetch feeds')
    return res.json()
  },

  async refreshFeeds(): Promise<{ status: string; count: number }> {
    const res = await fetch(`${API_URL}/api/feeds/refresh`, { method: 'POST' })
    if (!res.ok) throw new Error('Failed to refresh feeds')
    return res.json()
  },

  async getFeedsHealth(): Promise<FeedHealthSnapshot> {
    const res = await fetch(`${API_URL}/api/feeds/health`)
    if (!res.ok) throw new Error('Failed to fetch feed health')
    return res.json()
  },

  async getSources(): Promise<Source[]> {
    const res = await fetch(`${API_URL}/api/sources`)
    if (!res.ok) throw new Error('Failed to fetch sources')
    return res.json()
  },

  async createSource(source: Omit<Source, 'id' | 'lastFetched' | 'successRate' | 'status'>): Promise<Source> {
    const res = await fetch(`${API_URL}/api/sources`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(source),
    })
    if (!res.ok) throw new Error('Failed to create source')
    return res.json()
  },

  async deleteSource(id: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/sources/${id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete source')
  },

  async getLLMProviders(): Promise<LLMProvider[]> {
    const res = await fetch(`${API_URL}/api/llm/providers`)
    if (!res.ok) throw new Error('Failed to fetch LLM providers')
    return res.json()
  },

  async chat(message: string, useVoting?: boolean): Promise<ReadableStream<Uint8Array>> {
    const res = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, useVoting }),
    })
    if (!res.ok) throw new Error('Failed to send message')
    return res.body!
  },

  async getConversations(): Promise<{ id: string; title: string; createdAt: string }[]> {
    const res = await fetch(`${API_URL}/api/conversations`)
    if (!res.ok) throw new Error('Failed to fetch conversations')
    return res.json()
  },

  async getConversationMessages(conversationId: string): Promise<ChatMessage[]> {
    const res = await fetch(`${API_URL}/api/conversations/${conversationId}/messages`)
    if (!res.ok) throw new Error('Failed to fetch messages')
    return res.json()
  },

  // RAG Knowledge Base
  async getRAGDocuments(): Promise<{ documents: RAGDocument[]; total: number }> {
    const res = await fetch(`${API_URL}/api/rag/documents`)
    if (!res.ok) throw new Error('Failed to fetch RAG documents')
    return res.json()
  },

  async getRAGSources(): Promise<{ sources: RAGSource[] }> {
    const res = await fetch(`${API_URL}/api/rag/sources`)
    if (!res.ok) throw new Error('Failed to fetch RAG sources')
    return res.json()
  },

  async getRAGStats(): Promise<{ total_documents: number; status: string }> {
    const res = await fetch(`${API_URL}/api/rag/stats`)
    if (!res.ok) throw new Error('Failed to fetch RAG stats')
    return res.json()
  },

  async addRAGText(data: { content: string; title: string; source?: string; url?: string }): Promise<{ doc_id: string; chunks: number; title: string }> {
    const res = await fetch(`${API_URL}/api/rag/index`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to index document')
    return res.json()
  },

  async uploadRAGFile(file: File): Promise<{ doc_id: string; chunks: number; title: string; filename: string }> {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(`${API_URL}/api/rag/upload`, {
      method: 'POST',
      body: formData,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }))
      throw new Error(err.detail || 'Failed to upload file')
    }
    return res.json()
  },

  async deleteRAGDocument(docId: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/rag/documents/${docId}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete document')
  },

  // Conversations
  async listConversations(page = 1, pageSize = 20): Promise<{ conversations: Conversation[]; total: number; page: number; page_size: number }> {
    const res = await fetch(`${API_URL}/api/conversations?page=${page}&page_size=${pageSize}`)
    if (!res.ok) throw new Error('Failed to fetch conversations')
    return res.json()
  },

  async createConversation(data: { title?: string; model?: string; use_voting?: boolean }): Promise<Conversation> {
    const res = await fetch(`${API_URL}/api/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to create conversation')
    return res.json()
  },

  async getConversation(id: string): Promise<Conversation> {
    const res = await fetch(`${API_URL}/api/conversations/${id}`)
    if (!res.ok) throw new Error('Failed to fetch conversation')
    return res.json()
  },

  async deleteConversation(id: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/conversations/${id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete conversation')
  },

  async getMessages(conversationId: string, limit = 50): Promise<ConversationMessage[]> {
    const res = await fetch(`${API_URL}/api/conversations/${conversationId}/messages?limit=${limit}`)
    if (!res.ok) throw new Error('Failed to fetch messages')
    return res.json()
  },

  async chatWithConversation(message: string, conversationId?: string, useVoting = false, useRag = true): Promise<ReadableStream<Uint8Array>> {
    const res = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, conversation_id: conversationId, use_voting: useVoting, use_rag: useRag }),
    })
    if (!res.ok) throw new Error('Failed to send message')
    return res.body!
  },

  // Memories
  async listMemories(page = 1, pageSize = 20, factType?: string): Promise<{ memories: Memory[]; total: number; page: number; page_size: number }> {
    let url = `${API_URL}/api/memories?page=${page}&page_size=${pageSize}`
    if (factType) url += `&fact_type=${factType}`
    const res = await fetch(url)
    if (!res.ok) throw new Error('Failed to fetch memories')
    return res.json()
  },

  async createMemory(data: { content: string; fact_type: string; category?: string; tags?: string[]; confidence?: number }): Promise<Memory> {
    const res = await fetch(`${API_URL}/api/memories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to create memory')
    return res.json()
  },

  async updateMemory(memoryId: string, data: { content?: string; fact_type?: string; category?: string; tags?: string[]; confidence?: number }): Promise<Memory> {
    const res = await fetch(`${API_URL}/api/memories/${memoryId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to update memory')
    return res.json()
  },

  async deleteMemory(memoryId: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/memories/${memoryId}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete memory')
  },

  async getMemoryStats(): Promise<MemoryStats> {
    const res = await fetch(`${API_URL}/api/memories/stats`)
    if (!res.ok) throw new Error('Failed to fetch memory stats')
    return res.json()
  },

  async searchMemories(query: string, limit = 10, factType?: string): Promise<{ results: Memory[]; total: number }> {
    let url = `${API_URL}/api/memories/search?query=${encodeURIComponent(query)}&limit=${limit}`
    if (factType) url += `&fact_type=${factType}`
    const res = await fetch(url)
    if (!res.ok) throw new Error('Failed to search memories')
    return res.json()
  },

  async getUserProfile(): Promise<{ preferences: Memory[]; facts: Memory[]; total_preferences: number; total_facts: number }> {
    const res = await fetch(`${API_URL}/api/memories/profile`)
    if (!res.ok) throw new Error('Failed to fetch user profile')
    return res.json()
  },

  // ========== Knowledge Base (New Multi-KB API) ==========

  async getKnowledgeBases(): Promise<{ knowledge_bases: Array<{
    id: string
    name: string
    description: string
    document_count: number
    chunk_count: number
    status: string
  }> }> {
    const res = await fetch(`${API_URL}/api/rag/knowledge-bases`)
    if (!res.ok) throw new Error('Failed to fetch knowledge bases')
    return res.json()
  },

  async createKnowledgeBase(name: string, description: string = ''): Promise<{ success: boolean; knowledge_base: { id: string; name: string } }> {
    const res = await fetch(`${API_URL}/api/rag/knowledge-bases`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description }),
    })
    if (!res.ok) throw new Error('Failed to create knowledge base')
    return res.json()
  },

  async deleteKnowledgeBase(kbId: string): Promise<{ success: boolean; message: string }> {
    const res = await fetch(`${API_URL}/api/rag/knowledge-bases/${kbId}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete knowledge base')
    return res.json()
  },

  async updateKnowledgeBase(kbId: string, data: { name?: string; description?: string }): Promise<{ success: boolean; knowledge_base: { id: string; name: string; description: string } }> {
    const res = await fetch(`${API_URL}/api/rag/knowledge-bases/${kbId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error('Failed to update knowledge base')
    return res.json()
  },

  async getKnowledgeBaseStats(kbId: string): Promise<{ total_chunks: number; total_documents: number; status: string }> {
    const res = await fetch(`${API_URL}/api/rag/knowledge-bases/${kbId}/stats`)
    if (!res.ok) throw new Error('Failed to fetch knowledge base stats')
    return res.json()
  },

  async getDocuments(kbId: string): Promise<{ documents: RAGDocument[]; total: number }> {
    const res = await fetch(`${API_URL}/api/rag/knowledge-bases/${kbId}/documents`)
    if (!res.ok) throw new Error('Failed to fetch documents')
    return res.json()
  },

  async uploadFile(kbId: string, file: File, source?: string): Promise<{ success: boolean; doc_id?: string; title?: string; chunks?: number; error?: string }> {
    const formData = new FormData()
    formData.append('file', file)
    if (source) formData.append('source', source)

    const res = await fetch(`${API_URL}/api/rag/knowledge-bases/${kbId}/documents/file`, {
      method: 'POST',
      body: formData,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }))
      throw new Error(err.detail || 'Failed to upload file')
    }
    return res.json()
  },

  async indexWebpage(kbId: string, url: string): Promise<{ success: boolean; doc_id?: string; title?: string; chunks?: number; error?: string }> {
    const res = await fetch(`${API_URL}/api/rag/knowledge-bases/${kbId}/documents/web`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    })
    if (!res.ok) throw new Error('Failed to index webpage')
    return res.json()
  },

  async deleteDocument(kbId: string, docId: string): Promise<{ success: boolean }> {
    const res = await fetch(`${API_URL}/api/rag/knowledge-bases/${kbId}/documents/${docId}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete document')
    return res.json()
  },

  async searchKnowledgeBase(kbId: string, query: string, limit: number = 5): Promise<{ query: string; total: number; results: Array<{
    content: string
    title: string
    source: string
    url: string
    score: number
  }> }> {
    const res = await fetch(`${API_URL}/api/rag/knowledge-bases/${kbId}/search?query=${encodeURIComponent(query)}&limit=${limit}`)
    if (!res.ok) throw new Error('Failed to search knowledge base')
    return res.json()
  },

  async webSearch(params: {
    query: string
    kb_id?: string
    engine_type?: string
    time_range?: string
    auto_index?: boolean
    limit?: number
  }): Promise<{
    success: boolean
    error?: string
    search?: {
      total: number
      results: Array<{
        title: string
        link: string
        snippet: string
        source: string
        published_time?: string
        score?: number
      }>
    }
    indexed?: {
      count: number
      documents: Array<{ doc_id: string; title: string; source: string; score: number }>
    }
  }> {
    const res = await fetch(`${API_URL}/api/rag/web-search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    })
    if (!res.ok) throw new Error('Failed to perform web search')
    return res.json()
  },

  // ── 信息转知识库 ─────────────────────────────────
  async feedToKnowledgeBase(
    feedItemId: string,
    kbId: string,
    options?: { notes?: string; extract_deep?: boolean }
  ): Promise<{
    success: boolean
    knowledge_link_id?: string
    document_id?: string
    message: string
  }> {
    const res = await fetch(`${API_URL}/api/feeds/${feedItemId}/to-knowledge-base`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        kb_id: kbId,
        notes: options?.notes,
        extract_deep: options?.extract_deep || false,
      }),
    })
    if (!res.ok) throw new Error('Failed to transfer to knowledge base')
    return res.json()
  },

  async getFeedKnowledgeLinks(feedItemId: string): Promise<Array<{
    id: string
    kb_id: string
    status: string
    linked_at: string | null
    notes: string | null
  }>> {
    const res = await fetch(`${API_URL}/api/feeds/${feedItemId}/knowledge-links`)
    if (!res.ok) throw new Error('Failed to fetch knowledge links')
    const data = await res.json()
    return data as Array<{
      id: string
      kb_id: string
      status: string
      linked_at: string | null
      notes: string | null
    }>
  },

  // ========== IKE v0.1 Experimental API ==========

  async inspectObservation(feedItem: {
    source_id: string
    title: string
    summary?: string
    fetched_at?: string
    url?: string
  }): Promise<{
    ref: {
      id: string
      kind: string
      id_scope: 'provisional'
      stability: 'experimental'
      permalink: null
    }
    data: {
      id: string
      kind: 'observation'
      title: string
      summary: string
      source_ref: string
      [key: string]: any
    }
  }> {
    const res = await fetch(`${API_URL}/api/ike/v0/observations/inspect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feed_item: feedItem }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Inspection failed' }))
      throw new Error(err.detail || 'Failed to inspect observation')
    }
    return res.json()
  },

  async inspectChain(artifactId: string): Promise<{
    ref: {
      id: string
      kind: string
      id_scope: 'provisional'
      stability: 'experimental'
      permalink: null
    }
    data: {
      chain_id: string
      is_complete: boolean
      observation?: any
      entity?: any
      claim?: any
      research_task?: any
      experiment?: any
      decision?: any
      harness_case?: any
      [key: string]: any
    }
    completeness: {
      chain_id: string
      is_complete: boolean
      objects: Record<string, string | null>
      object_count: number
    }
  }> {
    const res = await fetch(`${API_URL}/api/ike/v0/chains/inspect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ artifact_id: artifactId }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Chain inspection failed' }))
      throw new Error(err.detail || 'Failed to inspect chain')
    }
    return res.json()
  },
}
