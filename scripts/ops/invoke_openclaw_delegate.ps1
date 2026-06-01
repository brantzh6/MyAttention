<#
.SYNOPSIS
  Invoke an OpenClaw delegate with mandatory unique session isolation.

.DESCRIPTION
  Controller-authored dispatch helper that:
  - Requires an explicit --agent <id> and --message <text>
  - Generates a fresh GUID for --session-id by default (isolated turn)
  - Supports --resume to continue an existing session when explicitly intended
  - Always invokes: openclaw.cmd agent --agent <id> --session-id <guid> ...
  - Supports --dry-run to render the full argument list without launching a model call
  - Supports --stdout-file / --stderr-file to capture observable output paths

.EXAMPLE
  # Fresh isolated dispatch
  .\invoke_openclaw_delegate.ps1 -AgentId "ike-pm" -Message "run audit"

  # Resume an existing session
  .\invoke_openclaw_delegate.ps1 -AgentId "ike-pm" -Message "continue" -Resume -SessionId "existing-guid"

  # Dry-run to inspect rendered args (no model call)
  .\invoke_openclaw_delegate.ps1 -AgentId "ike-pm" -Message "run audit" -DryRun
#>
[CmdletBinding(DefaultParameterSetName = "Fresh")]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$AgentId,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Message,

    [Parameter(ParameterSetName = "Resume")]
    [switch]$Resume,

    [Parameter(ParameterSetName = "Resume")]
    [ValidateNotNullOrEmpty()]
    [string]$SessionId,

    [Parameter(ParameterSetName = "Fresh")]
    [Parameter(ParameterSetName = "Resume")]
    [switch]$DryRun,

    [Parameter(ParameterSetName = "Fresh")]
    [Parameter(ParameterSetName = "Resume")]
    [string]$StdoutFile,

    [Parameter(ParameterSetName = "Fresh")]
    [Parameter(ParameterSetName = "Resume")]
    [string]$StderrFile,

    [Parameter(ParameterSetName = "Fresh")]
    [Parameter(ParameterSetName = "Resume")]
    [string]$Model,

    [Parameter(ParameterSetName = "Fresh")]
    [Parameter(ParameterSetName = "Resume")]
    [switch]$Stream
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -- Validate message for quote boundary ------------------------------
# Embedded double quotes are rejected because openclaw.cmd introduces
# cmd.exe re-parsing, which makes quote escaping unreliable.
# Controller packets should use quote-free message text pointing to
# file-backed task packets instead.
if ($Message -match '"') {
    Write-Error "[invoke_openclaw_delegate] Message contains embedded double quotes, which are not supported due to cmd.exe re-parsing risk. Use quote-free message text pointing to a file-backed task packet instead. Aborting."
    exit 1
}

# -- Resolve session ID ----------------------------------------------
$effectiveSessionId = $null

if ($Resume) {
    # Resume mode: session ID must be explicitly supplied
    if (-not $SessionId -or [string]::IsNullOrWhiteSpace($SessionId)) {
        Write-Error "[invoke_openclaw_delegate] --resume requires an explicit --session-id. Aborting."
        exit 1
    }
    $effectiveSessionId = $SessionId
} else {
    # Fresh mode: always generate a new GUID
    $effectiveSessionId = [guid]::NewGuid().ToString()
}

# -- Build argument string -------------------------------------------
$openclawCmd = "openclaw.cmd"

# Build argument list as array first for dry-run JSON output
$argArray = @(
    "agent"
    "--agent", $AgentId
    "--session-id", $effectiveSessionId
    "--message", $Message
)

if ($Model) {
    $argArray += "--model", $Model
}
if ($Stream) {
    $argArray += "--stream"
}

# Escape arguments for Windows command line:
# - Arguments containing spaces must be quoted
# - Embedded double quotes are rejected before reaching this point
function Escape-Arg($arg) {
    if ($arg -match '\s') {
        # Contains spaces - needs quoting (no embedded quotes possible here)
        return "`"$arg`""
    }
    return $arg
}

$argString = ($argArray | ForEach-Object { Escape-Arg $_ }) -join " "

# -- Dry-run / render mode -------------------------------------------
if ($DryRun) {
    $rendered = ($argArray | ForEach-Object {
        if ($_ -match '\s') { "'$_'" } else { $_ }
    }) -join " "
    Write-Host "[DRY-RUN] $openclawCmd $rendered"

    # Emit structured JSON to stdout for programmatic consumption
    $info = @{
        command      = $openclawCmd
        args         = $argArray
        args_escaped = $argString
        session_id   = $effectiveSessionId
        agent_id     = $AgentId
        mode         = $(if ($Resume) { "resume" } else { "fresh" })
        dry_run      = $true
    }
    $info | ConvertTo-Json -Depth 3
    exit 0
}

# -- Execute ---------------------------------------------------------
Write-Host "[invoke_openclaw_delegate] agent=$AgentId session=$effectiveSessionId mode=$(if($Resume){'resume'}else{'fresh'})"

# Use single escaped argument string for robust Windows invocation
$procParams = @{
    FilePath     = $openclawCmd
    ArgumentList = $argString
    NoNewWindow  = $true
    Wait         = $true
    PassThru     = $true
}

if ($StdoutFile) {
    $procParams["RedirectStandardOutput"] = $StdoutFile
}
if ($StderrFile) {
    $procParams["RedirectStandardError"] = $StderrFile
}

$process = Start-Process @procParams

if ($process.ExitCode -ne 0) {
    Write-Error "[invoke_openclaw_delegate] openclaw exited with code $($process.ExitCode)"
    exit $process.ExitCode
}

Write-Host "[invoke_openclaw_delegate] completed successfully (exit 0)"
exit 0
