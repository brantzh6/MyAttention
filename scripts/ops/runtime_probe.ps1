# runtime_probe.ps1
# Lightweight runtime reachability probe. No model / no LLM.
# Runs every 10 minutes. Observation only; no restart or mutation.
#
# Probes: Web, API, Redis, Postgres.
# Writes machine-readable result to ops/runtime/latest.json.

param(
    [switch]$DryRun,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$WarningPreference = "Continue"

# Paths
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$RuntimeDir  = Join-Path $ProjectRoot (Join-Path "ops" "runtime")
$OutputFile  = Join-Path $RuntimeDir "latest.json"

if (-not (Test-Path $RuntimeDir)) {
    New-Item -Path $RuntimeDir -ItemType Directory -Force | Out-Null
}

$ApiUrl  = "http://127.0.0.1:8000"
$WebUrl  = "http://127.0.0.1:3000"
$RedisH  = "127.0.0.1"
$RedisP  = 6379
$PgH     = "127.0.0.1"
$PgP     = 5432
$PgSvc   = "MyAttentionPostgres"
$TO      = 5

function LogMsg($msg) {
    $ts = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
    Write-Output "[$ts] $msg"
}

function VLog($msg) {
    if ($Verbose) { LogMsg $msg }
}

function ProbeHttp($url, $path) {
    $fullUrl = "$url$path"
    try {
        $r = Invoke-WebRequest -Uri $fullUrl -Method Get -TimeoutSec $TO -UseBasicParsing -ErrorAction Stop
        return @{ status="healthy"; code=$r.StatusCode; url=$fullUrl; content=$r.Content }
    }
    catch {
        $code = $null
        if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
        return @{ status="unreachable"; code=$code; url=$fullUrl; error=$_.Exception.Message }
    }
}

function HasMarker($content, $marker) {
    if (-not $content) { return $false }
    return $content -match [regex]::Escape($marker)
}

function Classify-WebStatus($rootReachable, $controlReachable, $bothMarkers) {
    # Extracted pure decision function for testability.
    # Behaviour is identical to the previous inline logic.
    $webStatus = "unreachable"
    if ($rootReachable) {
        if ($controlReachable -and $bothMarkers) {
            $webStatus = "healthy"
        }
        else {
            $webStatus = "degraded"
        }
    }
    return $webStatus
}

function ProbeWebWithControl($webUrl, $timeoutSec) {
    $rootProbe = ProbeHttp $webUrl "/"
    $rootReachable = $rootProbe.status -eq "healthy"
    $rootCode = $rootProbe.code

    $controlProbe = ProbeHttp $webUrl "/control"
    $controlReachable = $controlProbe.status -eq "healthy"
    $controlCode = $controlProbe.code

    $hasFileDerived = HasMarker $controlProbe.content "file_derived"
    $hasPmWatchDigest = HasMarker $controlProbe.content "PM Watch Digest"
    $bothMarkers = $hasFileDerived -and $hasPmWatchDigest

    $webStatus = Classify-WebStatus $rootReachable $controlReachable $bothMarkers

    return @{
        web_status           = $webStatus
        root_reachable       = $rootReachable
        root_code            = $rootCode
        root_url             = $rootProbe.url
        control_reachable    = $controlReachable
        control_code         = $controlCode
        control_url          = $controlProbe.url
        marker_file_derived  = $hasFileDerived
        marker_pm_watch_digest = $hasPmWatchDigest
        both_markers_present = $bothMarkers
    }
}

function ProbeTcp($tHost, $tPort, $tMs) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $res = $tcp.BeginConnect($tHost, $tPort, $null, $null)
        $ok = $res.AsyncWaitHandle.WaitOne($tMs)
        if ($ok) { $tcp.EndConnect($res); $tcp.Close(); return @{ status="reachable"; target_host=$tHost; target_port=$tPort } }
        else { $tcp.Close(); return @{ status="timeout"; target_host=$tHost; target_port=$tPort } }
    }
    catch { return @{ status="unreachable"; target_host=$tHost; target_port=$tPort; error=$_.Exception.Message } }
}

function ProbeSvc($svcName) {
    try {
        $s = Get-Service -Name $svcName -ErrorAction Stop
        $st = if ($s.Status -eq "Running") { "running" } else { "stopped" }
        return @{ status=$st; service_name=$svcName; windows_status=$s.Status.ToString() }
    }
    catch { return @{ status="not_found"; service_name=$svcName; error=$_.Exception.Message } }
}

