param(
    [string]$NssmPath = "C:\tools\nssm\nssm.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $NssmPath)) {
    throw "NSSM not found: $NssmPath"
}

foreach ($service in @("MyAttentionWatchdog", "MyAttentionWeb", "MyAttentionApi")) {
    & $NssmPath stop $service confirm | Out-Null
    & $NssmPath remove $service confirm | Out-Null
}

Write-Host "Removed MyAttentionApi / MyAttentionWeb / MyAttentionWatchdog"
