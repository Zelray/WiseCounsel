#Requires -Version 7.0
<#
.SYNOPSIS
  Three-probe verification for every Track-1 grader (task-suite QA).
.DESCRIPTION
  For each Track-1 task card, runs the frozen checker against:
    1. the reference solution     -> must score the FULL test count, exit 0
    2. a no-function stub         -> must score 0, exit 0 (machinery ok, no crash)
    3. an always-false stub       -> must run machinery-ok, emit parseable
                                     RULE lines, score within [0, total]
  Proves full-credit AND partial-credit machinery for every grader, and
  re-verifies the pilot tasks after any Python/toolchain change.
  Zero network, zero spend.
.EXAMPLE
  pwsh -File eval/Invoke-VerifyGraders.ps1
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$evalRoot = $PSScriptRoot
$tasksDir = Join-Path $evalRoot 'tasks'

$t1 = @(Get-ChildItem -LiteralPath $tasksDir -Filter 'task-*.json' | Sort-Object Name | ForEach-Object {
  Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
} | Where-Object { $_.track -eq 1 })
if ($t1.Count -eq 0) { Write-Host 'VERIFY-FAIL: no Track-1 cards found'; exit 1 }

$work = Join-Path ([System.IO.Path]::GetTempPath()) ("wc-verify-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $work | Out-Null

function Get-EntrySymbols([object]$Card) {
  # Suite contract: test files either declare FUNCTION_NAME = "<name>" or
  # resolve entries via getattr(solution, "<name>", ...). Collect all names.
  $testsPath = Join-Path $tasksDir $Card.tests_file
  if (-not (Test-Path -LiteralPath $testsPath)) { return @() }
  $text = Get-Content -LiteralPath $testsPath -Raw -Encoding UTF8
  $names = @([regex]::Matches($text, 'FUNCTION_NAME\s*=\s*"([^"]+)"') | ForEach-Object { $_.Groups[1].Value })
  $names += @([regex]::Matches($text, 'getattr\(solution, "([^"]+)"') | ForEach-Object { $_.Groups[1].Value })
  return @($names | Select-Object -Unique)
}

function Get-StubBody([object]$Card, [string[]]$Symbols) {
  # Function symbols -> always-false function; class symbols (checked against
  # the reference solution's own definitions) -> *args/**kwargs-tolerant class
  # whose missing attributes resolve to callables returning False.
  $refPath = Join-Path $tasksDir $Card.reference_solution
  $ref = if (Test-Path -LiteralPath $refPath) { Get-Content -LiteralPath $refPath -Raw -Encoding UTF8 } else { '' }
  $lines = [System.Collections.Generic.List[string]]::new()
  foreach ($sym in $Symbols) {
    if ($ref -match "(?m)^\s*class\s+$([regex]::Escape($sym))\b") {
      $lines.Add("class ${sym}:")
      $lines.Add('    def __init__(self, *args, **kwargs): pass')
      $lines.Add('    def __getattr__(self, name):')
      $lines.Add('        def _any_method(*args, **kwargs): return False')
      $lines.Add('        return _any_method')
      $lines.Add('')
    } else {
      $lines.Add("def $sym(*args, **kwargs):")
      $lines.Add('    return False')
      $lines.Add('')
    }
  }
  return ($lines -join "`n")
}

function Invoke-CheckerProbe([object]$Card, [string]$SolutionPath, [string]$Tag) {
  $slug = $Card.task_id -replace '^T[12]-', ''
  $checker = Get-ChildItem (Join-Path $evalRoot 'tasks') -Filter "check-*-$slug.ps1" | Select-Object -First 1
  if (-not $checker) { return @{ exit = 3; passed = -1; total = -1; rules = 0 } }
  $outFile = Join-Path $work "$($Card.task_id -replace '[^A-Za-z0-9-]', '_')-$Tag.json"
  & $checker.FullName -SolutionPath $SolutionPath -OutFile $outFile *> $null
  $exit = $LASTEXITCODE
  if ($exit -ne 0 -or -not (Test-Path $outFile)) { return @{ exit = $exit; passed = -1; total = -1; rules = 0 } }
  $s = Get-Content $outFile -Raw -Encoding UTF8 | ConvertFrom-Json
  $ruleLines = @(@($s.raw_tail) | Where-Object { "$_" -match '^RULE\s+\S+\s+(PASS|FAIL)' })
  return @{ exit = $exit; passed = [int]$s.passed; total = [int]$s.total; rules = $ruleLines.Count }
}

$failures = [System.Collections.Generic.List[string]]::new()
foreach ($card in $t1) {
  $symbols = Get-EntrySymbols $card
  $refPath = Join-Path $tasksDir $card.reference_solution

  # Probe 1: reference solution -> full score, exit 0
  $r1 = @{ exit = -1; passed = -1; total = -1; rules = 0 }
  if (Test-Path -LiteralPath $refPath) { $r1 = Invoke-CheckerProbe $card $refPath 'ref' }
  $refOk = ($r1.exit -eq 0 -and $r1.total -gt 0 -and $r1.passed -eq $r1.total)

  # Probe 2: no-function stub -> score 0, exit 0
  $stubEmpty = Join-Path $work "$($card.task_id -replace '[^A-Za-z0-9-]', '_')-stub-empty.py"
  Set-Content -LiteralPath $stubEmpty -Value '# empty stub: defines nothing' -Encoding UTF8
  $r2 = Invoke-CheckerProbe $card $stubEmpty 'stub'
  $stubOk = ($r2.exit -eq 0 -and $r2.passed -eq 0)

  # Probe 3: always-false stub(s) -> machinery ok + RULE lines + score in range
  $r3 = @{ exit = -1; passed = -1; total = -1; rules = 0 }
  if ($symbols.Count -gt 0) {
    $stubFalse = Join-Path $work "$($card.task_id -replace '[^A-Za-z0-9-]', '_')-stub-false.py"
    Set-Content -LiteralPath $stubFalse -Value ((Get-StubBody $card $symbols) + "`n") -Encoding UTF8
    $r3 = Invoke-CheckerProbe $card $stubFalse 'false'
    $falseOk = ($r3.exit -eq 0 -and $r3.total -gt 0 -and $r3.passed -ge 0 -and $r3.passed -le $r3.total -and $r3.rules -gt 0)
  } else {
    $falseOk = $false
  }

  $ok = $refOk -and $stubOk -and $falseOk
  if (-not $ok) {
    $failures.Add("$($card.task_id): ref(exit=$($r1.exit) $($r1.passed)/$($r1.total)) stub(exit=$($r2.exit) $($r2.passed)) false(exit=$($r3.exit) $($r3.passed)/$($r3.total) rules=$($r3.rules))")
  }
  Write-Host ("  {0,-28} ref={1,-6} falsestub={2,-6} {3}" -f $card.task_id, "$($r1.passed)/$($r1.total)", "$($r3.passed)/$($r3.total)", $(if ($ok) { 'OK' } else { 'FAIL' }))
}

Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue

if ($failures.Count -gt 0) {
  Write-Host 'GRADERS-FAILED:'
  $failures
  exit 1
}
Write-Host "GRADERS-VERIFIED ($($t1.Count) Track-1 tasks: ref=max, stub=0, falsestub=machinery-ok on all)"
exit 0
