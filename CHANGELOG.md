# Changelog

All notable changes to WiseCounsel. Format: loose Keep-a-Changelog; dates are
US-independent (ISO). Versioning per `Agents.md`: patch for config/roster/doc
changes, minor for new modes or doors.

## v0.2.1 — 2026-10-05

Hygiene pass from the 2026-10-05 ponytail audit (whole-repo over-engineering
review): 9 freeze-safe cuts, net −455 lines, zero behavior change — offline
end-to-end mock pipeline re-run green (DRYRUN-SMOKE-PASSED), all 30 Track-1
graders re-verified (GRADERS-VERIFIED), freeze-manifest drift set unchanged.

### Removed
- `eval/results/summary.csv` and its writer in `Invoke-Analyze.ps1` — a
  write-only lossy copy of `manifest.jsonl`, zero readers.
- `eval/results/pilot-launch.log` — unreferenced, superseded session log
  (the 56 pilot rows live in the manifest; the file remains in git history).
- CI "Parse all PowerShell scripts" step — PSScriptAnalyzer already fails
  the build on parse errors.
- The always-null `council_exit` manifest field (zero non-null values in
  all 381 recorded rows; historical rows keep it).

### Changed
- `Invoke-Eval.ps1`: the 4× repeated synthesis→matcher→answers block is now
  one `Add-Enrichment` helper; the OpenRouter key loader and the
  fenced-python extractor moved to a new dot-sourced `eval/common.ps1`,
  deduplicating `Invoke-Calibrate.ps1`.
- `Invoke-FreezeCheck.ps1`: `-ManifestPath` is now mandatory — the old
  silent default pointed at the pilot manifest, which can never verify again
  (the live oracle is `FROZEN-HASHES-v3.txt`).
- README / Agents.md: self-duplicated zones collapsed to pointers;
  Agents.md's hand-maintained structure tree (already silently drifted)
  replaced by a `git ls-files` pointer.

## v0.2.0 — 2026-10-05

The product pivot after the wave-2 confirmatory eval (300 runs, 30 calibrated
tasks, pre-registered — full read in `docs/RESULTS.md`): the question-answer
scaffold is the product; the multi-model council is opt-in diversity.

### Added
- **`clarify` mode — now the DEFAULT.** On any big task, the frontier model
  itself generates at most 5 build-changing questions (the measured wave-2
  arm-C shape: "no external review is available; rely on your own analysis"),
  asks the user, merges the answers (with a per-question "use best judgment"
  fallback) into an ENRICHED BRIEF + VERIFY-LATER checklist, then builds.
  $0 extra cost, no sub-models, no latency hit. Measured lift: +13.2 pp
  first-attempt pass rate (44.8% → 58.0%, p = 0.0002).
- `CHANGELOG.md` (this file).
- `docs/DESIGN.md` section "What wave 2 taught us".
- Track-2 judge acceptance ledger `GATES-V02.md` (same discipline as
  `GATES-WAVE2.md`).

### Changed
- **The council is now opt-in only.** `premortem` / `critique` / `debate`
  still work exactly as in v0.1.0 (templates unchanged — they are the
  measured arm-B path) but run ONLY on an explicit "convene the council".
  Prime directive 5 is now "OPT-IN TIERING": clarify is the default; the
  council is never automatic, roster still hard-capped at 6.
- README re-led with the honest framing: the scaffold is the product; the
  council is opt-in diversity. Roadmap de-staled (pilot and wave-2 done).
- `Agents.md` / `CLAUDE.md` re-framed to clarify-default / council-opt-in.

### Fixed
- **Track-2 judge plumbing** (code only — NO re-run; a re-run is new spend
  gated on owner approval + a dated prereg addendum): per-judge raw
  request/response files (the three judges no longer overwrite the same
  `judge.json`), strict JSON-only judge instruction, judge `maxTokens`
  512 → 2048 (512 truncated the 6-dimension rubric output; 50/75 judge slots
  came back null in wave 2).

### Honest-corrections
- README's Evidence section no longer claims raw transcripts "ship in the
  repo": summaries + the manifest ship; raw transcripts are retained locally
  (`eval/results/raw/` is gitignored).

## v0.1.0 — 2026-10-01

Initial public release (github.com/Zelray/WiseCounsel, tag `v0.1.0`, CI
green).

- WiseCounsel skill package: `SKILL.md` (3 council modes — premortem /
  critique / debate — 4 prompt templates), OpenRouter engine
  (`Invoke-WiseCounsel.ps1`: parallel round 1, sequential debate round 2,
  dossiers, cost accounting), config + presets (balanced-six / free-six /
  pair-minimum), installer with live catalog validation.
- Pre-registered eval harness (`eval/`): task calibration, freeze manifests,
  runner + three-judge Track-2 panel, analyzer, offline dry-run smoke.
- Pilot eval run (56 runs, $0.61): B−A = +15.8 pp (p = 0.125, n = 6) —
  superseded by wave 2, kept as history.
- Wave-2 confirmatory run (325 runs, $2.21 billed, under the $8 cap):
  scaffold lift confirmed (+13.2 pp, p = 0.0002), council premium refuted
  (B−C = −0.5 pp, p = 0.90 — published as a null per the pre-registered
  decision rule). Full numbers: `docs/RESULTS.md`.
