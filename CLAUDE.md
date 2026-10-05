# CLAUDE.md — WiseCounsel

**Read `Agents.md` first — it is the canonical conventions document for this
project** (structure, prime directives, testing rules, safety rules, known
constraints). Everything in `Agents.md` applies to Claude sessions.

Project in one line: WiseCounsel is an agent skill whose DEFAULT `clarify`
mode has the frontier model itself generate ≤5 build-changing questions, ask
the user, and build against an enriched brief ($0 — the measured +13.2 pp
scaffold); the 2–6 cheap/free-model council (OpenRouter / OpenCodeGo) is
opt-in, only on "convene the council".

Claude Code specifics:
- Skill installs to `~/.claude/skills/wise-counsel/` via
  `scripts/Install-WiseCounsel.ps1` (repo copy is source of truth).
- Invoke explicitly: "wise counsel" / "council this" before a big task.
- PowerShell 7+ for all script work; never bash-ify the .ps1 files.
- Status updates go in `STATUS.md`; session notes in `HANDOFF-<date>.md`.
