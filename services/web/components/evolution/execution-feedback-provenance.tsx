import type { FlywheelWorkerProvenance } from '@/lib/api-client'

type ProvenanceInputProps = {
  workerRunId: string
  workerProvider: string
  workerModel: string
  workerArtifactRef: string
  onWorkerRunIdChange: (value: string) => void
  onWorkerProviderChange: (value: string) => void
  onWorkerModelChange: (value: string) => void
  onWorkerArtifactRefChange: (value: string) => void
}

function hasProvenanceValue(
  provenance: FlywheelWorkerProvenance | null | undefined,
): provenance is FlywheelWorkerProvenance {
  return Boolean(
    provenance &&
      (provenance.worker_run_id ||
        provenance.worker_provider ||
        provenance.worker_model ||
        provenance.worker_artifact_ref),
  )
}

export function ExecutionFeedbackProvenanceInputs({
  workerRunId,
  workerProvider,
  workerModel,
  workerArtifactRef,
  onWorkerRunIdChange,
  onWorkerProviderChange,
  onWorkerModelChange,
  onWorkerArtifactRefChange,
}: ProvenanceInputProps) {
  return (
    <div className="rounded-md border border-dashed bg-muted/20 px-3 py-2">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-xs font-medium text-muted-foreground">Worker provenance (optional, inspect-only)</span>
        <span className="text-[10px] text-muted-foreground">caller-provided, not verified</span>
      </div>
      <div className="grid gap-2 md:grid-cols-4">
        <div>
          <label className="mb-0.5 block text-[10px] text-muted-foreground">run_id</label>
          <input
            value={workerRunId}
            onChange={(e) => onWorkerRunIdChange(e.target.value)}
            placeholder="e.g. run-abc123"
            className="w-full rounded-md border bg-background px-2 py-1.5 text-xs placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
        <div>
          <label className="mb-0.5 block text-[10px] text-muted-foreground">provider</label>
          <input
            value={workerProvider}
            onChange={(e) => onWorkerProviderChange(e.target.value)}
            placeholder="e.g. claude-worker"
            className="w-full rounded-md border bg-background px-2 py-1.5 text-xs placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
        <div>
          <label className="mb-0.5 block text-[10px] text-muted-foreground">model</label>
          <input
            value={workerModel}
            onChange={(e) => onWorkerModelChange(e.target.value)}
            placeholder="e.g. glm-5"
            className="w-full rounded-md border bg-background px-2 py-1.5 text-xs placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
        <div>
          <label className="mb-0.5 block text-[10px] text-muted-foreground">artifact_ref</label>
          <input
            value={workerArtifactRef}
            onChange={(e) => onWorkerArtifactRefChange(e.target.value)}
            placeholder="e.g. final.json"
            className="w-full rounded-md border bg-background px-2 py-1.5 text-xs placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>
    </div>
  )
}

export function ExecutionFeedbackProvenanceDisplay({
  provenance,
}: {
  provenance: FlywheelWorkerProvenance | null | undefined
}) {
  if (!hasProvenanceValue(provenance)) return null

  return (
    <div className="rounded-md border border-dashed bg-amber-50/30 px-3 py-2">
      <div className="mb-1.5 flex items-center gap-2">
        <span className="text-xs font-medium text-muted-foreground">Worker provenance</span>
        <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] text-amber-700">
          inspect-only / caller-provided / unverified
        </span>
      </div>
      <div className="grid gap-1.5 text-xs md:grid-cols-4">
        {provenance.worker_run_id && (
          <div className="text-muted-foreground">
            <span className="font-medium">run_id:</span> {provenance.worker_run_id}
          </div>
        )}
        {provenance.worker_provider && (
          <div className="text-muted-foreground">
            <span className="font-medium">provider:</span> {provenance.worker_provider}
          </div>
        )}
        {provenance.worker_model && (
          <div className="text-muted-foreground">
            <span className="font-medium">model:</span> {provenance.worker_model}
          </div>
        )}
        {provenance.worker_artifact_ref && (
          <div className="text-muted-foreground">
            <span className="font-medium">artifact_ref:</span> {provenance.worker_artifact_ref}
          </div>
        )}
      </div>
    </div>
  )
}
