#Requires -Version 7.0
<#
.SYNOPSIS
    Grader for WiseCounsil eval task 06 (T1-cutoff-dates).

.DESCRIPTION
    Copies the candidate solution plus the hidden-spec test file into a throwaway
    temp directory, runs the tests there with python, parses the final SCORE line,
    and emits a JSON verdict (to -OutFile when given, otherwise stdout). Never
    prints the solution file's content.

.EXAMPLE
    pwsh -NoProfile -File check-06-cutoff-dates.ps1 -SolutionPath ref-06-cutoff-dates.py
#>
param(
    [Parameter(Mandatory = $true)][string]$SolutionPath,
    [string]$OutFile = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$taskId    = 'T1-cutoff-dates'
$taskDir   = $PSScriptRoot
$testsName = 'tests-06-cutoff-dates.py'
$testsFile = Join-Path $taskDir $testsName

function Fail([string]$Message) {
    Write-Output "CHECK-FAIL $Message"
    exit 3
}

try {
    if (-not (Test-Path -LiteralPath $testsFile)) { Fail "missing tests file: $testsFile" }

    $source = (Resolve-Path -LiteralPath $SolutionPath -ErrorAction Stop).Path

    $tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("wc-eval-06-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

    Copy-Item -LiteralPath $source -Destination (Join-Path $tempDir 'solution.py') -Force
    Copy-Item -LiteralPath $testsFile -Destination (Join-Path $tempDir $testsName) -Force

    $pyExit = $null
    $output = @()
    Push-Location $tempDir
    try {
        $output = @(& python $testsName 'solution.py' 2>&1 | ForEach-Object { "$_" })
        $pyExit = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    $passed = $null
    $total  = $null
    for ($i = $output.Count - 1; $i -ge 0; $i--) {
        if ($output[$i] -match '^SCORE\s+(\d+)/(\d+)\s*$') {
            $passed = [int]$Matches[1]
            $total  = [int]$Matches[2]
            break
        }
    }
    if ($null -eq $passed) { Fail "no SCORE line in test output (python exit $pyExit)" }

    $score = if ($total -gt 0) { [math]::Round($passed / $total, 2) } else { 0 }
    $rawTail = @($output | Select-Object -Last 30)

    $verdict = [ordered]@{
        task_id  = $taskId
        passed   = $passed
        total    = $total
        score    = $score
        raw_tail = $rawTail
    }
    $json = $verdict | ConvertTo-Json -Depth 4

    if ($OutFile) {
        [System.IO.File]::WriteAllText($OutFile, $json + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
    }
    else {
        Write-Output $json
    }

    Write-Output ("CHECK-OK score={0}/{1}" -f $passed, $total)
    exit 0
}
catch {
    Write-Output "CHECK-FAIL $($_.Exception.Message)"
    exit 3
}
