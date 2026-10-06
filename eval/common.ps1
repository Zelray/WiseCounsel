#Requires -Version 7.0
# Shared helpers for the eval drivers. Dot-source, never invoke:
#   . "$PSScriptRoot/common.ps1"

function Get-OpenRouterKey {
  # OpenRouter key from the environment or the client key file. Never printed.
  if ($env:OPENROUTER_API_KEY) { return $env:OPENROUTER_API_KEY }
  $keyFile = Join-Path $HOME '.openrouter-client.key'
  if (Test-Path -LiteralPath $keyFile) { return (Get-Content -LiteralPath $keyFile -Raw).Trim() }
  return ''
}

function Get-FencedPython {
  # Extract the fenced python block from a model response. Whole-content
  # fallback strips bare/unclosed fence lines so a response that opens a fence
  # but never closes it cannot poison the graded file (this zeroed 2 pilot
  # baseline runs; see wave-2 addendum).
  param([string]$Content, [string]$RunDir)
  $m = [regex]::Match($Content, '(?s)```python\s*(.*?)```')
  $code = if ($m.Success) { $m.Groups[1].Value }
          else { ($Content -replace '(?m)^\s*```(python)?\s*$', '').Trim() }
  $p = Join-Path $RunDir 'solution.py'
  Set-Content -LiteralPath $p -Value $code -Encoding UTF8
  return $p
}
