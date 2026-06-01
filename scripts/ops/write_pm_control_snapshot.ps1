# write_pm_control_snapshot.ps1
# Deterministic compact PM snapshot generator.
# No LLM. Reads accepted state and observed/runtime state, produces
# a bounded JSON snapshot for PM coordination decisions.
#
# Usage:
#   .\scripts\ops\write_pm_control_snapshot.ps1 [-DryRun] [-Verbose]
#
# Output:
#   ops/state/pm_control_state.json

param(
    [switch]$DryRun,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# -- Paths --
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$CurrentStatePath = Join-Path $ProjectRoot "ops/state/current_state.json"
$ObservedStatePath = Join-Path $ProjectRoot "ops/state/observed_state.json"
$RuntimeLatestPath = Join-Path $ProjectRoot "ops/runtime/latest.json"
$OutputPath = Join-Path $ProjectRoot "ops/state/pm_control_state.json"

# -- Helpers --
function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
    Write-Host "[$ts] $msg"
}

function VerboseLog($msg) {
    if ($Verbose) { Log "VERBOSE: $msg" }
}

function SafeReadJson($path) {
    if (Test-Path $path) {
        try { return Get-Content $path -Raw | ConvertFrom-Json -ErrorAction Stop }
        catch { Log "JSON parse failed: $path" }
    }
    return $null
}

# -- Read sources --
$accepted = SafeReadJson $CurrentStatePath
$observed = SafeReadJson $ObservedStatePath
$runtimeProbe = SafeReadJson $RuntimeLatestPath

if (-not $accepted) {
    Log "FATAL: Cannot read accepted state at $CurrentStatePath"
    exit 1
}

$now = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"

# -- 1. Accepted state fields --
$ps = $accepted.product_state
$rs = $accepted.runtime_state
$na = $accepted.next_action

$acceptedBlock = @{
    updated_at           = $accepted.updated_at
    last_real_progress_at = $accepted.last_real_progress_at
    controller_state     = if ($ps) { $ps.controller_state } else { "unknown" }
    mainline             = if ($ps) { $ps.mainline } else { "unknown" }
    active_gate          = if ($rs) { $rs.gate } else { "unknown" }
    next_action_owner    = if ($na) { $na.owner } else { "unknown" }
    next_action_action   = if ($na) { $na.action } else { "unknown" }
    next_action_stop_condition = if ($na) { $na.stop_condition } else { "unknown" }
}

# -- 2. Observed state --
$obsAttention = $false
$obsAt = $null
if ($observed) {
    $obsAttention = [bool]$observed.controller_attention_required
    $obsAt = $observed.observed_at
}

$observedBlock = @{
    observed_at   = $obsAt
    attention_flag = $obsAttention
}

# -- 3. Runtime readiness --
function SummarizeRuntime {
    if (-not $rs -or -not $rs.services) {
        return @{ summary = "unknown"; api = $false; web = $false; pg = $false; redis = $false }
    }
    $s = $rs.services

    $apiOk = $s.api -and ($s.api.status -match "^healthy")
    $webOk = $s.web -and ($s.web.status -match "^healthy")
    $pgOk  = $s.postgres -and ($s.postgres.status -match "^healthy")
    $redisOk = $s.redis -and ($s.redis.status -match "^healthy")

    $healthyCount = ($apiOk, $webOk, $pgOk, $redisOk | Where-Object { $_ }).Count
    $totalChecked = 4

    $summary = "unknown"
    if ($healthyCount -eq $totalChecked) { $summary = "healthy" }
    elseif ($healthyCount -ge 2) { $summary = "degraded" }
    elseif ($healthyCount -eq 0) { $summary = "unreachable" }
    else { $summary = "degraded" }

    return @{ summary = $summary; api = $apiOk; web = $webOk; pg = $pgOk; redis = $redisOk }
}

$rt = SummarizeRuntime

# Also check runtime probe if available
if ($runtimeProbe -and $runtimeProbe.services) {
    $probeOk = 0
    $probeTotal = 0
    foreach ($svc in $runtimeProbe.services.PSObject.Properties) {
        $probeTotal++
        $sv = $svc.Value
        if ($sv.status -and ($sv.status -match "^healthy|^reachable")) {
            $probeOk++
        }
    }
    if ($probeTotal -gt 0) {
        if ($probeOk -eq $probeTotal) { $rt.summary = "healthy" }
        elseif ($probeOk -eq 0) { $rt.summary = "unreachable" }
        elseif ($rt.summary -eq "unknown") { $rt.summary = "degraded" }
    }
}

