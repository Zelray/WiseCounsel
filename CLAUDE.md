# CLAUDE.md — WiseCounsil

**Read `Agents.md` first — it is the canonical conventions document for this
project** (structure, prime directives, testing rules, safety rules, known
constraints). Everything in `Agents.md` applies to Claude sessions.

Project in one line: WiseCounsil is an agent skill that convenes a council of
2–6 cheap/free models (OpenRouter / OpenCodeGo) to attack a task brief before
the frontier model starts work.

Claude Code specifics:
- Skill installs to `~/.claude/skills/wise-counsil/` via
  `scripts/Install-WiseCounsil.ps1` (repo copy is source of truth).
- Invoke explicitly: "wise counsil" / "council this" before a big task.
- PowerShell 7+ for all script work; never bash-ify the .ps1 files.
- Status updates go in `STATUS.md`; session notes in `HANDOFF-<date>.md`.
