#Requires -Version 7.0
<#
.SYNOPSIS
  Analyze a WiseCounsil eval manifest into summary tables + statistics.
.DESCRIPTION
  Implements the pre-registered analysis in docs/EVAL-DESIGN.md: paired
  task-level deltas, exact sign-flip permutation test (2^n, exhaustive up to
  n=16), 95% percentile bootstrap CI (10,000 resamples, seed 42), arm cost
  and latency, council health, and the B-vs-C question-overlap diversity
  audit. Reads ONLY eval/results/manifest.jsonl and the raw run dirs — no
  hand-typed numbers. Writes summary.md + summary.csv next to the manifest.
.EXAMPLE
  pwsh -File eval/Invoke-Analyze.ps1                       # latest experiment
  pwsh -File eval/Invoke-Analyze.ps1 -ExpId exp-20261001-120000
#>
[CmdletBinding()]
param(
  [string]$ResultsDir = '',
  [string]$ExpId = ''
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$evalRoot = $PSScriptRoot
if (-not $ResultsDir) { $ResultsDir = Join-Path $evalRoot 'results' }
$manifestPath = Join-Path $ResultsDir 'manifest.jsonl'
if (-not (Test-Path $manifestPath)) { Write-Host "ERROR: no manifest at $manifestPath"; exit 3 }

$rows = @(Get-Content $manifestPath -Encoding UTF8 | Where-Object { $_.Trim() } | ForEach-Object { $_ | ConvertFrom-Json })
if ($rows.Count -eq 0) { Write-Host 'ERROR: manifest is empty'; exit 3 }

if (-not $ExpId) {
  $ExpId = @($rows | Sort-Object ts | Select-Object -Last 1)[0].expid
}
$rows = @($rows | Where-Object { $_.expid -eq $ExpId })
if ($rows.Count -eq 0) { Write-Host "ERROR: no rows for expid $ExpId"; exit 3 }
$mock = @($rows)[0].mock

# --- per arm x task means ---------------------------------------------------------
$taskIds = @($rows | ForEach-Object { $_.task_id } | Select-Object -Unique)
$arms = @($rows | ForEach-Object { $_.arm } | Select-Object -Unique)
$mean = @{ }
foreach ($arm in $arms) {
  foreach ($t in $taskIds) {
    $cell = @($rows | Where-Object { $_.arm -eq $arm -and $_.task_id -eq $t })
    if ($cell.Count -gt 0) { $mean["$arm|$t"] = ($cell | Measure-Object -Property score -Average).Average }
  }
}

function Get-Deltas([string]$ArmX, [string]$ArmY) {
  $d = @()
  foreach ($t in $taskIds) {
    if ($mean.ContainsKey("$ArmX|$t") -and $mean.ContainsKey("$ArmY|$t")) {
      $d += $mean["$ArmX|$t"] - $mean["$ArmY|$t"]
    }
  }
  return ,@($d)
}

$rng = [System.Random]::new(42)
function Get-PermP([double[]]$deltas) {
  $n = $deltas.Count
  if ($n -eq 0) { return $null }
  $obs = [math]::Abs(($deltas | Measure-Object -Average).Average)
  if ($n -le 16) {
    $total = [math]::Pow(2, $n); $ge = 0
    for ($mask = 0; $mask -lt $total; $mask++) {
      $s = 0.0
      for ($i = 0; $i -lt $n; $i++) { $s += $(if ($mask -band (1 -shl $i)) { -$deltas[$i] } else { $deltas[$i] }) }
      if ([math]::Abs($s / $n) -ge $obs - 1e-12) { $ge++ }
    }
    return $ge / $total
  }
  $ge = 0; $trials = 10000
  for ($k = 0; $k -lt $trials; $k++) {
    $s = 0.0
    for ($i = 0; $i -lt $n; $i++) { $s += $(if ($rng.Next(2) -eq 1) { -$deltas[$i] } else { $deltas[$i] }) }
    if ([math]::Abs($s / $n) -ge $obs - 1e-12) { $ge++ }
  }
  return $ge / $trials
}

function Get-BootstrapCI([double[]]$deltas) {
  $n = $deltas.Count
  if ($n -eq 0) { return @(0.0, 0.0) }
  $means = New-Object double[] 10000
  for ($k = 0; $k -lt 10000; $k++) {
    $s = 0.0
    for ($i = 0; $i -lt $n; $i++) { $s += $deltas[$rng.Next($n)] }
    $means[$k] = $s / $n
  }
  $sorted = @($means | Sort-Object)
  return @($sorted[[int](0.025 * 10000)], $sorted[[int](0.975 * 10000) - 1])
}

# --- diversity audit: B vs C question overlap --------------------------------------
function Get-QuestionOverlap {
  $overlaps = @()
  $rawRoot = Join-Path $ResultsDir "raw\$ExpId"
  foreach ($t in $taskIds) {
    $qb = Join-Path $rawRoot "B\$t-rep1\questions.json"
    $qc = Join-Path $rawRoot "C\$t-rep1\questions.json"
    if ((Test-Path $qb) -and (Test-Path $qc)) {
      $tok = { param($file)
        $qs = @(Get-Content $file -Raw -Encoding UTF8 | ConvertFrom-Json)
        @(($qs -join ' ').ToLower() -split '[^a-z0-9]+' | Where-Object { $_.Length -gt 3 } | Select-Object -Unique)
      }
      $b = & $tok $qb; $c = & $tok $qc
      if ($b.Count -gt 0 -and $c.Count -gt 0) {
        $inter = @($b | Where-Object { $c -contains $_ }).Count
        $union = @(@($b) + @($c) | Select-Object -Unique).Count
        if ($union -gt 0) { $overlaps += $inter / $union }
      }
    }
  }
  if ($overlaps.Count -eq 0) { return $null }
  return [math]::Round(($overlaps | Measure-Object -Average).Average, 3)
}

# --- build summary -------------------------------------------------------------------
$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine("# Eval summary — $ExpId $(if ($mock) { '(MOCK)' })")
[void]$sb.AppendLine('')
[void]$sb.AppendLine("Runs: $($rows.Count) | Tasks: $($taskIds.Count) | Arms: $($arms -join ', ') | Total spend: `$$([math]::Round(($rows | Measure-Object -Property cost_usd -Sum).Sum, 4))")
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| Arm | Mean score | Task cells | Cost USD | Council/executor failures |')
[void]$sb.AppendLine('|---|---|---|---|---|')
foreach ($arm in $arms) {
  $ar = @($rows | Where-Object { $_.arm -eq $arm })
  $cells = @($taskIds | Where-Object { $mean.ContainsKey("$arm|$_") })
  $m = ($cells | ForEach-Object { $mean["$arm|$_"] } | Measure-Object -Average).Average
  $cost = ($ar | Measure-Object -Property cost_usd -Sum).Sum
  $fails = @($ar | Where-Object { $_.flags.Count -gt 0 }).Count
  [void]$sb.AppendLine("| $arm | $([math]::Round($m, 4)) | $($cells.Count) | `$$([math]::Round($cost, 4)) | $fails |")
}
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Pre-registered comparisons (paired task-level deltas, score fraction)')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| Comparison | Mean delta (pp) | 95% CI (pp) | p (sign-flip) | n tasks |')
[void]$sb.AppendLine('|---|---|---|---|---|')
foreach ($cmp in @(@('B','C'), @('B','A'), @('C','A'), @('B','E'), @('B','F'), @('E','A'), @('F','A'))) {
  $d = Get-Deltas $cmp[0] $cmp[1]
  if ($d.Count -eq 0) { continue }
  $md = ($d | Measure-Object -Average).Average
  $ci = Get-BootstrapCI ([double[]]$d)
  $p = Get-PermP ([double[]]$d)
  [void]$sb.AppendLine("| $($cmp[0]) - $($cmp[1]) | $([math]::Round(100 * $md, 2)) | [$([math]::Round(100 * $ci[0], 2)), $([math]::Round(100 * $ci[1], 2))] | $(if ($null -ne $p) { [math]::Round($p, 4) } else { 'n/a' }) | $($d.Count) |")
}
[void]$sb.AppendLine('')
$bFlags = @($rows | Where-Object { $_.arm -eq 'B' })
$cFails = @($bFlags | Where-Object { $_.flags -contains 'council-failed' }).Count
$overlap = Get-QuestionOverlap
[void]$sb.AppendLine("## Council health: $($(($bFlags.Count - $cFails) / [math]::Max(1, $bFlags.Count)) * 100)% round-1 success ($($cFails) failed of $($bFlags.Count))")
if ($null -ne $overlap) { [void]$sb.AppendLine("## Diversity audit: mean B-vs-C question-token overlap (Jaccard) = $overlap") }
[void]$sb.AppendLine('')
[void]$sb.AppendLine('_Machine-generated by eval/Invoke-Analyze.ps1; interpretation lives in docs/RESULTS.md._')

$summaryPath = Join-Path $ResultsDir 'summary.md'
Set-Content -LiteralPath $summaryPath -Value $sb.ToString() -Encoding UTF8

$csv = Join-Path $ResultsDir 'summary.csv'
$rows | Select-Object expid, arm, task_id, rep, score, passed, total, questions_asked, cost_usd, latency_ms, mock, leak |
  ForEach-Object { [pscustomobject]$_ } | Export-Csv -LiteralPath $csv -NoTypeInformation -Encoding UTF8

Write-Host "ANALYZE-OK expid=$ExpId summary=$summaryPath"
exit 0
