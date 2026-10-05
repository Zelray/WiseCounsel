# CLAUDE.md — WiseCounsel

**Read `Agents.md` first — it is the canonical conventions document for this
project** (structure, prime directives, testing rules, safety rules, known
constraints). Everything in `Agents.md` applies to Claude sessions.

Project in one line: WiseCounsel is an agent skill that convenes a council of
2–6 cheap/free models (OpenRouter / OpenCodeGo) to attack a task brief before
the frontier model starts work.

Claude Code specifics:
- Skill installs to `~/.claude/skills/wise-counsel/` via
  `scripts/Install-WiseCounsel.ps1` (repo copy is source of truth).
- Invoke explicitly: "wise counsel" / "council this" before a big task.
- PowerShell 7+ for all script work; never bash-ify the .ps1 files.
- Status updates go in `STATUS.md`; session notes in `HANDOFF-<date>.md`.
