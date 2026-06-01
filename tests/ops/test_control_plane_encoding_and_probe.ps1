# test_control_plane_encoding_and_probe.ps1
# Deterministic tests for UTF-8 no-BOM encoding and probe structure.
# No model calls. No network access.
# Run: powershell -NoProfile -ExecutionPolicy Bypass -File tests/ops/test_control_plane_encoding_and_probe.ps1

$ErrorActionPreference = "Stop"

$Script:PassCount = 0
$Script:FailCount = 0

function Assert-True($condition, $label) {
    if ($condition) {
        $Script:PassCount++
        Write-Output "  PASS: $label"
    } else {
        $Script:FailCount++
        Write-Output "  FAIL: $label"
    }
}

function Assert-Equal($actual, $expected, $label) {
    Assert-True ($actual -eq $expected) "$label (expected='$expected', actual='$actual')"
}

function Assert-NoBom($filePath, $label) {
    $bytes = [System.IO.File]::ReadAllBytes($filePath)
    $hasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
    Assert-True (-not $hasBom) "$label (BOM=$hasBom)"
}

function Assert-ParsableJson($filePath, $label) {
    try {
        $null = Get-Content $filePath -Raw | ConvertFrom-Json -ErrorAction Stop
        Assert-True $true "$label (valid JSON)"
    } catch {
        Assert-True $false "$label (parse error: $_)"
    }
}

# -----------------------------------------------------------
# Test suite
# -----------------------------------------------------------
Write-Output "=== Control Plane Encoding & Probe Tests ==="
$here = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$helpers = Join-Path $here "scripts/ops/ops_encoding_helpers.ps1"
$probeScript = Join-Path $here "scripts/ops/runtime_probe.ps1"
$reconcilerScript = Join-Path $here "scripts/ops/control_plane_reconciler.ps1"

# --- T1: Encoding helpers exist and can be dot-sourced ---
Write-Output "-- T1: Encoding helpers --"
Assert-True (Test-Path $helpers) "ops_encoding_helpers.ps1 exists"
$dotSourceOk = $false
try {
    . $helpers
    $dotSourceOk = $true
} catch { }
Assert-True $dotSourceOk "Helpers dot-source successfully"

# --- T2: Write-JsonUtf8NoBom writes valid JSON without BOM ---
Write-Output "-- T2: Write-JsonUtf8NoBom --"
$tmpDir = Join-Path $env:TEMP "ops_encoding_test"
if (Test-Path $tmpDir) { Remove-Item $tmpDir -Recurse -Force }
New-Item $tmpDir -ItemType Directory -Force | Out-Null
$tmpFile = Join-Path $tmpDir "test.json"

$obj = @{ name = "test"; value = 42; nested = @{ ok = $true } }
Write-JsonUtf8NoBom -Object $obj -Path $tmpFile -Depth 3

Assert-True (Test-Path $tmpFile) "Output file created"
Assert-NoBom $tmpFile "No BOM in test output"
Assert-ParsableJson $tmpFile "Valid JSON"

$parsed = Get-Content $tmpFile -Raw | ConvertFrom-Json
Assert-Equal $parsed.name "test" "Round-trip name field"
Assert-Equal $parsed.value 42 "Round-trip value field"
Assert-True $parsed.nested.ok "Round-trip nested field"

# --- T3: Test-FileHasBom helper ---
Write-Output "-- T3: Test-FileHasBom helper --"
$bomResult = Test-FileHasBom $tmpFile
Assert-True ($bomResult -eq $false) "No-BOM file reports $false"

# Create a file WITH BOM
$bomBytes = [byte[]](0xEF, 0xBB, 0xBF) + [System.Text.Encoding]::UTF8.GetBytes('{"a":1}')
$withBom = Join-Path $tmpDir "with_bom.json"
[System.IO.File]::WriteAllBytes($withBom, $bomBytes)
$bomResult2 = Test-FileHasBom $withBom
Assert-True ($bomResult2 -eq $true) "BOM file reports $true"

