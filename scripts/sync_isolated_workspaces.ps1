param(
    [string]$SourceRoot = "D:\code\MyAttention",
    [string[]]$DestinationRoots = @(
        "D:\code\IKE",
        "D:\code\_agent-runtimes\openclaw-workspaces\myattention-coder",
        "D:\code\_agent-runtimes\openclaw-workspaces\myattention-reviewer",
        "D:\code\_agent-runtimes\openclaw-workspaces\myattention-kimi-review"
    )
)

$ErrorActionPreference = "Stop"

$excludeDirFragments = @(
    ".git",
    ".runtime",
    ".openclaw",
    ".codex",
    ".claude",
    ".qoder",
    "memory",
    ".pytest_cache",
    "__pycache__",
    ".tmp",
    ".venv",
    "node_modules",
    ".next",
    "dist",
    "build",
    "services\api\data\qdrant",
    "services\web\.next"
)

$excludeFileFragments = @(
    "services\web\tsconfig.tsbuildinfo",
    "services\api\api.log",
    "services\api\chat_debug.log"
)

function Sync-Tree {
    param(
        [string]$From,
        [string]$To
    )

    New-Item -ItemType Directory -Force $To | Out-Null

    $args = @(
        $From,
        $To,
        "/E",
        "/R:1",
        "/W:1",
        "/NFL",
        "/NDL",
        "/NJH",
        "/NJS",
        "/NP"
    )

    $resolvedExcludeDirs = @()
    foreach ($fragment in $excludeDirFragments) {
        $resolvedExcludeDirs += (Join-Path $From $fragment)
    }

    $resolvedExcludeFiles = @()
    foreach ($fragment in $excludeFileFragments) {
        $resolvedExcludeFiles += (Join-Path $From $fragment)
    }

    if ($resolvedExcludeDirs.Count -gt 0) {
        $args += "/XD"
        $args += $resolvedExcludeDirs
    }

    if ($resolvedExcludeFiles.Count -gt 0) {
        $args += "/XF"
        $args += $resolvedExcludeFiles
    }

    & robocopy @args | Out-Host
    if ($LASTEXITCODE -gt 7) {
        throw "robocopy failed for destination $To with exit code $LASTEXITCODE"
    }
}

foreach ($destination in $DestinationRoots) {
    if ([string]::Equals((Resolve-Path $SourceRoot), (Resolve-Path $destination), [System.StringComparison]::OrdinalIgnoreCase)) {
        continue
    }
    Sync-Tree -From $SourceRoot -To $destination
}

Write-Output "sync_isolated_workspaces_ok"
