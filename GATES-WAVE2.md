# Gates: wave-2 confirmatory eval (2026-10-05)

> Wave-2 acceptance ledger, same discipline as the pilot `GATES.md` (which
> records G1–G7 and stays as history). Each gate states one observable
> outcome; runnable gates carry the exact command (`CHECK`) and success
> marker (`EXPECT`). W7 and W10 are human approval gates recorded by hand.

OWNS: docs/EVAL-DESIGN.md (addenda only), eval/Invoke-Eval.ps1, eval/Invoke-Analyze.ps1,
eval/Invoke-FreezeCheck.ps1, eval/Invoke-DryRunSmoke.ps1, eval/Invoke-VerifyGraders.ps1,
eval/Invoke-Calibrate.ps1, eval/tasks/**, eval/FROZEN-HASHES-wave2.txt, docs/RESULTS.md,
README.md, STATUS.md
NOT-OURS: wise-counsil/** (frozen measured artifact; must stay diff-empty),
eval/FROZEN-HASHES.txt (pilot's historical freeze record)

Scope: a pre-registered confirmatory evaluation — 30 calibrated Track-1 tasks x
arms A/B/C/E/F x 2 reps + 5 Track-2 decision tasks x 5 arms x 1 rep — run
inside an $8 hard cap after Mike's explicit go, analyzed against the
pre-registered decision rules verbatim (null or negative B−C published exactly
as a positive), with the pilot freeze and pilot numbers preserved as history.

- [ ] W1: Wave-2 preregistration addendum is appended to docs/EVAL-DESIGN.md (dated 2026-10-05, under "Preregistration addenda") covering: scope (30 T1 incl. 6 pilot re-run fresh + 24 new; 5 T2 incl. storage-ADR replaced), arms A/B/C/E/F with D dropped, confirmatory primary B−C with pre-stated secondaries, decision rule (B−C ≥ +5 pp AND p < 0.05 AND bootstrap CI excludes 0), budget estimate $2.50–4.00 with $8 cap, parser-hardening note, freeze manifest v2 filename, arm E/F mechanics, and the supersession clause
  CHECK: pwsh -NoProfile -Command "$h = Get-Content 'docs/EVAL-DESIGN.md' -Raw; $req = 'Wave-2 addendum (2026-10-05)','B − C','$8','FROZEN-HASHES-wave2.txt','Arm E','Arm F','supersedes pilot numbers','parser','calibration'; $miss = @($req | Where-Object { $h -notmatch [regex]::Escape($_) }); if ($miss.Count -eq 0) { 'W1-ADDENDUM-COMPLETE' } else { \"MISSING: $($miss -join ', ')\"; exit 1 }"
  EXPECT: W1-ADDENDUM-COMPLETE
  EVIDENCE: 2026-10-05 — output `W1-ADDENDUM-COMPLETE` (first run flagged the hyphen-form 'B - C' as missing because the design doc consistently uses the en-dash form 'B − C'; check corrected, second run clean). Addendum committed BEFORE any wave-2 model call (commit hash in git log; wave-2 data collection has not started).

- [ ] W2: Harness ready for wave 2 — hardened solution-fence fallback, arms E and F implemented end-to-end, analyzer comparison list updated, freeze script takes -ManifestPath — with all eval scripts parsing clean, the offline dry-run smoke passing on arms A,B,C,E,F, pilot graders still verifying, and wise-counsil/ diff-empty
  CHECK: pwsh -NoProfile -File eval/Invoke-DryRunSmoke.ps1
  EXPECT: DRYRUN-SMOKE-PASSED
  EVIDENCE: 2026-10-05 — `DRYRUN-SMOKE-PASSED (40 runs, 8 tasks, spend=$0, network=none)` on arms A,B,C,E,F; `PARSE-CLEAN` (12 scripts); `Invoke-VerifyGraders.ps1` on the pilot suite: all 6 graders ref=10/10, empty-stub=0, always-false-stub machinery-ok (username-validator false-stub scores 4/10 = genuine partial-credit proof); `WISE-COUNSIL-DIFF-EMPTY`; pilot freeze `FREEZE-INTACT (33 files)`. Defects found and fixed during prep: (1) verifier's FUNCTION_NAME-only symbol discovery missed the getattr-style loaders and the Order class — broadened to collect all entry symbols and emit type-aware stubs; (2) `$(Get-Date).ToUniversalTime()` subexpression bug in Calibrate per machine notes; (3) PSScriptAnalyzerSettings.psd1 used a here-string (a .psd1 must evaluate to data only) — the linter rejected the whole settings file, which would have failed the FIRST-EVER CI run at publish; converted to comments + added two documented rule exclusions (BOM rule would force a byte-change of the frozen artifact; plural-noun helpers are established); (4) Calibrate unused $repoRoot + MaxSpendUsd now passed explicitly. Local lint (CI-parity): LINT-CLEAN.

- [ ] W3: Task suite expanded to 30 Track-1 + 5 Track-2 cards, all valid JSON, all PowerShell checkers parse, storage-ADR card replaced (deleted), new cards numbered 09+ with blind provenance
  CHECK: pwsh -NoProfile -Command "$cards = @(Get-ChildItem 'eval/tasks' -Filter 'task-*.json' | ForEach-Object { Get-Content $_.FullName -Raw | ConvertFrom-Json }); $t1 = @($cards | Where-Object { $_.track -eq 1 }); $t2 = @($cards | Where-Object { $_.track -eq 2 }); $blind = @($cards | Where-Object { $_.provenance.authored_by -match 'blind' }); $adr = Test-Path 'eval/tasks/task-08-storage-adr.json'; if ($t1.Count -eq 30 -and $t2.Count -eq 5 -and $blind.Count -ge 28 -and -not $adr) { \"TASKS-WAVE2-OK t1=$($t1.Count) t2=$($t2.Count) blind=$($blind.Count)\" } else { \"BAD t1=$($t1.Count) t2=$($t2.Count) blind=$($blind.Count) adr-still-present=$adr\"; exit 1 }"
  EXPECT: TASKS-WAVE2-OK t1=30 t2=5
  EVIDENCE: 2026-10-05 — `TASKS-WAVE2-OK t1=30 t2=5 blind=34` (34 = 28 new blind-authored + count includes blind string in revised pilot-adjacent cards; storage-ADR card deleted via git rm). All 30 checkers parse; all JSON valid.

- [ ] W4: Every Track-1 grader verified three ways — reference solution scores max with exit 0; a no-function stub scores 0 with exit 0 (machinery-ok); an always-false stub scores within [0, max] with parseable RULE lines — across ALL 30 T1 tasks (pilot 01-06 re-verified too)
  CHECK: pwsh -NoProfile -File eval/Invoke-VerifyGraders.ps1
  EXPECT: GRADERS-VERIFIED
  EVIDENCE: 2026-10-05 — `GRADERS-VERIFIED (30 Track-1 tasks: ref=max, stub=0, falsestub=machinery-ok on all)`, re-run after every authoring/rewrite wave and after the task-09→37 swap. Partial credit proven via always-false stubs (hex-color 6/10, license-plate 6/10, username-validator 4/10, badge-eligibility 2/10, loan-payoff 1/10). Defect caught and repaired: the 429-killed rewrite agent left task-29's ref at 9/10 (stale expected value) — repaired, re-verified 10/10.

- [ ] W5: Calibration pass documented — every NEW Track-1 task got exactly one executor-on-plain-brief call, scores recorded in eval/tasks/CALIBRATION-wave2.md, and each new task landed in the 30–70% band or was rewritten/discarded with the outcome recorded BEFORE freeze v2
  CHECK: pwsh -NoProfile -Command "$c = Get-Content 'eval/tasks/CALIBRATION-wave2.md' -Raw; $n = ([regex]::Matches($c, '(?m)^\| task-')).Count; $disc = ([regex]::Matches($c, '(?i)discard')).Count; if ($n -ge 24 -and $c -match '30-70' -and $disc -ge 1) { \"CALIBRATION-OK rows=$n discard-noted=$disc\" } else { \"BAD rows=$n discard=$disc\"; exit 1 }"
  EXPECT: CALIBRATION-OK rows=
  EVIDENCE: 2026-10-05 — `CALIBRATION-OK rows=24 discard-noted=6`. Four rounds: round-1 kept 12/24 in band; round-2 rewrites lifted 9 more; round-3+4 fixed cart-promotions (60%) and hotel-stay-total (70%, integer-month ambiguity + guest fee). task-09-courier-rates stayed bimodal (0% then 80%) across 4 rounds and was DISCARDED per the pre-registered rule; replacement task-37-dryclean-order authored with the calibration lessons and landed in band at 40% first try. Final suite: 24/24 new tasks in band. Spend ~$0.09; raw transcripts per round preserved (round-1 copies suffixed -round1).

- [ ] W6: Freeze v2 — eval/FROZEN-HASHES-wave2.txt created AFTER suite finalization and BEFORE any wave-2 council/executor call, and verifies INTACT; pilot manifest FROZEN-HASHES.txt untouched
  CHECK: pwsh -NoProfile -File eval/Invoke-FreezeCheck.ps1 -ManifestPath eval/FROZEN-HASHES-wave2.txt
  EXPECT: FREEZE-INTACT
  EVIDENCE: 2026-10-05 — `FREEZE-CREATED (133 files)` then `FREEZE-INTACT (133 files match the pre-registration freeze)` for eval/FROZEN-HASHES-wave2.txt, created after suite finalization and before any wave-2 council/executor/judge call (only pre-registered control-arm calibration calls preceded it). Pilot manifest FROZEN-HASHES.txt untouched on disk (historical record; per the wave-2 addendum it no longer matches the tree by design — the wave-2 manifest is the live oracle).

- [ ] W7: MANUAL — Mike explicitly approves the wave-2 spend (final estimate presented: expected $2.50–4.00, hard cap $8.00) BEFORE launch; launch commands exactly per HANDOFF-WAVE2 §4 with -MaxSpendUsd 8, logged, 2-minute sanity check performed and documented
  EVIDENCE: pending

- [ ] W8: Confirmatory analysis produced for both tracks — T1 summary is the B−C-primary confirmatory table with the full pre-registered comparison hierarchy; T2 summary saved as summary-t2.md; integrity probes reported (leak-check verdicts, council success rate, arm-probe interpretation)
  CHECK: pwsh -NoProfile -Command "$s1 = Get-Content 'eval/results/summary.md' -Raw; $s2 = Get-Content 'eval/results/summary-t2.md' -Raw; $need = @('B - C','B - A','C - A','B - E','B - F','E - A','F - A'); $miss = @($need | Where-Object { $s1 -notmatch [regex]::Escape($_) }); if ($miss.Count -eq 0 -and $s2 -match 'B - C') { 'ANALYSIS-OK' } else { \"MISSING: $($miss -join ',')\"; exit 1 }"
  EXPECT: ANALYSIS-OK
  EVIDENCE: pending

- [ ] W9: Honest writeup committed — docs/RESULTS.md leads with wave-2 tables and applies the pre-registered decision rules VERBATIM (a null/negative B−C is stated as a null/negative result, not spun); README Evidence section updated with confirmatory numbers; STATUS.md chart rows current
  CHECK: pwsh -NoProfile -Command "$r = Get-Content 'docs/RESULTS.md' -Raw; if ($r -match 'Wave 2' -and $r -match 'B − C|B - C' -and $r -match 'decision rule|Decision rule|verdict') { 'RESULTS-WAVE2-OK' } else { 'RESULTS-INCOMPLETE'; exit 1 }"
  EXPECT: RESULTS-WAVE2-OK
  EVIDENCE: pending

- [ ] W10: MANUAL — before any publish action (repo creation, push, tag): Mike confirms repo name, public visibility, and that he accepts the published result whatever it says
  EVIDENCE: pending
