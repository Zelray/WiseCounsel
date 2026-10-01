<#
.SYNOPSIS
    Grader harness for eval task 01 - T1-overtime.

.DESCRIPTION
    Copies the candidate solution and the task's tests file into a throwaway
    temp dir, runs the stdlib unittest grader there with python, parses the
    final SCORE line, and emits a small JSON report. The candidate's source
    is never printed.

    Exit 0 = machinery worked (even a 0/10 score), exit 3 = machinery failure.
#>
param(
    [Parameter(Mandatory = $true)][string]$SolutionPath,
    [string]$OutFile = ''
)

$taskId = 'T1-overtime'
$testsName = 'tests-01-overtime.py'
$taskDir = $PSScriptRoot

function Write-Fail {
    param([string]$Message)
    Write-Output "CHECK-FAIL $Message"
    exit 3
}

if ([string]::IsNullOrWhiteSpace($SolutionPath)) { Write-Fail 'no solution path given' }
if (-not (Test-Path -LiteralPath $SolutionPath -PathType Leaf)) { Write-Fail "solution not found: $SolutionPath" }

$testsPath = Join-Path $taskDir $testsName
if (-not (Test-Path -LiteralPath $testsPath -PathType Leaf)) { Write-Fail "tests file missing: $testsPath" }

$python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $python) { Write-Fail 'python not found on PATH' }

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("wc-eval-01-" + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

$completed = $false
try {
    Copy-Item -LiteralPath $SolutionPath -Destination (Join-Path $tempDir 'solution.py') -Force
    Copy-Item -LiteralPath $testsPath -Destination (Join-Path $tempDir $testsName) -Force

    Push-Location $tempDir
    try {
        $output = & python $testsName 'solution.py' 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    $lines = @($output | ForEach-Object { "$_" })
    if ($exitCode -ne 0) {
        $tail = ($lines | Select-Object -Last 5) -join ' | '
        Write-Fail "python exited $exitCode : $tail"
    }

    $scoreLine = @($lines | Where-Object { $_ -match '^SCORE (\d+)/(\d+)\s*$' })[-1]
    if ([string]::IsNullOrWhiteSpace($scoreLine)) { Write-Fail 'no SCORE line produced by the tests file' }
    $null = $scoreLine -match '^SCORE (\d+)/(\d+)\s*$'
    $passed = [int]$Matches[1]
    $total = [int]$Matches[2]
    $score = if ($total -gt 0) { [math]::Round($passed / $total, 2) } else { 0 }

    $report = [ordered]@{
        task_id  = $taskId
        passed   = $passed
        total    = $total
        score    = $score
        raw_tail = @($lines | Select-Object -Last 30)
    }
    $json = $report | ConvertTo-Json -Depth 3

    if ([string]::IsNullOrWhiteSpace($OutFile)) {
        Write-Output $json
    }
    else {
        Set-Content -LiteralPath $OutFile -Value $json -Encoding utf8
    }
    $completed = $true
}
finally {
    Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}

if (-not $completed) { exit 3 }
Write-Output "CHECK-OK score=$passed/$total"
exit 0
