# control_plane_reconciler.ps1
# Deterministic control-plane reconciler for the OpenClaw PM loop.
# No model / no LLM. Runs every 15 minutes.
#
# Responsibilities:
#   1. Reconcile detached bridge states (queued -> dispatched -> running ->
#      completed|failed|timeout -> consumed).
#   2. Detect expired leases, dead PIDs, result-artifact existence, and stale
#      lock files. Clean only proven-safe stale lock files.
#   3. Write machine-readable observed state to ops/state/observed_state.json.
#   4. Never mutate controller-owned accepted state; emit
#      controller_attention_required with evidence when observed conflicts with
#      accepted state.
#   5. Generate a compact PM snapshot (ops/state/pm_control_state.json) that
#      routine PM cycles read first. Deep read current_state.json only when the
#      compact snapshot is missing, invalid, stale, contradictory, or indicates
#      controller consultation.

param(
    [switch]$DryRun,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$WarningPreference = "Continue"

# -- Paths --
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$OpsRoot     = Join-Path $ProjectRoot "ops"
$StateDir    = Join-Path $OpsRoot "state"
$BridgeRuns  = Join-Path (Join-Path $OpsRoot "bridge") "runs"
$TriggersDir = Join-Path $OpsRoot "triggers"
$PmRunsDir   = Join-Path $OpsRoot "pm-runs"

$LeaseFile       = Join-Path $StateDir "codex_controller_lease.json"
$LockFile        = Join-Path $StateDir "codex_controller_lease.lock"
$ObservedState   = Join-Path $StateDir "observed_state.json"
$CurrentState    = Join-Path $StateDir "current_state.json"
$SchemasDir      = Join-Path $OpsRoot "schemas"

# -- Helpers --
. (Join-Path $PSScriptRoot "ops_encoding_helpers.ps1")

function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
    Write-Host "[$ts] $msg"
}

function FLog($msg) {
    # Log inside phase functions: uses Write-Host to avoid polluting return streams.
    $ts = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
    Write-Host "[$ts] $msg"
}

function VerboseLog($msg) {
    if ($Verbose) { FLog $msg }
}

function SafeReadJson($path) {
    if (Test-Path $path) {
        try { return Get-Content $path -Raw | ConvertFrom-Json -ErrorAction Stop }
        catch { VerboseLog "JSON parse failed: $path" }
    }
    return $null
}

function SafeWriteJson($path, $obj) {
    if (-not $DryRun) {
        Write-JsonUtf8NoBom -Object $obj -Path $path -Depth 5
    }
}

function Test-PidAlive($procId) {
    try {
        $proc = Get-Process -Id $procId -ErrorAction Stop
        return $null -ne $proc
    }
    catch { return $false }
}

function Get-CodexOutputPath($run) {
    # Read output path from either top-level codex_output_path or nested codex.output_path.
    if ($run.codex_output_path) { return $run.codex_output_path }
    if ($run.codex -and $run.codex.output_path) { return $run.codex.output_path }
    return $null
}

function Get-CodexPid($run) {
    # Read PID from either top-level codex_pid or nested codex.pid.
    if ($null -ne $run.codex_pid) { return $run.codex_pid }
    if ($run.codex -and ($null -ne $run.codex.pid)) { return $run.codex.pid }
    return $null
}

# Lease expiry defaults to 2 hours.
$LeaseExpiryMinutes = 120

