#Requires -Version 7.0
<#
.SYNOPSIS
  Offline end-to-end proof of the eval machinery: zero network, zero spend.
.DESCRIPTION
  Runs Invoke-Eval.ps1 in -Mock mode (deterministic in-process fakes: the mock
  executor returns each task's reference solution, so every score must be
  1.0), then runs the analyzer on the result. Asserts: expected run count,
  all mock scores 1.0, zero cost, summary produced. Exits 0 with
  DRYRUN-SMOKE-PASSED, or nonzero with the reason.
#>
[CmdletBinding()]
param([switch]$Keep)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$evalRoot = $PSScriptRoot
$work = Join-Path ([System.IO.Path]::GetTempPath()) ("wc-dryrun-" + (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force -Path $work | Out-Null

function Fail([string]$why) {
  Write-Host "DRYRUN-SMOKE-FAILED: $why (workdir: $work)"
  exit 1
}

# 1. Full mock pipeline
& (Join-Path $evalRoot 'Invoke-Eval.ps1') -Mock -Arms A,B,C,D -Reps 1 -ResultsDir $work *> (Join-Path $work 'eval-log.txt')
if ($LASTEXITCODE -ne 0) { Fail "Invoke-Eval -Mock exited $LASTEXITCODE (see eval-log.txt)" }

# 2. Manifest sanity
$manifest = Join-Path $work 'manifest.jsonl'
if (-not (Test-Path $manifest)) { Fail 'manifest.jsonl missing' }
$rows = @(Get-Content $manifest -Encoding UTF8 | Where-Object { $_.Trim() } | ForEach-Object { $_ | ConvertFrom-Json })
if ($rows.Count -eq 0) { Fail 'manifest empty' }
$taskIds = @($rows | ForEach-Object { $_.task_id } | Select-Object -Unique)
$arms = @($rows | ForEach-Object { $_.arm } | Select-Object -Unique)
$expected = $taskIds.Count * $arms.Count * 1
if ($rows.Count -ne $expected) { Fail "manifest rows $($rows.Count) != expected $expected" }

# 3. Mock executor returns reference solutions -> every score must be 1.0
$bad = @($rows | Where-Object { [double]$_.score -ne 1.0 })
if ($bad.Count -gt 0) { Fail "mock scores not all 1.0: $(($bad | ForEach-Object { "$($_.arm)/$($_.task_id)=$($_.score)" }) -join ', ')" }

# 4. Zero spend, zero network by construction
$spend = ($rows | Measure-Object -Property cost_usd -Sum).Sum
if ([double]$spend -ne 0.0) { Fail "mock spend not zero: $spend" }

# 5. Analyzer runs and produces the comparison table
& (Join-Path $evalRoot 'Invoke-Analyze.ps1') -ResultsDir $work *> (Join-Path $work 'analyze-log.txt')
if ($LASTEXITCODE -ne 0) { Fail "Invoke-Analyze exited $LASTEXITCODE (see analyze-log.txt)" }
$summary = Join-Path $work 'summary.md'
if (-not (Test-Path $summary)) { Fail 'summary.md missing' }
$sum = Get-Content $summary -Raw
if ($sum -notmatch 'B - A') { Fail 'summary missing B vs A comparison' }

if (-not $Keep) { Remove-Item $work -Recurse -Force }
Write-Host "DRYRUN-SMOKE-PASSED ($($rows.Count) runs, $($taskIds.Count) tasks, spend=`$0, network=none)"
exit 0