# --- T4: Probe script uses UTF-8 no-BOM pattern (source inspection) ---
Write-Output "-- T4: Probe script encoding pattern --"
$probeSrc = Get-Content $probeScript -Raw
$hasUtf8NoBomPattern = $probeSrc -match 'UTF8Encoding.*\(\s*\$false\s*\)'
Assert-True $hasUtf8NoBomPattern "runtime_probe.ps1 uses UTF8Encoding(false)"

$hasWriteAllText = $probeSrc -match 'WriteAllText'
Assert-True $hasWriteAllText "runtime_probe.ps1 uses WriteAllText (not Out-File -Encoding utf8)"

$hasControlProbe = $probeSrc -match 'ProbeWebWithControl|control'
Assert-True $hasControlProbe "runtime_probe.ps1 probes /control"

$hasMarkerCheck = $probeSrc -match 'file_derived'
Assert-True $hasMarkerCheck "runtime_probe.ps1 checks file_derived marker"

$hasPmWatchDigest = $probeSrc -match 'PM Watch Digest'
Assert-True $hasPmWatchDigest "runtime_probe.ps1 checks PM Watch Digest marker"

$hasDegradedLogic = $probeSrc -match 'degraded'
Assert-True $hasDegradedLogic "runtime_probe.ps1 has degraded status logic"

# --- T5: Reconciler dot-sources encoding helper ---
Write-Output "-- T5: Reconciler encoding pattern --"
$reconcilerSrc = Get-Content $reconcilerScript -Raw
$dotSourcesHelper = $reconcilerSrc -match 'ops_encoding_helpers'
Assert-True $dotSourcesHelper "Reconciler dot-sources ops_encoding_helpers.ps1"

$usesWriteJsonUtf8 = $reconcilerSrc -match 'Write-JsonUtf8NoBom'
Assert-True $usesWriteJsonUtf8 "Reconciler uses Write-JsonUtf8NoBom"

# --- T6: Write-JsonUtf8NoBom handles directory creation ---
Write-Output "-- T6: Directory creation --"
$deepPath = Join-Path $tmpDir "a/b/c/deep.json"
Write-JsonUtf8NoBom -Object @{ x = 1 } -Path $deepPath -Depth 3
Assert-True (Test-Path $deepPath) "Deep directory created and file written"
Assert-NoBom $deepPath "Deep file has no BOM"

# --- T7: Behavioral tests for Web probe classification (exercise decision logic) ---
Write-Output "-- T7: Web probe classification behavioral tests --"

# Import the probe script's Classify-WebStatus function by dot-sourcing.
# The guard at the top of runtime_probe.ps1 prevents live probe execution.
$null = . $probeScript

# Case 1: root 200 + /control 200 + both markers -> healthy
Assert-Equal (Classify-WebStatus $true $true $true) "healthy" "T7-C1: root ok, control ok, both markers => healthy"

# Case 2: root 200 + /control 200 + one marker missing -> degraded
Assert-Equal (Classify-WebStatus $true $true $false) "degraded" "T7-C2: root ok, control ok, one marker missing => degraded"

# Case 3: root 200 + /control 200 + both markers missing -> degraded
Assert-Equal (Classify-WebStatus $true $true $false) "degraded" "T7-C3: root ok, control ok, both markers missing => degraded"

# Case 4: root 200 + /control unreachable -> degraded
Assert-Equal (Classify-WebStatus $true $false $false) "degraded" "T7-C4: root ok, control unreachable => degraded"

# Case 5: root unreachable -> unreachable
Assert-Equal (Classify-WebStatus $false $false $false) "unreachable" "T7-C5: root unreachable => unreachable"

# --- Cleanup ---
Remove-Item $tmpDir -Recurse -Force -ErrorAction SilentlyContinue

# --- Summary ---
Write-Output ""
Write-Output "=== Test Summary ==="
Write-Output "Passed: $($Script:PassCount)"
Write-Output "Failed: $($Script:FailCount)"

if ($Script:FailCount -gt 0) {
    Write-Output "RESULT: FAILED"
    exit 1
}
else {
    Write-Output "RESULT: ALL PASSED"
    exit 0
}
