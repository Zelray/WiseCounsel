# STATUS.md — WiseCounsel

> One-glance chart. Detailed handoffs go in `HANDOFF-<date>.md`, never here.
> Conventions: `Agents.md`.

| Item | Status |
|---|---|
| Version | **v0.2.0** (2026-10-05) — clarify-default pivot |
| Skill definition (`SKILL.md`: triggers, **4 modes — `clarify` DEFAULT + 3 opt-in council modes**, 4 council templates + clarify protocol) | ✅ ships (v0.2.0; council templates byte-unchanged from v0.1.0) |
| Clarify mode (frontier model generates ≤5 build-changing questions → user answers → enriched brief + verify-later; **$0, no sub-models**) | ✅ shipped 2026-10-05, live-exercised in-session (GATES-V02 V7) |
| Council modes (`premortem` / `critique` / `debate`) | ✅ working, now **OPT-IN only** ("convene the council") per wave-2 null |
| OpenRouter engine (`Invoke-WiseCounsel.ps1`: parallel round 1, debate round 2, dossiers, cost accounting) | ✅ ships — unchanged in v0.2.0 |
| Config + presets (balanced-six / free-six / pair-minimum) | ✅ ships |
| Installer (live catalog validation, key check, OpenCode + Claude dirs) | ✅ ships — live installs refreshed 2026-10-05, hashes match repo (GATES-V02 V3/V6); Claude Code skill registry hot-reloaded the new description |
| Docs (README / DESIGN / Agents / CLAUDE / **CHANGELOG new**) | ✅ v0.2.0: README re-led (scaffold is the product, council opt-in) + transcript-claim honesty fix; DESIGN "What wave 2 taught us"; Agents/CLAUDE re-framed |
| Track-2 judge plumbing (per-judge response files, strict JSON-only, maxTokens 512→2048; probe overwrite fixed too) | ✅ fixed 2026-10-05 (code only) — **re-run pending Mike's explicit go + prereg addendum** |
| Build acceptance ledger `GATES-V02.md` | ✅ V1–V8 met with evidence; V9 (publish) closed on the v0.2.0 push |
| Live smoke test, premortem, 2 paid members (deepseek-v4.1-flash, gpt-oss-120b) | ✅ PASSED 2026-10-01 — 2/2, $0.0015 total (history) |
| Live smoke test, free endpoints | ⚠️ partial — ZDR account setting excludes many `:free` endpoints (unchanged) |
| OpenCodeGo native door (Door B) | 🟡 designed, not live-tested |
| Web app (plus-button model manager) | ⬜ phase 2, deliberately deferred |
| God-king experiment (mid-tier model + council brief) | ⬜ idea, documented in DESIGN.md |
| Debate mode (rounds 1–2) live test | ⬜ not yet exercised end-to-end |
| Eval design (docs/EVAL-DESIGN.md, pre-registered) | ✅ (history — wave-2 addendum final; no new measurement in v0.2.0) |
| Eval harness (eval/: run + judge + analyze + $0 dry-run smoke) | ✅ all green; post-judge-fix smoke `DRYRUN-SMOKE-PASSED (175 runs, 35 tasks, spend=$0)` |
| Pilot task suite + freezes (FROZEN-HASHES / -wave2 / -v3) | ✅ untouched measurement history; **v0.2.0 drift vs -v3 noted in HANDOFF-V02-BUILD.md, deliberately not re-frozen** |
| Pilot eval run | ✅ (history — superseded by wave 2) |
| Wave-2 confirmatory run | ✅ (history): scaffold +13.2 pp (p=0.0002) confirmed; council premium NULL (B−C −0.5 pp, p=0.90); full read docs/RESULTS.md |
| Public-repo readiness + GitHub | ✅ published v0.1.0 (2026-10-05, CI green); v0.2.0 push → tag on CI green |
| Engine `-OutDir` default writes inside the package (wise-counsel/runs/) | 🟡 still known; gitignored; **follow-up candidate now that the eval is done** (not in v0.2.0 scope) |

## Next steps
1. **Track-2 judge re-run decision (Mike's go required)** — plumbing is fixed; a small (<$0.50) Track-2-only re-run would validate the panel, but it is NEW SPEND and needs a dated prereg addendum BEFORE data per HANDOFF-V02-PIVOT.
2. Exercise `debate` mode end-to-end.
3. Build + test Door B (OpenCodeGo subagents) inside OpenCode.
4. Follow-up candidate: fix engine `-OutDir` default (package no longer frozen by an active measurement).
