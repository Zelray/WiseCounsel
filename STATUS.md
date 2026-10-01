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
| Eval harness (eval/: run + judge + analyze + $0 dry-run smoke) | 🟡 scaffolded, gate checks in progress |
| Pilot task suite (6 hidden-spec + 2 decision tasks, frozen checkers) | 🟡 authoring in progress |
| Pilot eval run (real API spend, ≈$4.89 worst case, $6 hard cap) | ⬜ awaiting Mike's approval (gate G7) |
| Public-repo readiness (LICENSE, CI, README Evidence, .gitignore hygiene) | 🟡 in progress |
| Engine `-OutDir` default writes inside the package (wise-counsil/runs/) | 🟡 known; gitignored (unanchored `runs/` rule); fix scheduled AFTER the eval — package is the frozen measured artifact |

## Next steps
1. Finish eval gates (G1–G6): task cards + dry-run green.
2. **Mike approves preregistration + pilot budget (G7)** — the money gate.
3. Run the pilot eval (≈$1.30–2.00 expected, $4.89 worst case), publish results in docs/RESULTS.md whatever they say.
4. Exercise `debate` mode end-to-end.
5. Build + test Door B (OpenCodeGo subagents) inside OpenCode.
6. After 2–3 weeks of real use: decide whether the web app earns building.
