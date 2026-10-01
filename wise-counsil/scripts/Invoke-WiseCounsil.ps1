#Requires -Version 7.0
<#
.SYNOPSIS
  WiseCounsil: fire 2-6 cheap/free models in parallel to pre-think a task.
.DESCRIPTION
  Door A (OpenRouter) engine for the wise-counsil skill. Sends the user's
  verbatim prompt to each roster member with a strict attack-don't-answer
  template, collects responses, and prints a per-model dossier.
  Debate mode adds round 2 (peer rebuttals, anonymized, sequential).
  Never prints or logs the API key.
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)][ValidateSet('premortem','debate','critique')][string]$Mode,
  [string]$Task = '',
  [string]$TaskFile = '',
  [string]$Context = '',
  [string]$ConfigPath = '',
  [string]$Preset = '',
  [string[]]$Models = @(),
  [int]$Rounds = 0,
  [int]$MaxOutputTokens = 0,
  [string]$OutDir = '',
  [string]$ApiKey = ''
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$skillRoot = Split-Path -Parent $PSScriptRoot

# --- resolve task text -------------------------------------------------------
if (-not $Task -and $TaskFile) {
  if (-not (Test-Path -LiteralPath $TaskFile)) { Write-Host "ERROR: TaskFile not found: $TaskFile"; exit 3 }
  $Task = Get-Content -LiteralPath $TaskFile -Raw
}
if (-not $Task) { Write-Host "ERROR: no task given (use -Task or -TaskFile)"; exit 3 }

# --- resolve config ----------------------------------------------------------
if (-not $ConfigPath) { $ConfigPath = Join-Path $skillRoot 'config\wisecounsil.json' }
if (-not (Test-Path -LiteralPath $ConfigPath)) { Write-Host "ERROR: config not found: $ConfigPath"; exit 3 }
$cfg = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json

if ($cfg.provider -ne 'openrouter') {
  Write-Host "ERROR: this script only serves provider 'openrouter'; configured provider is '$($cfg.provider)'. Use the OpenCodeGo subagent door (see SKILL.md)."
  exit 3
}

# --- resolve model list ------------------------------------------------------
if ($Preset) {
  $presetsPath = Join-Path $skillRoot 'config\presets.json'
  if (-not (Test-Path -LiteralPath $presetsPath)) { Write-Host "ERROR: presets not found: $presetsPath"; exit 3 }
  $presets = Get-Content -LiteralPath $presetsPath -Raw -Encoding UTF8 | ConvertFrom-Json
  if (-not $presets.$Preset) { Write-Host "ERROR: unknown preset '$Preset'"; exit 3 }
  $Models = @($presets.$Preset | ForEach-Object { $_.id })
}
if ($Models.Count -eq 0) { $Models = @($cfg.models | ForEach-Object { $_.id }) }
if ($Models.Count -lt $cfg.minModels) { Write-Host "ERROR: need at least $($cfg.minModels) models, got $($Models.Count)"; exit 3 }
if ($Models.Count -gt $cfg.maxModels) {
  Write-Host "NOTE: roster capped to $($cfg.maxModels) (was $($Models.Count))"
  $Models = $Models[0..($cfg.maxModels - 1)]
}
$labels = @{}
foreach ($m in $cfg.models) { $labels[$m.id] = $m.label }

# --- resolve key (never printed) ---------------------------------------------
$key = $ApiKey
if (-not $key -and $env:OPENROUTER_API_KEY) { $key = $env:OPENROUTER_API_KEY }
if (-not $key) {
  $keyFile = Join-Path $HOME '.openrouter-client.key'
  if (Test-Path -LiteralPath $keyFile) { $key = (Get-Content -LiteralPath $keyFile -Raw).Trim() }
}
if (-not $key) { Write-Host "ERROR: no OpenRouter key (set OPENROUTER_API_KEY or create ~\.openrouter-client.key)"; exit 3 }

# --- mode parameters ---------------------------------------------------------
if ($Rounds -le 0) { $Rounds = if ($Mode -eq 'debate') { 2 } else { 1 } }
$Rounds = [Math]::Min($Rounds, 2)
if ($MaxOutputTokens -le 0) { $MaxOutputTokens = $cfg.limits.maxOutputTokens }
$timeout = $cfg.limits.timeoutSec
$temp = if ($Mode -eq 'debate') { $cfg.limits.temperatureDebate } else { $cfg.limits.temperaturePremortem }

