---
name: wise-counsil
description: >-
  Convene a cheap-model council BEFORE tackling a big task: 2-6 cheap or free
  models (OpenRouter or OpenCodeGo) independently pre-mortem a coding brief,
  debate a research question, or critique a plan; their findings merge into an
  enriched brief with open questions and a verify-later checklist before the
  frontier model starts work. Triggers: "wise counsil", "council this",
  "pre-think", "second opinion", "convene the council" — or beginning a new
  app/project build, a domain-rule-heavy feature (state math, tax/legal/
  compliance rules, calculators), a buy/sell or pick-X research decision, or a
  major architecture decision. Do NOT use for quick fixes, typos, small
  well-specified edits, high-volume routine work, or casual chat.
---

# WiseCounsil — cheap-model pre-think council

## Prime directives (never violate)

1. **ATTACK, DON'T ANSWER.** Council members attack the brief (find holes,
   list rules and edge cases, sketch approaches). They do NOT produce the
   final answer, code, or the truth. The frontier model executes and decides.
2. **CANDIDATES, NOT FACTS.** Everything a council member says is a
   candidate consideration to verify. Never inject a council member's claim
   into code, comments, docs, or the final answer as an established fact.
   Uncertain items are phrased as "Verify: ..." questions.
3. **ADDITIVE BRIEF.** The enriched brief extends the user's prompt; it never
   replaces the user's intent. If a council member's reading conflicts with
   the user's words, the user's words win.
4. **ATTRIBUTION ALWAYS.** When relaying council findings, keep the model tag
   (e.g. `[qwen]`) so disagreement stays visible. Never launder six opinions
   into one anonymous "everybody says".
5. **OPT-IN ONLY.** Never run the council unprompted for small or
   well-specified work. When unsure, ask the user.

## When to convene vs. refuse

| Convene when | Refuse when |
|---|---|
| New app/project from scratch | Quick fix, typo, one-liner |
| Domain-rule-heavy feature (state math, tax/legal/compliance, calculators) | Small, well-specified edit |
| Buy/sell, pick-X, compare-options research decision | High-volume routine work |
| Major architecture decision | Casual chat or simple question |
| User explicitly says "wise counsil" / "council this" | User is in a hurry and the task is clear |

## Step 1 — Resolve the roster

Resolution order (first hit wins):
1. `wisecounsil.json` in the current project's `config/` folder (per-project override)
2. This skill's own `config/wisecounsil.json`

Validate: at least `minModels` (2), at most `maxModels` (6). If the config is
missing or invalid, tell the user and proceed WITHOUT the council — never
invent a roster.

## Step 2 — Pick the mode

