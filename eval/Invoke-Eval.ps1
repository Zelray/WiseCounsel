#Requires -Version 7.0
<#
.SYNOPSIS
  WiseCounsel A/B evaluation harness (pilot, per docs/EVAL-DESIGN.md).
.DESCRIPTION
  Runs task cards through arms A (baseline), B (council), C (self-questions),
  D (single critic) under identical conditions, grades Track-1 deliverables
  with the frozen deterministic checkers and Track-2 deliverables with a
  three-judge panel, and writes a full audit trail (manifest + per-run
  transcripts) under eval/results/.

  -Mock runs the ENTIRE pipeline with deterministic in-process fakes: zero
  network calls, zero API spend, zero key reads. Use it to test machinery.

  A hard spend cap (config budget.maxSpendUsd) aborts the run the moment
  cumulative provider-reported cost crosses it. The API key is never printed.
.EXAMPLE
  pwsh -File eval/Invoke-Eval.ps1 -Mock -Arms A,B -Reps 1
#>
[CmdletBinding()]
param(
  [string[]]$Arms = @('A','B','C','D'),
  [string[]]$TaskFilter = @(),
  [int]$Reps = 2,
  [string]$ResultsDir = '',
  [switch]$Mock,
  [double]$MaxSpendUsd = -1,
  [string]$ConfigPath = ''
)

