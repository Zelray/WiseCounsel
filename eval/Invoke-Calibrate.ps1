#Requires -Version 7.0
<#
.SYNOPSIS
  Difficulty calibration for NEW Track-1 tasks (suite construction only —
  NOT part of the measured experiment; see docs/EVAL-DESIGN.md, Difficulty
  calibration, and the wave-2 addendum).
.DESCRIPTION
  For each Track-1 card whose task-FILE number is >= -MinNumber, runs ONE
  executor call on the public brief alone using the arm-A-identical prompt
  scaffold, extracts the solution with the same hardened fence logic as the
  harness, grades it with the task's frozen checker, and records the score.
  Tasks landing outside the 30-70% baseline band are marked for rewrite or
  discard BEFORE the wave-2 freeze. Raw transcripts land under
  eval/results/raw/calibration-wave2/. Cost counted against -MaxSpendUsd
  (aborts, exit 4, on crossing). Re-run with -Only <slug-substring> to
  recalibrate individual tasks after rewrites.
.EXAMPLE
  pwsh -File eval/Invoke-Calibrate.ps1 -MinNumber 9 -MaxSpendUsd 1
#>
[CmdletBinding()]
param(
  [int]$MinNumber = 9,
  [double]$MaxSpendUsd = 1.0,
  [string]$Only = '',
  [string]$OutFile = '',
  [string]$ResultsDir = ''
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$evalRoot = $PSScriptRoot
$tasksDir = Join-Path $evalRoot 'tasks'
if (-not $OutFile) { $OutFile = Join-Path $tasksDir 'CALIBRATION-wave2.md' }
if (-not $ResultsDir) { $ResultsDir = Join-Path $evalRoot 'results' }

# --- key (never printed) -------------------------------------------------------
$key = ''
if ($env:OPENROUTER_API_KEY) { $key = $env:OPENROUTER_API_KEY }
else {
  $keyFile = Join-Path $HOME '.openrouter-client.key'
  if (Test-Path -LiteralPath $keyFile) { $key = (Get-Content -LiteralPath $keyFile -Raw).Trim() }
}
if (-not $key) { Write-Host 'ERROR: no OpenRouter key (set OPENROUTER_API_KEY or ~\.openrouter-client.key)'; exit 3 }

$cfg = Get-Content -LiteralPath (Join-Path $evalRoot 'config.json') -Raw -Encoding UTF8 | ConvertFrom-Json

# --- target cards: Track 1, file number >= MinNumber, optional -Only filter ----
$targets = @(Get-ChildItem -LiteralPath $tasksDir -Filter 'task-*.json' | Sort-Object Name | ForEach-Object {
  $fileNum = 0
  if ($_.Name -match '^task-(\d+)-') { $fileNum = [int]$Matches[1] }
  @{ file = $_.Name; num = $fileNum; card = (Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json) }
} | Where-Object { $_.num -ge $MinNumber -and $_.card.track -eq 1 })
if ($Only) { $targets = @($targets | Where-Object { $_.card.task_id -like "*$Only*" }) }
if ($targets.Count -eq 0) { Write-Host 'ERROR: no calibration targets matched'; exit 3 }
Write-Host "Calibrating $($targets.Count) task(s): one executor call on the public brief each"

$rawRoot = Join-Path $ResultsDir 'raw\calibration-wave2'
New-Item -ItemType Directory -Force -Path $rawRoot | Out-Null

$script:Spend = 0.0

function Invoke-ExecutorCall {
  param([object]$Card, [string]$RunDir, [double]$CapUsd)
  if ($script:Spend -gt $CapUsd) { throw "BUDGET-CAP: spent $([math]::Round($script:Spend,4)) exceeds cap $CapUsd" }
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  $sys = 'You are a senior engineer producing a final deliverable.'
  # Arm-A-identical scaffold (plain brief, no answer block, track-1 trailer).
  $user = "TASK BRIEF:`n$($Card.public_brief)`n`nProduce the final deliverable: the complete implementation in a single ``````python fenced code block. State assumptions as code comments. Do not mention any review, question, or answer process."
  $bodyObj = @{
    model       = $cfg.executor.id
    messages    = @(
      @{ role = 'system'; content = $sys },
      @{ role = 'user';   content = $user }
    )
    max_tokens  = $cfg.executor.maxTokens
    temperature = $cfg.executor.temperature
    usage       = @{ include = $true }
  }
  $body = $bodyObj | ConvertTo-Json -Depth 6
  try {
    $resp = Invoke-RestMethod -Uri $cfg.endpoint -Method Post -Headers @{
      Authorization = "Bearer $key"
      'X-Title'     = 'WiseCounsil-Calibration'
    } -ContentType 'application/json; charset=utf-8' -Body $body -TimeoutSec $cfg.executor.timeoutSec
    $resp | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $RunDir 'response.json') -Encoding UTF8
    $bodyObj | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $RunDir 'request.json') -Encoding UTF8
    $cost = 0.0; if ($resp.usage.cost) { $cost = [double]$resp.usage.cost }
    $script:Spend += $cost
    return [pscustomobject]@{ ok = $true; content = $resp.choices[0].message.content; cost = $cost; latencyMs = $sw.ElapsedMilliseconds }
  } catch {
    $err = $_.Exception.Message
    if ($_.ErrorDetails -and $_.ErrorDetails.Message) { $err = $_.ErrorDetails.Message }
    Set-Content (Join-Path $RunDir 'error.txt') -Value $err -Encoding UTF8
    return [pscustomobject]@{ ok = $false; content = ''; cost = 0.0; latencyMs = $sw.ElapsedMilliseconds }
  }
}

