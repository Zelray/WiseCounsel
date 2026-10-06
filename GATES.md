# Gates: eval-harness scaffold + public-GitHub readiness (2026-10-01)

> What a public reader needs to know: this is the repo's machine-checkable
> acceptance ledger. Each gate states one observable outcome; runnable gates
> carry the exact command that decides them (`CHECK`) and the success marker
> (`EXPECT`) they must emit. Gate G7 is a human approval gate and is recorded
> by hand.

OWNS: eval/**, docs/EVAL-DESIGN.md, docs/RESULTS.md, README.md, LICENSE, .github/**, .gitignore, GATES.md

Scope: A tested eval harness (dry-run first, $0), a preregistered methodology doc,
a pilot task suite with ground-truth checkers, and public-repo readiness artifacts —
with the shipping skill package byte-identical throughout.

- [x] G1: Preregistration methodology doc exists and contains every required section (hypothesis, arms, tasks, grading, stats, budget, honesty plan)
  CHECK: pwsh -NoProfile -Command "$h = Get-Content 'docs/EVAL-DESIGN.md' -Raw; $req = 'Hypothesis','Arm A','Arm B','Arm C','Ground truth','Judge','Statistics','Budget','Preregistration'; $miss = @($req | Where-Object { $h -notmatch [regex]::Escape($_) }); if ($miss.Count -eq 0) { 'EVAL-DESIGN-COMPLETE' } else { \"MISSING: $($miss -join ', ')\"; exit 1 }"
  EXPECT: EVAL-DESIGN-COMPLETE
  EVIDENCE: 2026-10-01 — ran CHECK inline, output `G1: EVAL-DESIGN-COMPLETE`. Doc written after 4-agent debate (skeptic/builder/architect/prior-art) and BEFORE any data collection.

- [x] G2: Task suite has at least 6 task cards, all valid JSON, each with a checker script that parses
  CHECK: pwsh -NoProfile -Command "$cards = Get-ChildItem 'eval/tasks' -Filter 'task-*.json' -ErrorAction Stop; $bad = @(); foreach ($c in $cards) { try { Get-Content $c.FullName -Raw | ConvertFrom-Json | Out-Null } catch { $bad += $c.Name } }; $chks = Get-ChildItem 'eval/tasks' -Filter 'check-*.ps1' -ErrorAction Stop; $parseFail = @(); foreach ($k in $chks) { $t=$null;$e=$null; [System.Management.Automation.Language.Parser]::ParseFile($k.FullName,[ref]$t,[ref]$e) | Out-Null; if ($e.Count -gt 0) { $parseFail += $k.Name } }; if ($cards.Count -ge 6 -and $bad.Count -eq 0 -and $parseFail.Count -eq 0) { \"TASKS-OK count=$($cards.Count) checkers=$($chks.Count)\" } else { \"BAD json=$($bad -join ',') parse=$($parseFail -join ',') count=$($cards.Count)\"; exit 1 }"
  EXPECT: TASKS-OK count=
  EVIDENCE: 2026-10-01 — output `G2: TASKS-OK count=8 checkers=6` (6 hidden-spec + 2 decision cards; the 6 Track-1 graders each verified 10/10 against reference solutions, negative-control stubs scored 0-7/10 as expected, verified directly in-session after an inter-agent bug report on task 05 was investigated and disproven).

- [x] G3: Every PowerShell script in eval/ parses clean (no syntax errors)
  CHECK: pwsh -NoProfile -Command "$fails=@(); Get-ChildItem 'eval' -Recurse -Filter '*.ps1' | ForEach-Object { $t=$null;$e=$null; [System.Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$t,[ref]$e) | Out-Null; if ($e.Count -gt 0) { $fails += "$($_.Name): $($e[0].Message)" } }; if ($fails.Count -eq 0) { 'PARSE-CLEAN' } else { $fails; exit 1 }"
  EXPECT: PARSE-CLEAN
  EVIDENCE: 2026-10-01 — first run FAILED (foreach-statement pipeline in Invoke-FreezeCheck.ps1), fixed; second run FAILED (string subexpression method call), fixed; final output `G3: PARSE-CLEAN (10 scripts)`. The gate caught two real authoring-time defects.

- [x] G4: Harness dry-run executes end-to-end (mock council + mock executor + mock judge) producing analysis outputs with zero network calls and zero API spend
  CHECK: pwsh -NoProfile -File eval/Invoke-DryRunSmoke.ps1
  EXPECT: DRYRUN-SMOKE-PASSED
  EVIDENCE: 2026-10-01 — `DRYRUN-SMOKE-PASSED (32 runs, 8 tasks, spend=$0, network=none)`, exit 0. All mock scores 1.0 (mock executor emits reference solutions; real Python graders confirm the full grading chain). Harness bugs found and fixed during pre-flight: comma-array binding under -File, questions.json format contract, analyzer percentile index arithmetic, over-escaped interpolations.

- [x] G5: Shipping skill package + task suite match the frozen SHA-256 manifest (measured artifact unmodified from the pre-registration freeze; this repo has no commits yet, so git cannot decide this — the freeze manifest, which the pre-registration requires anyway, is the oracle)
  CHECK: pwsh -NoProfile -File eval/Invoke-FreezeCheck.ps1
  EXPECT: FREEZE-INTACT
  EVIDENCE: 2026-10-01 — `FREEZE-CREATED (33 files)` then `FREEZE-INTACT (33 files match the pre-registration freeze)`. Manifest: eval/FROZEN-HASHES.txt (committed with the repo; created before any data collection).
  ADDENDUM 2026-10-05 — this gate's oracle is RETIRED, not replayable: `Invoke-FreezeCheck.ps1` now requires an explicit `-ManifestPath` (v0.2.1), and the pilot manifest it pointed at can no longer verify by design (superseded by FROZEN-HASHES-v3.txt; see STATUS.md freeze row). Historical result stands.

- [x] G6: Public-readiness artifacts exist: LICENSE, CI workflow, README with Evidence section, .gitignore covers eval raw outputs
  CHECK: pwsh -NoProfile -Command "$need = @('LICENSE','.github/workflows/ci.yml'); $miss = @($need | Where-Object { -not (Test-Path $_) }); $rd = Get-Content 'README.md' -Raw; $gi = Get-Content '.gitignore' -Raw; if ($miss.Count -eq 0 -and $rd -match 'Evidence' -and $gi -match 'eval') { 'PUBLIC-READY' } else { \"MISSING: $($miss -join ',') readme-evidence=$($rd -match 'Evidence') gitignore=$($gi -match 'eval')\"; exit 1 }"
  EXPECT: PUBLIC-READY
  EVIDENCE: 2026-10-01 — output `G6: PUBLIC-READY`. LICENSE (MIT), .github/workflows/ci.yml (windows-latest: parse+JSON+lint+installer+dry-run, no secrets), README Evidence section with pre-registration framing, .gitignore covers eval/results/raw/ + HANDOFF-*.md + .claude/ + __pycache__/ and documents why `runs/` stays unanchored.

- [x] G7: MANUAL — Mike approves the preregistered methodology AND the pilot budget before any paid API call (safety gate: costs money)
  EVIDENCE: 2026-10-01 — Mike approved in session ("sounds good amigo. i approve") after being presented the preregistration summary and the budget (expected $1.30–2.00, worst case $4.89, hard cap $6.00 in eval/config.json).
