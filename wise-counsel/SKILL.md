---
name: wise-counsel
description: >-
  Before tackling a big task, run the clarify scaffold: generate at most 5
  build-changing questions about the brief, ask the user, and merge the answers
  into an enriched brief with a verify-later checklist before starting work —
  the measured +13-point lift on first-attempt pass rate, at $0 extra cost, no
  sub-models, no latency hit. Optionally convene a council of 2-6 cheap or free
  models (OpenRouter or OpenCodeGo) to premortem a coding brief, debate a
  research question, or critique a plan — the council is OPT-IN: only on an
  explicit "convene the council". Triggers: "wise counsel", "council this",
  "pre-think", "second opinion", "convene the council" — or beginning a new
  app/project build, a domain-rule-heavy feature (state math, tax/legal/
  compliance rules, calculators), a buy/sell or pick-X research decision, or a
  major architecture decision. Do NOT use for quick fixes, typos, small
  well-specified edits, high-volume routine work, or casual chat.
---

# WiseCounsel — clarify first, council on request

**What the evidence says (read this before choosing a path).** The wave-2
confirmatory eval (300 runs, 30 calibrated tasks, pre-registered, p = 0.0002)
proved the question-answer scaffold lifts first-attempt pass rate by +13.2
points and beats compute-matched best-of-3 (which gained exactly zero). It also
refuted the council premium: the executor asking its OWN questions matched the
council's questions (B − C = −0.5 pp, p = 0.90), and a sham dossier matched a
real one. Full numbers: `docs/RESULTS.md`. Therefore: **clarify is the default
product; the council is opt-in diversity.**

## Prime directives (never violate)

1. **ATTACK, DON'T ANSWER.** Council members attack the brief (find holes,
   list rules and edge cases, sketch approaches). They do NOT produce the
   final answer, code, or the truth. The frontier model executes and decides.
2. **CANDIDATES, NOT FACTS.** Everything a council member says is a
   candidate consideration to verify. Never inject a council member's claim
   into code, comments, docs, or the final answer as an established fact.
   Uncertain items are phrased as "Verify: ..." questions.
3. **ADDITIVE BRIEF.** The enriched brief extends the user's prompt; it never
   replaces the user's intent. If any question, answer, or council reading
   conflicts with the user's words, the user's words win.
4. **ATTRIBUTION ALWAYS.** When relaying council findings, keep the model tag
   (e.g. `[qwen]`) so disagreement stays visible. Never launder six opinions
   into one anonymous "everybody says".
5. **OPT-IN TIERING.** `clarify` is the DEFAULT mode: self-generated
   questions, no sub-models, $0. The multi-model council runs ONLY when the
   user explicitly asks for it — "convene the council" — never unprompted,
   never always-on, roster hard-capped at 6 members. When unsure whether the
   user wants the council, default to clarify and mention the council option.

## When to use vs. refuse

| Use when | Refuse when |
|---|---|
| New app/project from scratch | Quick fix, typo, one-liner |
| Domain-rule-heavy feature (state math, tax/legal/compliance, calculators) | Small, well-specified edit |
| Buy/sell, pick-X, compare-options research decision | High-volume routine work |
| Major architecture decision | Casual chat or simple question |
| User explicitly says "wise counsel" / "council this" | User is in a hurry and the task is clear |

## Step 1 — Pick the mode

| Mode | Use when | Cost |
|---|---|---|
| `clarify` (DEFAULT) | The skill fired on a big task and the user did not ask for the council | $0, no sub-models |
| `premortem` (council; opt-in) | User convened the council; coding/build task; attack the brief before implementation | ~$0.001–0.003 |
| `critique` (council; opt-in) | User convened the council; a plan already exists; attack the plan | ~$0.001–0.003 |
| `debate` (council; opt-in) | User convened the council; research/decision question | ~$0.002–0.006 |

The council modes exist for users who want multi-model diversity anyway (or
for task classes not yet tested, like long research briefs) — but the user
must ask. "wise counsel" alone selects `clarify`.

## Step 2 — Run `clarify` (the default scaffold)

Zero sub-models, zero API calls, zero extra wall time. You (the frontier
agent) do all of it:

### 2a. Generate the questions — use the measured shape

Apply the exact arm-C synthesis shape to yourself, with the empty-dossier
stanza (this shape is the measured +13.2-point arm; do not improvise a new
one):

```text
You are the senior engineer who will execute the TASK BRIEF below.
No external review is available; rely on your own analysis.

Produce, in EXACTLY this structure and nothing else:
ENRICHED BRIEF
<the brief with material gaps merged in, max 300 words; the user's stated intent wins any conflict>
OPEN QUESTIONS
Q: <at most 5 questions, one per line, only ones that change the build>
VERIFY-LATER
<checklist of items to verify during implementation>
DISSENT
<one line where reviewers disagreed, or 'none'>
```

