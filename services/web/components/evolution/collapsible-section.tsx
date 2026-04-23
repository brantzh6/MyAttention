'use client'

import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'

type CollapsibleSectionProps = {
  title: string
  open: boolean
  defaultOpen?: boolean
  children: React.ReactNode
}

export function CollapsibleSection({
  title,
  open,
  defaultOpen = false,
  children,
}: CollapsibleSectionProps) {
  const [expanded, setExpanded] = useState(defaultOpen)
  const isForced = open

  if (!isForced && !expanded) {
    return (
      <button
        type="button"
        onClick={() => setExpanded(true)}
        className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-sm font-medium text-muted-foreground hover:bg-muted"
      >
        <ChevronRight className="h-3.5 w-3.5" />
        {title}
      </button>
    )
  }

  return (
    <div className="rounded-lg border bg-background/50">
      <button
        type="button"
        onClick={() => !isForced && setExpanded(false)}
        className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-sm font-medium hover:bg-muted"
      >
        <ChevronDown className="h-3.5 w-3.5" />
        {title}
      </button>
      <div className="px-3 pb-3 pt-1">{children}</div>
    </div>
  )
}
