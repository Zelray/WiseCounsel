# STATUS.md — WiseCounsil

> One-glance chart. Detailed handoffs go in `HANDOFF-<date>.md`, never here.
> Conventions: `Agents.md`.

| Item | Status |
|---|---|
| Version | **v0.1.0** (2026-10-01) |
| Skill definition (`SKILL.md`: triggers, 3 modes, 4 templates) | ✅ ships |
| OpenRouter engine (`Invoke-WiseCounsil.ps1`: parallel round 1, debate round 2, dossiers, cost accounting) | ✅ ships |
| Config + presets (balanced-six / free-six / pair-minimum) | ✅ ships |
| Installer (live catalog validation, key check, OpenCode + Claude dirs) | ✅ ships |
| Docs (README / DESIGN / Agents / CLAUDE) | ✅ ships |
| Live smoke test, premortem, 2 paid members (deepseek-v4.1-flash, gpt-oss-120b) | ✅ PASSED 2026-10-01 — 2/2, $0.0015 total |
| Live smoke test, free endpoints | ⚠️ partial — ZDR account setting excludes many `:free` endpoints |
| OpenCodeGo native door (Door B) | 🟡 designed, not live-tested |
| Web app (plus-button model manager) | ⬜ phase 2, deliberately deferred |
| God-king experiment (mid-tier model + council brief) | ⬜ idea, documented in DESIGN.md |
| Debate mode (rounds 1–2) live test | ⬜ not yet exercised end-to-end |
| Claude Code install/test | ⬜ installer supports it; not yet exercised |
| Eval design (docs/EVAL-DESIGN.md, pre-registered: arms, grading, stats, $6 cap) | ✅ written 2026-10-01, debate-tested (skeptic/builder/architect/prior-art) |
| Eval harness (eval/: run + judge + analyze + $0 dry-run smoke) | ✅ all gates green (G1–G6), 10 scripts parse, 32-run offline smoke passed |
| Pilot task suite (6 hidden-spec + 2 decision tasks, frozen checkers) | ✅ 33-file SHA-256 freeze intact |
| Pilot eval run — G7 approved by Mike | ✅ RAN 2026-10-01: 56 runs, **$0.61 total** (cap $6) — Track 1: **B−A = +15.8 pp** (CI [3.3, 35.8], p=0.125, n=6 — signal, NOT confirmed); question-overlap 21.6%; full read in docs/RESULTS.md |
| Wave-2 confirmatory run (30 calibrated tasks, arms E+F, hardened parser) | ⬜ owner decision on ~$2–5 spend — prereg scale-gate did not fire by its letter (p=0.125 > 0.10) |
| Public-repo readiness (LICENSE, CI, README Evidence, .gitignore hygiene) | ✅ done — badge URLs need OWNER/REPO at push |
| Initial commit / GitHub repo | 🟡 committed on `main` (3e273b2); repo creation + push = Mike's call |
| Engine `-OutDir` default writes inside the package (wise-counsil/runs/) | 🟡 known; gitignored (unanchored `runs/` rule); fix scheduled AFTER the eval — package is the frozen measured artifact |

## Next steps
1. **Wave 2 (confirmatory run)** — ⏭️ **START HERE in a fresh session: read `HANDOFF-WAVE2.md`** (exhaustive instructions: prep, 24+3 new tasks, arms E+F, freeze v2, launch commands, analysis, publish steps). Owner decision on ~$2.50–4.00 spend happens inside that flow.
2. Create the GitHub repo (Mike's account) and push; fix README badge URLs. *(§6 of HANDOFF-WAVE2 — after the wave-2 verdict.)*
3. Exercise `debate` mode end-to-end.
4. Build + test Door B (OpenCodeGo subagents) inside OpenCode.
