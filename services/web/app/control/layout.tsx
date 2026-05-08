import { ReactNode } from 'react'

export default function ControlLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-full flex-col">
      <div className="border-b bg-muted/20 p-4">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-semibold">IKE Project Control Surface</h1>
          <span className="rounded bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary border border-primary/20">
            Anchor P0
          </span>
        </div>
      </div>
      <div className="flex-1 overflow-auto p-4 md:p-6 lg:p-8 bg-background">
        {children}
      </div>
    </div>
  )
}
