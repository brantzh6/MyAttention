'use client'

// 强制重新编译标记: v4 - IndexedDB缓存+智能刷新+错误处理
import { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { ExternalLink, Star, Check, Clock, RefreshCw, Loader2, X, ArrowUpDown, Wifi, WifiOff, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { apiClient, type FeedHealthSnapshot, type FeedItem } from '@/lib/api-client'
import { feedCache, localStorageCache } from '@/lib/feed-cache'

// 分类和Tag配置
const CATEGORY_CONFIG = {
  '科技': {
    subTags: [
      { id: 'ai', name: 'AI/大模型', keywords: ['AI', 'GPT', '大模型', '人工智能', '深度学习', 'LLM', '神经网络', 'OpenAI', 'Claude', 'DeepSeek'] },
      { id: 'chip', name: '芯片/半导体', keywords: ['芯片', '半导体', 'GPU', '英伟达', 'NVIDIA', '台积电', '光刻'] },
      { id: 'ev', name: '新能源车', keywords: ['特斯拉', '电动车', '新能源', '比亚迪', '蔚来', '小鹏', '理想', '自动驾驶'] },
      { id: 'robot', name: '机器人', keywords: ['机器人', '具身智能', '人形机器人', '机械臂'] },
    ]
  },
  '财经': {
    subTags: [
      { id: 'macro', name: '宏观政策', keywords: ['央行', '降准', '降息', '加息', '美联储', '货币政策', 'GDP', 'CPI', '通胀', '财政部'] },
      { id: 'market', name: '市场行情', keywords: ['A股', '港股', '大涨', '大跌', '涨停', '跌停', '牛市', '熊市', '震荡', '沪指', '深成指'] },
      { id: 'company', name: '公司动态', keywords: ['财报', '季报', '年报', '业绩', '盈利', '营收', 'IPO', '上市', '融资', '并购', '收购'] },
    ]
  },
  '海外财经': {
    subTags: [
      { id: 'usstock', name: '美股', keywords: ['美股', '道琼斯', '纳斯达克', '标普', '苹果', '微软', '谷歌', '特斯拉', '英伟达', 'Meta'] },
      { id: 'global', name: '全球市场', keywords: ['全球', '欧洲', '亚洲', '新兴市场', '汇率', '美元', '欧元', '日元', '英镑'] },
      { id: 'commodity', name: '大宗商品', keywords: ['原油', '黄金', '白银', '铜', '铁矿石', '期货', '石油', 'OPEC'] },
    ]
  },
}

type SortMode = 'time' | 'importance-desc'

// 缓存配置
const CACHE_KEY = 'feeds_cache_v2'
const CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存有效期
const FETCH_TIMEOUT = 30000 // 30秒请求超时（海外源需要代理，时间较长）
const RETRY_DELAY = 3000 // 重试延迟
const MAX_RETRIES = 2 // 最大重试次数

// 带超时的 fetch 封装
async function fetchWithTimeout<T>(fetchFn: () => Promise<T>, timeout = FETCH_TIMEOUT): Promise<T> {
  return Promise.race([
    fetchFn(),
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error('请求超时，请检查网络连接')), timeout)
    ),
  ])
}

// 计算数据指纹（用于快速比较数据变化）
function computeDataFingerprint(feeds: FeedItem[]): string {
  // 使用前10条的ID+时间戳组合作为指纹
  return feeds
    .slice(0, 10)
    .map(f => `${f.id}:${new Date(f.published_at).getTime()}`)
    .join('|')
}

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  return `${days}天前`
}