# -- 1. Reconcile bridge run files --
function ReconcileBridgeRuns {
    FLog "Phase 1: Reconciling bridge runs..."
    $results = @()

    $runFiles = Get-ChildItem -Path $BridgeRuns -Filter "*.json" -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending

    foreach ($rf in $runFiles) {
        $run = SafeReadJson $rf.FullName
        if (-not $run) {
            $results += @{ file = $rf.Name; state = "unreadable"; has_output = $false }
            continue
        }

        $state = "unknown"
        if ($run.reconciled_status) {
            $state = $run.reconciled_status
        }
        elseif ($run.bridge_status) { $state = $run.bridge_status }
        elseif ($run.status)        { $state = $run.status }

        $outputPath = Get-CodexOutputPath $run
        $hasOutput = $false
        if ($outputPath) {
            $hasOutput = Test-Path $outputPath
        }

        $runPid = Get-CodexPid $run
        $terminalStates = @("completed", "failed", "timeout")
        $alreadyReconciled = $terminalStates -contains $state

        # Persist inferred reconciliation only when the state is non-terminal
        # and we can determine a terminal state. Do NOT mark consumed;
        # controller absorption owns that transition.
        if (-not $alreadyReconciled) {
            # If dispatched but output exists, mark as completed
            if ($state -eq "dispatched" -and $hasOutput) {
                $state = "completed"
                VerboseLog "$($rf.Name): dispatched + output artifact -> completed"
            }

            # If dispatched with no output and > 4 hours old, mark as timeout
            if ($state -eq "dispatched" -and -not $hasOutput) {
                $age = ((Get-Date) - $rf.LastWriteTime).TotalMinutes
                if ($age -gt 240) {
                    $state = "timeout"
                    VerboseLog "$($rf.Name): dispatched, no output, age=$age min -> timeout"
                }
            }

            # If running but PID is dead, mark as failed or completed
            if ($state -eq "running" -and ($null -ne $runPid)) {
                if (-not (Test-PidAlive $runPid)) {
                    if ($hasOutput) {
                        $state = "completed"
                        VerboseLog "$($rf.Name): running, dead PID but output exists -> completed"
                    } else {
                        $state = "failed"
                        VerboseLog "$($rf.Name): running, dead PID, no output -> failed"
                    }
                }
            }
        }

        # Persist reconciled_status back to the bridge run JSON when state
        # changed from its original non-reconciled value.
        if (-not $alreadyReconciled -and $state -ne "unknown") {
            $originalStatus = if ($run.bridge_status) { $run.bridge_status }
                              elseif ($run.status)    { $run.status }
                              else                    { "unknown" }
            if ($state -ne $originalStatus) {
                $now = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
                $run | Add-Member -NotePropertyName "reconciled_status" -NotePropertyValue $state -Force
                $run | Add-Member -NotePropertyName "reconciled_at" -NotePropertyValue $now -Force
                SafeWriteJson $rf.FullName $run
            }
        }

        $results += @{
            file       = $rf.Name
            state      = $state
            has_output = $hasOutput
        }
    }

    return $results
}

# -- 2. Lease & lock reconciliation --
function ReconcileLease {
    FLog "Phase 2: Reconciling lease and lock..."
    $leaseInfo = @{
        lease_file_exists      = $false
        lock_file_exists       = $false
        lease_status           = "none"
        lease_expired          = $false
        lease_pid_alive        = $null
        lock_is_stale          = $false
        lock_removed           = $false
        controller_attention_required = $false
        attention_evidence     = @()
    }

    # -- Lease --
    if (Test-Path $LeaseFile) {
        $leaseInfo.lease_file_exists = $true
        $lease = SafeReadJson $LeaseFile
        if ($lease) {
            $leaseInfo.lease_status = $lease.status

            if ($lease.expires_at) {
                try {
                    $expiry = [DateTimeOffset]::Parse($lease.expires_at)
                    $leaseInfo.lease_expired = ([DateTimeOffset]::UtcNow -gt $expiry)
                } catch {}
            }

            $leasePid = $null
            if ($lease.codex_pid) { $leasePid = $lease.codex_pid }
            elseif ($lease.codex -and $lease.codex.pid) { $leasePid = $lease.codex.pid }

            if ($null -ne $leasePid) {
                $leaseInfo.lease_pid_alive = Test-PidAlive $leasePid
            }

            # For an expired dead running_detached lease, terminalize it.
            # If result artifact exists -> completed; otherwise -> timeout.
            # This means the lease no longer needs controller attention.
            if (($lease.status -eq "running_detached") -and
                $leaseInfo.lease_expired -and
                (-not $leaseInfo.lease_pid_alive)) {

                # Determine if result artifact exists
                $leaseOutputPath = Get-CodexOutputPath $lease
                $hasLeaseOutput = $false
                if ($leaseOutputPath) {
                    $hasLeaseOutput = Test-Path $leaseOutputPath
                }
                # Also check top-level codex_output_path if present
                if (-not $hasLeaseOutput -and $lease.codex_output_path) {
                    $hasLeaseOutput = Test-Path $lease.codex_output_path
                }

                $now = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
                if ($hasLeaseOutput) {
                    $lease.status = "completed"
                    $lease | Add-Member -NotePropertyName "completed_at" -NotePropertyValue $now -Force
                    $leaseInfo.lease_status = "completed"
                    FLog "Lease $($lease.run_id) terminalized: completed (artifact exists)"
                } else {
                    $lease.status = "timeout"
                    $lease | Add-Member -NotePropertyName "completed_at" -NotePropertyValue $now -Force
                    $leaseInfo.lease_status = "timeout"
                    FLog "Lease $($lease.run_id) terminalized: timeout (no artifact)"
                }

                # Persist terminalized lease
                SafeWriteJson $LeaseFile $lease

                # Do NOT flag controller_attention_required for a terminalized lease.
            }
        }
    }

    # -- Lock --
    if (Test-Path $LockFile) {
        $leaseInfo.lock_file_exists = $true

        # Lock is stale if lease is expired/gone and lock is > 30 minutes old
        $lockAge = ((Get-Date) - (Get-Item $LockFile).LastWriteTime).TotalMinutes
        $lockIsStale = $false

        if ($leaseInfo.lease_expired -or (-not $leaseInfo.lease_file_exists)) {
            if ($lockAge -gt 30) {
                $lockIsStale = $true
            }
        }

        # Also stale if lease exists but PID is dead and lock > 5 minutes old
        if (-not $lockIsStale -and ($leaseInfo.lease_pid_alive -eq $false)) {
            if ($lockAge -gt 5) {
                $lockIsStale = $true
            }
        }

        $leaseInfo.lock_is_stale = $lockIsStale

        if ($lockIsStale -and -not $DryRun) {
            try {
                Remove-Item $LockFile -Force -ErrorAction Stop
                $leaseInfo.lock_removed = $true
                Log "Removed stale lock file (age=${lockAge}m)"
            }
            catch {
                FLog "WARNING: Could not remove stale lock: $_"
                $leaseInfo.attention_evidence += "Stale lock removal failed: $_"
                $leaseInfo.controller_attention_required = $true
            }
        }
        elseif ($lockIsStale -and $DryRun) {
            FLog "[DRY-RUN] Would remove stale lock file (age=${lockAge}m)"
        }
    }

    return $leaseInfo
}

