'use client'

import { AlertTriangle, Check, Copy, Loader2 } from 'lucide-react'
import type { TaskPacketPreviewResponse } from '@/lib/api-client'

type TaskPreviewSectionProps = {
  taskPreviewLoading: boolean
  taskPreviewError: string | null
  taskPreviewResult: TaskPacketPreviewResponse | null
  taskPreviewCopied: boolean
  selectedPreviewCount: number
  onRequestPreview: () => void
  onCopyPreview: () => void
}

export function TaskPreviewSection({
  taskPreviewLoading,
  taskPreviewError,
  taskPreviewResult,
  taskPreviewCopied,
  selectedPreviewCount,
  onRequestPreview,
  onCopyPreview,
}: TaskPreviewSectionProps) {
  return (
    <div className="mt-4 rounded-lg border bg-muted/20">
      <div className="flex items-center justify-between px-3 py-2 border-b">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold">后端任务包预览</span>
          <span className="text-[10px] text-muted-foreground">
            Task-Packet Preview - 后端生成，仅供审查参考
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={onRequestPreview}
            disabled={taskPreviewLoading || selectedPreviewCount === 0}
            className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs hover:bg-muted transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {taskPreviewLoading && <Loader2 className="h-3 w-3 animate-spin" />}
            请求预览
          </button>
          {taskPreviewResult && (
            <button
              type="button"
              onClick={onCopyPreview}
              className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-1 text-xs hover:bg-muted transition-colors"
              title="复制预览包到剪贴板"
            >
              {taskPreviewCopied ? (
                <>
                  <Check className="h-3 w-3 text-green-600" />
                  <span className="text-green-600">已复制</span>
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  <span>复制</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {taskPreviewError && (
        <div className="px-3 py-2 flex items-start gap-2 text-sm text-red-700">
          <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
          {taskPreviewError}
        </div>
      )}

      {taskPreviewLoading && (
        <div className="px-3 py-2 flex items-center gap-2 text-xs text-muted-foreground">
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
          正在请求后端任务包预览...
        </div>
      )}

      {taskPreviewResult && (
        <div className="px-3 py-2 space-y-1.5 text-xs">
          <div className="grid grid-cols-[90px_1fr] gap-x-2">
            <span className="text-muted-foreground shrink-0">摘要</span>
            <span className="font-medium truncate">{taskPreviewResult.task_packet_summary}</span>
          </div>
          <div className="grid grid-cols-[90px_1fr] gap-x-2">
            <span className="text-muted-foreground shrink-0">意图</span>
            <span>{taskPreviewResult.packet_intent}</span>
          </div>
          <div className="grid grid-cols-[90px_1fr] gap-x-2">
            <span className="text-muted-foreground shrink-0">建议处理通道</span>
            <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">{taskPreviewResult.suggested_lane}</span>
          </div>
          {taskPreviewResult.suggested_next_step && (
            <div className="grid grid-cols-[90px_1fr] gap-x-2">
              <span className="text-muted-foreground shrink-0">建议下一步</span>
              <span>{taskPreviewResult.suggested_next_step}</span>
            </div>
          )}
          {taskPreviewResult.selected_label_groups.length > 0 && (
            <div className="grid grid-cols-[90px_1fr] gap-x-2">
              <span className="text-muted-foreground shrink-0">已选标签组</span>
              <div className="flex flex-wrap gap-1">
                {taskPreviewResult.selected_label_groups.map((group, index) => (
                  <span key={index} className="rounded bg-muted px-1.5 py-0.5 text-[10px]">
                    [{group.label_type}] {group.count}项
                  </span>
                ))}
              </div>
            </div>
          )}
          {taskPreviewResult.controller_packet?.reason_tags?.length > 0 && (
            <div className="grid grid-cols-[90px_1fr] gap-x-2">
              <span className="text-muted-foreground shrink-0">原因标签</span>
              <div className="flex flex-wrap gap-1">
                {taskPreviewResult.controller_packet.reason_tags.map((tag, index) => (
                  <span key={index} className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
          <div className="grid grid-cols-[90px_1fr] gap-x-2">
            <span className="text-muted-foreground shrink-0">事实状态</span>
            <span className="text-muted-foreground">{taskPreviewResult.promotion_state}</span>
          </div>
        </div>
      )}

      {!taskPreviewResult && !taskPreviewError && !taskPreviewLoading && (
        <div className="px-3 py-2 text-xs text-muted-foreground">
          {selectedPreviewCount === 0
            ? '请先选择至少一个知识/进化/来源项，再请求后端预览'
            : '点击“请求预览”从后端获取规范化任务包预览'}
        </div>
      )}
    </div>
  )
}