$templates = @{
  premortem = @'
You are one member of a cheap-model "pre-think council". A senior AI engineer will implement the TASK BRIEF below. Your job is to attack the brief BEFORE implementation. Do not solve the task.

Produce EXACTLY these five sections, no preamble:
## Missing
Unstated requirements, domain rules, edge cases, inputs/outputs, or data the implementer would have to guess.
## Ambiguous
Places where two reasonable readings would produce two different builds. State both readings.
## Risky assumptions
Assumptions that may not hold. Phrase each as a question to verify ("Verify: ..."), never as a fact.
## Approach sketch
Your build approach in at most 5 bullets. No code.
## Watchlist
The 2-3 things most likely to make the finished product wrong or unusable.

Rules: max 300 words total. No code. If you are unsure whether something is true, phrase it as a verification question. Do not restate the task back.
'@
  critique = @'
You are one member of a cheap-model review council. A senior AI engineer wrote the PLAN below. Attack the plan BEFORE it is executed. Do not rewrite it.

Produce EXACTLY these five sections, no preamble:
## Missing
Steps, requirements, or edge cases the plan does not cover.
## Ambiguous
Steps two engineers would read differently. State both readings.
## Risky assumptions
Assumptions that may not hold. Phrase each as a question to verify ("Verify: ..."), never as a fact.
## Sequencing risks
Steps that depend on each other in ways the plan ignores.
## Watchlist
The 2-3 things most likely to make the executed result wrong or broken.

Rules: max 300 words total. No code. Do not restate the plan back.
'@
  debate1 = @'
You are one member of an independent analysts' council. QUESTION: {0}

Give your position in EXACTLY this structure, max 350 words, no preamble:
## Position
One paragraph. Take a real stance; do not hedge into "it depends" without resolving it.
## Key evidence
3-5 bullets. For each: the claim, and whether it is (a) verifiable fact you are confident in, (b) plausible inference, or (c) speculation. Label each bullet (a)/(b)/(c).
## What would change my mind
The 2-3 strongest counter-considerations, stated fairly.
## Confidence
Low / Medium / High, with one sentence why.
'@
  debate2 = @'
You are the same council member, now shown your peers' round-1 positions (anonymized):

{0}

Update your position in EXACTLY this structure, max 300 words, no preamble:
## Rebuttal
Where your peers are wrong, and specifically why. Attack the STRONGEST peer argument, not the weakest.
## Concession
What a peer said that you now think is right, and why it moved you (or "none").
## Updated position
One paragraph, final stance.
## Confidence
Low / Medium / High + one sentence.
'@
}

$subject = $Task
if ($Context) { $subject = "$Task`n`nCONTEXT / MATERIALS:`n$Context" }
$sys = if ($Mode -eq 'debate') { $templates.debate1 -f $subject } else { $templates[$Mode] + "`n`nSUBJECT:`n$subject" }

# --- run directory -----------------------------------------------------------
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
if (-not $OutDir) { $OutDir = Join-Path $skillRoot "runs\$stamp-$Mode" }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function Get-Label([string]$id) {
  if ($labels.ContainsKey($id)) { return $labels[$id] }
  return ($id -replace '^[^/]+/', '')
}

function Normalize-Result($rows) {
  foreach ($r in $rows) {
    if ($r.ok -and [string]::IsNullOrWhiteSpace("$($r.content)")) {
      $r.ok = $false
      $r.error = 'empty content (reasoning budget likely exhausted or provider glitch)'
    }
  }
}

# --- round 1: parallel dispatch ---------------------------------------------
Write-Host "WiseCounsil: convening $($Models.Count) members ($Mode), round 1 (parallel)..."
$sys1 = $sys
$r1 = $Models | ForEach-Object -Parallel {
  $model = $_   # capture BEFORE try/catch: inside catch, $_ is the ErrorRecord
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  try {
    $bodyObj = @{
      model       = $model
      messages    = @(
        @{ role = 'system'; content = $using:sys1 },
        @{ role = 'user';   content = 'Proceed.' }
      )
      max_tokens  = $using:MaxOutputTokens
      temperature = $using:temp
      reasoning   = @{ exclude = $true }
      usage       = @{ include = $true }
    }
    $body = $bodyObj | ConvertTo-Json -Depth 6
    $resp = Invoke-RestMethod -Uri 'https://openrouter.ai/api/v1/chat/completions' -Method Post -Headers @{
      Authorization = "Bearer $($using:key)"
      'X-Title'     = 'WiseCounsil'
    } -ContentType 'application/json; charset=utf-8' -Body $body -TimeoutSec $using:timeout
    [pscustomobject]@{
      ok = $true; model = $model; round = 1
      content = $resp.choices[0].message.content
      tokens = $resp.usage.total_tokens; cost = $resp.usage.cost
      latencyMs = $sw.ElapsedMilliseconds; error = ''
    }
  } catch {
    $err = $_.Exception.Message
    if ($_.ErrorDetails -and $_.ErrorDetails.Message) { $err = $_.ErrorDetails.Message }
    [pscustomobject]@{
      ok = $false; model = $model; round = 1
      content = ''; tokens = 0; cost = 0
      latencyMs = $sw.ElapsedMilliseconds; error = $err
    }
  }
} -ThrottleLimit 6