# -- 3. Compare observed vs accepted state --
function CompareObservedVsAccepted {
    FLog "Phase 3: Comparing observed vs accepted state..."
    $comparison = @{
        observed_reachability     = $null
        accepted_reachability     = $null
        conflict_detected         = $false
        controller_attention_required = $false
        attention_evidence        = @()
    }

    $currentState = SafeReadJson $CurrentState
    if ($currentState -and $currentState.runtime_state) {
        $comparison.accepted_reachability = $currentState.runtime_state.reachability_status
    }

    # Runtime reachability is observed by the probe (see runtime_probe.ps1).
    # The reconciler itself does NOT probe -- it records the latest observed
    # state if the probe file exists.
    $runtimeLatestPath = Join-Path $ProjectRoot (Join-Path "ops" (Join-Path "runtime" "latest.json"))
    if (Test-Path $runtimeLatestPath) {
        $probe = SafeReadJson $runtimeLatestPath
        if ($probe) {
            # Derive a coarse reachability summary
            $okCount = 0
            $failCount = 0
            if ($probe.services) {
                foreach ($svc in $probe.services.PSObject.Properties) {
                    $s = $svc.Value
                    if ($s.status -and ($s.status -match "^healthy$|^running$|^reachable$|^reachable_")) {
                        $okCount++
                    }
                    else {
                        $failCount++
                    }
                }
            }
            if ($failCount -eq 0 -and $okCount -gt 0) {
                $comparison.observed_reachability = "all_healthy"
            }
            elseif ($okCount -gt 0) {
                $comparison.observed_reachability = "partially_degraded"
            }
            else {
                $comparison.observed_reachability = "unreachable"
            }

            # Conflict detection
            if ($comparison.accepted_reachability -and
                $comparison.observed_reachability -ne $null) {
                $accepted = $comparison.accepted_reachability
                $observed = $comparison.observed_reachability

                # If accepted says "ready" but observed says "unreachable", conflict
                if ($accepted -match "ready" -and $observed -eq "unreachable") {
                    $comparison.conflict_detected = $true
                    $comparison.controller_attention_required = $true
                    $comparison.attention_evidence += "Accepted reachability='$accepted' but observed='$observed'. Accepted state may be stale."
                }

                # If accepted says "not_ready" but observed says "all_healthy", conflict
                if ($accepted -match "not.*ready" -and $observed -eq "all_healthy") {
                    $comparison.conflict_detected = $true
                    $comparison.controller_attention_required = $true
                    $comparison.attention_evidence += "Accepted reachability='$accepted' but observed='$observed'. Accepted state may be stale."
                }
            }
        }
    }

    return $comparison
}

