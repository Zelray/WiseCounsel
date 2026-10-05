#Requires -Version 7.0
<#
.SYNOPSIS
  Install the WiseCounsel skill into OpenCode and/or Claude Code skill dirs.
.DESCRIPTION
  Validates the roster config, optionally checks every model id against the
  live OpenRouter catalog, checks for an API key, then copies the whole
  wise-counsel package to the skill directories. Never prints the key.
.EXAMPLE
  pwsh -File scripts\Install-WiseCounsel.ps1                  # both harnesses
  pwsh -File scripts\Install-WiseCounsel.ps1 -OpenCode -SkipValidation
#>
[CmdletBinding()]
param(
  [switch]$OpenCode,
  [switch]$Claude,
  [switch]$SkipValidation
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$pkg = Join-Path $repo 'wise-counsel'
if (-not (Test-Path -LiteralPath (Join-Path $pkg 'SKILL.md'))) { Write-Host "ERROR: skill package not found at $pkg"; exit 1 }

if (-not $OpenCode -and -not $Claude) { $OpenCode = $true; $Claude = (Test-Path -LiteralPath "$HOME\.claude") }

# --- config sanity -------------------------------------------------------------
$cfgPath = Join-Path $pkg 'config\WiseCounsel.json'
$cfg = Get-Content -LiteralPath $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json
$count = @($cfg.models).Count
if ($count -lt $cfg.minModels -or $count -gt $cfg.maxModels) {
  Write-Host "ERROR: roster has $count models; must be between $($cfg.minModels) and $($cfg.maxModels)"; exit 1
}
Write-Host "Roster: $count models ($($cfg.models.family -join ', '))"

# --- live catalog check --------------------------------------------------------
if (-not $SkipValidation) {
  try {
    $catalog = (Invoke-RestMethod -Uri 'https://openrouter.ai/api/v1/models' -TimeoutSec 60).data
    $ids = @{}; foreach ($c in $catalog) { $ids[$c.id] = $true }
    foreach ($m in $cfg.models) {
      if ($ids.ContainsKey($m.id)) { Write-Host "  OK      $($m.id)" }
      else { Write-Host "  UNKNOWN $($m.id)  <- not in live catalog; fix or remove" }
    }
  } catch {
    Write-Host "  (could not reach OpenRouter catalog: $($_.Exception.Message) — skipping validation)"
  }
}

# --- key presence (presence only, never the value) ------------------------------
$hasKey = $false
if ($env:OPENROUTER_API_KEY) { $hasKey = $true }
elseif (Test-Path -LiteralPath (Join-Path $HOME '.openrouter-client.key')) { $hasKey = $true }
Write-Host "OpenRouter key present: $hasKey $(if (-not $hasKey) { '(skill will fail until one exists)' })"

# --- install --------------------------------------------------------------------
$targets = @()
if ($OpenCode) { $targets += Join-Path $HOME '.config\opencode\skills\wise-counsel' }
if ($Claude) { $targets += Join-Path $HOME '.claude\skills\wise-counsel' }
foreach ($t in $targets) {
  New-Item -ItemType Directory -Force -Path $t | Out-Null
  Copy-Item -LiteralPath (Join-Path $pkg 'SKILL.md') -Destination $t -Force
  foreach ($sub in 'config', 'scripts') {
    New-Item -ItemType Directory -Force -Path (Join-Path $t $sub) | Out-Null
    Copy-Item -Path (Join-Path $pkg "$sub\*") -Destination (Join-Path $t $sub) -Recurse -Force
  }
  Write-Host "Installed: $t"
}

Write-Host ""
Write-Host "Done. Use it by saying: 'wise counsel' / 'council this' before a big task."
Write-Host "Rosters can be switched with the -Preset flag (balanced-six, free-six, pair-minimum)."
