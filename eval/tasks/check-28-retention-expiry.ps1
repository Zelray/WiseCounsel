#Requires -Version 7
<#
.SYNOPSIS
    Grader for task 28 (T1-retention-expiry). Copies the submitted solution into a
    temp dir, runs the hidden-spec unittest file there, and emits a JSON verdict.
#>
param(
    [Parameter(Mandatory = $true)][string]$SolutionPath,
    [string]$OutFile = ''
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$taskId = 'T1-retention-expiry'
$taskDir = $PSScriptRoot
$testsFile = Join-Path $taskDir 'tests-28-retention-expiry.py'

function Fail([string]$Message) {
    # Machinery failure: report on stderr and exit 3 (Write-Error would throw under
    # ErrorActionPreference=Stop and mask the exit code, so write to the stream directly).
    [Console]::Error.WriteLine("CHECK-FAIL ($taskId): $Message")
    exit 3
}

if (-not (Test-Path -LiteralPath $testsFile -PathType Leaf)) {
    Fail "tests file not found: $testsFile"
}

$resolvedSolution = $null
try {
    $resolvedSolution = (Resolve-Path -LiteralPath $SolutionPath -ErrorAction Stop).Path
} catch {
    Fail "solution file not found: $SolutionPath"
}
if (-not (Test-Path -LiteralPath $resolvedSolution -PathType Leaf)) {
    Fail "solution path is not a file: $resolvedSolution"
}

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("wc-check-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

try {
    Copy-Item -LiteralPath $resolvedSolution -Destination (Join-Path $tempDir 'solution.py')
    Copy-Item -LiteralPath $testsFile -Destination $tempDir

    Push-Location $tempDir
    try {
        $output = & python 'tests-28-retention-expiry.py' 'solution.py' 2>&1
        $pyExit = $LASTEXITCODE
    } finally {
        Pop-Location
    }

    $text = ($output | ForEach-Object { "$_" }) -join "`n"
    $scoreMatches = [regex]::Matches($text, 'SCORE\s+(\d+)\s*/\s*(\d+)')
    if ($scoreMatches.Count -eq 0) {
        Fail "no SCORE line in tests output (python exit=$pyExit)"
    }
    $last = $scoreMatches[$scoreMatches.Count - 1]
    $passed = [int]$last.Groups[1].Value
    $total = [int]$last.Groups[2].Value
    $score = if ($total -gt 0) { [math]::Round($passed / $total, 2) } else { 0 }

    $rawTail = @($output | ForEach-Object { "$_" } | Select-Object -Last 30)

    $verdict = [ordered]@{
        task_id  = $taskId
        passed   = $passed
        total    = $total
        score    = $score
        raw_tail = $rawTail
    }
    $json = $verdict | ConvertTo-Json -Depth 4

    if ($OutFile) {
        Set-Content -LiteralPath $OutFile -Value $json -Encoding utf8NoBOM
    } else {
        Write-Output $json
    }

    Write-Output "CHECK-OK score=$passed/$total"
    exit 0
} finally {
    Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
