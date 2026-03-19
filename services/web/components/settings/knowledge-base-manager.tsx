'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import {
  Plus,
  Trash2,
  Search,
  Upload,
  Globe,
  Database,
  FileText,
  FolderOpen,
  RefreshCw,
  ExternalLink,
  File,
  FileType,
  FileType2,
  MoreVertical,
  Pencil,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { apiClient } from '@/lib/api-client'

interface KnowledgeBase {
  id: string
  name: string
  description: string
  document_count: number
  chunk_count: number
  status: string
}

interface Document {
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

interface FileUploadResult {
  success: boolean
  doc_id?: string
  title?: string
  chunks?: number
  error?: string
}

const SUPPORTED_FORMATS = {
  '.txt': { label: '文本文件', icon: FileText, color: 'text-gray-500' },
  '.md': { label: 'Markdown', icon: FileType, color: 'text-blue-500' },
  '.pdf': { label: 'PDF 文档', icon: FileType2, color: 'text-red-500' },
  '.docx': { label: 'Word 文档', icon: FileType2, color: 'text-blue-600' },
  '.html': { label: 'HTML 网页', icon: Globe, color: 'text-orange-500' },
  '.htm': { label: 'HTML 网页', icon: Globe, color: 'text-orange-500' },
}

// Knowledge Base Card with dropdown menu
function KnowledgeBaseCard({
  kb,
  isSelected,
  onSelect,
  onRename,
  onDelete,
}: {
  kb: KnowledgeBase
  isSelected: boolean
  onSelect: () => void
  onRename: () => void
  onDelete: () => void
}) {
  const [showMenu, setShowMenu] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setShowMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div
      className={cn(
        'relative flex items-center gap-2 px-4 py-2 rounded-lg border transition-all group',
        isSelected
          ? 'bg-primary text-primary-foreground border-primary'
          : 'bg-background hover:bg-muted'
      )}
    >
      <button
        onClick={onSelect}
        className="flex items-center gap-2 flex-1"
      >
        <Database className="h-4 w-4" />
        <span className="font-medium">{kb.name}</span>
        <span className="text-xs opacity-70">({kb.document_count})</span>
      </button>

      {/* More button */}
      <button
        onClick={(e) => {
          e.stopPropagation()
          setShowMenu(!showMenu)
        }}
        className={cn(
          'p-1 rounded hover:bg-black/10 transition-opacity',
          isSelected ? 'opacity-70 hover:opacity-100' : 'opacity-0 group-hover:opacity-100'
        )}
      >
        <MoreVertical className="h-4 w-4" />
      </button>

      {/* Dropdown menu */}
      {showMenu && (
        <div
          ref={menuRef}
          className="absolute top-full left-0 mt-1 bg-background border rounded-lg shadow-lg z-10 min-w-[120px] overflow-hidden"
        >
          <button
            onClick={(e) => {
              e.stopPropagation()
              setShowMenu(false)
              onRename()
            }}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted text-left"
          >
            <Pencil className="h-4 w-4" />
            重命名
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              setShowMenu(false)
              onDelete()
            }}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted text-left text-destructive"
          >
            <Trash2 className="h-4 w-4" />
            删除
          </button>
        </div>
      )}
    </div>
  )
}

