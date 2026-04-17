import { Brain, BookOpen, Globe2, Radar } from 'lucide-react'

import { FeedList } from '@/components/feed/feed-list'

const layers = [
  {
    title: '信息大脑',
    icon: Brain,
    description: '接收、筛选、归一化外部信号，形成可消费的当前信息面。',
    points: ['抓取与降噪', '来源与对象识别', '当前关注面'],
  },
  {
    title: '知识大脑',
    icon: BookOpen,
    description: '把稳定信号沉淀成可追踪、可回看、可复用的知识结构。',
    points: ['知识归档', '版本连续性', '可回溯摘要'],
  },
  {
    title: '进化大脑',
    icon: Radar,
    description: '对方法、规则与模型输出做评估，推动系统持续调整。',
    points: ['review 与 absorption', '多模型判断', '方法论迭代'],
  },
  {
    title: '世界模型',
    icon: Globe2,
    description: '把信息、知识和进化结果组织成一个持续更新的整体认知框架。',
    points: ['跨域关系', '时间演化', '策略与决策上下文'],
  },
]

export default function HomePage() {
  return (
    <div className="space-y-6 p-6">
      <header className="rounded-2xl border bg-gradient-to-br from-background via-background to-muted/30 p-6 shadow-sm">
        <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground">IKE Control Surface</p>
        <h1 className="mt-2 text-3xl font-semibold text-foreground">信息大脑、知识大脑、进化大脑与世界模型</h1>
        <p className="mt-2 max-w-3xl text-muted-foreground">
          这个页面不再只展示信息流，而是把当前系统按四层组织：先处理信息，再沉淀知识，再推动进化，最后汇总到可更新的世界模型。
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {layers.map((layer) => {
          const Icon = layer.icon

          return (
            <article key={layer.title} className="rounded-xl border bg-card p-4 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-primary/10 p-2 text-primary">
                  <Icon className="h-5 w-5" />
                </div>
                <h2 className="text-lg font-semibold text-foreground">{layer.title}</h2>
              </div>
              <p className="mt-3 text-sm text-muted-foreground">{layer.description}</p>
              <ul className="mt-4 space-y-2 text-sm text-foreground">
                {layer.points.map((point) => (
                  <li key={point} className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </article>
          )
        })}
      </section>

      <section className="rounded-2xl border bg-card p-6 shadow-sm">
        <header className="mb-4">
          <h2 className="text-xl font-semibold text-foreground">信息大脑当前流</h2>
          <p className="mt-1 text-sm text-muted-foreground">下面仍保留当前信息流视图，但它现在只是四层结构中的一层。</p>
        </header>
        <FeedList />
      </section>
    </div>
  )
}