Normalize-Result $r1

# --- round 2 (debate only): sequential, anonymized peers ---------------------
$ok1 = @($r1 | Where-Object { $_.ok })
if ($Mode -eq 'debate' -and $ok1.Count -ge 2 -and $Rounds -ge 2) {
  Write-Host "WiseCounsil: round 2 (peer rebuttals, sequential)..."
  $letters = 'ABCDEFGH'
  $peers = New-Object System.Text.StringBuilder
  for ($i = 0; $i -lt $ok1.Count; $i++) {
    [void]$peers.AppendLine("Analyst $($letters[$i]):")
    [void]$peers.AppendLine($ok1[$i].content)
    [void]$peers.AppendLine('')
  }
  $sys2 = $templates.debate2 -f $peers.ToString()
  $r2 = foreach ($m in $ok1) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
      $bodyObj = @{
        model = $m.model
        messages = @(
          @{ role = 'system'; content = $sys2 },
          @{ role = 'user';   content = 'Proceed.' }
        )
        max_tokens = $MaxOutputTokens
        temperature = $temp
        reasoning = @{ exclude = $true }
        usage = @{ include = $true }
      }
      $body = $bodyObj | ConvertTo-Json -Depth 6
      $resp = Invoke-RestMethod -Uri 'https://openrouter.ai/api/v1/chat/completions' -Method Post -Headers @{
        Authorization = "Bearer $key"
        'X-Title' = 'WiseCounsil'
      } -ContentType 'application/json; charset=utf-8' -Body $body -TimeoutSec $timeout
      [pscustomobject]@{ ok = $true; model = $m.model; round = 2; content = $resp.choices[0].message.content; tokens = $resp.usage.total_tokens; cost = $resp.usage.cost; latencyMs = $sw.ElapsedMilliseconds; error = '' }
    } catch {
      $err = $_.Exception.Message
      if ($_.ErrorDetails -and $_.ErrorDetails.Message) { $err = $_.ErrorDetails.Message }
      [pscustomobject]@{ ok = $false; model = $m.model; round = 2; content = ''; tokens = 0; cost = 0; latencyMs = $sw.ElapsedMilliseconds; error = $err }
    }
  }
  Normalize-Result $r2
  $all = @($r1) + @($r2)
} else {
  $all = @($r1)
}

# --- dossier ------------------------------------------------------------------
$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("# WiseCounsil dossier")
[void]$sb.AppendLine("mode=$Mode rounds=$Rounds date=$stamp outDir=$OutDir")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("TASK (verbatim):")
[void]$sb.AppendLine($Task)
[void]$sb.AppendLine("")
$totalCost = 0.0; $totalTokens = 0
foreach ($r in $all) {
  $tag = Get-Label $r.model
  [void]$sb.AppendLine("---")
  if ($r.ok) {
    $totalCost += [double]$r.cost; $totalTokens += [int]$r.tokens
    [void]$sb.AppendLine("## [$tag] ($($r.model)) round=$($r.round) $([math]::Round($r.latencyMs/1000,1))s cost=$($r.cost)")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine($r.content)
  } else {
    [void]$sb.AppendLine("## [$tag] ($($r.model)) round=$($r.round) FAILED after $([math]::Round($r.latencyMs/1000,1))s")
    [void]$sb.AppendLine("error: $($r.error)")
  }
  [void]$sb.AppendLine("")
}
[void]$sb.AppendLine("---")
[void]$sb.AppendLine("TOTAL: $($ok1.Count)/$($Models.Count) round-1 successes, $totalTokens tokens, cost=$totalCost")

$dossier = $sb.ToString()
$dossierPath = Join-Path $OutDir 'dossier.md'
$rawPath = Join-Path $OutDir 'raw.json'
Set-Content -LiteralPath $dossierPath -Value $dossier -Encoding UTF8
$all | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $rawPath -Encoding UTF8

Write-Host ""
Write-Host $dossier
if ($ok1.Count -eq 0) { exit 2 }
exit 0