function ProbeRedis($rHost, $rPort) {
    $tcp = ProbeTcp $rHost $rPort 5000
    if ($tcp.status -eq "reachable") {
        try {
            $c = New-Object System.Net.Sockets.TcpClient($rHost, $rPort)
            $st = $c.GetStream()
            $pb = [System.Text.Encoding]::ASCII.GetBytes("*1`r`n`$4`r`nPING`r`n")
            $st.Write($pb, 0, $pb.Length); $st.Flush()
            Start-Sleep -Milliseconds 200
            $buf = New-Object byte[] 64
            $n = $st.Read($buf, 0, 64)
            $resp = [System.Text.Encoding]::ASCII.GetString($buf, 0, $n).Trim()
            $c.Close()
            if ($resp -match "\+PONG") { $tcp.status="healthy"; $tcp.response=$resp }
            else { $tcp.status="reachable_no_pong"; $tcp.response=$resp }
        }
        catch { $tcp.status="reachable_ping_failed"; $tcp.error=$_.Exception.Message }
    }
    return $tcp
}

# Run probes
# Do not execute live probe when dot-sourced for tests.
if ($MyInvocation.MyCommand.Path -eq $null) { return }

LogMsg "=== Runtime Probe ==="
$now = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"

$apiR   = ProbeHttp $ApiUrl "/health"
$webProbe = ProbeWebWithControl $WebUrl $TO
$webR = @{
    status = $webProbe.web_status
    root_reachable       = $webProbe.root_reachable
    root_code            = $webProbe.root_code
    root_url             = $webProbe.root_url
    control_reachable    = $webProbe.control_reachable
    control_code         = $webProbe.control_code
    control_url          = $webProbe.control_url
    marker_file_derived  = $webProbe.marker_file_derived
    marker_pm_watch_digest = $webProbe.marker_pm_watch_digest
    both_markers_present = $webProbe.both_markers_present
}
$redisR = ProbeRedis $RedisH $RedisP
$pgTcpR = ProbeTcp $PgH $PgP 5000
$pgSvcR = ProbeSvc $PgSvc

$pgResult = @{
    status = $pgSvcR.status
    target_host = $PgH
    target_port = $PgP
    service_check = $pgSvcR
    tcp_check = $pgTcpR
}
if ($pgSvcR.status -eq "not_found") { $pgResult.status = $pgTcpR.status; $pgResult.service_check = $null }

$services = @{ api=$apiR; web=$webR; redis=$redisR; postgres=$pgResult }

$hc = 0; $tc = 4
$hasDegraded = $false
foreach ($e in $services.GetEnumerator()) {
    $v = $e.Value
    $s = ""
    if ($v.status) { $s = $v.status }
    elseif ($v.tcp_check -and $v.tcp_check.status) { $s = $v.tcp_check.status }
    if ($s -match "^healthy$|^running$|^reachable$|^reachable_") { $hc++ }
    if ($s -eq "degraded") { $hasDegraded = $true }
}

$overall = "unknown"
if ($hasDegraded) { $overall = "degraded" }
elseif ($hc -eq $tc) { $overall = "all_healthy" }
elseif ($hc -ge 3) { $overall = "mostly_healthy" }
elseif ($hc -ge 1) { $overall = "partially_degraded" }
else { $overall = "unreachable" }

$result = @{
    schema_version = 1
    probed_at = $now
    probe_version = "v1"
    mode = $(if ($DryRun) { "dry_run" } else { "live" })
    overall_reachability = $overall
    services = $services
    summary = @{ healthy_count = $hc; total_count = $tc }
}

if (-not $DryRun) {
    # Write UTF-8 without BOM (Windows PowerShell 5.1 compatible)
    $json = $result | ConvertTo-Json -Depth 5
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    $dir = Split-Path -Parent $OutputFile
    if (-not (Test-Path $dir)) { New-Item -Path $dir -ItemType Directory -Force | Out-Null }
    [System.IO.File]::WriteAllText($OutputFile, $json, $utf8NoBom)
    LogMsg "Probe result written to $OutputFile"
}
else {
    LogMsg "[DRY-RUN] Would write probe result to $OutputFile"
}

LogMsg "--- Probe Summary ---"
LogMsg "API:      $($apiR.status) ($($apiR.url))"
LogMsg "Web:      $($webR.status) (root=$($webProbe.root_url) control=$($webProbe.control_url))"
LogMsg "Redis:    $($redisR.status) ($($redisR.target_host):$($redisR.target_port))"
LogMsg "Postgres: $($pgResult.status) ($($PgH):$($PgP))"
LogMsg "Overall:  $overall"
LogMsg "=== Probe complete ==="
