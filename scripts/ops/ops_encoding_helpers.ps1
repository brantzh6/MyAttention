# ops_encoding_helpers.ps1
# Shared UTF-8 no-BOM encoding helpers for ops scripts.
# Compatible with PowerShell 5.1 and 7+.

$ErrorActionPreference = "Stop"

# Lazily initialised so callers can dot-source without side effects.
$Script:Utf8NoBom = [System.Text.UTF8Encoding]::new($false)

function Write-JsonUtf8NoBom {
    <#
    .SYNOPSIS
        Serialise an object to JSON and write it as UTF-8 without BOM.
    .PARAMETER Object
        Hashtable / PSCustomObject to serialise.
    .PARAMETER Path
        Target file path.
    .PARAMETER Depth
        JSON serialisation depth (default 5).
    .PARAMETER WhatIf
        Dry-run support.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [object]$Object,

        [Parameter(Mandatory = $true)]
        [string]$Path,

        [int]$Depth = 5
    )

    $json = $Object | ConvertTo-Json -Depth $Depth
    if ($PSCmdlet.ShouldProcess($Path, "Write JSON UTF-8 no-BOM")) {
        $dir = Split-Path -Parent $Path
        if ($dir -and -not (Test-Path $dir)) {
            New-Item -Path $dir -ItemType Directory -Force | Out-Null
        }
        [System.IO.File]::WriteAllText($Path, $json, $Script:Utf8NoBom)
    }
}

function Test-FileHasBom {
    <#
    .SYNOPSIS
        Check whether a file starts with a UTF-8 BOM (EF BB BF).
    .RETURNS
        $true if BOM present, $false otherwise.
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) { return $null }

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 3) { return $false }
    return ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
}