| Mode | Use when | Rounds |
|---|---|---|
| `premortem` (default) | Coding/build tasks; attack the brief before implementation | 1 |
| `critique` | A plan already exists (yours or the user's); attack the plan | 1 |
| `debate` | Research/decision questions (buy/sell, pick X, compare options) | 2 |

For `debate` on financial topics, keep the herding caveat in mind and in the
output: these models share overlapping training data and will converge on
consensus narratives. The debate protocol's "what would change my mind"
section exists to fight exactly that.

## Step 3 — Run the council

### Door A — OpenRouter (default, works everywhere)

Run the bundled script (resolve paths relative to this skill's folder; the
project fallback path is recorded in the repo's `Agents.md`):

```
pwsh -NoProfile -File "<skill_dir>\scripts\Invoke-WiseCounsil.ps1" `
  -Mode premortem `
  -TaskFile "<temp file containing the user's verbatim prompt>" `
  -ConfigPath "<config path>"
```

- `-Task` works for short prompts; `-TaskFile` for long ones (write the
  user's verbatim prompt to a temp file first — never paraphrase it).
- Optional: `-Context "<extra material, e.g. articles or code>"`,
  `-Rounds`, `-Models "<override ids>"`, `-Preset "<preset name>"`.
- The script prints a **dossier**: one section per model with its full
  response, tags, latency, and cost. Raw JSON + dossier are saved under
  `runs/<timestamp>-<mode>/`.
- Exit codes: `0` = at least one member responded · `2` = ALL members
  failed · `3` = config or key problem.

### Door B — OpenCodeGo (flat-rate, $0 marginal per council)

When `config.provider` is `"opencodego"` (or Door A is unavailable):
dispatch one subagent per roster model via the Task tool, using the generated
agent names in `config.opencodego.agentsNamespace` (e.g. `wisecounsil-qwen`,
`wisecounsil-gpt-oss`), feeding each the SAME verbatim template from Step 5.
Collect their replies, then merge them yourself exactly as in Step 4. If the
subagent door misbehaves, fall back to Door A.

## Step 4 — Synthesize the dossier into the final brief

Read the dossier and produce a **final brief** with exactly these sections,
capped at ~600 words total:

1. **Enriched brief** — the user's prompt + the material gaps/ambiguities
   merged in, with model tags preserved.
2. **Open questions for the user** — at most 5, and only ones that change
   the build (never trivia the user would shrug at).
3. **Verify-later checklist** — every "Verify:" item, verbatim enough to
   check during execution.
4. **Dissent notes** — where members disagreed, one line each.

Present the open questions to the user BEFORE building. Answer the rest
yourself through verification during execution.

## Step 5 — Prompt templates (send verbatim, with the brief appended)

### Premortem (per member)

```text
You are one member of a cheap-model "pre-think council". A senior AI
engineer will implement the TASK BRIEF below. Your job is to attack the
brief BEFORE implementation. Do not solve the task.

Produce EXACTLY these five sections, no preamble:
## Missing
Unstated requirements, domain rules, edge cases, inputs/outputs, or data
the implementer would have to guess.
## Ambiguous
Places where two reasonable readings would produce two different builds.
State both readings.
## Risky assumptions
Assumptions that may not hold. Phrase each as a question to verify
("Verify: ..."), never as a fact.
## Approach sketch
Your build approach in at most 5 bullets. No code.
## Watchlist
The 2-3 things most likely to make the finished product wrong or unusable.

Rules: max 300 words total. No code. If you are unsure whether something is
true, phrase it as a verification question. Do not restate the task back.
```

### Critique (per member)

```text
You are one member of a cheap-model review council. A senior AI engineer
wrote the PLAN below. Attack the plan BEFORE it is executed. Do not rewrite
it.

Produce EXACTLY these five sections, no preamble:
## Missing
Steps, requirements, or edge cases the plan does not cover.
## Ambiguous
Steps two engineers would read differently. State both readings.
## Risky assumptions
Phrase each as a question to verify ("Verify: ..."), never as a fact.
## Sequencing risks
Steps that depend on each other in ways the plan ignores.
## Watchlist
The 2-3 things most likely to make the executed result wrong or broken.

Rules: max 300 words total. No code. Do not restate the plan back.
```

### Debate, round 1 (per member — independent positions)

```text
You are one member of an independent analysts' council. QUESTION: <the
user's question and any attached materials>.

Give your position in EXACTLY this structure, max 350 words, no preamble:
## Position
One paragraph. Take a real stance; do not hedge into "it depends" without
resolving it.
## Key evidence
3-5 bullets. For each: the claim, and whether it is (a) verifiable fact you
are confident in, (b) plausible inference, or (c) speculation. Label each
bullet (a)/(b)/(c).
## What would change my mind
The 2-3 strongest counter-considerations, stated fairly.
## Confidence
Low / Medium / High, with one sentence why.
```

### Debate, round 2 (per member — sees anonymized peers)

```text
You are the same council member, now shown your peers' round-1 positions
(anonymized):

<peers' round-1 sections>

Update your position in EXACTLY this structure, max 300 words, no preamble:
## Rebuttal
Where your peers are wrong, and specifically why. Attack the STRONGEST peer
argument, not the weakest.
## Concession
What a peer said that you now think is right, and why it moved you (or
"none").
## Updated position
One paragraph, final stance.
## Confidence
Low / Medium / High + one sentence.
```

## Step 6 — Execution protocol (after the council)

- Ask the user the build-changing open questions FIRST (max 5).
- Turn every "Verify:" item into an explicit checklist entry in your plan;
  verify each during execution, and state in the final summary which were
  verified and which remain open for the user.
- Never cite a council member as an authority for a factual claim in code,
  comments, docs, or your final answer. Verify independently, or surface it
  as an open question.
- Cite the dossier path (`runs/...`) in your final answer so the user can
  audit the reasoning.

## Failure handling

- Exit `2` (no members responded): skip the council, proceed with the task
  normally, and tell the user the council was unavailable.
- 1-2 members failed: proceed with the survivors; say which were skipped.
- Repeated timeouts: raise `limits.timeoutSec` once and retry that member;
  if it still fails, skip it.

## Cost and latency expectations

- `balanced-six` preset: roughly $0.001–0.003 per full council (each member
  gets a 1200-token budget; visible output is capped at 300 words by the
  template, the rest absorbs hidden reasoning on thinking models).
- `free-six` preset: $0.00.
- Wall time ≈ slowest member (~15–45 s, members fire in parallel).
- `debate` round 2 runs sequentially and adds ~1–2 minutes.

## Config reference

`config/wisecounsil.json`:
- `provider`: `"openrouter"` (Door A) or `"opencodego"` (Door B)
- `models`: array of `{ id, label, family }`, 2–6 entries — THE roster
- `limits`: `{ maxOutputTokens, timeoutSec, temperaturePremortem,
  temperatureDebate }`
- `opencodego`: `{ enabled, agentsNamespace }` for Door B agent names

Presets live in `config/presets.json`: `balanced-six` (default),
`free-six`, `pair-minimum`. To change the roster: edit the project copy,
then re-run `scripts/Install-WiseCounsil.ps1` to sync the installed copy
(or edit the installed copy directly for a quick experiment).