function Get-Solution([string]$content, [string]$RunDir) {
  # Same hardened fence logic as eval/Invoke-Eval.ps1 Get-Track1Solution.
  $m = [regex]::Match($content, '(?s)```python\s*(.*?)```')
  $code = if ($m.Success) { $m.Groups[1].Value }
          else { ($content -replace '(?m)^\s*```(python)?\s*$', '').Trim() }
  $p = Join-Path $RunDir 'solution.py'
  Set-Content -LiteralPath $p -Value $code -Encoding UTF8
  return $p
}

$rows = foreach ($t in $targets) {
  $card = $t.card
  $runDir = Join-Path $rawRoot $card.task_id
  New-Item -ItemType Directory -Force -Path $runDir | Out-Null
  $r = Invoke-ExecutorCall -Card $card -RunDir $runDir -CapUsd $MaxSpendUsd
  $score = 0.0; $passed = 0; $total = 0; $flag = ''
  if (-not $r.ok) {
    $flag = 'executor-failed'
  } else {
    $solPath = Get-Solution -content $r.content -RunDir $runDir
    $slug = $card.task_id -replace '^T[12]-', ''
    $checker = Get-ChildItem (Join-Path $evalRoot 'tasks') -Filter "check-*-$slug.ps1" | Select-Object -First 1
    if (-not $checker) { $flag = 'checker-missing' } else {
      $outScore = Join-Path $runDir 'score.json'
      & $checker.FullName -SolutionPath $solPath -OutFile $outScore *> "$runDir\check-log.txt"
      if ($LASTEXITCODE -ne 0 -or -not (Test-Path $outScore)) { $flag = 'checker-failed' } else {
        $s = Get-Content $outScore -Raw -Encoding UTF8 | ConvertFrom-Json
        $passed = [int]$s.passed; $total = [int]$s.total
        $score = if ($total -gt 0) { [math]::Round([double]$s.score, 4) } else { 0.0 }
      }
    }
  }
  $pct = [math]::Round(100 * $score)
  $verdict = switch ($flag) { '' { if ($pct -ge 30 -and $pct -le 70) { 'KEPT (in 30-70 band)' } else { if ($pct -gt 70) { 'REWRITE (too easy)' } else { 'REWRITE (too hard)' } } } default { "FAILED ($flag)" } }
  [pscustomobject]@{ file = $t.file; task_id = $card.task_id; archetype = $card.archetype; pct = $pct; passed = $passed; total = $total; verdict = $verdict; latencyMs = $r.latencyMs }
  Write-Host ("  {0,-28} {1,3}% ({2}/{3})  {4}  spend=`${5}" -f $card.task_id, $pct, $passed, $total, $verdict, [math]::Round($script:Spend, 4))
}

# --- write the documented calibration ledger -----------------------------------
$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine('# Track-1 wave-2 calibration (suite construction record — NOT experiment data)')
[void]$sb.AppendLine('')
[void]$sb.AppendLine("Generated $((Get-Date).ToUniversalTime().ToString('o')) — one executor call ($($cfg.executor.id), temperature $($cfg.executor.temperature)) per task on the PUBLIC BRIEF ALONE, arm-A-identical scaffold, graded by the task's frozen checker. Tasks outside the 30-70% band are rewritten or discarded BEFORE the wave-2 freeze (docs/EVAL-DESIGN.md, Difficulty calibration + wave-2 addendum).")
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| task file | task_id | archetype | baseline % | passed/total | verdict |')
[void]$sb.AppendLine('|---|---|---|---|---|---|')
foreach ($row in $rows) {
  [void]$sb.AppendLine("| $($row.file) | $($row.task_id) | $($row.archetype) | $($row.pct)% | $($row.passed)/$($row.total) | $($row.verdict) |")
}
[void]$sb.AppendLine('')
$inBand = @($rows | Where-Object { $_.verdict -like 'KEPT*' }).Count
$rewrites = @($rows | Where-Object { $_.verdict -like 'REWRITE*' }).Count
$failed = @($rows | Where-Object { $_.verdict -like 'FAILED*' }).Count
[void]$sb.AppendLine("Summary: $($rows.Count) tasks calibrated - $inBand in band (KEPT), $rewrites out of band (REWRITE), $failed machinery failures. Spend: `$$([math]::Round($script:Spend, 4)). Rewrite outcomes are appended below as they happen.")
Set-Content -LiteralPath $OutFile -Value $sb.ToString() -Encoding UTF8
Write-Host "CALIBRATION-OK tasks=$($rows.Count) inband=$inBand rewrite=$rewrites failed=$failed spend=`$$([math]::Round($script:Spend,4)) ledger=$OutFile"
exit 0
