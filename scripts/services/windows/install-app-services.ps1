param(
    [string]$RepoRoot = "D:\code\IKE",
    [string]$ServicePrefix = "IKE",
    [string]$NssmPath = "C:\tools\nssm\nssm.exe",
    [string]$BindHost = "0.0.0.0",
    [int]$ApiPort = 8000,
    [int]$WebPort = 3000
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
$apiServiceName = "$ServicePrefix`Api"
$webServiceName = "$ServicePrefix`Web"
$watchdogServiceName = "$ServicePrefix`Watchdog"

& $NssmPath install $apiServiceName $python "-m uvicorn main:app --host $BindHost --port $ApiPort"
& $NssmPath set $apiServiceName AppDirectory $apiWorkdir
& $NssmPath set $apiServiceName AppStdout (Join-Path $runtimeRoot "api-service.log")
& $NssmPath set $apiServiceName AppStderr (Join-Path $runtimeRoot "api-service.log")
& $NssmPath set $apiServiceName AppRotateFiles 1
& $NssmPath set $apiServiceName Start SERVICE_AUTO_START
& sc.exe failure $apiServiceName reset= 86400 actions= restart/60000/restart/60000/restart/60000 | Out-Null
& sc.exe failureflag $apiServiceName 1 | Out-Null

& $NssmPath install $webServiceName $node $webScript
& $NssmPath set $webServiceName AppDirectory $webWorkdir
& $NssmPath set $webServiceName AppEnvironmentExtra "PORT=$WebPort" "HOSTNAME=127.0.0.1" "API_URL=http://127.0.0.1:$ApiPort" "NEXT_PUBLIC_API_URL=http://127.0.0.1:$ApiPort"
& $NssmPath set $webServiceName AppStdout (Join-Path $runtimeRoot "web-service.log")
& $NssmPath set $webServiceName AppStderr (Join-Path $runtimeRoot "web-service.log")
& $NssmPath set $webServiceName AppRotateFiles 1
& $NssmPath set $webServiceName Start SERVICE_AUTO_START
& sc.exe failure $webServiceName reset= 86400 actions= restart/60000/restart/60000/restart/60000 | Out-Null
& sc.exe failureflag $webServiceName 1 | Out-Null

& $NssmPath install $watchdogServiceName $python "$watchdogScript --mode local-process"
& $NssmPath set $watchdogServiceName AppDirectory $RepoRoot
& $NssmPath set $watchdogServiceName AppStdout (Join-Path $runtimeRoot "watchdog-service.log")
& $NssmPath set $watchdogServiceName AppStderr (Join-Path $runtimeRoot "watchdog-service.log")
& $NssmPath set $watchdogServiceName AppRotateFiles 1
& $NssmPath set $watchdogServiceName Start SERVICE_AUTO_START
& sc.exe failure $watchdogServiceName reset= 86400 actions= restart/60000/restart/60000/restart/60000 | Out-Null
& sc.exe failureflag $watchdogServiceName 1 | Out-Null

Write-Host "Installed $apiServiceName / $webServiceName / $watchdogServiceName"
