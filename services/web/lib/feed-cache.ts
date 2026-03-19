'use client'

/**
 * Feed缓存管理器 - 使用 IndexedDB 替代 localStorage
 * 解决 localStorage 5MB 容量限制问题
 */

const DB_NAME = 'myattention_cache'
const DB_VERSION = 1
const STORE_NAME = 'feeds'

interface CacheData<T> {
  data: T
  timestamp: number
  version: number
}

class FeedCache {
  private db: IDBDatabase | null = null
  private initPromise: Promise<void> | null = null

  async init(): Promise<void> {
    if (this.db) return
    if (this.initPromise) return this.initPromise

    this.initPromise = this.doInit()
    return this.initPromise
  }

  private async doInit(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onerror = () => {
        console.error('[FeedCache] 数据库打开失败')
        reject(request.error)
      }

      request.onsuccess = () => {
        this.db = request.result
        console.log('[FeedCache] 数据库已连接')
        resolve()
      }

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME)
          console.log('[FeedCache] 创建存储对象:', STORE_NAME)
        }
      }
    })
  }

  async get<T>(key: string): Promise<T | null> {
    await this.init()
    if (!this.db) return null

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readonly')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.get(key)

      request.onsuccess = () => {
        const result = request.result as CacheData<T> | undefined
        if (result) {
          resolve(result.data)
        } else {
          resolve(null)
        }
      }

      request.onerror = () => {
        console.error('[FeedCache] 读取失败:', key)
        resolve(null)
      }
    })
  }

  async set<T>(key: string, data: T): Promise<void> {
    await this.init()
    if (!this.db) return

    const cacheData: CacheData<T> = {
      data,
      timestamp: Date.now(),
      version: 1,
    }

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readwrite')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.put(cacheData, key)

      request.onsuccess = () => resolve()
      request.onerror = () => {
        console.error('[FeedCache] 写入失败:', key)
        resolve() // 静默失败，不影响主流程
      }
    })
  }

  async getTimestamp(key: string): Promise<number | null> {
    await this.init()
    if (!this.db) return null

    return new Promise((resolve) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readonly')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.get(key)

      request.onsuccess = () => {
        const result = request.result as CacheData<unknown> | undefined
        resolve(result?.timestamp || null)
      }

      request.onerror = () => resolve(null)
    })
  }

  async clear(): Promise<void> {
    await this.init()
    if (!this.db) return

    return new Promise((resolve) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readwrite')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.clear()

      request.onsuccess = () => resolve()
      request.onerror = () => resolve()
    })
  }

  // 清理过期缓存（保留最近7天的）
  async cleanup(maxAge: number = 7 * 24 * 60 * 60 * 1000): Promise<void> {
    await this.init()
    if (!this.db) return

    const cutoff = Date.now() - maxAge

    return new Promise((resolve) => {
      const transaction = this.db!.transaction([STORE_NAME], 'readwrite')
      const store = transaction.objectStore(STORE_NAME)
      const request = store.openCursor()

      request.onsuccess = () => {
        const cursor = request.result
        if (cursor) {
          const value = cursor.value as CacheData<unknown>
          if (value.timestamp < cutoff) {
            cursor.delete()
          }
          cursor.continue()
        }
      }

      transaction.oncomplete = () => resolve()
      transaction.onerror = () => resolve()
    })
  }
}

// 单例实例
export const feedCache = new FeedCache()

// 兼容 localStorage 的降级方案
export const localStorageCache = {
  get<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(key)
      if (!item) return null
      return JSON.parse(item) as T
    } catch {
      return null
    }
  },

  set<T>(key: string, data: T): void {
    try {
      localStorage.setItem(key, JSON.stringify(data))
    } catch (e) {
      // 可能是容量不足，尝试清理旧数据
      console.warn('[localStorageCache] 写入失败，尝试清理空间:', e)
      this.cleanup()
      try {
        localStorage.setItem(key, JSON.stringify(data))
      } catch (e2) {
        console.error('[localStorageCache] 写入失败:', e2)
      }
    }
  },

  getTimestamp(key: string): number | null {
    try {
      const timeKey = `${key}_time`
      const timeStr = localStorage.getItem(timeKey)
      return timeStr ? parseInt(timeStr) : null
    } catch {
      return null
    }
  },

  setTimestamp(key: string, timestamp: number): void {
    try {
      localStorage.setItem(`${key}_time`, timestamp.toString())
    } catch {
      // 忽略错误
    }
  },

  cleanup(): void {
    try {
      // 清理非关键数据
      const keysToKeep = ['feeds_cache_v2', 'feeds_cache_time_v2']
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key && !keysToKeep.some(k => key.includes(k))) {
          localStorage.removeItem(key)
        }
      }
    } catch {
      // 忽略错误
    }
  },
}
