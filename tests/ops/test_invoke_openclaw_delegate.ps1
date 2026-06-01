<#
.SYNOPSIS
  Focused tests for invoke_openclaw_delegate.ps1.

.DESCRIPTION
  Tests:
  1. Fresh dispatch generates a valid GUID for --session-id (dry-run).
  2. Resume without explicit --session-id fails.
  3. Resume with explicit --session-id renders the supplied value.
  4. Multiple fresh dispatches produce distinct session IDs.
  5. --agent and --message are always present in rendered args.
  6. Message containing spaces remains one argument (not split).
  7. Message containing embedded double quotes is rejected before launch.

  All tests use -DryRun so no model call is launched.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "..\..\scripts\ops\invoke_openclaw_delegate.ps1"
$testsPassed = 0
$testsFailed = 0
$totalTests = 7

function Write-TestResult {
    param([string]$Name, [bool]$Passed, [string]$Detail = "")
    if ($Passed) {
        $script:testsPassed++
        Write-Host "  PASS $Name" -ForegroundColor Green
    } else {
        $script:testsFailed++
        Write-Host "  FAIL $Name - $Detail" -ForegroundColor Red
    }
}

Write-Host "`n=== invoke_openclaw_delegate.ps1 - Focused Tests ===`n"

# -- Test 1: Fresh dispatch generates a valid GUID --------------------
Write-Host "[Test 1] Fresh dispatch generates a valid --session-id GUID..."
$output1 = & $scriptPath -AgentId "test-agent" -Message "hello" -DryRun 2>&1
$json1 = $output1 | Where-Object { $_.TrimStart().StartsWith("{") } | ConvertFrom-Json
$guid1 = $json1.session_id

$isValidGuid1 = [guid]::TryParse($guid1, [ref]([guid]::Empty))
Write-TestResult -Name "Fresh GUID is valid" -Passed $isValidGuid1 -Detail "got '$guid1'"

# -- Test 2: Resume without explicit --session-id fails --------------
Write-Host "`n[Test 2] Resume without --session-id aborts..."
$exitCode2 = 0
try {
    $output2 = & $scriptPath -AgentId "test-agent" -Message "continue" -Resume -DryRun 2>&1
    $exitCode2 = $LASTEXITCODE
} catch {
    $exitCode2 = 1
}

$resumeGuard = ($exitCode2 -ne 0)
Write-TestResult -Name "Resume guard blocks missing session-id" -Passed $resumeGuard -Detail "exit code $exitCode2"

# -- Test 3: Resume with explicit --session-id renders the value -----
Write-Host "`n[Test 3] Resume with --session-id renders the supplied value..."
$explicitGuid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
$output3 = & $scriptPath -AgentId "test-agent" -Message "continue" -Resume -SessionId $explicitGuid -DryRun 2>&1
$json3 = $output3 | Where-Object { $_.TrimStart().StartsWith("{") } | ConvertFrom-Json
$guid3 = $json3.session_id

$guidMatch = ($guid3 -eq $explicitGuid)
Write-TestResult -Name "Resume renders explicit session-id" -Passed $guidMatch -Detail "expected '$explicitGuid', got '$guid3'"

# -- Test 4: Multiple fresh dispatches produce distinct GUIDs --------
Write-Host "`n[Test 4] Multiple fresh dispatches produce distinct session IDs..."
$output4a = & $scriptPath -AgentId "test-agent" -Message "hello" -DryRun 2>&1
$json4a = $output4a | Where-Object { $_.TrimStart().StartsWith("{") } | ConvertFrom-Json
$output4b = & $scriptPath -AgentId "test-agent" -Message "hello" -DryRun 2>&1
$json4b = $output4b | Where-Object { $_.TrimStart().StartsWith("{") } | ConvertFrom-Json

$distinct = ($json4a.session_id -ne $json4b.session_id)
Write-TestResult -Name "Fresh GUIDs are distinct across calls" -Passed $distinct -Detail "$($json4a.session_id) vs $($json4b.session_id)"

# -- Test 5: --agent and --message always present in rendered args ---
Write-Host "`n[Test 5] --agent and --message always present in rendered args..."
$argAgent = $json1.args -contains "test-agent"
$argSession = $json1.args -contains $guid1
$argMessage = $json1.args -contains "hello"

$allPresent = ($argAgent -and $argSession -and $argMessage)
Write-TestResult -Name "Required args present (--agent, --session-id, --message)" -Passed $allPresent -Detail "agent=$argAgent session=$argSession message=$argMessage"

# -- Test 6: Message containing spaces remains one argument ----------
Write-Host "`n[Test 6] Message containing spaces remains one argument..."
$spacedMessage = "run audit with spaces in message"
$output6 = & $scriptPath -AgentId "test-agent" -Message $spacedMessage -DryRun 2>&1
$json6 = $output6 | Where-Object { $_.TrimStart().StartsWith("{") } | ConvertFrom-Json

# Check that the spaced message appears as a single element in args array
$spacedInArgs = $json6.args -contains $spacedMessage
# Check that escaped string has the message properly quoted
$escapedHasQuotes = $json6.args_escaped -match '"run audit with spaces in message"'
$spacePreserved = ($spacedInArgs -and $escapedHasQuotes)
Write-TestResult -Name "Spaced message preserved as single argument" -Passed $spacePreserved -Detail "in_args=$spacedInArgs escaped_correct=$escapedHasQuotes"

# -- Test 7: Message containing embedded double quotes is rejected ----
Write-Host "`n[Test 7] Message containing embedded double quotes is rejected..."
$quotedMessage = 'message with "quoted text" inside'
$exitCode7 = 0
try {
    $output7 = & $scriptPath -AgentId "test-agent" -Message $quotedMessage -DryRun 2>&1
    $exitCode7 = $LASTEXITCODE
} catch {
    $exitCode7 = 1
}

# Quoted message must fail before launch (non-zero exit code)
$quoteRejected = ($exitCode7 -ne 0)
Write-TestResult -Name "Quoted message rejected before launch" -Passed $quoteRejected -Detail "exit code $exitCode7 (expected non-zero)"

# -- Summary ---------------------------------------------------------
Write-Host "`n=== Results: $testsPassed/$totalTests passed, $testsFailed failed ===`n"

if ($testsFailed -gt 0) {
    Write-Host "TESTS FAILED" -ForegroundColor Red
    exit 1
} else {
    Write-Host "ALL TESTS PASSED" -ForegroundColor Green
    exit 0
}