function formatAbsoluteTime(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function FeedList() {
  // ========== 数据状态 ==========
  const [feeds, setFeeds] = useState<FeedItem[]>([])
  const [loading, setLoading] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [cacheTime, setCacheTime] = useState<number>(0)
  const [initialLoadDone, setInitialLoadDone] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isOffline, setIsOffline] = useState(false)
  const [showKbModal, setShowKbModal] = useState(false)
  const [selectedFeedId, setSelectedFeedId] = useState<string | null>(null)
  const [kbList, setKbList] = useState<{id: string; name: string}[]>([])
  const [loadingKb, setLoadingKb] = useState(false)
  const [kbSubmitting, setKbSubmitting] = useState(false)
  const [kbMessage, setKbMessage] = useState<{type: 'success' | 'error'; text: string} | null>(null)
  const [feedHealth, setFeedHealth] = useState<FeedHealthSnapshot | null>(null)
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const dataFingerprintRef = useRef<string>('')

  const loadFeedHealth = useCallback(async () => {
    try {
      const health = await apiClient.getFeedsHealth()
      setFeedHealth(health)
    } catch (e) {
      console.error('[FeedList] 获取 feed health 失败:', e)
    }
  }, [])

  // ========== 筛选状态 ==========
  const [category, setCategory] = useState<string | null>(null)
  const [subTag, setSubTag] = useState<string | null>(null)
  const [importanceLevel, setImportanceLevel] = useState<string>('all')
  const [sourceFilter, setSourceFilter] = useState<string | null>(null)
  const [sortMode, setSortMode] = useState<SortMode>('time')
  const [showLow, setShowLow] = useState(false)

  // ========== 初始化：优先从缓存加载，无论缓存是否过期 ==========
  useEffect(() => {
    const init = async () => {
      let hasCachedData = false
      setError(null)

      // 1. 首先尝试从 IndexedDB 缓存加载
      try {
        const cached = await feedCache.get<FeedItem[]>(CACHE_KEY)
        const timestamp = await feedCache.getTimestamp(CACHE_KEY)

        if (cached && cached.length > 0) {
          setFeeds(cached)
          dataFingerprintRef.current = computeDataFingerprint(cached)
          hasCachedData = true
          if (timestamp) {
            setCacheTime(timestamp)
          }
          console.log('[FeedList] 从 IndexedDB 加载了', cached.length, '条数据')
        }
      } catch (e) {
        console.error('[FeedList] IndexedDB 读取失败:', e)
      }

      // 2. IndexedDB 失败，尝试 localStorage 降级
      if (!hasCachedData) {
        try {
          const cached = localStorageCache.get<FeedItem[]>(CACHE_KEY)
          const timestamp = localStorageCache.getTimestamp(CACHE_KEY)

          if (cached && cached.length > 0) {
            setFeeds(cached)
            dataFingerprintRef.current = computeDataFingerprint(cached)
            hasCachedData = true
            if (timestamp) {
              setCacheTime(timestamp)
            }
            console.log('[FeedList] 从 localStorage 加载了', cached.length, '条数据')
          }
        } catch (e) {
          console.error('[FeedList] localStorage 读取失败:', e)
        }
      }

      // 3. 如果没有缓存，显示 loading 并从 API 加载
      if (!hasCachedData) {
        setLoading(true)
        await loadFeedsWithRetry(0)
        setLoading(false)
      } else {
        // 4. 有缓存，检查是否需要后台刷新
        const cacheAge = Date.now() - cacheTime

        // 缓存超过5分钟，后台刷新
        if (cacheAge > CACHE_DURATION || cacheTime === 0) {
          console.log('[FeedList] 缓存过期，开始后台刷新')
          refreshFeedsSilently()
        }
      }

      await loadFeedHealth()

      setInitialLoadDone(true)
    }

    init()

    // 清理定时器
    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current)
      }
    }
  }, [loadFeedHealth])

  useEffect(() => {
    if (!initialLoadDone) return

    const interval = setInterval(() => {
      loadFeedHealth()
    }, 60_000)

    return () => clearInterval(interval)
  }, [initialLoadDone, loadFeedHealth])

  // ========== 带重试的加载 ==========
  const loadFeedsWithRetry = async (retryCount: number): Promise<void> => {
    try {
      setError(null)
      const data = await fetchWithTimeout(() => apiClient.getFeeds())

      setFeeds(data)
      dataFingerprintRef.current = computeDataFingerprint(data)
      const now = Date.now()
      setCacheTime(now)
      setIsOffline(false)

      // 保存到缓存（IndexedDB + localStorage 双保险）
      await Promise.all([
        feedCache.set(CACHE_KEY, data).catch(() => {}),
        Promise.resolve(localStorageCache.set(CACHE_KEY, data)),
        Promise.resolve(localStorageCache.setTimestamp(CACHE_KEY, now)),
      ])

      await loadFeedHealth()

      console.log('[FeedList] API 加载成功:', data.length, '条')
    } catch (e) {
      const errorMsg = e instanceof Error ? e.message : '加载失败'
      console.error('[FeedList] 加载失败:', errorMsg)

      // 如果已有缓存数据，不显示错误，静默失败
      if (feeds.length === 0) {
        setError(errorMsg)
        setIsOffline(true)
      }

      // 自动重试
      if (retryCount < MAX_RETRIES) {
        console.log(`[FeedList] ${RETRY_DELAY}ms 后第 ${retryCount + 1} 次重试...`)
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY))
        return loadFeedsWithRetry(retryCount + 1)
      }
    }
  }

  // ========== 后台静默刷新 ==========
  const refreshFeedsSilently = useCallback(async () => {
    if (isRefreshing) return

    setIsRefreshing(true)
    setError(null)

    try {
      console.log('[FeedList] 后台刷新开始...')
      const data = await fetchWithTimeout(() => apiClient.getFeeds())

      // 使用指纹快速比较数据变化
      const newFingerprint = computeDataFingerprint(data)
      const hasChanged = newFingerprint !== dataFingerprintRef.current

      if (hasChanged) {
        console.log('[FeedList] 数据有更新，条数:', data.length)
        setFeeds(data)
        dataFingerprintRef.current = newFingerprint

        // 更新缓存
        const now = Date.now()
        setCacheTime(now)
        await Promise.all([
          feedCache.set(CACHE_KEY, data).catch(() => {}),
          Promise.resolve(localStorageCache.set(CACHE_KEY, data)),
          Promise.resolve(localStorageCache.setTimestamp(CACHE_KEY, now)),
        ])
      } else {
        console.log('[FeedList] 数据无变化')
        // 只更新时间戳
        const now = Date.now()
        setCacheTime(now)
        await Promise.resolve(localStorageCache.setTimestamp(CACHE_KEY, now))
      }

      await loadFeedHealth()

      setIsOffline(false)
    } catch (e) {
      const errorMsg = e instanceof Error ? e.message : '刷新失败'
      console.error('[FeedList] 后台刷新失败:', errorMsg)
      // 后台刷新失败不显示错误，保持现有数据
      if (errorMsg.includes('超时')) {
        setIsOffline(true)
      }
    } finally {
      setIsRefreshing(false)
    }
  }, [isRefreshing, loadFeedHealth])

  // ========== 客户端筛选（纯内存计算，零延迟） ==========
  const filteredFeeds = useMemo(() => {
    let result = feeds

    // 1. 分类筛选
    if (category) {
      const catMap: Record<string, string[]> = {
        '科技': ['科技商业', '科技资讯', '商业科技', '科技前沿', '效率工具', 'AI研究'],
        '财经': ['财经'],
        '海外财经': ['海外财经'],
        '国内': ['国内'],
        '开发者': ['开发者'],
        '国际科技': ['国际科技'],
      }
      const cats = catMap[category] || [category]
      result = result.filter(f => cats.includes(f.category))
    }

    // 2. 子Tag筛选
    if (subTag && category && CATEGORY_CONFIG[category as keyof typeof CATEGORY_CONFIG]) {
      const config = CATEGORY_CONFIG[category as keyof typeof CATEGORY_CONFIG]
      const tag = config.subTags.find(t => t.id === subTag)
      if (tag) {
        result = result.filter(f => {
          const text = (f.title + ' ' + f.summary).toLowerCase()
          return tag.keywords.some(k => text.includes(k.toLowerCase()))
        })
      }
    }

    // 3. 重要性筛选
    if (importanceLevel !== 'all') {
      const levels: Record<string, [number, number]> = {
        'critical': [0.9, 1],
        'high': [0.75, 0.9],
        'medium': [0.6, 0.75],
        'low': [0, 0.6],
      }
      const [min, max] = levels[importanceLevel] || [0, 1]
      result = result.filter(f => f.importance >= min && f.importance < max)
    }

    // 4. 来源筛选
    if (sourceFilter) {
      result = result.filter(f => f.source_id === sourceFilter)
    }

    // 5. 排序
    result.sort((a, b) => {
      if (sortMode === 'importance-desc') {
        return b.importance - a.importance || +new Date(b.published_at) - +new Date(a.published_at)
      }
      return +new Date(b.published_at) - +new Date(a.published_at)
    })

    return result
  }, [feeds, category, subTag, importanceLevel, sourceFilter, sortMode])

  // ========== 按重要性分组 ==========
  const groups = useMemo(() => ({
    critical: filteredFeeds.filter(f => f.importance >= 0.9),
    high: filteredFeeds.filter(f => f.importance >= 0.75 && f.importance < 0.9),
    medium: filteredFeeds.filter(f => f.importance >= 0.6 && f.importance < 0.75),
    low: filteredFeeds.filter(f => f.importance < 0.6),
  }), [filteredFeeds])

  // ========== 来源列表（去重） ==========
  const sources = useMemo(() => {
    const seen = new Set<string>()
    const result: { id: string; name: string }[] = []
    feeds.forEach(f => {
      if (!seen.has(f.source_id)) {
        seen.add(f.source_id)
        result.push({ id: f.source_id, name: f.source })
      }
    })
    return result
  }, [feeds])

  const latestPublishedAt = useMemo(() => {
    if (feeds.length === 0) return null
    return feeds.reduce((latest, item) => {
      if (!latest) return item.published_at
      return new Date(item.published_at).getTime() > new Date(latest).getTime()
        ? item.published_at
        : latest
    }, null as string | null)
  }, [feeds])

  // ========== 事件处理 ==========
  const handleCategoryClick = (cat: string | null) => {
    setCategory(cat)
    setSubTag(null)
  }

  const clearFilters = () => {
    setCategory(null)
    setSubTag(null)
    setImportanceLevel('all')
    setSourceFilter(null)
  }

  const toggleRead = (id: string) => {
    setFeeds(prev => prev.map(f => f.id === id ? { ...f, is_read: !f.is_read } : f))
  }

  const toggleFavorite = (id: string) => {
    setFeeds(prev => prev.map(f => f.id === id ? { ...f, is_favorite: !f.is_favorite } : f))
  }

  // ========== 知识库相关 ==========
  const handleToKnowledge = async (feedId: string) => {
    setSelectedFeedId(feedId)
    setKbMessage(null)

    // 获取知识库列表
    setLoadingKb(true)
    try {
      const kbData = await apiClient.getKnowledgeBases()
      setKbList(kbData.knowledge_bases)
      setShowKbModal(true)
    } catch (e) {
      console.error('获取知识库列表失败:', e)
      setKbMessage({ type: 'error', text: '获取知识库列表失败' })
    } finally {
      setLoadingKb(false)
    }
  }

  const handleTransferToKb = async (kbId: string, kbName: string) => {
    if (!selectedFeedId) return

    setKbSubmitting(true)
    try {
      const result = await apiClient.feedToKnowledgeBase(selectedFeedId, kbId)
      if (result.success) {
        setKbMessage({ type: 'success', text: `已转入知识库: ${kbName}` })
        setTimeout(() => {
          setShowKbModal(false)
          setKbMessage(null)
          setSelectedFeedId(null)
        }, 1500)
      } else {
        setKbMessage({ type: 'error', text: result.message || '转入失败' })
      }
    } catch (e) {
      console.error('转入知识库失败:', e)
      setKbMessage({ type: 'error', text: '转入知识库失败' })
    } finally {
      setKbSubmitting(false)
    }
  }

  // ========== 渲染 ==========
  // 首次加载且无缓存时显示 loading
  if (loading && feeds.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-muted-foreground space-y-4">
        <Loader2 className="h-8 w-8 animate-spin" />
        <p>正在加载信息流...</p>
      </div>
    )
  }

  // 格式化缓存时间显示
  const formatCacheTime = () => {
    if (!cacheTime) return ''
    const diff = Date.now() - cacheTime
    if (diff < 60000) return '刚刚更新'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    return `${Math.floor(diff / 3600000)}小时前`
  }

  const cacheAgeMs = cacheTime > 0 ? Date.now() - cacheTime : null
  const cacheIsStale = cacheAgeMs !== null && cacheAgeMs > CACHE_DURATION
  const freshnessBadgeLabel = isRefreshing ? '后台刷新中' : cacheIsStale ? '缓存快照' : '新鲜'
  const freshnessSummary = isRefreshing
    ? '正在同步最新内容'
    : cacheTime > 0
      ? cacheIsStale
        ? '当前优先展示本地缓存快照，后台需要补刷'
        : '当前界面已加载最近快照'
      : '等待首批数据加载'
  const sortModeLabel = sortMode === 'time' ? '按最新发布时间排序' : '按重要性排序'
  const backendReadBackend = feedHealth?.storage.feeds_read_backend || 'unknown'
  const backendCacheLayers = feedHealth?.storage.cache_layers?.join(' + ') || 'memory'
  const backendLatestFeedAt = feedHealth?.freshness.last_feed_item_at || null
  const backendSyncLabel = feedHealth
    ? feedHealth.summary.status === 'healthy'
      ? '后端同步正常'
      : '后端同步需关注'
    : '等待后端状态'
  const backendSyncDetail = feedHealth
    ? `后端读取：${backendReadBackend} · 缓存层：${backendCacheLayers}`
    : '正在获取后端同步状态'
  const backendThroughput = feedHealth
    ? `近1小时新增 ${feedHealth.counts.feed_items_1h} 条 · 24小时活跃源 ${feedHealth.counts.active_sources_24h} 个`
    : null

  return (
    <div className="space-y-4">
      {/* 错误提示 */}
      {error && feeds.length === 0 && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-medium text-red-800 dark:text-red-200">加载失败</h4>
              <p className="text-sm text-red-600 dark:text-red-300 mt-1">{error}</p>
              <button
                onClick={() => loadFeedsWithRetry(0)}
                className="mt-2 text-sm text-red-700 dark:text-red-300 underline hover:no-underline"
              >
                点击重试
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 离线提示 */}
      {isOffline && feeds.length > 0 && (
        <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-3">
          <div className="flex items-center gap-2 text-sm text-orange-700 dark:text-orange-300">
            <WifiOff className="h-4 w-4" />
            <span>网络连接异常，显示离线数据</span>
          </div>
        </div>
      )}

      <div
        className={cn(
          'rounded-xl border px-4 py-3',
          isRefreshing
            ? 'border-blue-300 bg-blue-50/70 dark:bg-blue-950/20'
            : cacheIsStale
              ? 'border-amber-300 bg-amber-50/70 dark:bg-amber-950/20'
              : 'border-border bg-muted/30'
        )}
      >
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm font-medium">
              {isRefreshing ? (
                <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />
              ) : cacheIsStale ? (
                <AlertCircle className="h-4 w-4 text-amber-500" />
              ) : (
                <Wifi className="h-4 w-4 text-green-500" />
              )}
              <span>{freshnessSummary}</span>
            </div>
            <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
              {cacheTime > 0 && (
                <span>
                  界面快照：{formatCacheTime()} ({formatAbsoluteTime(new Date(cacheTime).toISOString())})
                </span>
              )}
              {latestPublishedAt && (
                <span>
                  最新内容：{formatTime(latestPublishedAt)} ({formatAbsoluteTime(latestPublishedAt)})
                </span>
              )}
              <span>{sortModeLabel}</span>
              <span>{backendSyncDetail}</span>
            </div>
            <div className="flex flex-wrap gap-x-4 gap-y-1 pt-1 text-xs text-muted-foreground">
              <span>{backendSyncLabel}</span>
              {backendLatestFeedAt && (
                <span>
                  后端最新入库：{formatTime(backendLatestFeedAt)} ({formatAbsoluteTime(backendLatestFeedAt)})
                </span>
              )}
              {backendThroughput && <span>{backendThroughput}</span>}
            </div>
          </div>
          <span
            className={cn(
              'rounded-full px-2.5 py-1 text-xs font-medium',
              isRefreshing
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-950/30 dark:text-blue-300'
                : cacheIsStale
                  ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/30 dark:text-amber-300'
                  : 'bg-green-100 text-green-700 dark:bg-green-950/30 dark:text-green-300'
            )}
          >
            {freshnessBadgeLabel}
          </span>
        </div>
      </div>

      {/* 顶部工具栏 */}
      <div className="flex flex-wrap items-center gap-2 pb-3 border-b">
        {/* 分类按钮 */}
        {['全部', '科技', '财经', '海外财经', '国内', '开发者', 'AI研究', '国际科技'].map(cat => {
          const isActive = cat === '全部' ? category === null : category === cat
          return (
            <button
              key={cat}
              onClick={() => handleCategoryClick(cat === '全部' ? null : cat)}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
                isActive
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              )}
            >
              {cat}
            </button>
          )
        })}
      </div>

      {/* 二级筛选栏 */}
      <div className="flex flex-wrap items-center gap-3">
        {/* 子Tag筛选 - 仅在科技/财经/海外财经下显示 */}
        {category && ['科技', '财经', '海外财经'].includes(category) && (
          <div className="flex items-center gap-2 bg-blue-50 dark:bg-blue-900/20 px-3 py-2 rounded-lg animate-in fade-in slide-in-from-top-2">
            <span className="text-xs text-blue-600 dark:text-blue-400 font-medium">子分类:</span>
            <div className="flex gap-1">
              <button
                onClick={() => setSubTag(null)}
                className={cn(
                  'px-2 py-1 rounded text-xs transition-colors',
                  subTag === null ? 'bg-blue-500 text-white' : 'bg-white dark:bg-gray-800 text-gray-700'
                )}
              >
                全部
              </button>
              {CATEGORY_CONFIG[category as keyof typeof CATEGORY_CONFIG]?.subTags.map(tag => (
                <button
                  key={tag.id}
                  onClick={() => setSubTag(tag.id)}
                  className={cn(
                    'px-2 py-1 rounded text-xs transition-colors',
                    subTag === tag.id ? 'bg-blue-500 text-white' : 'bg-white dark:bg-gray-800 text-gray-700'
                  )}
                >
                  {tag.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 重要性筛选 */}
        <select
          value={importanceLevel}
          onChange={(e) => setImportanceLevel(e.target.value)}
          className="px-3 py-2 rounded-lg text-sm border bg-background"
        >
          <option value="all">全部重要性</option>
          <option value="critical">🔴 紧急 (≥0.9)</option>
          <option value="high">🟠 重要 (0.75-0.9)</option>
          <option value="medium">🟡 一般 (0.6-0.75)</option>
          <option value="low">⚪ 低 (&lt;0.6)</option>
        </select>

        {/* 排序 */}
        <button
          onClick={() => setSortMode(prev => prev === 'time' ? 'importance-desc' : 'time')}
          className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm border bg-background hover:bg-muted"
        >
          <ArrowUpDown className="h-4 w-4" />
          {sortMode === 'time' ? '时间排序' : '重要性排序'}
        </button>

        {/* 刷新 - 支持后台刷新 */}
        <button
          onClick={() => refreshFeedsSilently()}
          disabled={isRefreshing}
          className={cn(
            'p-2 rounded-lg border hover:bg-muted disabled:opacity-50 transition-all',
            isRefreshing && 'border-blue-300 bg-blue-50'
          )}
          title={isRefreshing ? '正在刷新...' : '刷新数据'}
        >
          <RefreshCw className={cn('h-4 w-4', isRefreshing && 'animate-spin text-blue-500')} />
        </button>

        {/* 刷新状态指示 */}
        {isRefreshing && (
          <span className="text-xs text-blue-500 animate-pulse">
            更新中...
          </span>
        )}

        {/* 缓存时间 */}
        {cacheTime > 0 && !isRefreshing && (
          <span className="text-xs text-muted-foreground flex items-center gap-1">
            <Wifi className="h-3 w-3" />
            {formatCacheTime()}
          </span>
        )}

        {/* 清除筛选 */}
        {(category || subTag || importanceLevel !== 'all' || sourceFilter) && (
          <button
            onClick={clearFilters}
            className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm text-red-600 hover:bg-red-50"
          >
            <X className="h-4 w-4" />
            清除筛选
          </button>
        )}
      </div>

      {/* 来源快捷筛选 */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs text-muted-foreground">来源:</span>
        <button
          onClick={() => setSourceFilter(null)}
          className={cn(
            'px-2 py-1 rounded text-xs transition-colors',
            sourceFilter === null ? 'bg-primary text-primary-foreground' : 'bg-muted hover:bg-muted/80'
          )}
        >
          全部
        </button>
        {sources.slice(0, 12).map((s, index) => (
          <button
            key={`${s.id}-${index}`}
            onClick={() => setSourceFilter(sourceFilter === s.id ? null : s.id)}
            className={cn(
              'px-2 py-1 rounded text-xs transition-colors',
              sourceFilter === s.id ? 'bg-primary text-primary-foreground' : 'bg-muted hover:bg-muted/80'
            )}
            title={s.name}
          >
            {s.name.length > 8 ? s.name.slice(0, 8) + '...' : s.name}
          </button>
        ))}
        {sources.length > 12 && (
          <select
            value={sourceFilter || ''}
            onChange={(e) => setSourceFilter(e.target.value || null)}
            className="px-2 py-1 rounded text-xs border bg-background"
          >
            <option value="">更多来源...</option>
            {sources.slice(12).map((s, index) => (
              <option key={`${s.id}-${index}`} value={s.id}>{s.name}</option>
            ))}
          </select>
        )}
      </div>

      {/* 统计栏 - 添加缓存时间和数据新鲜度指示 */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="text-xs text-muted-foreground">
          共 {filteredFeeds.length} 条
          {category && ` · ${category}`}
          {subTag && ` · ${CATEGORY_CONFIG[category as keyof typeof CATEGORY_CONFIG]?.subTags.find(t => t.id === subTag)?.name}`}
          {sourceFilter && ` · ${sources.find(s => s.id === sourceFilter)?.name}`}
          <button
            onClick={() => setShowLow(!showLow)}
            className="ml-4 text-blue-600 hover:underline"
          >
            {showLow ? '隐藏' : '显示'}低重要性({groups.low.length})
          </button>
        </div>

        {/* 数据新鲜度指示 */}
        <div className="flex items-center gap-2 text-xs">
          {isRefreshing ? (
            <span className="flex items-center gap-1 text-blue-500">
              <Wifi className="h-3 w-3 animate-pulse" />
              正在更新...
            </span>
          ) : cacheTime ? (
            <span className={cn(
              "flex items-center gap-1",
              Date.now() - cacheTime > CACHE_DURATION ? "text-orange-500" : "text-green-500"
            )}>
              <Wifi className="h-3 w-3" />
              {formatCacheTime()}
            </span>
          ) : (
            <span className="flex items-center gap-1 text-gray-400">
              <WifiOff className="h-3 w-3" />
              离线数据
            </span>
          )}
        </div>
      </div>

      {/* 信息流 */}
      <div className="space-y-3">
        {/* 紧急 */}
        {groups.critical.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-2 px-1">
              <div className="w-2 h-2 rounded-full bg-red-600 animate-pulse" />
              <span className="text-sm font-bold text-red-600">紧急信息 {groups.critical.length}</span>
            </div>
            {groups.critical.map(f => <FeedCard key={f.id} feed={f} onRead={toggleRead} onFav={toggleFavorite} onToKnowledge={handleToKnowledge} />)}
          </section>
        )}

        {/* 重要 */}
        {groups.high.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-2 px-1">
              <div className="w-2 h-2 rounded-full bg-orange-500" />
              <span className="text-sm font-medium text-orange-600">重要信息 {groups.high.length}</span>
            </div>
            {groups.high.map(f => <FeedCard key={f.id} feed={f} onRead={toggleRead} onFav={toggleFavorite} onToKnowledge={handleToKnowledge} />)}
          </section>
        )}

        {/* 一般 */}
        {groups.medium.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-2 px-1">
              <div className="w-2 h-2 rounded-full bg-yellow-500" />
              <span className="text-sm font-medium text-yellow-600">一般信息 {groups.medium.length}</span>
            </div>
            {groups.medium.map(f => <FeedCard key={f.id} feed={f} onRead={toggleRead} onFav={toggleFavorite} onToKnowledge={handleToKnowledge} />)}
          </section>
        )}

        {/* 低重要性（可折叠） */}
        {showLow && groups.low.length > 0 && (
          <section className="opacity-70">
            <div className="flex items-center gap-2 mb-2 px-1">
              <div className="w-2 h-2 rounded-full bg-gray-400" />
              <span className="text-sm text-gray-500">低重要性 {groups.low.length}</span>
            </div>
            {groups.low.map(f => <FeedCard key={f.id} feed={f} onRead={toggleRead} onFav={toggleFavorite} onToKnowledge={handleToKnowledge} compact />)}
          </section>
        )}
      </div>

      {filteredFeeds.length === 0 && !loading && (
        <div className="text-center py-12 text-muted-foreground">
          <p>暂无符合条件的信息</p>
          <button onClick={clearFilters} className="mt-2 text-sm text-primary hover:underline">
            清除筛选条件
          </button>
        </div>
      )}

      {/* 知识库选择弹窗 */}
      {showKbModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card rounded-lg shadow-xl w-full max-w-md p-6 border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">转入知识库</h3>
              <button onClick={() => { setShowKbModal(false); setKbMessage(null); setSelectedFeedId(null); }} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            {loadingKb ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
                <span className="ml-2 text-muted-foreground">加载知识库...</span>
              </div>
            ) : kbList.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-muted-foreground mb-4">暂无可用知识库</p>
                <a href="/settings/knowledge" className="text-primary hover:underline text-sm">
                  去创建知识库 →
                </a>
              </div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {kbList.map(kb => (
                  <button
                    key={kb.id}
                    onClick={() => handleTransferToKb(kb.id, kb.name)}
                    disabled={kbSubmitting}
                    className="w-full text-left px-4 py-3 rounded-lg border hover:bg-muted hover:border-primary/50 transition-colors flex items-center justify-between"
                  >
                    <span className="font-medium">{kb.name}</span>
                    {kbSubmitting && selectedFeedId && <Loader2 className="h-4 w-4 animate-spin" />}
                  </button>
                ))}
              </div>
            )}

            {kbMessage && (
              <div className={cn(
                "mt-4 p-3 rounded-lg text-sm",
                kbMessage.type === 'success' ? "bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400" : "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400"
              )}>
                {kbMessage.text}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// 单条信息卡片
function FeedCard({
  feed,
  onRead,
  onFav,
  onToKnowledge,
  compact = false,
}: {
  feed: FeedItem
  onRead: (id: string) => void
  onFav: (id: string) => void
  onToKnowledge?: (id: string) => void
  compact?: boolean
}) {
  const importanceColor =
    feed.importance >= 0.9 ? 'bg-red-600 text-white' :
    feed.importance >= 0.75 ? 'bg-orange-100 text-orange-700' :
    feed.importance >= 0.6 ? 'bg-yellow-100 text-yellow-700' :
    'bg-gray-100 text-gray-700'

  return (
    <div className={cn(
      'p-4 rounded-lg border bg-card hover:border-primary/50 transition-all',
      feed.is_read && 'opacity-50',
      compact && 'p-3'
    )}>
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          {/* 元信息 */}
          <div className="flex items-center gap-2 mb-1.5 flex-wrap text-xs">
            <span className="font-medium text-gray-700 dark:text-gray-300">{feed.source}</span>
            <span className="text-muted-foreground">·</span>
            <span className="text-muted-foreground">{feed.category}</span>
            <span className="text-muted-foreground">·</span>
            <span className="text-muted-foreground flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatTime(feed.published_at)}
            </span>
            <span className={cn('px-1.5 py-0.5 rounded text-xs font-medium', importanceColor)}>
              {feed.importance >= 0.9 ? '紧急' : feed.importance >= 0.75 ? '重要' : feed.importance >= 0.6 ? '一般' : '低'}
            </span>
          </div>

          {/* 标题 */}
          <h3 className={cn('font-medium leading-snug mb-1', compact && 'text-sm')}>
            <a href={feed.url} target="_blank" rel="noopener noreferrer" className="hover:text-primary hover:underline">
              {feed.title}
            </a>
          </h3>

          {/* 摘要 */}
          {!compact && feed.summary && (
            <p className="text-sm text-muted-foreground line-clamp-2">{feed.summary}</p>
          )}
        </div>

        {/* 操作按钮 */}
        <div className="flex items-center gap-1 shrink-0">
          <button
            onClick={() => onFav(feed.id)}
            className={cn('p-2 rounded-md hover:bg-muted transition-colors', feed.is_favorite && 'text-yellow-500')}
            title="收藏"
          >
            <Star className="h-4 w-4" fill={feed.is_favorite ? 'currentColor' : 'none'} />
          </button>
          <button
            onClick={() => onRead(feed.id)}
            className={cn('p-2 rounded-md hover:bg-muted transition-colors', feed.is_read && 'text-green-500')}
            title="标记已读"
          >
            <Check className="h-4 w-4" />
          </button>
          {onToKnowledge && (
            <button
              onClick={() => onToKnowledge(feed.id)}
              className="p-2 rounded-md hover:bg-muted text-muted-foreground hover:text-primary"
              title="转入知识库"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
            </button>
          )}
          <a
            href={feed.url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 rounded-md hover:bg-muted text-muted-foreground"
            title="在新窗口打开"
          >
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>
      </div>
    </div>
  )
}