$runtimeBlock = @{
    summary      = $rt.summary
    api_healthy  = $rt.api
    web_healthy  = $rt.web
    postgres_healthy = $rt.pg
    redis_healthy = $rt.redis
    gate         = if ($rs) { $rs.gate } else { "unknown" }
}

# -- 4. Review absorption --
$rvs = $accepted.review_state
$reviewPending = $false
$reviewPackage = $null
if ($rvs) {
    $rvsStatus = $rvs.status
    if ($rvsStatus -and ($rvsStatus -match "pending|unabsorbed|in_progress")) {
        $reviewPending = $true
    }
    if ($rvs.open_findings_to_absorb) {
        if ($rvs.open_findings_to_absorb.Count -gt 0) {
            $reviewPending = $true
        }
    }
    $reviewPackage = $rvs.current_package
}

$reviewBlock = @{
    pending         = $reviewPending
    current_package = $reviewPackage
}

# -- 5. Dirty tree gate --
$dts = $accepted.dirty_tree_state
$dirtyTreeBlock = @{
    new_feature_coding_allowed = if ($dts) { [bool]$dts.new_feature_coding_allowed } else { $false }
    status                     = if ($dts) { $dts.status } else { "unknown" }
}

# -- 6. Runner availability --
# Map next_action to needed runner roles. Active action owner is typically codex-controller.
# Determine which runners are actually available for the active next action.
$runnersAvailable = $true
$unavailableRunners = @()

# Parse active action text to infer needed runner roles
$activeActionText = if ($na) { $na.action } else { "" }
$neededRunners = @("codex-controller")

# If action mentions operator/test-runner/dispatch, add them
if ($activeActionText -match "operator|dispatch|runtime") {
    $neededRunners += "openclaw-ike-operator", "claude-code-runtime-operator"
}
if ($activeActionText -match "test|smoke|browser|E2E|validation") {
    $neededRunners += "claude-code-test-runner"
}

# Check registry for runner health summary
$runnerSummary = @{}
if ($accepted.runner_state -and $accepted.runner_state.health_summary) {
    $hs = $accepted.runner_state.health_summary
    foreach ($prop in $hs.PSObject.Properties) {
        $status = $prop.Value
        $isAvailable = $true
        if ($status -match "unavailable|blocked|error|failed|invalid") {
            $isAvailable = $false
        }
        $runnerSummary[$prop.Name] = $isAvailable
    }
}

# Map registry names to runner IDs we check
$idMap = @{
    "codex-controller" = "codex_controller"
    "openclaw-ike-operator" = "openclaw_ike_operator"
    "claude-code-runtime-operator" = "claude_code_runtime_operator"
    "claude-code-test-runner" = "claude_code_test_runner"
}

foreach ($rid in $neededRunners) {
    $summaryKey = $idMap[$rid]
    if ($summaryKey -and $runnerSummary.ContainsKey($summaryKey)) {
        if (-not $runnerSummary[$summaryKey]) {
            $runnersAvailable = $false
            $unavailableRunners += $rid
        }
    }
}

$runnerBlock = @{
    required_for_active_action = $neededRunners
    all_available              = $runnersAvailable
    unavailable                = $unavailableRunners
}

# -- 7. Decision hint --
$escalationNeeded = $obsAttention -or
    ($rt.summary -eq "unreachable") -or
    ($reviewPending -and $na -and $na.owner -eq "codex-controller") -or
    (-not $runnersAvailable)

$decisionBlock = @{
    read_compact_only   = (-not $escalationNeeded)
    escalation_needed   = $escalationNeeded
}

# -- Assemble --
$snapshot = [ordered]@{
    schema_version          = 1
    pm_control_state_version = 1
    generated_at            = $now
    generator               = "write_pm_control_snapshot.ps1"
    accepted_state          = $acceptedBlock
    observed_state          = $observedBlock
    runtime_readiness       = $runtimeBlock
    review_absorption       = $reviewBlock
    dirty_tree_gate         = $dirtyTreeBlock
    runner_availability     = $runnerBlock
    decision_hint           = $decisionBlock
}

$json = $snapshot | ConvertTo-Json -Depth 5

if (-not $DryRun) {
    # Write UTF-8 without BOM (Windows PowerShell 5.1 compatible)
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($OutputPath, $json, $utf8NoBom)
    Log "Snapshot written to $OutputPath"
} else {
    Log "[DRY-RUN] Would write snapshot to $OutputPath"
    Log "Snapshot content:"
    Log $json
}

Log "=== PM control snapshot complete ==="
