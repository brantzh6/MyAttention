'use client'

import { useState, useEffect, useCallback } from 'react'
import { Plus, Upload, Trash2, FileText, Database, Search, Loader2, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { apiClient, RAGDocument, RAGSource } from '@/lib/api-client'

const SOURCE_LABELS: Record<string, string> = {
  manual: '手动添加',
  upload: '文件上传',
  rss: 'RSS',
  web: '网页',
  documentation: '文档',
}

const SOURCE_COLORS: Record<string, string> = {
  manual: 'bg-blue-100 text-blue-700',
  upload: 'bg-green-100 text-green-700',
  rss: 'bg-orange-100 text-orange-700',
  web: 'bg-purple-100 text-purple-700',
  documentation: 'bg-cyan-100 text-cyan-700',
}

export function KnowledgeManager() {
  const [documents, setDocuments] = useState<RAGDocument[]>([])
  const [sources, setSources] = useState<RAGSource[]>([])
  const [stats, setStats] = useState<{ total_documents: number; status: string } | null>(null)
  const [selectedSource, setSelectedSource] = useState<string>('all')
  const [isLoading, setIsLoading] = useState(true)
  const [showAddText, setShowAddText] = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState<RAGDocument | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Add text form state
  const [newTitle, setNewTitle] = useState('')
  const [newContent, setNewContent] = useState('')
  const [newSource, setNewSource] = useState('manual')
  const [newUrl, setNewUrl] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const loadData = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [docsRes, sourcesRes, statsRes] = await Promise.all([
        apiClient.getRAGDocuments(),
        apiClient.getRAGSources(),
        apiClient.getRAGStats(),
      ])
      setDocuments(docsRes.documents)
      setSources(sourcesRes.sources)
      setStats(statsRes)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const filteredDocs = selectedSource === 'all'
    ? documents
    : documents.filter(d => d.source === selectedSource)

  const handleAddText = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newContent.trim()) return
    setIsSubmitting(true)
    try {
      await apiClient.addRAGText({
        content: newContent,
        title: newTitle || '未命名文档',
        source: newSource,
        url: newUrl,
      })
      setShowAddText(false)
      setNewTitle('')
      setNewContent('')
      setNewSource('manual')
      setNewUrl('')
      await loadData()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setIsSubmitting(true)
    try {
      await apiClient.uploadRAGFile(file)
      setShowUpload(false)
      await loadData()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
      e.target.value = ''
    }
  }

  const handleDelete = async (doc: RAGDocument) => {
    setIsSubmitting(true)
    try {
      await apiClient.deleteRAGDocument(doc.doc_id)
      setDeleteConfirm(null)
      await loadData()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Error display */}
      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-lg flex justify-between items-center">
          <span className="text-sm">{error}</span>
          <button onClick={() => setError(null)}><X className="h-4 w-4" /></button>
        </div>
      )}

      {/* Stats bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Database className="h-4 w-4" />
            <span>
              {stats ? `${documents.length} 个文档 / ${stats.total_documents} 个向量` : '加载中...'}
            </span>
          </div>
          {stats && (
            <span className={cn(
              'text-xs px-2 py-0.5 rounded-full',
              stats.status === 'green' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
            )}>
              {stats.status === 'green' ? '正常' : stats.status}
            </span>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowAddText(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            <Plus className="h-4 w-4" />
            添加文本
          </button>
          <button
            onClick={() => setShowUpload(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-sm font-medium hover:bg-muted transition-colors"
          >
            <Upload className="h-4 w-4" />
            上传文件
          </button>
        </div>
      </div>

      {/* Source filter tabs */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setSelectedSource('all')}
          className={cn(
            'px-3 py-1 rounded-full text-xs font-medium transition-colors',
            selectedSource === 'all'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground hover:bg-muted/80'
          )}
        >
          全部 ({documents.length})
        </button>
        {sources.map(s => (
          <button
            key={s.name}
            onClick={() => setSelectedSource(s.name)}
            className={cn(
              'px-3 py-1 rounded-full text-xs font-medium transition-colors',
              selectedSource === s.name
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            )}
          >
            {SOURCE_LABELS[s.name] || s.name} ({s.count})
          </button>
        ))}
      </div>

      {/* Documents list */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : filteredDocs.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium">暂无文档</p>
          <p className="text-sm mt-1">点击「添加文本」或「上传文件」添加知识库内容</p>
        </div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-4 py-3 font-medium">标题</th>
                <th className="text-left px-4 py-3 font-medium">来源</th>
                <th className="text-center px-4 py-3 font-medium">Chunks</th>
                <th className="text-left px-4 py-3 font-medium">预览</th>
                <th className="text-center px-4 py-3 font-medium w-20">操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredDocs.map(doc => (
                <tr key={doc.doc_id} className="border-t hover:bg-muted/30 transition-colors">
                  <td className="px-4 py-3 font-medium">
                    {doc.title || '未命名'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={cn(
                      'px-2 py-0.5 rounded-full text-xs font-medium',
                      SOURCE_COLORS[doc.source] || 'bg-gray-100 text-gray-700'
                    )}>
                      {SOURCE_LABELS[doc.source] || doc.source}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="text-xs bg-muted px-1.5 py-0.5 rounded">
                      {doc.chunk_count}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground max-w-xs truncate">
                    {doc.preview}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => setDeleteConfirm(doc)}
                      className="text-muted-foreground hover:text-destructive transition-colors p-1"
                      title="删除文档"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add text modal */}
      {showAddText && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background rounded-lg p-6 w-full max-w-lg mx-4 shadow-xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">添加文本文档</h3>
              <button onClick={() => setShowAddText(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>
            <form onSubmit={handleAddText} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">标题</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={e => setNewTitle(e.target.value)}
                  placeholder="文档标题"
                  className="w-full px-3 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">内容 *</label>
                <textarea
                  value={newContent}
                  onChange={e => setNewContent(e.target.value)}
                  placeholder="输入文档内容..."
                  rows={6}
                  className="w-full px-3 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">来源</label>
                  <select
                    value={newSource}
                    onChange={e => setNewSource(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="manual">手动添加</option>
                    <option value="documentation">文档</option>
                    <option value="web">网页</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">URL (可选)</label>
                  <input
                    type="url"
                    value={newUrl}
                    onChange={e => setNewUrl(e.target.value)}
                    placeholder="https://..."
                    className="w-full px-3 py-2 border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddText(false)}
                  className="px-4 py-2 border rounded-lg text-sm hover:bg-muted transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !newContent.trim()}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
                >
                  {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : '添加'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Upload modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background rounded-lg p-6 w-full max-w-md mx-4 shadow-xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">上传文件</h3>
              <button onClick={() => setShowUpload(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="border-2 border-dashed rounded-lg p-8 text-center">
              <Upload className="h-10 w-10 mx-auto mb-3 text-muted-foreground" />
              <p className="text-sm text-muted-foreground mb-1">选择 TXT 文件上传</p>
              <p className="text-xs text-muted-foreground mb-4">支持 UTF-8 和 GBK 编码</p>
              <label className="inline-flex items-center gap-1.5 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium cursor-pointer hover:bg-primary/90 transition-colors">
                {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
                {isSubmitting ? '上传中...' : '选择文件'}
                <input
                  type="file"
                  accept=".txt"
                  onChange={handleUpload}
                  className="hidden"
                  disabled={isSubmitting}
                />
              </label>
            </div>
            <div className="flex justify-end mt-4">
              <button
                onClick={() => setShowUpload(false)}
                className="px-4 py-2 border rounded-lg text-sm hover:bg-muted transition-colors"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete confirmation modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background rounded-lg p-6 w-full max-w-sm mx-4 shadow-xl">
            <h3 className="text-lg font-semibold mb-2">确认删除</h3>
            <p className="text-sm text-muted-foreground mb-4">
              确定删除「{deleteConfirm.title || '未命名'}」吗？将删除 {deleteConfirm.chunk_count} 个向量块。此操作不可撤销。
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="px-4 py-2 border rounded-lg text-sm hover:bg-muted transition-colors"
              >
                取消
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
                disabled={isSubmitting}
                className="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg text-sm font-medium hover:bg-destructive/90 disabled:opacity-50 transition-colors"
              >
                {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : '删除'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
