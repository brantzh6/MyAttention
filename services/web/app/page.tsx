import { ArrowDown, Brain, BookOpen, Globe2, Radar, Wrench } from 'lucide-react'

import { FeedList } from '@/components/feed/feed-list'

const brainLayers = [
  {
    title: '信息大脑',
    icon: Brain,
    summary: '接收、筛选、归一化外部信号，形成当前可消费的信息面。',
    points: ['抓取与降噪', '来源与对象识别', '当前关注面'],
  },
  {
    title: '知识大脑',
    icon: BookOpen,
    summary: '把稳定信号沉淀为可追踪、可回看、可复用的知识结构。',
    points: ['知识归档', '版本连续性', '可回溯摘要'],
  },
  {
    title: '进化大脑',
    icon: Radar,
    summary: '对方法、规则和模型输出做评估，推动系统持续调整。',
    points: ['review 与 absorption', '多模型判断', '方法论迭代'],
  },
]

const crossCuttingLayers = [
  {
    title: '世界模型',
    icon: Globe2,
    summary: '贯穿三个主脑的整体认知骨架，负责关系、时间和策略上下文的统一。',
    points: ['跨域关系', '时间演化', '策略与决策上下文'],
  },
  {
    title: '思维工具',
    icon: Wrench,
    summary: '方法层，不是单独脑区，而是给各层注入分析框架、推理模板和方法论迭代能力。',
    points: ['可迭代方法', '分析框架', '工具箱吸收'],
  },
]

export default function HomePage() {
  return (
    <div className="space-y-6 p-6">
      <header className="rounded-2xl border bg-gradient-to-br from-background via-background to-muted/30 p-6 shadow-sm">
        <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground">IKE Control Surface</p>
        <h1 className="mt-2 text-3xl font-semibold text-foreground">层级脑 + 贯穿层</h1>
        <p className="mt-2 max-w-3xl text-muted-foreground">
          这里的结构不是平铺的入口列表，而是一个可进化的认知体系：信息大脑先接收信号，知识大脑再沉淀稳定结构，进化大脑负责方法迭代。
          世界模型与思维工具不是附属项，它们是贯穿全局的方法层。
        </p>
      </header>

      <section className="rounded-2xl border bg-card p-6 shadow-sm">
        <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
          <span className="rounded-full bg-primary/10 px-3 py-1 text-primary">信息大脑</span>
          <ArrowDown className="h-4 w-4" />
          <span className="rounded-full bg-primary/10 px-3 py-1 text-primary">知识大脑</span>
          <ArrowDown className="h-4 w-4" />
          <span className="rounded-full bg-primary/10 px-3 py-1 text-primary">进化大脑</span>
          <span className="ml-2 rounded-full border px-3 py-1">世界模型贯穿其上</span>
          <span className="rounded-full border px-3 py-1">思维工具贯穿其上</span>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {brainLayers.map((layer, index) => {
          const Icon = layer.icon

          return (
            <article key={layer.title} className="rounded-xl border bg-card p-4 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-semibold">
                  {index + 1}
                </div>
                <div className="rounded-lg bg-primary/10 p-2 text-primary">
                  <Icon className="h-5 w-5" />
                </div>
                <h2 className="text-lg font-semibold text-foreground">{layer.title}</h2>
              </div>
              <p className="mt-3 text-sm text-muted-foreground">{layer.summary}</p>
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

      <section className="grid gap-4 md:grid-cols-2">
        {crossCuttingLayers.map((layer) => {
          const Icon = layer.icon

          return (
            <article key={layer.title} className="rounded-xl border bg-card p-5 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-secondary p-2 text-secondary-foreground">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-foreground">{layer.title}</h2>
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Cross-cutting layer</p>
                </div>
              </div>
              <p className="mt-3 text-sm text-muted-foreground">{layer.summary}</p>
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
          <p className="mt-1 text-sm text-muted-foreground">信息流仍然保留，但它现在只是一层，不再是页面的唯一组织方式。</p>
        </header>
        <FeedList />
      </section>
    </div>
  )
}
