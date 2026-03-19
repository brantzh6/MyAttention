'use client'

import { useState, useEffect, useCallback } from 'react'
import { apiClient, Memory, MemoryStats } from '@/lib/api-client'
import { cn } from '@/lib/utils'
import { 
  Brain, Heart, Lightbulb, CheckCircle, Plus, Trash2, 
  Search, RefreshCw, X, Edit2, Save, Tag
} from 'lucide-react'

const FACT_TYPES = [
  { value: 'all', label: '全部', icon: Brain },
  { value: 'preference', label: '偏好', icon: Heart },
  { value: 'fact', label: '事实', icon: CheckCircle },
  { value: 'decision', label: '决策', icon: Lightbulb },
  { value: 'insight', label: '洞察', icon: Brain },
] as const

const TYPE_COLORS: Record<string, string> = {
  preference: 'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-300',
  fact: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  decision: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  insight: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
}

export function MemoryManager() {
  const [memories, setMemories] = useState<Memory[]>([])
  const [stats, setStats] = useState<MemoryStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedType, setSelectedType] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [showAdd, setShowAdd] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  
  // Add form state
  const [newContent, setNewContent] = useState('')
  const [newType, setNewType] = useState<string>('fact')
  const [newCategory, setNewCategory] = useState('')
  const [newTags, setNewTags] = useState('')
  
  // Edit form state
  const [editContent, setEditContent] = useState('')
  const [editType, setEditType] = useState<string>('')
  const [editCategory, setEditCategory] = useState('')
  const [editTags, setEditTags] = useState('')

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [memoriesRes, statsRes] = await Promise.all([
        searchQuery 
          ? apiClient.searchMemories(searchQuery, 50, selectedType !== 'all' ? selectedType : undefined)
          : apiClient.listMemories(1, 50, selectedType !== 'all' ? selectedType : undefined),
        apiClient.getMemoryStats(),
      ])
      
      if ('results' in memoriesRes) {
        setMemories(memoriesRes.results)
      } else {
        setMemories(memoriesRes.memories)
      }
      setStats(statsRes)
    } catch (error) {
      console.error('Failed to load memories:', error)
    } finally {
      setLoading(false)
    }
  }, [selectedType, searchQuery])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleAdd = async () => {
    if (!newContent.trim()) return
    
    try {
      await apiClient.createMemory({
        content: newContent,
        fact_type: newType,
        category: newCategory || undefined,
        tags: newTags ? newTags.split(',').map(t => t.trim()) : undefined,
      })
      setNewContent('')
      setNewCategory('')
      setNewTags('')
      setShowAdd(false)
      loadData()
    } catch (error) {
      console.error('Failed to create memory:', error)
    }
  }

  const handleDelete = async (memoryId: string) => {
    if (!confirm('确定要删除这条记忆吗？')) return
    
    try {
      await apiClient.deleteMemory(memoryId)
      loadData()
    } catch (error) {
      console.error('Failed to delete memory:', error)
    }
  }

  const handleEdit = (memory: Memory) => {
    setEditingId(memory.memory_id)
    setEditContent(memory.content)
    setEditType(memory.fact_type)
    setEditCategory(memory.category || '')
    setEditTags(memory.tags.join(', '))
  }

  const handleSaveEdit = async () => {
    if (!editingId || !editContent.trim()) return
    
    try {
      await apiClient.updateMemory(editingId, {
        content: editContent,
        fact_type: editType,
        category: editCategory || undefined,
        tags: editTags ? editTags.split(',').map(t => t.trim()) : undefined,
      })
      setEditingId(null)
      loadData()
    } catch (error) {
      console.error('Failed to update memory:', error)
    }
  }

  const TypeIcon = ({ type }: { type: string }) => {
    const found = FACT_TYPES.find(t => t.value === type)
    const Icon = found?.icon || Brain
    return <Icon className="h-4 w-4" />
  }

  return (
    <div className="space-y-6">
      {/* Stats Bar */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-card rounded-lg p-4 border">
            <div className="text-2xl font-bold">{stats.total_memories}</div>
            <div className="text-sm text-muted-foreground">总记忆数</div>
          </div>
          {Object.entries(stats.type_distribution).map(([type, count]) => (
            <div key={type} className="bg-card rounded-lg p-4 border">
              <div className="flex items-center gap-2">
                <span className={cn('px-2 py-0.5 rounded text-xs', TYPE_COLORS[type])}>
                  {FACT_TYPES.find(t => t.value === type)?.label || type}
                </span>
              </div>
              <div className="text-2xl font-bold mt-1">{count}</div>
            </div>
          ))}
        </div>
      )}

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex gap-2 flex-wrap">
          {FACT_TYPES.map(type => (
            <button
              key={type.value}
              onClick={() => setSelectedType(type.value)}
              className={cn(
                'inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                selectedType === type.value
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted hover:bg-muted/80 text-muted-foreground'
              )}
            >
              <type.icon className="h-4 w-4 mr-1" />
              {type.label}
            </button>
          ))}
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="搜索记忆..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <button
            onClick={loadData}
            className="p-2 rounded-md border bg-background hover:bg-muted transition-colors"
          >
            <RefreshCw className={cn('h-4 w-4', loading && 'animate-spin')} />
          </button>
          <button
            onClick={() => setShowAdd(true)}
            className="inline-flex items-center px-3 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            <Plus className="h-4 w-4 mr-1" />
            添加
          </button>
        </div>
      </div>

      {/* Add Modal */}
      {showAdd && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card rounded-lg p-6 w-full max-w-lg mx-4 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">添加记忆</h3>
              <button
                onClick={() => setShowAdd(false)}
                className="p-1 rounded hover:bg-muted transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-1 block">类型</label>
                <div className="flex gap-2">
                  {FACT_TYPES.filter(t => t.value !== 'all').map(type => (
                    <button
                      key={type.value}
                      onClick={() => setNewType(type.value)}
                      className={cn(
                        'inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                        newType === type.value
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted hover:bg-muted/80 text-muted-foreground'
                      )}
                    >
                      <type.icon className="h-4 w-4 mr-1" />
                      {type.label}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">内容</label>
                <textarea
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  className="w-full min-h-[100px] p-3 rounded-md border bg-background resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="输入记忆内容..."
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">分类</label>
                  <input
                    type="text"
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    placeholder="如: llm, work, personal"
                    className="w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1 block">标签</label>
                  <input
                    type="text"
                    value={newTags}
                    onChange={(e) => setNewTags(e.target.value)}
                    placeholder="用逗号分隔"
                    className="w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-4">
              <button
                onClick={() => setShowAdd(false)}
                className="px-4 py-2 rounded-md border bg-background hover:bg-muted text-sm font-medium transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleAdd}
                disabled={!newContent.trim()}
                className="px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Memory List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : memories.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>暂无记忆</p>
          <p className="text-sm mt-1">系统会自动从对话中提取重要信息，或点击上方按钮手动添加</p>
        </div>
      ) : (
        <div className="space-y-3">
          {memories.map(memory => (
            <div
              key={memory.memory_id}
              className="bg-card rounded-lg border p-4 hover:border-primary/50 transition-colors"
            >
              {editingId === memory.memory_id ? (
                <div className="space-y-3">
                  <div className="flex gap-2">
                    {FACT_TYPES.filter(t => t.value !== 'all').map(type => (
                      <button
                        key={type.value}
                        onClick={() => setEditType(type.value)}
                        className={cn(
                          'inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                          editType === type.value
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted hover:bg-muted/80 text-muted-foreground'
                        )}
                      >
                        {type.label}
                      </button>
                    ))}
                  </div>
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="w-full min-h-[80px] p-2 rounded-md border bg-background resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="text"
                      value={editCategory}
                      onChange={(e) => setEditCategory(e.target.value)}
                      placeholder="分类"
                      className="w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                    <input
                      type="text"
                      value={editTags}
                      onChange={(e) => setEditTags(e.target.value)}
                      placeholder="标签 (逗号分隔)"
                      className="w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => setEditingId(null)}
                      className="px-3 py-1.5 rounded-md border bg-background hover:bg-muted text-sm font-medium transition-colors"
                    >
                      取消
                    </button>
                    <button
                      onClick={handleSaveEdit}
                      className="inline-flex items-center px-3 py-1.5 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
                    >
                      <Save className="h-4 w-4 mr-1" />
                      保存
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={cn('px-2 py-0.5 rounded text-xs flex items-center gap-1', TYPE_COLORS[memory.fact_type])}>
                          <TypeIcon type={memory.fact_type} />
                          {FACT_TYPES.find(t => t.value === memory.fact_type)?.label || memory.fact_type}
                        </span>
                        {memory.category && (
                          <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                            {memory.category}
                          </span>
                        )}
                        <span className="text-xs text-muted-foreground">
                          置信度: {Math.round(memory.confidence * 100)}%
                        </span>
                      </div>
                      <p className="text-sm">{memory.content}</p>
                      {memory.tags.length > 0 && (
                        <div className="flex gap-1 mt-2 flex-wrap">
                          {memory.tags.map((tag, i) => (
                            <span key={i} className="text-xs bg-muted px-2 py-0.5 rounded flex items-center gap-1">
                              <Tag className="h-3 w-3" />
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                      <div className="text-xs text-muted-foreground mt-2">
                        访问次数: {memory.access_count} · 创建于 {new Date(memory.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => handleEdit(memory)}
                        className="p-2 rounded hover:bg-muted transition-colors"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(memory.memory_id)}
                        className="p-2 rounded hover:bg-muted transition-colors text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
