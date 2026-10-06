#Requires -Version 7.0
<#
.SYNOPSIS
  Freeze-manifest integrity check for the WiseCounsel eval.
.DESCRIPTION
  Creates (with -Update) or verifies (default) SHA-256 hashes for every file
  of the measured artifact (wise-counsel/) and the frozen task suite
  (eval/tasks/, eval/config.json, eval/templates/). The manifest is the
  pre-registration freeze record required by docs/EVAL-DESIGN.md; it is
  created BEFORE any evaluation data collection and never edited afterwards
  (a deliberate re-freeze after the eval would be a dated addendum, not an
  overwrite in place).
#>
[CmdletBinding()]
param(
  [switch]$Update,
  # Manifest is always explicit: no default that could silently point at a
  # dead historical freeze (the pilot manifest can never verify again).
  [Parameter(Mandatory)] [string]$ManifestPath
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$evalRoot = $PSScriptRoot
$repoRoot = Split-Path -Parent $evalRoot

$targets = @()
$targets += Get-ChildItem (Join-Path $repoRoot 'wise-counsel') -Recurse -File |
  Where-Object { $_.FullName -notmatch '\\runs\\' }
$targets += Get-ChildItem (Join-Path $evalRoot 'tasks') -File
$targets += Get-ChildItem (Join-Path $evalRoot 'templates') -File
$targets += Get-Item (Join-Path $evalRoot 'config.json')

$sortedTargets = @($targets | Sort-Object FullName)
$lines = foreach ($f in $sortedTargets) {
  $rel = $f.FullName.Substring($repoRoot.Length + 1).Replace('\', '/')
  $hash = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash
  "$hash  $rel"
}

if ($Update) {
  if (Test-Path $manifestPath) { Write-Host 'FREEZE-REFUSED: manifest already exists (re-freeze is a dated addendum, not an overwrite)'; exit 3 }
  $header = "# WiseCounsel eval freeze manifest — $((Get-Date).ToUniversalTime().ToString('o')) — SHA-256"
  $all = @($header) + @($lines)
  Set-Content -LiteralPath $manifestPath -Value $all -Encoding UTF8
  Write-Host "FREEZE-CREATED ($(@($lines).Count) files)"
  exit 0
}

if (-not (Test-Path $manifestPath)) { Write-Host 'FREEZE-MISSING: no manifest; create it with -Update BEFORE data collection'; exit 3 }
$existing = @(Get-Content $manifestPath -Encoding UTF8 | Where-Object { $_ -and -not $_.StartsWith('#') })
$now = @($lines)
if ($existing.Count -ne $now.Count) { Write-Host "FREEZE-CHANGED: file count changed (frozen $($existing.Count), now $($now.Count))"; exit 1 }
$diffs = @()
for ($i = 0; $i -lt $now.Count; $i++) { if ($now[$i] -ne $existing[$i]) { $diffs += $now[$i] } }
if ($diffs.Count -gt 0) { Write-Host 'FREEZE-CHANGED:'; $diffs; exit 1 }
Write-Host "FREEZE-INTACT ($($now.Count) files match the pre-registration freeze)"
exit 0
