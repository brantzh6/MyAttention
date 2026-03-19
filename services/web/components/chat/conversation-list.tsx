'use client'

import { useState, useEffect, useCallback } from 'react'
import { apiClient, Conversation } from '@/lib/api-client'
import { cn } from '@/lib/utils'
import { 
  MessageSquare, Plus, Trash2, MoreVertical, 
  ChevronLeft, ChevronRight, RefreshCw
} from 'lucide-react'

interface ConversationListProps {
  currentConversationId?: string
  onSelectConversation: (id: string) => void
  onNewConversation: () => void
  collapsed?: boolean
  onToggleCollapse?: () => void
}

export function ConversationList({
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  collapsed = false,
  onToggleCollapse,
}: ConversationListProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [showMenu, setShowMenu] = useState<string | null>(null)

  const loadConversations = useCallback(async () => {
    setLoading(true)
    try {
      const res = await apiClient.listConversations(1, 50)
      setConversations(res.conversations)
    } catch (error) {
      console.error('Failed to load conversations:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('确定要删除这个会话吗？')) return
    
    try {
      await apiClient.deleteConversation(id)
      loadConversations()
      if (currentConversationId === id) {
        onNewConversation()
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    }
    setShowMenu(null)
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

  if (collapsed) {
    return (
      <div className="w-12 border-r bg-card flex flex-col items-center py-4">
        <button
          onClick={onNewConversation}
          title="新对话"
          className="p-2 rounded hover:bg-muted transition-colors"
        >
          <Plus className="h-5 w-5" />
        </button>
        <button
          onClick={onToggleCollapse}
          title="展开侧边栏"
          className="p-2 rounded hover:bg-muted transition-colors mt-auto"
        >
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
    )
  }

  return (
    <div className="w-64 border-r bg-card flex flex-col">
      {/* Header */}
      <div className="p-3 border-b flex items-center justify-between">
        <h3 className="font-medium text-sm">会话历史</h3>
        <div className="flex gap-1">
          <button
            onClick={loadConversations}
            className="p-1.5 rounded hover:bg-muted transition-colors"
          >
            <RefreshCw className={cn('h-4 w-4', loading && 'animate-spin')} />
          </button>
          <button
            onClick={onToggleCollapse}
            className="p-1.5 rounded hover:bg-muted transition-colors"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-2">
        <button 
          onClick={onNewConversation}
          className="w-full flex items-center justify-start px-3 py-2 rounded-md border bg-background hover:bg-muted text-sm font-medium transition-colors"
        >
          <Plus className="h-4 w-4 mr-2" />
          新对话
        </button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {loading ? (
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
              onClick={() => onSelectConversation(conv.id)}
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
                <div className="relative">
                  <button
                    className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-muted transition-all"
                    onClick={(e) => {
                      e.stopPropagation()
                      setShowMenu(showMenu === conv.id ? null : conv.id)
                    }}
                  >
                    <MoreVertical className="h-4 w-4" />
                  </button>
                  {showMenu === conv.id && (
                    <div className="absolute right-0 top-6 bg-popover border rounded-md shadow-lg z-10 py-1 min-w-[100px]">
                      <button
                        className="w-full px-3 py-1.5 text-sm text-left hover:bg-accent flex items-center gap-2 text-destructive"
                        onClick={(e) => handleDelete(conv.id, e)}
                      >
                        <Trash2 className="h-4 w-4" />
                        删除
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
