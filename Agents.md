# Agents.md — WiseCounsel conventions

Any agent (Claude, OpenCode, or other) working in this repository: read this
file first. It is the canonical conventions doc. `CLAUDE.md` is a pointer to
this file for Claude Code sessions.

## What this project is

**WiseCounsel** is a harness-native skill: before a frontier model starts a
big task, it convenes a council of 2–6 cheap/free models (OpenRouter or
OpenCodeGo) that *attack the user's prompt* — surfacing gaps, ambiguities,
risky assumptions, and approach sketches. Their findings are merged into an
enriched brief (open questions + verify-later checklist) that the frontier
model then executes against.

Core design principle: **cheap models attack, frontier model decides.**
Council members never produce final answers; their claims are always
candidates to verify. See `docs/DESIGN.md` for the full rationale and
`wise-counsel/SKILL.md` for the operating protocol.

## Structure map

```
WiseCounsel/
├── Agents.md            ← this file (canonical conventions)
├── CLAUDE.md            ← thin pointer for Claude Code sessions
├── README.md            ← plain-English pitch + quickstart (PM-readable)
├── STATUS.md            ← one-glance status chart (consumed by Joey)
├── docs/DESIGN.md       ← design rationale, failure modes, roadmap
├── runs/                ← (gitignored) dossiers from real councils
└── wise-counsel/        ← THE INSTALLABLE SKILL PACKAGE (self-contained)
    ├── SKILL.md         ← skill definition: triggers, modes, templates
    ├── config/
    │   ├── WiseCounsel.json   ← live roster + limits (source of truth)
    │   └── presets.json       ← balanced-six / free-six / pair-minimum
    └── scripts/
        ├── Invoke-WiseCounsel.ps1   ← Door A engine (OpenRouter, parallel)
        └── Install-WiseCounsel.ps1  ← installs package into skill dirs
```

Installed copies live at `~/.config/opencode/skills/wise-counsel/` (OpenCode)
and `~/.claude/skills/wise-counsel/` (Claude Code). The repo copy is the
source of truth; re-run the installer after editing the repo copy, or edit an
installed copy directly for quick experiments.

## Prime directives (apply to every change and every session)

1. **Attack, don't answer** — council templates must ask models to find holes,
   never to produce the final artifact.
2. **Candidates, not facts** — council claims are framed as verification
   questions in everything downstream (briefs, code comments, final answers).
3. **Additive brief** — the enriched brief extends the user's prompt; user's
   words win any conflict.
4. **Attribution always** — model tags survive merging; no anonymous consensus.
5. **Opt-in only** — the skill must never make itself always-on; rosters are
   hard-capped at 6 members.

## How to modify things

- **Roster/models**: edit `wise-counsel/config/WiseCounsel.json` (2–6 models,
  diverse families preferred), then run `Install-WiseCounsel.ps1` to validate
  IDs against the live OpenRouter catalog and re-sync installed copies.
- **Prompt templates / protocol**: edit `wise-counsel/SKILL.md`. Keep the
  "max N words" and "phrase uncertain items as Verify:" rules — they are load-
  bearing against hallucination contamination and context bloat.
- **Engine script**: edit `Invoke-WiseCounsel.ps1`, then (a) syntax-check with
  `[System.Management.Automation.Language.Parser]::ParseFile`, (b) smoke-test
  with the `free-six` or a 2-member `:free` override, zero cost.

## Testing rules

- Default to `:free` models for tests (OpenRouter). Free endpoints may be
  excluded by this machine's OpenRouter account privacy setting (ZDR) — see
  Known Constraints.
- Paid smoke tests: keep total cost ≤ $0.01 (the `pair-minimum` preset runs
  ~$0.0015). Anything more: get Mike's explicit OK first.
- Never run paid tests against premium/frontier models "just to see".

## Safety rules (hard)

- Never print, log, or commit an API key. The script reads
  `~/.openrouter-client.key` or `env:OPENROUTER_API_KEY` and stays silent.
- `runs/` is gitignored: dossiers contain the user's raw prompts and must not
  be committed without review.
- Never widen the roster cap beyond 6 or make the skill auto-trigger on every
  request — both destroy the cost/latency case.

## Windows notes

- PowerShell 7+ only (`#Requires -Version 7.0`), UTF-8 output encoding is set
  inside the scripts. Parallel round 1 uses `ForEach-Object -Parallel`
  (ThrottleLimit 6). Debate round 2 is intentionally sequential.

## Known constraints (as of v0.1.0)

- **ZDR privacy setting**: Mike's OpenRouter account excludes endpoints that
  don't meet its data policy — several `:free` endpoints 404 with
  "zdr-violation-by-account". Paid models route fine (verified). Free presets
  may fail partially; check https://openrouter.ai/settings/privacy.
- **OpenCodeGo door (Door B)** is designed but not yet live-tested: it
  requires generated subagent definitions pinned to OpenCodeGo models inside
  OpenCode. Test on first use; fall back to Door A on misbehavior.
- **Thinking models**: reasoning is excluded from responses
  (`reasoning.exclude`) and the per-member token budget is 1200 so hidden
  reasoning can't eat the visible answer (found via smoke test 2026-10-01).

## Documentation conventions

- Update `STATUS.md` on every substantive change (chart, not prose).
- For significant sessions, write `HANDOFF-<date>.md` with what changed, what
  was tested, and what's next.
- Version bumps: patch for config/roster/doc changes; minor for new modes or
  doors; record in STATUS.md.
