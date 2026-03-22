import { FeedList } from '@/components/feed/feed-list'

export default function HomePage() {
  return (
    <div className="p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-foreground">信息流</h1>
        <p className="mt-1 text-muted-foreground">今日更新的信息摘要与重点条目。</p>
      </header>
      <FeedList />
    </div>
  )
}