# -- 4. Write observed state --
function WriteObservedState($bridgeResults, $leaseInfo, $comparison) {
    FLog "Phase 4: Writing observed state..."

    $now = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"

    # Build state_counts map from results
    $stateCounts = @{}
    foreach ($r in $bridgeResults) {
        $s = $r.state
        if ($stateCounts.ContainsKey($s)) { $stateCounts[$s] = $stateCounts[$s] + 1 }
        else { $stateCounts[$s] = 1 }
    }

    $terminalCount = ($bridgeResults | Where-Object { $_.state -in @("completed","failed","timeout","consumed") }).Count
    $activeCount   = ($bridgeResults | Where-Object { $_.state -in @("running","dispatched","queued") }).Count
    $unreadable    = ($bridgeResults | Where-Object { $_.state -eq "unreadable" }).Count
    $otherCount    = $bridgeResults.Count - $terminalCount - $activeCount - $unreadable

    $observed = @{
        schema_version      = 1
        observed_at         = $now
        reconciler_version  = "v1"
        mode                = $(if ($DryRun) { "dry_run" } else { "live" })

        bridge_runs_summary = @{
            total_scanned   = $bridgeResults.Count
            terminal_count  = $terminalCount
            active_count    = $activeCount
            unreadable      = $unreadable
            other_count     = $otherCount
            state_counts    = $stateCounts
            recent_10       = $bridgeResults | Select-Object -First 10
        }

        lease_and_lock    = $leaseInfo

        state_comparison   = $comparison

        controller_attention_required = $(
            $leaseInfo.controller_attention_required -or
            $comparison.controller_attention_required
        )

        attention_evidence = [array]@( @(
            $leaseInfo.attention_evidence
            $comparison.attention_evidence
        ) | Where-Object { $_ -ne $null -and $_ -ne "" } )
    }

    if (-not $DryRun) {
        Write-JsonUtf8NoBom -Object $observed -Path $ObservedState -Depth 5
        FLog "Observed state written to $ObservedState"
    }
    else {
        FLog "[DRY-RUN] Would write observed state to $ObservedState"
    }

    return $observed
}

# -- Main --
Log "=== Control Plane Reconciler ==="
Log "Mode: $(if ($DryRun) { 'DRY-RUN' } else { 'LIVE' })"

$bridgeResults = ReconcileBridgeRuns
$leaseInfo     = ReconcileLease
$comparison    = CompareObservedVsAccepted
$observed      = WriteObservedState $bridgeResults $leaseInfo $comparison

# -- Summary --
Log "--- Summary ---"
Log "Bridge runs scanned: $($bridgeResults.Count)"
Log "  Terminal: $(($bridgeResults | Where-Object { $_.state -in @('completed','failed','timeout','consumed') }).Count)"
Log "  Active:   $(($bridgeResults | Where-Object { $_.state -in @('running','dispatched','queued') }).Count)"
Log "Lease status: $($leaseInfo.lease_status) (expired=$($leaseInfo.lease_expired))"
Log "Lock stale: $($leaseInfo.lock_is_stale) removed=$($leaseInfo.lock_removed)"
Log "State conflict: $($comparison.conflict_detected)"
Log "Controller attention required: $($observed.controller_attention_required)"

if ($observed.controller_attention_required) {
    Log "Attention evidence:"
    foreach ($ev in $observed.attention_evidence) {
        Log "  - $ev"
    }
}

# -- 5. Generate compact PM snapshot --
$snapshotScript = Join-Path $ProjectRoot "scripts/ops/write_pm_control_snapshot.ps1"
if (Test-Path $snapshotScript) {
    try {
        if ($DryRun) {
            Log "[DRY-RUN] Invoking snapshot generator (dry-run)..."
            & $snapshotScript -DryRun
        } else {
            Log "Phase 5: Generating compact PM snapshot..."
            & $snapshotScript
        }
    }
    catch {
        Log "WARNING: Compact snapshot generation failed: $_"
    }
}
else {
    Log "WARNING: Snapshot script not found at $snapshotScript"
}

Log "=== Reconciler complete ==="
