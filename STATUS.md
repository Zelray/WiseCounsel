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
| Pilot eval run — G7 approved by Mike | ✅ RAN 2026-10-01: 56 runs, $0.61 total — B−A = +15.8 pp (p=0.125, n=6). **Superseded by wave 2** per prereg; numbers kept as history |
| Wave-2 confirmatory run — G7 approved by Mike | ✅ RAN 2026-10-05: 325 runs, **$2.21 billed** (cap $8; itemized $1.92, log counter superseded) — **primary B−C = −0.5 pp, p=0.90: NULL — council premium refuted at n=30**; scaffold lift B−A = +13.2 pp (p=0.0002) confirmed; sham dossier ≈ real dossier; best-of-3 = zero gain. Track 2 unreliable (67% judge nulls, mechanical). Full read: docs/RESULTS.md |
| Public-repo readiness (LICENSE, CI, README Evidence, .gitignore hygiene) | ✅ done — README Evidence carries wave-2 verdict; lint settings fixed (psd1 data contract); badge URLs need OWNER/REPO at push |
| Initial commit / GitHub repo | 🟡 committed on `main` (341504b wave-2 verdict); repo creation + push = Mike's call |
| Engine `-OutDir` default writes inside the package (wise-counsil/runs/) | 🟡 known; gitignored (unanchored `runs/` rule); fix scheduled AFTER the eval — package is the frozen measured artifact |

## Next steps
1. **Owner decision: publish or not** — the wave-2 verdict is committed (null council premium, confirmed scaffold lift, honest caveats). §6 of HANDOFF-WAVE2: repo name, visibility, and Mike's acceptance of the published result whatever it says — then `gh repo create`, badge URLs, CI-green check, tag v0.1.0.
2. **Product pivot options from the verdict** (Mike's call): ship the question-answer scaffold with self-questions as default (council = opt-in), and/or fix Track 2's judge layer (67% null output — JSON-only instruction, larger max_tokens, structured output) and test the diversity premise on decision/research briefs where it might actually matter.
3. Exercise `debate` mode end-to-end.
4. Build + test Door B (OpenCodeGo subagents) inside OpenCode.