export function KnowledgeBaseManager() {
  // ========== State ==========
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKB, setSelectedKB] = useState<string>('default')
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'files' | 'web' | 'search'>('files')

  // Create KB modal
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newKBName, setNewKBName] = useState('')
  const [newKBDescription, setNewKBDescription] = useState('')

  // Rename KB modal
  const [showRenameModal, setShowRenameModal] = useState(false)
  const [renameKBId, setRenameKBId] = useState<string>('')
  const [renameKBName, setRenameKBName] = useState('')
  const [renameKBDescription, setRenameKBDescription] = useState('')
  const [renaming, setRenaming] = useState(false)

  // Upload state
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<string>('')

  // Web indexing
  const [webUrl, setWebUrl] = useState('')
  const [indexingWeb, setIndexingWeb] = useState(false)

  // Web search
  const [searchQuery, setSearchQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [autoIndex, setAutoIndex] = useState(true)

  // ========== Load Data ==========
  const loadKnowledgeBases = useCallback(async () => {
    try {
      const data = await apiClient.getKnowledgeBases()
      setKnowledgeBases(data.knowledge_bases)
      // Set default selection if not set
      if (!selectedKB && data.knowledge_bases.length > 0) {
        setSelectedKB(data.knowledge_bases[0].id)
      }
    } catch (e) {
      console.error('Failed to load knowledge bases:', e)
    }
  }, [selectedKB])

  const loadDocuments = useCallback(async () => {
    try {
      setLoading(true)
      const data = await apiClient.getDocuments(selectedKB)
      setDocuments(data.documents)
    } catch (e) {
      console.error('Failed to load documents:', e)
    } finally {
      setLoading(false)
    }
  }, [selectedKB])

  useEffect(() => {
    loadKnowledgeBases()
  }, [loadKnowledgeBases])

  useEffect(() => {
    if (selectedKB) {
      loadDocuments()
    }
  }, [selectedKB, loadDocuments])

  // ========== Actions ==========
  const handleCreateKB = async () => {
    if (!newKBName.trim()) return

    try {
      const result = await apiClient.createKnowledgeBase(newKBName, newKBDescription)
      setNewKBName('')
      setNewKBDescription('')
      setShowCreateModal(false)
      loadKnowledgeBases()
      // Select the new KB
      if (result.knowledge_base?.id) {
        setSelectedKB(result.knowledge_base.id)
      }
    } catch (e) {
      console.error('Failed to create knowledge base:', e)
      alert('创建知识库失败')
    }
  }

  const handleDeleteKB = async (kbId: string) => {
    const kb = knowledgeBases.find(k => k.id === kbId)
    if (!confirm(`确定要删除知识库 "${kb?.name}" 吗？\n\n所有文档都将被永久删除，此操作不可撤销。`)) return

    try {
      await apiClient.deleteKnowledgeBase(kbId)
      if (selectedKB === kbId) {
        // Select another KB
        const remaining = knowledgeBases.filter(k => k.id !== kbId)
        setSelectedKB(remaining.length > 0 ? remaining[0].id : '')
      }
      loadKnowledgeBases()
    } catch (e) {
      console.error('Failed to delete knowledge base:', e)
      alert('删除知识库失败')
    }
  }

  const handleRenameKB = async () => {
    if (!renameKBName.trim() || renaming) return

    setRenaming(true)
    try {
      await apiClient.updateKnowledgeBase(renameKBId, {
        name: renameKBName,
        description: renameKBDescription,
      })
      setShowRenameModal(false)
      loadKnowledgeBases()
    } catch (e) {
      console.error('Failed to rename knowledge base:', e)
      alert('重命名失败')
    } finally {
      setRenaming(false)
    }
  }

  const openRenameModal = (kb: KnowledgeBase) => {
    setRenameKBId(kb.id)
    setRenameKBName(kb.name)
    setRenameKBDescription(kb.description)
    setShowRenameModal(true)
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setUploading(true)
    setUploadProgress(`准备上传 ${files.length} 个文件...`)

    const results: FileUploadResult[] = []

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      setUploadProgress(`正在上传: ${file.name} (${i + 1}/${files.length})`)

      try {
        const result = await apiClient.uploadFile(selectedKB, file)
        results.push(result)
      } catch (e: any) {
        results.push({
          success: false,
          error: e.message || '上传失败'
        })
      }
    }

    setUploading(false)
    setUploadProgress('')

    // Show summary
    const successCount = results.filter(r => r.success).length
    if (successCount === files.length) {
      alert(`成功上传 ${successCount} 个文件`)
    } else {
      alert(`上传完成: ${successCount}/${files.length} 成功`)
    }

    // Refresh documents
    loadDocuments()
    loadKnowledgeBases()

    // Reset input
    e.target.value = ''
  }

  const handleIndexWebpage = async () => {
    if (!webUrl.trim()) return

    setIndexingWeb(true)
    try {
      const result = await apiClient.indexWebpage(selectedKB, webUrl)
      if (result.success) {
        alert(`网页索引成功: ${result.title}`)
        setWebUrl('')
        loadDocuments()
        loadKnowledgeBases()
      } else {
        alert(`索引失败: ${result.error}`)
      }
    } catch (e: any) {
      alert(`索引失败: ${e.message}`)
    } finally {
      setIndexingWeb(false)
    }
  }

  const handleWebSearch = async () => {
    if (!searchQuery.trim()) return

    setSearching(true)
    setSearchResults([])

    try {
      const result = await apiClient.webSearch({
        query: searchQuery,
        kb_id: selectedKB,
        auto_index: autoIndex,
        limit: 10
      })

      if (result.success) {
        setSearchResults(result.search?.results || [])
        if (autoIndex && result.indexed) {
          alert(`搜索完成，已自动索引 ${result.indexed.count} 条结果到知识库`)
          loadDocuments()
          loadKnowledgeBases()
        }
      } else {
        alert(`搜索失败: ${result.error}`)
      }
    } catch (e: any) {
      alert(`搜索失败: ${e.message}`)
    } finally {
      setSearching(false)
    }
  }

  const handleDeleteDocument = async (docId: string) => {
    if (!confirm('确定要删除这个文档吗？')) return

    try {
      await apiClient.deleteDocument(selectedKB, docId)
      loadDocuments()
      loadKnowledgeBases()
    } catch (e) {
      console.error('Failed to delete document:', e)
      alert('删除失败')
    }
  }

  // ========== Render ==========
  const currentKB = knowledgeBases.find(kb => kb.id === selectedKB)

  return (
    <div className="space-y-6">
      {/* Knowledge Base Selector */}
      <div className="flex items-start gap-4">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium">知识库</label>
            <button
              onClick={() => {
                setNewKBName('')
                setNewKBDescription('')
                setShowCreateModal(true)
              }}
              className="flex items-center gap-1 px-3 py-1 text-sm text-primary hover:bg-primary/10 rounded-md transition-colors"
            >
              <Plus className="h-4 w-4" />
              新建知识库
            </button>
          </div>
          <div className="flex gap-2 flex-wrap">
            {knowledgeBases.map(kb => (
              <KnowledgeBaseCard
                key={kb.id}
                kb={kb}
                isSelected={selectedKB === kb.id}
                onSelect={() => setSelectedKB(kb.id)}
                onRename={() => openRenameModal(kb)}
                onDelete={() => handleDeleteKB(kb.id)}
              />
            ))}
            {knowledgeBases.length === 0 && (
              <div className="text-sm text-muted-foreground py-2">
                暂无知识库，点击上方按钮创建
              </div>
            )}
          </div>
        </div>

        {currentKB && (
          <div className="text-right text-sm text-muted-foreground shrink-0">
            <p>{currentKB.document_count} 个文档</p>
            <p>{currentKB.chunk_count} 个片段</p>
          </div>
        )}
      </div>

      {/* Create KB Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background rounded-lg p-6 w-full max-w-md shadow-xl">
            <h3 className="text-lg font-semibold mb-4">新建知识库</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">名称 <span className="text-destructive">*</span></label>
                <input
                  type="text"
                  value={newKBName}
                  onChange={(e) => setNewKBName(e.target.value)}
                  className="w-full px-3 py-2 rounded-md border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="输入知识库名称"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">描述</label>
                <textarea
                  value={newKBDescription}
                  onChange={(e) => setNewKBDescription(e.target.value)}
                  className="w-full px-3 py-2 rounded-md border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  rows={3}
                  placeholder="知识库描述（可选）"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-md border hover:bg-muted transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handleCreateKB}
                  disabled={!newKBName.trim()}
                  className="px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
                >
                  创建
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Rename KB Modal */}
      {showRenameModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background rounded-lg p-6 w-full max-w-md shadow-xl">
            <h3 className="text-lg font-semibold mb-4">编辑知识库</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">名称 <span className="text-destructive">*</span></label>
                <input
                  type="text"
                  value={renameKBName}
                  onChange={(e) => setRenameKBName(e.target.value)}
                  className="w-full px-3 py-2 rounded-md border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="输入知识库名称"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">描述</label>
                <textarea
                  value={renameKBDescription}
                  onChange={(e) => setRenameKBDescription(e.target.value)}
                  className="w-full px-3 py-2 rounded-md border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  rows={3}
                  placeholder="知识库描述（可选）"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => setShowRenameModal(false)}
                  className="px-4 py-2 rounded-md border hover:bg-muted transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={handleRenameKB}
                  disabled={!renameKBName.trim() || renaming}
                  className="px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
                >
                  {renaming ? '保存中...' : '保存'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b">
        <div className="flex gap-4">
          {[
            { id: 'files', label: '文件上传', icon: Upload },
            { id: 'web', label: '网页索引', icon: Globe },
            { id: 'search', label: '网络搜索', icon: Search },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={cn(
                'flex items-center gap-2 px-4 py-3 border-b-2 transition-colors',
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="space-y-4">
        {/* Files Tab */}
        {activeTab === 'files' && (
          <div className="space-y-4">
            {/* Upload Area */}
            <div className="border-2 border-dashed rounded-lg p-8 text-center hover:bg-muted/50 transition-colors">
              <input
                type="file"
                multiple
                onChange={handleFileUpload}
                disabled={uploading}
                accept=".txt,.md,.pdf,.docx,.html,.htm"
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center gap-2"
              >
                <Upload className="h-8 w-8 text-muted-foreground" />
                <span className="text-muted-foreground">
                  {uploading ? uploadProgress : '点击或拖拽文件上传'}
                </span>
                <span className="text-xs text-muted-foreground">
                  支持: TXT, Markdown, PDF, Word, HTML
                </span>
              </label>
            </div>

            {/* Supported Formats */}
            <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
              {Object.entries(SUPPORTED_FORMATS).map(([ext, info]) => {
                const Icon = info.icon
                return (
                  <div
                    key={ext}
                    className="flex items-center gap-2 p-2 rounded-lg bg-muted/50"
                  >
                    <Icon className={cn('h-4 w-4', info.color)} />
                    <div className="text-xs">
                      <div className="font-medium">{ext}</div>
                      <div className="text-muted-foreground">{info.label}</div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Web Tab */}
        {activeTab === 'web' && (
          <div className="space-y-4">
            <div className="flex gap-2">
              <input
                type="url"
                value={webUrl}
                onChange={(e) => setWebUrl(e.target.value)}
                placeholder="https://example.com/article"
                className="flex-1 px-3 py-2 rounded-md border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <button
                onClick={handleIndexWebpage}
                disabled={indexingWeb || !webUrl.trim()}
                className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
              >
                {indexingWeb ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Globe className="h-4 w-4" />
                )}
                索引网页
              </button>
            </div>
            <p className="text-sm text-muted-foreground">
              输入网页 URL，系统将自动抓取并索引内容到当前知识库。
            </p>
          </div>
        )}

        {/* Search Tab */}
        {activeTab === 'search' && (
          <div className="space-y-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="输入搜索关键词..."
                className="flex-1 px-3 py-2 rounded-md border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                onKeyDown={(e) => e.key === 'Enter' && handleWebSearch()}
              />
              <button
                onClick={handleWebSearch}
                disabled={searching || !searchQuery.trim()}
                className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
              >
                {searching ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
                搜索
              </button>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="auto-index"
                checked={autoIndex}
                onChange={(e) => setAutoIndex(e.target.checked)}
                className="rounded"
              />
              <label htmlFor="auto-index" className="text-sm">
                自动将搜索结果索引到知识库
              </label>
            </div>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="border rounded-lg divide-y">
                {searchResults.map((result, idx) => (
                  <div key={idx} className="p-4 hover:bg-muted/50">
                    <div className="flex items-start gap-3">
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium truncate">
                          <a
                            href={result.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:text-primary hover:underline"
                          >
                            {result.title}
                          </a>
                        </h4>
                        <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                          {result.snippet}
                        </p>
                        <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                          <span>{result.source}</span>
                          {result.published_time && (
                            <>
                              <span>·</span>
                              <span>{result.published_time}</span>
                            </>
                          )}
                          {result.score > 0 && (
                            <>
                              <span>·</span>
                              <span>相关度: {(result.score * 100).toFixed(0)}%</span>
                            </>
                          )}
                        </div>
                      </div>
                      <a
                        href={result.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 rounded hover:bg-muted"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Documents List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-medium flex items-center gap-2">
            <FolderOpen className="h-4 w-4" />
            文档列表
            <span className="text-sm text-muted-foreground">({documents.length})</span>
          </h3>
          <button
            onClick={loadDocuments}
            className="p-2 rounded hover:bg-muted transition-colors"
            title="刷新"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>

        {loading ? (
          <div className="text-center py-8 text-muted-foreground">
            <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2" />
            加载中...
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground border rounded-lg">
            <File className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>暂无文档</p>
            <p className="text-sm">上传文件、索引网页或搜索网络来添加知识</p>
          </div>
        ) : (
          <div className="border rounded-lg divide-y">
            {documents.map((doc) => {
              const fileType = doc.file_type || '.txt'
              const typeInfo = SUPPORTED_FORMATS[fileType as keyof typeof SUPPORTED_FORMATS] || SUPPORTED_FORMATS['.txt']
              const Icon = typeInfo.icon

              return (
                <div
                  key={doc.doc_id}
                  className="flex items-center gap-3 p-4 hover:bg-muted/50 group"
                >
                  <Icon className={cn('h-5 w-5 shrink-0', typeInfo.color)} />

                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{doc.title}</div>
                    <div className="text-xs text-muted-foreground flex items-center gap-2">
                      <span>{doc.source}</span>
                      <span>·</span>
                      <span>{doc.chunk_count} 片段</span>
                      {doc.created_at && (
                        <>
                          <span>·</span>
                          <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                        </>
                      )}
                    </div>
                    {doc.preview && (
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-1">
                        {doc.preview}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {doc.url && (
                      <a
                        href={doc.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 rounded hover:bg-muted"
                        title="打开链接"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    )}
                    <button
                      onClick={() => handleDeleteDocument(doc.doc_id)}
                      className="p-2 rounded hover:bg-muted text-destructive"
                      title="删除"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
