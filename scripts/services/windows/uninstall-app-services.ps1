param(
    [string]$NssmPath = "C:\tools\nssm\nssm.exe",
    [string]$ServicePrefix = "IKE"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $NssmPath)) {
    throw "NSSM not found: $NssmPath"
}

foreach ($service in @(
    "$ServicePrefix" + "Watchdog",
    "$ServicePrefix" + "Web",
    "$ServicePrefix" + "Api"
)) {
    & $NssmPath stop $service confirm | Out-Null
    & $NssmPath remove $service confirm | Out-Null
}

Write-Host "Removed $ServicePrefix" + "Api / $ServicePrefix" + "Web / $ServicePrefix" + "Watchdog"