Internally work through that structure; then surface only what the user
needs. Question rules (load-bearing):

- **At most 5 questions.** Fewer is fine; zero is a valid outcome for a
  tight brief.
- **Only build-changing questions** — ones where two different answers would
  produce two different builds. Never trivia the user would shrug at.
- Phrase each so a non-coder can answer it in one line, and offer a sane
  default in parentheses, e.g. "Q3: Should dates be parsed as US or ISO
  format? (default: ISO 8601)".

### 2b. Ask the user, then merge

Present the questions and WAIT for the user's answers. Valid user replies
include full answers, "use best judgment", or silence on individual
questions. For anything unanswered, take the stated default (or the most
conservative sensible choice if none was offered) and carry it forward as an
explicit assumption — never silently.

Then produce the working brief in exactly this structure:

1. **ENRICHED BRIEF** — the user's prompt + the material gaps and their
   answers merged in, max 300 words. The user's words win any conflict.
2. **VERIFY-LATER** — every uncertain item as a checklist entry to verify
   during execution.

### 2c. Build against the brief

Execute the task. Turn every VERIFY-LATER item into an explicit checklist
entry in your plan; verify each during execution. In the final summary, state
which were verified and which remain open for the user. Do not cite clarify
itself as an authority — verify independently or surface it as an open
question. Clarify produces no dossier and writes no `runs/` directory.

## Step 3 — Council path: resolve the roster (ONLY on explicit opt-in)

If — and only if — the user said "convene the council" (or explicitly picked
`premortem` / `critique` / `debate`), proceed. Resolution order (first hit
wins):

1. `WiseCounsel.json` in the current project's `config/` folder (per-project override)
2. This skill's own `config/WiseCounsel.json`

Validate: at least `minModels` (2), at most `maxModels` (6). If the config is
missing or invalid, tell the user and fall back to `clarify` — never invent
a roster.

## Step 4 — Run the council (opt-in path)

### Door A — OpenRouter (default, works everywhere)

Run the bundled script (resolve paths relative to this skill's folder; the
project fallback path is recorded in the repo's `Agents.md`):

```
pwsh -NoProfile -File "<skill_dir>\scripts\Invoke-WiseCounsel.ps1" `
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
agent names in `config.opencodego.agentsNamespace` (e.g. `WiseCounsel-qwen`,
`WiseCounsel-gpt-oss`), feeding each the SAME verbatim template from Step 6.
Collect their replies, then merge them yourself exactly as in Step 5. If the
subagent door misbehaves, fall back to Door A.

## Step 5 — Synthesize the dossier into the final brief

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

## Step 6 — Council prompt templates (send verbatim, with the brief appended)

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

## Step 7 — Execution protocol (after either path)

- Ask the user the build-changing open questions FIRST (max 5) — in clarify
  this already happened at Step 2b.
- Turn every "Verify:" item into an explicit checklist entry in your plan;
  verify each during execution, and state in the final summary which were
  verified and which remain open for the user.
- Never cite a council member as an authority for a factual claim in code,
  comments, docs, or your final answer. Verify independently, or surface it
  as an open question.
- On the council path, cite the dossier path (`runs/...`) in your final
  answer so the user can audit the reasoning. Clarify has no dossier.

## Failure handling (council path)

- Exit `2` (no members responded): fall back to `clarify`, proceed with the
  task normally, and tell the user the council was unavailable.
- 1-2 members failed: proceed with the survivors; say which were skipped.
- Repeated timeouts: raise `limits.timeoutSec` once and retry that member;
  if it still fails, skip it.

## Cost and latency expectations

- `clarify` (default): **$0.00, no latency hit** — no sub-models are called.
- `balanced-six` preset: roughly $0.001–0.003 per full council (each member
  gets a 1200-token budget; visible output is capped at 300 words by the
  template, the rest absorbs hidden reasoning on thinking models).
- `free-six` preset: $0.00.
- Wall time ≈ slowest member (~15–45 s, members fire in parallel).
- `debate` round 2 runs sequentially and adds ~1–2 minutes.

## Config reference (council path)

`config/WiseCounsel.json`:
- `provider`: `"openrouter"` (Door A) or `"opencodego"` (Door B)
- `models`: array of `{ id, label, family }`, 2–6 entries — THE roster
- `limits`: `{ maxOutputTokens, timeoutSec, temperaturePremortem,
  temperatureDebate }`
- `opencodego`: `{ enabled, agentsNamespace }` for Door B agent names

Presets live in `config/presets.json`: `balanced-six` (default),
`free-six`, `pair-minimum`. To change the roster: edit the project copy,
then re-run `scripts/Install-WiseCounsel.ps1` to sync the installed copy
(or edit the installed copy directly for a quick experiment).
