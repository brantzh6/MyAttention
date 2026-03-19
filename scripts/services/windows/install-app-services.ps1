param(
    [string]$RepoRoot = "D:\code\MyAttention",
    [string]$NssmPath = "C:\tools\nssm\nssm.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $NssmPath)) {
    throw "NSSM not found: $NssmPath"
}

$runtimeRoot = Join-Path $RepoRoot ".runtime\logs"
New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null

$apiWorkdir = Join-Path $RepoRoot "services\api"
$webWorkdir = Join-Path $RepoRoot "services\web"
$python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$node = "C:\Program Files\nodejs\node.exe"
$watchdogScript = Join-Path $RepoRoot "runtime_watchdog.py"
$webScript = Join-Path $webWorkdir ".next\standalone\server.js"

& $NssmPath install MyAttentionApi $python "-m uvicorn main:app --host 0.0.0.0 --port 8000"
& $NssmPath set MyAttentionApi AppDirectory $apiWorkdir
& $NssmPath set MyAttentionApi AppStdout (Join-Path $runtimeRoot "api-service.log")
& $NssmPath set MyAttentionApi AppStderr (Join-Path $runtimeRoot "api-service.log")
& $NssmPath set MyAttentionApi AppRotateFiles 1
& $NssmPath set MyAttentionApi Start SERVICE_DEMAND_START

& $NssmPath install MyAttentionWeb $node $webScript
& $NssmPath set MyAttentionWeb AppDirectory $webWorkdir
& $NssmPath set MyAttentionWeb AppEnvironmentExtra "PORT=3000" "HOSTNAME=127.0.0.1" "API_URL=http://127.0.0.1:8000" "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000"
& $NssmPath set MyAttentionWeb AppStdout (Join-Path $runtimeRoot "web-service.log")
& $NssmPath set MyAttentionWeb AppStderr (Join-Path $runtimeRoot "web-service.log")
& $NssmPath set MyAttentionWeb AppRotateFiles 1
& $NssmPath set MyAttentionWeb Start SERVICE_DEMAND_START

& $NssmPath install MyAttentionWatchdog $python "$watchdogScript --mode local-process"
& $NssmPath set MyAttentionWatchdog AppDirectory $RepoRoot
& $NssmPath set MyAttentionWatchdog AppStdout (Join-Path $runtimeRoot "watchdog-service.log")
& $NssmPath set MyAttentionWatchdog AppStderr (Join-Path $runtimeRoot "watchdog-service.log")
& $NssmPath set MyAttentionWatchdog AppRotateFiles 1
& $NssmPath set MyAttentionWatchdog Start SERVICE_DEMAND_START

Write-Host "Installed MyAttentionApi / MyAttentionWeb / MyAttentionWatchdog"
