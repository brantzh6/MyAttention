import { SnapshotProvenance } from '@/lib/control-surface/types'
import { AlertTriangle } from 'lucide-react'

export function ProvenanceBlock({ provenance }: { provenance: SnapshotProvenance }) {
  return (
    <div className="mb-6 border border-amber-200 bg-amber-50 dark:border-amber-900/50 dark:bg-amber-900/20 rounded-lg p-4 text-sm text-amber-900 dark:text-amber-200">
      <div className="flex items-center gap-2 mb-2 font-semibold">
        <AlertTriangle className="h-4 w-4" />
        Provenance & Caveat
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-y-2 gap-x-4 mb-2 text-xs">
        <div>
          <span className="font-semibold text-amber-700 dark:text-amber-400 block mb-0.5">Source Kind</span>
          {provenance.sourceKind}
        </div>
        <div>
          <span className="font-semibold text-amber-700 dark:text-amber-400 block mb-0.5">Truth Status</span>
          {provenance.truthStatus}
        </div>
        <div>
          <span className="font-semibold text-amber-700 dark:text-amber-400 block mb-0.5">Source Label</span>
          {provenance.sourceLabel}
        </div>
        <div>
          <span className="font-semibold text-amber-700 dark:text-amber-400 block mb-0.5">Last Reviewed</span>
          {provenance.freshnessLabel}
        </div>
      </div>
      <div className="text-amber-800 dark:text-amber-300 bg-amber-100/50 dark:bg-amber-950/30 p-2 rounded border border-amber-200/50 dark:border-amber-900/50 mt-3 text-xs">
        <span className="font-semibold mr-2">Caveat:</span>
        {provenance.caveat}
      </div>
    </div>
  )
}
