# Gates: v0.2.0 product pivot (2026-10-05)

> v0.2.0 acceptance ledger, same discipline as `GATES-WAVE2.md` (which stays as
> history). Each gate states one observable outcome; runnable gates carry the
> exact command (`CHECK`) and success marker (`EXPECT`). V7 is a live
> behavioral exercise recorded by hand. Per `HANDOFF-V02-PIVOT.md`: no
> Track-1/Track-2 re-runs, no new API spend of any kind, measurement history
> untouched, freeze drift noted (not re-frozen).

OWNS: wise-counsel/SKILL.md, README.md, docs/DESIGN.md, Agents.md, CLAUDE.md,
CHANGELOG.md (new), STATUS.md, eval/config.json, eval/Invoke-Eval.ps1,
GATES-V02.md (this ledger), HANDOFF-V02-BUILD.md (session record)
NOT-OURS: eval/tasks/**, eval/results/**, eval/FROZEN-HASHES.txt,
eval/FROZEN-HASHES-wave2.txt, eval/FROZEN-HASHES-v3.txt (measurement history),
docs/EVAL-DESIGN.md, docs/RESULTS.md (no new efficacy claims in this build),
wise-counsel/scripts/Invoke-WiseCounsel.ps1, wise-counsel/config/**
(no engine/roster changes required by the pivot)

Scope: ship the proven scaffold as the product default — a new `clarify` mode
where the frontier agent itself generates at most 5 build-changing questions
(the wave-2 arm-C shape, empty-dossier form), asks the user, and merges answers
into an enriched brief with a verify-later checklist; council modes
(`premortem`/`debate`/`critique`) keep working exactly as today but run only on
explicit opt-in ("convene the council"). Bundled: Track-2 judge plumbing fix
(per-judge response files, strict JSON-only instruction, maxTokens above the
truncating 512) — code only, NO re-run. Docs re-led honestly (scaffold is the
product; council is opt-in diversity), README raw-transcript overclaim fixed,
CHANGELOG created, version 0.2.0. Zero model spend in this entire build.

- [x] V1: `clarify` is the DEFAULT mode in `wise-counsel/SKILL.md` with the full arm-C protocol — mode table lists clarify first and marked default; the protocol generates AT MOST 5 build-changing questions, presents them to the user, merges answers (with a best-judgment fallback), and produces the ENRICHED BRIEF + VERIFY-LATER structure using the self-analysis shape ("rely on your own analysis"); prime directive 5 states clarify is the default and the council runs only on explicit opt-in ("convene the council"); frontmatter description re-leaded on clarify with council opt-in and the $0 cost stated
  CHECK: pwsh -NoProfile -Command "$s = Get-Content 'wise-counsel/SKILL.md' -Raw; $req = '(?im)^\|.*clarify.*default','at most 5','ENRICHED BRIEF','VERIFY-LATER','rely on your own analysis','(?i)convene the council','(?i)opt-in','\$0','(?i)build-changing'; $miss = @($req | Where-Object { $s -notmatch $_ }); if ($miss.Count -eq 0) { 'V1-CLARIFY-DEFAULT' } else { \"MISSING: $($miss -join ', ')\"; exit 1 }"
  EXPECT: V1-CLARIFY-DEFAULT
  EVIDENCE: 2026-10-05 — `V1-CLARIFY-DEFAULT` (first run, all 9 markers matched). Council templates (Step 6) kept VERBATIM from v0.1.0 — they are the measured arm-B path; only the protocol around them changed (mode table, directive 5, new Step 2 clarify, roster/council steps renumbered and gated on explicit opt-in).

- [x] V2: Council/engine path still passes the offline end-to-end smoke after the judge-plumbing changes (mock pipeline, zero network, zero spend, analyzer table)
  CHECK: pwsh -NoProfile -File eval/Invoke-DryRunSmoke.ps1
  EXPECT: DRYRUN-SMOKE-PASSED
  EVIDENCE: 2026-10-05 — `DRYRUN-SMOKE-PASSED (175 runs, 35 tasks, spend=$0, network=none)`, run by the judge-fix agent AND re-run independently by the parent after the fix landed (parent re-verification). Run-count growth vs wave-2's "40 runs/8 tasks" is the expanded wave-2 task suite being picked up by the mock smoke — expected, not a regression.

- [x] V3: Installer green in offline CI-parity mode (roster sanity, key presence, both skill dirs written)
  CHECK: pwsh -NoProfile -File wise-counsel/scripts/Install-WiseCounsel.ps1 -OpenCode -Claude -SkipValidation
  EXPECT: Installed:
  EVIDENCE: 2026-10-05 — `Installed:` x2 (both `~\.config\opencode\skills\wise-counsel` and `~\.claude\skills\wise-counsel`), `Roster: 6 models (DeepSeek, Alibaba, Mistral, OpenAI-open, Meta, Google)`, `OpenRouter key present: True`, EXIT=0.

- [x] V4: Local CI-parity battery passes — all .ps1 parse clean, all validated JSON parses, PSScriptAnalyzer (repo settings) zero findings
  CHECK: pwsh -NoProfile -Command "$fails = @(); $scripts = @(Get-ChildItem -Recurse -Filter *.ps1 | Where-Object { $_.FullName -notmatch '\\results\\|\\.unlazy' }); foreach ($s in $scripts) { $t = $null; $e = $null; [System.Management.Automation.Language.Parser]::ParseFile($s.FullName, [ref]$t, [ref]$e) | Out-Null; if ($e.Count -gt 0) { $fails += \"parse $($s.Name): $($e[0].Message)\" } }; $json = @(Get-ChildItem wise-counsel/config/*.json) + @(Get-ChildItem eval/*.json) + @(Get-ChildItem eval/tasks/*.json -ErrorAction SilentlyContinue); foreach ($f in $json) { try { Get-Content $f.FullName -Raw | ConvertFrom-Json | Out-Null } catch { $fails += \"json $($f.Name): $($_.Exception.Message)\" } }; if (-not (Get-Module -ListAvailable PSScriptAnalyzer)) { Install-Module PSScriptAnalyzer -Force -Scope CurrentUser }; $lint = @(Invoke-ScriptAnalyzer -Path . -Settings ./PSScriptAnalyzerSettings.psd1 -Recurse); if ($lint.Count -gt 0) { $fails += ($lint | ForEach-Object { \"lint $($_.ScriptName): $($_.Message)\" }) }; if ($fails.Count -eq 0) { \"V4-CI-PARITY-OK (parse=$($scripts.Count) json=$($json.Count) lint=0)\" } else { $fails; exit 1 }"
  EXPECT: V4-CI-PARITY-OK
  EVIDENCE: 2026-10-05 — `V4-CI-PARITY-OK (parse=38 json=38 lint=0)` on the final tree (parent-run). Judge-fix agent independently reported PARSE_ERRORS=0 / LINT_FINDINGS=0 on its own footprint.

- [x] V5: Docs current and honest — README leads with the scaffold framing and no longer claims raw transcripts ship in the repo (states summaries + manifest ship, raw retained locally); DESIGN.md has a "what wave 2 taught us" section; CHANGELOG.md exists with a v0.2.0 entry; Agents.md and CLAUDE.md describe clarify-default/council-opt-in; STATUS.md carries v0.2.0
  CHECK: pwsh -NoProfile -Command "$r = Get-Content 'README.md' -Raw; $d = Get-Content 'docs/DESIGN.md' -Raw; $c = Get-Content 'CHANGELOG.md' -Raw; $a = Get-Content 'Agents.md' -Raw; $cl = Get-Content 'CLAUDE.md' -Raw; $st = Get-Content 'STATUS.md' -Raw; $fail = @(); if ($r -notmatch '(?i)clarify') { $fail += 'README: no clarify' }; if ($r -match 'ship in the repo') { $fail += 'README: overclaim still present' }; if ($r -notmatch '(?i)retained locally|not ship|kept locally|lives only on') { $fail += 'README: honesty fix wording missing' }; if ($d -notmatch '(?i)wave 2.{0,400}taught|taught us') { $fail += 'DESIGN: no wave-2 section' }; if ($c -notmatch '0\.2\.0') { $fail += 'CHANGELOG: no 0.2.0' }; if ($a -notmatch '(?i)clarify') { $fail += 'Agents.md: no clarify' }; if ($cl -notmatch '(?i)clarify') { $fail += 'CLAUDE.md: no clarify' }; if ($st -notmatch '0\.2\.0') { $fail += 'STATUS: no 0.2.0' }; if ($fail.Count -eq 0) { 'V5-DOCS-CURRENT' } else { $fail; exit 1 }"
  EXPECT: V5-DOCS-CURRENT
  EVIDENCE: 2026-10-05 — `V5-DOCS-CURRENT`. Beyond the greps: the README agent verified every wave-2 number character-identical (incl. U+2212 minus signs) and 0 matches for "ship in the repo"; the DESIGN agent cross-checked every figure against docs/RESULTS.md line-by-line (+61 lines, 0 deletions to existing sections).

- [x] V6: Live installs refreshed and identical to the repo package — installed SKILL.md hashes match the repo copy for both targets and contain the clarify markers
  CHECK: pwsh -NoProfile -Command "$repo = (Get-FileHash 'wise-counsel/SKILL.md').Hash; $targets = @(\"$HOME\.claude\skills\wise-counsel\SKILL.md\", \"$HOME\.config\opencode\skills\wise-counsel\SKILL.md\"); $fail = @(); foreach ($t in $targets) { if (-not (Test-Path $t)) { $fail += \"missing: $t\"; continue }; if ((Get-FileHash $t).Hash -ne $repo) { $fail += \"stale: $t\" } ; if ((Get-Content $t -Raw) -notmatch '(?i)clarify') { $fail += \"no-clarify: $t\" } }; if ($fail.Count -eq 0) { 'V6-INSTALL-SYNCED' } else { $fail; exit 1 }"
  EXPECT: V6-INSTALL-SYNCED
  EVIDENCE: 2026-10-05 — `V6-INSTALL-SYNCED` (hash match + clarify marker on both targets). Corroborating live signal: the running Claude Code session's skill registry hot-reloaded and now lists the NEW clarify-first description for wise-counsel.

- [x] V7: MANUAL — clarify mode exercised end-to-end LIVE in-session at zero cost: on a sample brief the frontier agent generates at most 5 build-changing questions, presents them, applies the best-judgment fallback, and produces the enriched brief + verify-later checklist; transcript recorded in EVIDENCE (no sub-models, no API spend)
  EVIDENCE: 2026-10-05 — exercised live in the build session on the sample brief "CLI tool that splits a restaurant bill among N people, with tip and per-item adjustments": exactly 5 build-changing questions generated (identity of diners / per-item claim mechanics / tip mode+tax base / tax source / output format), each with a parenthesized default; user reply simulated as "use best judgment" → all 5 defaults adopted and carried as explicit assumptions; produced ENRICHED BRIEF (~180 words, user intent intact, assumptions stated) + 4-item VERIFY-LATER checklist. Zero sub-model calls, zero API spend, no `runs/` writes. Transcript preserved in the session record; protocol followed exactly as written in SKILL.md Step 2 (2a→2b→2c).

- [x] V8: Measurement history untouched — the changed-file set is exactly the OWNS set; zero modifications under eval/tasks/**, eval/results/**, any FROZEN-HASHES*.txt, docs/EVAL-DESIGN.md, docs/RESULTS.md, and the engine/roster (wise-counsel/scripts/Invoke-WiseCounsel.ps1, wise-counsel/config/**); freeze drift vs FROZEN-HASHES-v3.txt recorded in the handoff, not re-frozen
  CHECK: pwsh -NoProfile -Command "$changed = @(git status --porcelain | ForEach-Object { $_.Substring(3).Trim('\"') }); $protected = @($changed | Where-Object { $_ -match '^eval/(tasks|results)/' -or $_ -match 'FROZEN-HASHES' -or $_ -match 'EVAL-DESIGN\.md' -or $_ -match 'docs/RESULTS\.md' -or $_ -match 'Invoke-WiseCounsel\.ps1' -or $_ -match 'wise-counsel/config/' }); if ($protected.Count -eq 0) { \"V8-HISTORY-UNTOUCHED (changed=$($changed.Count) files)\" } else { \"PROTECTED FILES TOUCHED: $($protected -join ', ')\"; exit 1 }"
  EXPECT: V8-HISTORY-UNTOUCHED
  EVIDENCE: 2026-10-05 — `V8-HISTORY-UNTOUCHED (changed=10 files)`: exactly the OWNS set (Agents.md, CLAUDE.md, README.md, STATUS.md, docs/DESIGN.md, eval/Invoke-Eval.ps1, eval/config.json, wise-counsel/SKILL.md, CHANGELOG.md, GATES-V02.md) + HANDOFF-V02-BUILD.md added post-check (also OWNS-listed in this ledger's companion docs). Freeze drift captured for the record: vs FROZEN-HASHES-v3.txt drift = EXACTLY eval/config.json + wise-counsel/SKILL.md (the two deliberate edits; FREEZE-CHANGED exit 1, expected, NOT re-frozen); vs FROZEN-HASHES-wave2.txt the extra 5 entries are the pre-v0.2.0 rename commit, already covered by the rename addendum. Zero drift anywhere in eval/tasks/** or eval/results/** — all three graders/freeze checkers that ran today confirmed the measurement history is byte-intact.

- [x] V9: Published — conventional-commit push to main, GitHub Actions CI green on the push, tag v0.2.0 created and pushed (repo operations pre-approved per HANDOFF-V02-PIVOT machine notes; no spend involved)
  CHECK: pwsh -NoProfile -Command "$run = gh run list --limit 1 --json conclusion,displayTitle --jq '.[0]'; $tag = git tag -l v0.2.0; if ($run -match 'success' -and $tag -eq 'v0.2.0') { 'V9-PUBLISHED-CI-GREEN' } else { \"run=$run tag=$tag\"; exit 1 }"
  EXPECT: V9-PUBLISHED-CI-GREEN
  EVIDENCE: 2026-10-05 — build commit `19eb6b9` (10 files, +439/−107) pushed; CI run 37346732064 GREEN in 35 s (parse / JSON / lint / installer smoke / eval dry-run all ✓; one upstream annotation: GitHub's Node.js-20 deprecation notice on actions/checkout@v4 — repo housekeeping, not this change). Closeout commit with this ledger's final state pushed, ITS CI verified green, then tagged `v0.2.0` and the tag pushed. No spend.

## Scope exclusions (recorded, not gates)

- **Track-2 re-run ($<0.50): intentionally NOT executed.** New API spend
  requires Mike's explicit go plus a dated prereg addendum before data
  (HANDOFF-V02-PIVOT §4). The judge-plumbing fix is code-only.
- **Freeze re-issue: intentionally NOT done.** SKILL.md and the two eval files
  will drift vs `eval/FROZEN-HASHES-v3.txt` by design; per the pivot handoff,
  a pure product change notes the drift instead of re-freezing. Re-freeze
  (v4) only if/when a v0.2 measurement actually happens.
- **`Invoke-WiseCounsel.ps1` `-OutDir` default** (STATUS known-issue): not in
  the v0.2.0 scope list; left for a follow-up.
