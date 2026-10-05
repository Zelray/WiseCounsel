# PSScriptAnalyzer settings for WiseCounsel CI.
#
# This file is the documented record of which lint rules this codebase
# knowingly deviates from, and why. Everything not excluded here is enforced
# at Error + Warning severity in CI (.github/workflows/ci.yml).
#
# Exclusions (apply to the FROZEN skill package in wise-counsel/ and the eval
# harness alike — the package must stay byte-identical during the eval, so
# style deviations there are documented here rather than fixed in place):
#
# - PSUseApprovedVerbs: Invoke-WiseCounsel.ps1 defines Normalize-Result;
#   "Normalize" is not an approved verb. Renaming it would break the frozen
#   measured artifact for zero functional gain.
# - PSAvoidUsingWriteHost: both shipping scripts are interactive CLI tools;
#   Write-Host is the deliberate console-UX choice (colored progress + final
#   dossier), not an accident.
# - PSUseShouldProcessForStateChangingFunctions: these are CLI scripts with
#   exit codes, not interactive cmdlets; -WhatIf/-Confirm support adds
#   surface area without value here.
# - PSUseBOMForUnicodeEncodedFile: several scripts (including the FROZEN
#   wise-counsel package, which must stay byte-identical and therefore can
#   never gain a BOM) use deliberate em-dashes in comments under UTF-8; the
#   rule would force either a BOM rewrite of the frozen artifact or an
#   ASCII-ification churn across the measured pipeline. Documented here
#   instead (2026-10-05, first actual lint run).
# - PSUseSingularNouns: established helper names (Get-Deltas,
#   Get-DeliveredAnswers, Get-EntrySymbols) return collections by design;
#   renaming working pipeline functions to satisfy a style rule is churn
#   without value. Documented here instead (2026-10-05).
#
# NOTE: a .psd1 must evaluate to data only — the documentation above is
# comment lines, not a here-string (a here-string made Invoke-ScriptAnalyzer
# reject the whole file: "does not contain a hashtable"; fixed 2026-10-05
# before the first-ever CI run).
@{
    Severity     = @('Error', 'Warning')
    ExcludeRules = @(
        'PSUseApprovedVerbs'
        'PSAvoidUsingWriteHost'
        'PSUseShouldProcessForStateChangingFunctions'
        'PSUseBOMForUnicodeEncodedFile'
        'PSUseSingularNouns'
    )
}
