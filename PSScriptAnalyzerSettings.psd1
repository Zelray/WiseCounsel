@'
# PSScriptAnalyzer settings for WiseCounsil CI.
#
# This file is the documented record of which lint rules this codebase
# knowingly deviates from, and why. Everything not excluded here is enforced
# at Error + Warning severity in CI (.github/workflows/ci.yml).
#
# Exclusions (apply to the FROZEN skill package in wise-counsil/ and the eval
# harness alike — the package must stay byte-identical during the eval, so
# style deviations there are documented here rather than fixed in place):
#
# - PSUseApprovedVerbs: Invoke-WiseCounsil.ps1 defines Normalize-Result;
#   "Normalize" is not an approved verb. Renaming it would break the frozen
#   measured artifact for zero functional gain.
# - PSAvoidUsingWriteHost: both shipping scripts are interactive CLI tools;
#   Write-Host is the deliberate console-UX choice (colored progress + final
#   dossier), not an accident.
# - PSUseShouldProcessForStateChangingFunctions: these are CLI scripts with
#   exit codes, not interactive cmdlets; -WhatIf/-Confirm support adds
#   surface area without value here.
@'
# NOTE: the here-string above is human documentation; the hashtable below is
# what PSScriptAnalyzer actually consumes (a .psd1 must evaluate to data only).
@{
    Severity     = @('Error', 'Warning')
    ExcludeRules = @(
        'PSUseApprovedVerbs'
        'PSAvoidUsingWriteHost'
        'PSUseShouldProcessForStateChangingFunctions'
    )
}