# Normalize comma-joined values: `pwsh -File x.ps1 -Arms A,B,C` delivers ONE
# string token, not an array. Accept both shapes.
if ($Arms.Count -eq 1 -and "$($Arms[0])" -match ',') {
  $Arms = @("$($Arms[0])" -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}
if ($TaskFilter.Count -eq 1 -and "$($TaskFilter[0])" -match ',') {
  $TaskFilter = @("$($TaskFilter[0])" -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}
$badArms = @($Arms | Where-Object { @('A','B','C','D','E','F') -notcontains $_ })
if ($badArms.Count -gt 0) { Write-Host "ERROR: unknown arm(s): $($badArms -join ', ') (valid: A, B, C, D, E, F)"; exit 3 }

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$evalRoot = $PSScriptRoot
$repoRoot = Split-Path -Parent $evalRoot
if (-not $ConfigPath) { $ConfigPath = Join-Path $evalRoot 'config.json' }
$cfg = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $ResultsDir) { $ResultsDir = Join-Path $evalRoot 'results' }
if ($MaxSpendUsd -le 0) { $MaxSpendUsd = [double]$cfg.budget.maxSpendUsd }

# --- key (real mode only; NEVER printed) --------------------------------------
$key = ''
if (-not $Mock) {
  if ($env:OPENROUTER_API_KEY) { $key = $env:OPENROUTER_API_KEY }
  else {
    $keyFile = Join-Path $HOME '.openrouter-client.key'
    if (Test-Path -LiteralPath $keyFile) { $key = (Get-Content -LiteralPath $keyFile -Raw).Trim() }
  }
  if (-not $key) { Write-Host 'ERROR: no OpenRouter key (set OPENROUTER_API_KEY or ~\.openrouter-client.key)'; exit 3 }
}

# --- load tasks ----------------------------------------------------------------
$tasksDir = Join-Path $evalRoot 'tasks'
$cards = @(Get-ChildItem -LiteralPath $tasksDir -Filter 'task-*.json' | ForEach-Object {
  Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
})
if ($TaskFilter.Count -gt 0) {
  $cards = @($cards | Where-Object { $tid = $_.task_id; @($TaskFilter | Where-Object { $tid -like "*$_*" }).Count -gt 0 })
}
if ($cards.Count -eq 0) { Write-Host 'ERROR: no task cards matched'; exit 3 }
foreach ($c in $cards) {
  if ($c.track -eq 1) {
    foreach ($f in 'tests_file','reference_solution') {
      if (-not (Test-Path (Join-Path $tasksDir $c.$f))) { Write-Host "ERROR: task $($c.task_id) missing $f"; exit 3 }
    }
  }
}

# --- experiment identity + dirs -------------------------------------------------
$expId = '{0}{1}' -f ($(if ($Mock) { 'mock-' } else { 'exp-' })), (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
$rawRoot = Join-Path $ResultsDir "raw\$expId"
New-Item -ItemType Directory -Force -Path $rawRoot | Out-Null
$manifestPath = Join-Path $ResultsDir 'manifest.jsonl'

$script:Spend = 0.0
$script:CouncilScript = Join-Path $repoRoot $cfg.council.scriptPath
$script:PremortemTemplate = Get-Content (Join-Path $evalRoot 'templates\premortem.txt') -Raw
# Arm E: one sham dossier per donor task, generated once and reused across
# repetitions (fixed-question-sets rule); a failed sham council is cached as
# '' and its run proceeds without enrichment, same as arm B's failure rule.
$script:ShamDossiers = @{}
# Fixed task order for arm E's rotation (post-filter launch order).
$cardIdxByTaskId = @{}
for ($i = 0; $i -lt $cards.Count; $i++) { $cardIdxByTaskId[$cards[$i].task_id] = $i }

# --- model call ------------------------------------------------------------------
function Invoke-ModelCall {
  param(
    [string]$Model, [string]$System, [string]$User,
    [double]$Temperature, [int]$MaxTokens, [int]$TimeoutSec,
    [string]$Purpose, [string]$RunDir = '', [object]$TaskCard = $null
  )
  if ($Mock) { return Invoke-MockCall -Purpose $Purpose -TaskCard $TaskCard }

  if ($script:Spend -gt $MaxSpendUsd) { throw "BUDGET-CAP: spent $([math]::Round($script:Spend,4)) exceeds cap $MaxSpendUsd" }
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  $bodyObj = @{
    model       = $Model
    messages    = @(
      @{ role = 'system'; content = $System },
      @{ role = 'user';   content = $User }
    )
    max_tokens  = $MaxTokens
    temperature = $Temperature
    usage       = @{ include = $true }
  }
  $body = $bodyObj | ConvertTo-Json -Depth 6
  try {
    $resp = Invoke-RestMethod -Uri $cfg.endpoint -Method Post -Headers @{
      Authorization = "Bearer $key"
      'X-Title'     = 'WiseCounsel-Eval'
    } -ContentType 'application/json; charset=utf-8' -Body $body -TimeoutSec $TimeoutSec
    if ($RunDir) {
      @{ purpose = $Purpose; model = $Model; body = $bodyObj } |
        ConvertTo-Json -Depth 8 | Set-Content (Join-Path $RunDir "prompts\$Purpose.json") -Encoding UTF8
      $resp | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $RunDir "responses\$Purpose.json") -Encoding UTF8
    }
    $cost = 0.0; if ($resp.usage.cost) { $cost = [double]$resp.usage.cost }
    $script:Spend += $cost
    return [pscustomobject]@{
      ok = $true; content = $resp.choices[0].message.content
      tokens = $resp.usage.total_tokens; cost = $cost
      latencyMs = $sw.ElapsedMilliseconds; servedModel = $resp.model; error = ''
    }
  } catch {
    $err = $_.Exception.Message
    if ($_.ErrorDetails -and $_.ErrorDetails.Message) { $err = $_.ErrorDetails.Message }
    return [pscustomobject]@{ ok = $false; content = ''; tokens = 0; cost = 0; latencyMs = $sw.ElapsedMilliseconds; servedModel = ''; error = $err }
  }
}

function Invoke-MockCall {
  param([string]$Purpose, [object]$TaskCard)
  if ($Purpose -eq 'council') {
    $content = @'
# WiseCounsel dossier (MOCK)
## [mock-a] (mock/a-1)
## Missing
The brief does not state rounding, validation, or boundary rules.
## Ambiguous
"Handle overtime" has at least two readings (single rate vs tiered).
## Risky assumptions
Verify: what input validation is expected?
## Approach sketch
- implement the stated contract; add defensive validation
## Watchlist
- hidden domain rules; output formatting
'@
    return [pscustomobject]@{ ok = $true; content = $content; tokens = 0; cost = 0.0; latencyMs = 0; servedModel = 'mock'; error = '' }
  }
  if ($Purpose -eq 'synthesis') {
    $content = @'
ENRICHED BRIEF
Implement the stated contract; add conventional validation and formatting.
OPEN QUESTIONS
Q: What rounding rule should apply to money values?
Q: What input validation and error behavior is expected?
Q: Are there thresholds, caps, or tiered rates to respect?
Q: What output format and types are expected?
VERIFY-LATER
- rounding mode
- validation rules
DISSENT
none
'@
    return [pscustomobject]@{ ok = $true; content = $content; tokens = 0; cost = 0.0; latencyMs = 0; servedModel = 'mock'; error = '' }
  }
  if ($Purpose -eq 'matcher') {
    # deterministic clerical mapping: question i -> sheet entry i (wraps); exercises delivery + fallback
    $qs = @($script:CurrentQuestions)
    $sheet = @($TaskCard.answer_sheet)
    $pairs = foreach ($i in 0..($qs.Count - 1)) {
      $eid = if ($sheet.Count -gt 0) { $sheet[$i % $sheet.Count].id } else { '' }
      @{ question = ($i + 1); entry_ids = @($eid) }
    }
    return [pscustomobject]@{ ok = $true; content = ($pairs | ConvertTo-Json -Depth 4); tokens = 0; cost = 0.0; latencyMs = 0; servedModel = 'mock'; error = '' }
  }
  if ($Purpose -like 'executor*') {
    if ($TaskCard.track -eq 1) {
      $refPath = Join-Path $evalRoot "tasks\$($TaskCard.reference_solution)"
      $code = Get-Content -LiteralPath $refPath -Raw -Encoding UTF8
      $content = '```python' + "`n" + $code + '```'
    } else {
      $content = @'
# Recommendation (MOCK)
Pick option B. It meets the stated volume at the lowest all-in cost, with an explicit rollback path.
'@
    }
    return [pscustomobject]@{ ok = $true; content = $content; tokens = 0; cost = 0.0; latencyMs = 0; servedModel = 'mock'; error = '' }
  }
  if ($Purpose -eq 'judge') {
    $dims = @($TaskCard.rubric) | ForEach-Object { "`"$($_.id)`": 2" }
    $content = '{' + ($dims -join ',') + ',"total":' + (2 * @($TaskCard.rubric).Count) + ',"one_line":"mock"}'
    return [pscustomobject]@{ ok = $true; content = $content; tokens = 0; cost = 0.0; latencyMs = 0; servedModel = 'mock'; error = '' }
  }
  if ($Purpose -eq 'selector') {
    return [pscustomobject]@{ ok = $true; content = '1'; tokens = 0; cost = 0.0; latencyMs = 0; servedModel = 'mock'; error = '' }
  }
  if ($Purpose -eq 'probe') {
    return [pscustomobject]@{ ok = $true; content = 'baseline'; tokens = 0; cost = 0.0; latencyMs = 0; servedModel = 'mock'; error = '' }
  }
  if ($Purpose -eq 'critic') {
    return Invoke-MockCall -Purpose 'council' -TaskCard $TaskCard
  }
  throw "Invoke-MockCall: unknown purpose '$Purpose'"
}

# --- pipeline steps ---------------------------------------------------------------
function Get-QuestionsFromSynthesis([string]$text) {
  $qs = @([regex]::Matches($text, '(?m)^\s*Q[:.)]\s*(.+)$') | ForEach-Object { $_.Groups[1].Value.Trim() })
  return @($qs | Select-Object -First 5)
}

function Invoke-CouncilStep {
  # BriefOverride (arm E only): run the council on a DIFFERENT task's brief
  # (sham context). The overridden brief is logged as brief-sham.txt so the
  # audit trail always shows the exact text the council saw.
  param([object]$Card, [string]$RunDir, [string]$BriefOverride = '', [string]$BriefFileName = 'brief.txt')
  $briefText = if ($BriefOverride) { $BriefOverride } else { $Card.public_brief }
  if ($Mock) {
    $r = Invoke-MockCall -Purpose 'council' -TaskCard $Card
    return @{ dossier = $r.content; cost = 0.0; exit = 0 }
  }
  $briefFile = Join-Path $RunDir $BriefFileName
  Set-Content -LiteralPath $briefFile -Value $briefText -Encoding UTF8
  $councilOut = Join-Path $RunDir 'council'
  & $script:CouncilScript -Mode premortem -TaskFile $briefFile -OutDir $councilOut *> "$RunDir\council-log.txt"
  $exit = $LASTEXITCODE
  if ($exit -ne 0) { return @{ dossier = ''; cost = 0.0; exit = $exit } }
  $dossier = Get-Content (Join-Path $councilOut 'dossier.md') -Raw -Encoding UTF8
  $cost = 0.0
  $rawPath = Join-Path $councilOut 'raw.json'
  if (Test-Path $rawPath) {
    $rows = Get-Content $rawPath -Raw | ConvertFrom-Json
    foreach ($row in @($rows)) { if ($row.cost) { $cost += [double]$row.cost } }
  }
  return @{ dossier = $dossier; cost = $cost; exit = $exit }
}

function Invoke-CriticStep {
  param([object]$Card, [string]$RunDir)
  $subject = $Card.public_brief
  $sys = $script:PremortemTemplate + "`n`nSUBJECT:`n$subject"
  if ($Mock) {
    $r = Invoke-MockCall -Purpose 'critic' -TaskCard $Card
  } else {
    $r = Invoke-ModelCall -Model $cfg.singleCritic.id -System $sys -User 'Proceed.' `
      -Temperature $cfg.singleCritic.temperature -MaxTokens $cfg.singleCritic.maxTokens `
      -TimeoutSec $cfg.singleCritic.timeoutSec -Purpose 'critic' -RunDir $RunDir
  }
  if (-not $r.ok) { return @{ dossier = ''; cost = 0.0; exit = 2 } }
  return @{ dossier = $r.content; cost = $r.cost; exit = 0 }
}

function Invoke-SynthesisStep {
  param([object]$Card, [string]$RunDir, [string]$Dossier)
  $dossierBlock = if ($Dossier) { "A review council attacked this brief. Their full findings:`n`n$Dossier`n`n" }
                  else { "No external review is available; rely on your own analysis.`n`n" }
  $sys = @"
You are the senior engineer who will execute the TASK BRIEF below.
$dossierBlock
Produce, in EXACTLY this structure and nothing else:
ENRICHED BRIEF
<the brief with material gaps merged in, max 300 words; the user's stated intent wins any conflict>
OPEN QUESTIONS
Q: <at most 5 questions, one per line, only ones that change the build>
VERIFY-LATER
<checklist of items to verify during implementation>
DISSENT
<one line where reviewers disagreed, or 'none'>
"@
  $r = Invoke-ModelCall -Model $cfg.executor.id -System $sys -User $Card.public_brief `
    -Temperature $cfg.executor.temperature -MaxTokens 2048 -TimeoutSec $cfg.executor.timeoutSec `
    -Purpose 'synthesis' -RunDir $RunDir
  if (-not $r.ok) { return @{ ok = $false; questions = @(); cost = $r.cost; error = $r.error } }
  return @{ ok = $true; questions = (Get-QuestionsFromSynthesis $r.content); cost = $r.cost; error = '' }
}

function Invoke-MatcherStep {
  param([object]$Card, [string[]]$Questions, [string]$RunDir)
  if ($Questions.Count -eq 0) { return @{ mapping = @(); cost = 0.0 } }
  $script:CurrentQuestions = $Questions
  $sheetTopics = @($Card.answer_sheet | ForEach-Object { @{ id = $_.id; topic = $_.topic } })
  $payload = @{ questions = $Questions; sheet = $sheetTopics } | ConvertTo-Json -Depth 4
  $sys = 'You are a clerical matcher. Given QUESTIONS and an ANSWER SHEET (ids + topics only), decide which sheet entries each question clearly asks about. Match by topic only; when unsure, return an empty list. Output ONLY a JSON array like: [{"question": 1, "entry_ids": ["R3"]}] — one object per question, in order. No other text.'
  $r = Invoke-ModelCall -Model $cfg.matcher.id -System $sys -User $payload `
    -Temperature $cfg.matcher.temperature -MaxTokens $cfg.matcher.maxTokens -TimeoutSec $cfg.matcher.timeoutSec `
    -Purpose 'matcher' -RunDir $RunDir -TaskCard $Card
  if (-not $r.ok) { return @{ mapping = @(); cost = 0.0 } }
  try {
    $m = $r.content.Trim() -replace '^```(json)?','' -replace '```$',''
    $mapping = @($m | ConvertFrom-Json)
    return @{ mapping = $mapping; cost = $r.cost }
  } catch { return @{ mapping = @(); cost = $r.cost } }
}

function Get-DeliveredAnswers {
  param([object]$Card, [string[]]$Questions, [object[]]$Mapping)
  $lines = @()
  $byQ = @{}
  foreach ($m in $Mapping) { $byQ[[int]$m.question] = @($m.entry_ids) }
  for ($i = 0; $i -lt $Questions.Count; $i++) {
    $q = $Questions[$i]
    $ids = $byQ[($i + 1)]
    if ($null -ne $ids -and @($ids).Count -gt 0) {
      foreach ($eid in $ids) {
        $entry = $Card.answer_sheet | Where-Object { $_.id -eq $eid } | Select-Object -First 1
        if ($entry) { $lines += "- Q$($i+1): $q -> [$($entry.id)] $($entry.answer)"; break }
      }
    } else {
      $lines += "- Q$($i+1): $q -> Not specified - use best judgment and state the assumption in a comment."
    }
  }
  return $lines
}

function Invoke-BuildStep {
  # PurposeSuffix (arm F only): disambiguates the logged prompts/responses of
  # the three independent candidate builds (-f1/-f2/-f3) inside one run dir.
  param([object]$Card, [string]$RunDir, [string[]]$AnswerLines, [string]$PurposeSuffix = '')
  $user = "TASK BRIEF:`n$($Card.public_brief)"
  if ($AnswerLines.Count -gt 0) {
    $user += "`n`nANSWERS TO YOUR OPEN QUESTIONS:`n" + ($AnswerLines -join "`n")
  }
  if ($Card.track -eq 1) {
    $user += "`n`nProduce the final deliverable: the complete implementation in a single ``````python fenced code block. State assumptions as code comments. Do not mention any review, question, or answer process."
  } else {
    $user += "`n`nProduce your recommendation as a structured markdown document: position up front, then the reasoning, risks with mitigations, and what would change your mind. State assumptions explicitly. Do not mention any review, question, or answer process."
  }
  $r = Invoke-ModelCall -Model $cfg.executor.id -System 'You are a senior engineer producing a final deliverable.' -User $user `
    -Temperature $cfg.executor.temperature -MaxTokens $cfg.executor.maxTokens -TimeoutSec $cfg.executor.timeoutSec `
    -Purpose "executor$PurposeSuffix" -RunDir $RunDir -TaskCard $Card
  return $r
}

function Invoke-SelectionStep {
  # Arm F: pick the best of the three candidate builds. Executor-family model,
  # temperature 0, single token answer. Pre-stated fallback (wave-2 addendum):
  # non-1-3 selector output -> candidate 1 + flag; selector call failure ->
  # candidate 1 + flag.
  param([object]$Card, [object[]]$Candidates, [string]$RunDir)
  $parts = for ($k = 0; $k -lt @($Candidates).Count; $k++) {
    $c = $Candidates[$k]
    $body = if ($c.ok) { $c.content } else { '(candidate failed to generate)' }
    "=== CANDIDATE $($k + 1) ===`n$body"
  }
  $sys = 'You will be given a TASK BRIEF and three candidate solutions. Reply with ONLY the number 1-3 of the solution that best satisfies the brief. No other text.'
  $user = "TASK BRIEF:`n$($Card.public_brief)`n`n" + ($parts -join "`n`n")
  $r = Invoke-ModelCall -Model $cfg.executor.id -System $sys -User $user `
    -Temperature 0.0 -MaxTokens 8 -TimeoutSec $cfg.executor.timeoutSec `
    -Purpose 'selector' -RunDir $RunDir
  if (-not $r.ok) { return @{ index = 1; raw = ''; cost = $r.cost; flag = 'selection-failed' } }
  $m = [regex]::Match($r.content, '[123]')
  if (-not $m.Success) { return @{ index = 1; raw = $r.content; cost = $r.cost; flag = 'selection-invalid' } }
  return @{ index = [int]$m.Value; raw = $r.content.Trim(); cost = $r.cost; flag = '' }
}

function Get-Track1Solution([string]$content, [string]$RunDir) {
  $m = [regex]::Match($content, '(?s)```python\s*(.*?)```')
  # Whole-content fallback: strip bare/unclosed fence lines so a response that
  # opens a fence but never closes it cannot poison the graded file (this
  # zeroed 2 pilot baseline runs; see wave-2 addendum).
  $code = if ($m.Success) { $m.Groups[1].Value }
          else { ($content -replace '(?m)^\s*```(python)?\s*$', '').Trim() }
  $p = Join-Path $RunDir 'solution.py'
  Set-Content -LiteralPath $p -Value $code -Encoding UTF8
  return $p
}

function Invoke-GradeTrack1 {
  param([object]$Card, [string]$SolutionPath, [string]$RunDir)
  $slug = $Card.task_id -replace '^T[12]-', ''
  $checker = Get-ChildItem (Join-Path $evalRoot 'tasks') -Filter "check-*-$slug.ps1" | Select-Object -First 1
  if (-not $checker) { return @{ score = 0.0; passed = 0; total = 0; flag = 'checker-missing' } }
  $outFile = Join-Path $RunDir 'score.json'
  & $checker.FullName -SolutionPath $SolutionPath -OutFile $outFile *> "$RunDir\check-log.txt"
  if ($LASTEXITCODE -ne 0 -or -not (Test-Path $outFile)) { return @{ score = 0.0; passed = 0; total = 0; flag = 'checker-failed' } }
  $s = Get-Content $outFile -Raw | ConvertFrom-Json
  return @{ score = [math]::Round([double]$s.score, 4); passed = [int]$s.passed; total = [int]$s.total; flag = '' }
}

function Invoke-JudgeTrack2 {
  param([object]$Card, [string]$Deliverable, [string]$RunDir)
  $rubricText = (@($Card.rubric) | ForEach-Object { "- $($_.id) ($($_.name)): $($_.description) [0-2]" }) -join "`n"
  $sys = @"
You are scoring one response to a decision brief. Score ONLY the substance against the rubric; do not reward length or style. Respond ONLY with JSON: {"<dim-id>": <0-2>, ..., "total": <sum>, "one_line": "<why>"}
RUBRIC:
$rubricText
"@
  $scores = @(); $probeOk = 0; $judgesCost = 0.0
  foreach ($j in $cfg.judges) {
    $r = Invoke-ModelCall -Model $j.id -System $sys -User "RESPONSE TO SCORE:`n$Deliverable" `
      -Temperature $j.temperature -MaxTokens $j.maxTokens -TimeoutSec $j.timeoutSec -Purpose 'judge' -RunDir $RunDir -TaskCard $Card
    $judgesCost += $r.cost
    if ($r.ok) {
      try {
        $j2 = ($r.content.Trim() -replace '^```(json)?','' -replace '```$','') | ConvertFrom-Json
        $scores += [double]$j2.total
      } catch { $scores += $null }
    } else { $scores += $null }
    if ($cfg.armProbe) {
      $p = Invoke-ModelCall -Model $j.id -System 'Answer with ONE word: enriched (if the response looks like it was produced with extra Q&A context) or baseline.' `
        -User "RESPONSE:`n$($Deliverable.Substring(0, [Math]::Min(2000, $Deliverable.Length)))" `
        -Temperature 0.0 -MaxTokens 8 -TimeoutSec $j.timeoutSec -Purpose 'probe' -RunDir $RunDir
      if ($p.ok -and $p.content -match 'enriched') { $probeOk++ }
    }
  }
  $valid = @($scores | Where-Object { $null -ne $_ })
  $maxTotal = 2 * @($Card.rubric).Count
  $score = if ($valid.Count -gt 0) { [math]::Round((($valid | Measure-Object -Average).Average) / $maxTotal, 4) } else { 0.0 }
  return @{ score = $score; judges = $scores; probe_enriched_votes = $probeOk; flag = $(if ($valid.Count -eq 0) { 'judge-failed' } else { '' }) }
}

# --- leak check (Arm A) -------------------------------------------------------------
function Test-SheetLeakage {
  param([object]$Card, [string]$PromptText, [string]$RunDir)
  function Tokenize([string]$s) {
    $t = @($s.ToLower() -split '[^a-z0-9]+' | Where-Object { $_.Length -gt 3 } | Select-Object -Unique)
    return $t
  }
  $pt = Tokenize $PromptText
  $maxOv = 0.0; $worst = ''
  foreach ($e in $Card.answer_sheet) {
    $et = Tokenize $e.answer
    if ($et.Count -eq 0) { continue }
    $inter = @($pt | Where-Object { $et -contains $_ }).Count
    $union = @(@($pt) + @($et) | Select-Object -Unique).Count
    $ov = $inter / $union
    if ($ov -gt $maxOv) { $maxOv = $ov; $worst = $e.id }
  }
  $verdict = if ($maxOv -lt 0.4) { 'OK' } else { 'FLAG' }
  Set-Content (Join-Path $RunDir 'leak-check.txt') -Value "max_overlap=$([math]::Round($maxOv,3)) worst_entry=$worst verdict=$verdict" -Encoding UTF8
  return $verdict
}

# --- schedule + run loop ------------------------------------------------------------
$schedule = @()
for ($rep = 1; $rep -le $Reps; $rep++) {
  foreach ($card in $cards) { foreach ($arm in $Arms) { $schedule += @{ card = $card; arm = $arm; rep = $rep } } }
}
Write-Host "WiseCounsel eval: $($cards.Count) tasks x $($Arms.Count) arms x $Reps reps = $($schedule.Count) runs (mode: $(if ($Mock) { 'MOCK' } else { 'LIVE' }), cap: `$$MaxSpendUsd)"

$done = 0
try {
foreach ($slot in $schedule) {
  $card = $slot.card; $arm = $slot.arm; $rep = $slot.rep
  $runDir = Join-Path $rawRoot "$arm\$($card.task_id)-rep$rep"
  New-Item -ItemType Directory -Force -Path (Join-Path $runDir 'prompts') | Out-Null
  New-Item -ItemType Directory -Force -Path (Join-Path $runDir 'responses') | Out-Null

  $flags = [System.Collections.Generic.List[string]]::new()
  $runCost = 0.0
  $questions = @()
  $shamDonorTask = $null

  # Arm-specific pre-build material
  $answerLines = @()
  if ($arm -eq 'B') {
    $c = Invoke-CouncilStep -Card $card -RunDir $runDir
    $runCost += $c.cost
    if ($c.exit -ne 0) { $flags.Add('council-failed') } else {
      $syn = Invoke-SynthesisStep -Card $card -RunDir $runDir -Dossier $c.dossier
      $runCost += $syn.cost
      if (-not $syn.ok) { $flags.Add('synthesis-failed') } else {
        $questions = $syn.questions
        $match = Invoke-MatcherStep -Card $card -Questions $questions -RunDir $runDir
        $runCost += $match.cost
        $answerLines = Get-DeliveredAnswers -Card $card -Questions $questions -Mapping $match.mapping
        $answerLines | Set-Content (Join-Path $runDir 'answers-delivered.txt') -Encoding UTF8
      }
    }
  } elseif ($arm -eq 'C') {
    $syn = Invoke-SynthesisStep -Card $card -RunDir $runDir -Dossier ''
    $runCost += $syn.cost
    if (-not $syn.ok) { $flags.Add('synthesis-failed') } else {
      $questions = $syn.questions
      $match = Invoke-MatcherStep -Card $card -Questions $questions -RunDir $runDir
      $runCost += $match.cost
      $answerLines = Get-DeliveredAnswers -Card $card -Questions $questions -Mapping $match.mapping
      $answerLines | Set-Content (Join-Path $runDir 'answers-delivered.txt') -Encoding UTF8
    }
  } elseif ($arm -eq 'D') {
    $c = Invoke-CriticStep -Card $card -RunDir $runDir
    $runCost += $c.cost
    if ($c.exit -ne 0) { $flags.Add('critic-failed') } else {
      $syn = Invoke-SynthesisStep -Card $card -RunDir $runDir -Dossier $c.dossier
      $runCost += $syn.cost
      if (-not $syn.ok) { $flags.Add('synthesis-failed') } else {
        $questions = $syn.questions
        $match = Invoke-MatcherStep -Card $card -Questions $questions -RunDir $runDir
        $runCost += $match.cost
        $answerLines = Get-DeliveredAnswers -Card $card -Questions $questions -Mapping $match.mapping
        $answerLines | Set-Content (Join-Path $runDir 'answers-delivered.txt') -Encoding UTF8
      }
    }
  } elseif ($arm -eq 'E') {
    # Sham context: the dossier comes from the NEXT task in the fixed order
    # (i+1 mod n) — one real council call per donor task, rotated by one, so
    # the synthesis gets realistic extra text about the WRONG task.
    $donor = $cards[($cardIdxByTaskId[$card.task_id] + 1) % $cards.Count]
    $shamDonorTask = $donor.task_id
    if (-not $script:ShamDossiers.ContainsKey($donor.task_id)) {
      $c = Invoke-CouncilStep -Card $card -RunDir $runDir -BriefOverride $donor.public_brief -BriefFileName 'brief-sham.txt'
      $runCost += $c.cost
      if ($c.exit -ne 0) { $script:ShamDossiers[$donor.task_id] = ''; $flags.Add('council-failed') }
      else { $script:ShamDossiers[$donor.task_id] = $c.dossier }
    }
    $dossier = $script:ShamDossiers[$donor.task_id]
    if ($dossier) {
      $syn = Invoke-SynthesisStep -Card $card -RunDir $runDir -Dossier $dossier
      $runCost += $syn.cost
      if (-not $syn.ok) { $flags.Add('synthesis-failed') } else {
        $questions = $syn.questions
        $match = Invoke-MatcherStep -Card $card -Questions $questions -RunDir $runDir
        $runCost += $match.cost
        $answerLines = Get-DeliveredAnswers -Card $card -Questions $questions -Mapping $match.mapping
        $answerLines | Set-Content (Join-Path $runDir 'answers-delivered.txt') -Encoding UTF8
      }
    }
  }
  ConvertTo-Json -InputObject @($questions) | Set-Content (Join-Path $runDir 'questions.json') -Encoding UTF8

  # Build (arm F: three plain-brief candidates + a selector call; others: one)
  if ($arm -eq 'F') {
    $candidates = @()
    for ($k = 1; $k -le 3; $k++) {
      $b = Invoke-BuildStep -Card $card -RunDir $runDir -AnswerLines @() -PurposeSuffix "-f$k"
      $runCost += $b.cost
      $candidates += $b
    }
    $sel = Invoke-SelectionStep -Card $card -Candidates $candidates -RunDir $runDir
    $runCost += $sel.cost
    if ($sel.flag) { $flags.Add($sel.flag) }
    @{ selector_reply = $sel.raw; chosen = $sel.index; selector_flag = $sel.flag } |
      ConvertTo-Json -Depth 4 | Set-Content (Join-Path $runDir 'best-of-3.json') -Encoding UTF8
    $build = @($candidates)[[math]::Max(1, $sel.index) - 1]
  } else {
    $build = Invoke-BuildStep -Card $card -RunDir $runDir -AnswerLines $answerLines
    $runCost += $build.cost
  }
  $score = 0.0; $passed = 0; $total = 0
  if (-not $build.ok) {
    $flags.Add('executor-failed')
  } else {
    if ($card.track -eq 1) {
      $solPath = Get-Track1Solution -content $build.content -RunDir $runDir
      if (-not (Test-Path $solPath)) { $flags.Add('no-solution') } else {
        $g = Invoke-GradeTrack1 -Card $card -SolutionPath $solPath -RunDir $runDir
        $score = $g.score; $passed = $g.passed; $total = $g.total
        if ($g.flag) { $flags.Add($g.flag) }
      }
    } else {
      $build.content | Set-Content (Join-Path $runDir 'deliverable.md') -Encoding UTF8
      $j = Invoke-JudgeTrack2 -Card $card -Deliverable $build.content -RunDir $runDir
      $score = $j.score
      if ($j.flag) { $flags.Add($j.flag) }
      @{ judges = $j.judges; probe_enriched_votes = $j.probe_enriched_votes } |
        ConvertTo-Json -Depth 4 | Set-Content (Join-Path $runDir 'judge.json') -Encoding UTF8
    }
  }

  # Leakage audit: baseline prompts must not carry sheet text
  $leakVerdict = 'n/a'
  if ($arm -eq 'A') {
    $leakVerdict = Test-SheetLeakage -Card $card -PromptText $card.public_brief -RunDir $runDir
    if ($leakVerdict -eq 'FLAG') { $flags.Add('leak-flag') }
  }

  $script:Spend += $runCost
  $row = [ordered]@{
    expid = $expId; ts = (Get-Date).ToUniversalTime().ToString('o')
    arm = $arm; task_id = $card.task_id; track = $card.track; rep = $rep
    score = $score; passed = $passed; total = $total
    questions_asked = $questions.Count
    council_exit = $null
    sham_donor_task = $shamDonorTask
    cost_usd = [math]::Round($runCost, 6); latency_ms = $build.latencyMs
    mock = [bool]$Mock
    flags = @($flags); leak = $leakVerdict
  }
  ($row | ConvertTo-Json -Depth 5 -Compress) | Add-Content -LiteralPath $manifestPath -Encoding UTF8
  $done++
  Write-Host ("[{0}/{1}] arm {2} {3} rep{4} score={5} spend=`${6}" -f $done, $schedule.Count, $arm, $card.task_id, $rep, $score, [math]::Round($script:Spend, 4))
}
} catch {
  if ("$($_.Exception.Message)" -match 'BUDGET-CAP') {
    Write-Host "ABORTED: $($_.Exception.Message) — completed runs are preserved in the manifest."
    exit 4
  }
  throw
}

Write-Host ''
Write-Host "DONE expid=$expId runs=$done total_spend=`$$([math]::Round($script:Spend,4)) manifest=$manifestPath"
exit 0
