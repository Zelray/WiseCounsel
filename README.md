# WiseCounsel

[![ci](https://github.com/Zelray/WiseCounsel/actions/workflows/ci.yml/badge.svg)](https://github.com/Zelray/WiseCounsel/actions/workflows/ci.yml)

**I bet that a council of cheap AI models, attacking your prompt before a
frontier model starts work, would make the frontier model's first try
better. I pre-registered the experiment, ran it for $2.21, and the data
killed the bet — so I shipped what the data supported instead.** The
+13-point winner turned out to be the scaffold: your model stopping to ask
you the questions that change what it builds. The multi-model council was a
null. Both findings are published here, because that was the commitment
made before the data existed.

That story in 90 seconds:

- **The question.** Do 2–6 cheap models from different training families,
  firing in parallel to attack a task brief (missing rules, ambiguities,
  risky assumptions), improve what a frontier model builds on its first
  attempt — enough to be worth their cost?
- **The method.** Decision rules, arms, grading, and a hard budget cap were
  committed to this repo **before** any data was collected
  ([docs/EVAL-DESIGN.md](docs/EVAL-DESIGN.md)). 30 coding tasks with hidden
  reference specs, deterministic unit-test graders calibrated to a 30–70%
  baseline band, and SHA-256-frozen task files. Five arms, including the two
  that matter: **self-questions** (same scaffold, no council — the ablation)
  and a **sham arm** (a dossier generated from a *different* task — the
  placebo control).
- **The result** (325 runs, ~$2.21 billed, 2026-10-05): the scaffold lifted
  first-attempt pass rate **+13.2 points** (44.8% → 58.0%, p = 0.0002) and
  beat compute-matched best-of-3-with-selection, which gained **exactly
  zero**. But the council matched the model asking its own questions —
  **B − C = −0.5 points (95% CI [−5.7, +4.5], p = 0.90)** — and the sham
  dossier performed identically to the real one. The expensive ingredient
  was inert; the discipline was the active ingredient.
- **The decision.** Kill the council's default status, ship the scaffold.
  That pivot **is** v0.2.0, and the honest boundary of the null is written
  down too: it covers *frontier executors on short, self-contained coding
  tasks* — not weaker executors, not knowledge-boundary tasks, not long
  research briefs. The council question stays open exactly where content
  could matter. Full numbers and caveats:
  [docs/RESULTS.md](docs/RESULTS.md), and the founder's own account of the
  call: [DECISION-MEMO.md](DECISION-MEMO.md).

## What shipped

**`clarify` (the default; $0):** say **"wise counsel"** before a big task
and your frontier model generates up to 5 build-changing questions about
your brief, asks you, and merges your answers into an enriched brief with a
verify-later checklist — no sub-models, no API calls, no latency hit.

**The council (opt-in):** say **"convene the council"** and 2–6 cheap or
free models fire **in parallel** and *attack* your brief. A full council
costs **~$0.003** and takes ~15–45 seconds. It also runs **debates** (six
models take positions, then rebut each other anonymously) and **plan
critiques** (cheap models attack your plan before you execute it).

## Evidence

**Wave-2 confirmatory result (300 runs, 30 calibrated tasks, 5 arms, ~$2.21
billed, 2026-10-05):** briefs enriched with answered open questions lifted
the executor's first-attempt pass rate **+13.2 points** (44.8% → 58.0%,
p = 0.0002) over baseline and beat compute-matched best-of-3-with-selection,
which gained **exactly zero** over a single attempt. The confirmatory
primary comparison — council vs the executor asking its own questions — came
in at **B − C = −0.5 points (95% CI [−5.7, +4.5], p = 0.90)**, and a sham
dossier built from a *different* task performed identically to the real
one. Per the pre-registered decision rule this is a **null on the council
premium**, published here exactly as a positive would be. (A further 25
Track-2 decision-brief runs were mechanically unreliable and are reported
as unvalidated — see docs/RESULTS.md.)

- **Arms:** baseline (brief alone) · council (the shipping skill) ·
  self-questions (the executor asks its own questions — the ablation) ·
  sham context (dossier from the wrong task) · compute-matched best-of-3.
- **Grading:** deterministic unit tests authored from hidden specs, blind
  to the skill's design, calibrated to a 30–70% baseline band, and frozen
  (SHA-256) before any model call — not model opinion.
- **Reproducibility:** the result summaries ([docs/RESULTS.md](docs/RESULTS.md),
  `eval/results/summary.md`, `eval/results/summary-t2.md`) and the run
  manifest (`eval/results/manifest.jsonl`) are committed to the repo; raw
  transcripts for all 325 wave-2 runs are retained locally but not committed
  (they contain unredacted model traffic).

**Run it yourself:** the whole pipeline proves out offline for zero dollars
with `pwsh -File eval/Invoke-DryRunSmoke.ps1` (mock executor, zero network).
The actual study was launched as
`pwsh -NoProfile -File eval/Invoke-Eval.ps1 -Arms A,B,C,E,F -Reps 2 -TaskFilter T1 -MaxSpendUsd 8`
plus the same with `-Reps 1 -TaskFilter T2` — real spend, on your own
OpenRouter key; see docs/EVAL-DESIGN.md for the protocol those commands
execute.

## Install

```powershell
git clone https://github.com/Zelray/WiseCounsel.git WiseCounsel
cd WiseCounsel\wise-counsel
pwsh -File scripts\Install-WiseCounsel.ps1
```

The installer validates every roster model against OpenRouter's live catalog,
checks your API key (`env:OPENROUTER_API_KEY` or `~\.openrouter-client.key`),
and copies the skill into `~\.config\opencode\skills\wise-counsel\` and
`~\.claude\skills\wise-counsel\`.

## Use

Say **"wise counsel"** (or "council this") before a big task. That runs
**`clarify`, the default mode**: your frontier model generates up to 5
build-changing questions, asks you, and merges your answers into an enriched
brief with a verify-later checklist — no sub-models, no API calls, no extra
wall time.

The council modes run **only on an explicit "convene the council"** (or when
you name one directly): `premortem` (attack a build brief), `debate`
(research/decision questions, 2 rounds), `critique` (attack an existing
plan).

## Cost

- `clarify` (default): **$0.00, no latency hit** — no sub-models are called.
- `balanced-six` (default council preset): **~$0.003 per council** — verified
  in the 2026-10-01 smoke test at $0.0015 for a two-member council.
- `free-six`: **$0.00** (subject to your OpenRouter account's privacy
  settings; see Known Constraints in Agents.md).
- OpenCodeGo users: flat-rate plan, so a council costs **$0 extra**.
- Wall time ≈ slowest member (~15–45 s; members fire in parallel).

## When NOT to use it

Quick fixes, typos, well-specified small edits, high-volume routine work,
tight-latency situations. This is for big, holey, high-stakes work — and it
is never always-on.

## Design rationale

Cheap models attack, the frontier model decides: council members never
produce final answers, every uncertain claim is phrased as a "Verify:"
question, and the enriched brief extends the user's words without ever
replacing them. The full rationale — three failure modes and their
mitigations, the synthesis split, "what wave 2 taught us," and the
engineering decision log — lives in
[docs/DESIGN.md](docs/DESIGN.md).

**v0.2.0 pivot:** wave-2 measured the scaffold's lift as real and the
council premium as null, so the design followed the data — `clarify` is now
the default and the council is opt-in. That is the point of pre-registering.

## Honest limits

Cheap models hallucinate confidently; the mitigations (attack-don't-answer
templates, candidates-not-facts framing, verify-later checklists) reduce but
do not eliminate contamination. Six models trained on overlapping internet
data herd toward consensus narratives — especially on finance. The scaffold
result was measured on short-to-medium coding tasks graded by deterministic
unit tests; it is not yet measured on long research briefs, and latent
quality beyond test-visible correctness was never graded. And the council's
home turf — where multi-model content might actually matter (weaker
executors, knowledge-boundary tasks, fuzzy decision briefs) — is exactly
where this eval did not look. That is the next experiment, not a settled
one.

## Roadmap

1. **Track-2 judge re-run** — pending the owner's go-ahead. The judge
   plumbing was fixed in v0.2.0, and a small (<$0.50) re-run would validate
   the decision-brief track; it needs explicit approval plus a
   pre-registration addendum first, so it is **not** committed to here.
2. **The council question's surviving cells** — a mid-tier ("god-king")
   executor with a council brief on knowledge-boundary tasks: the
   strongest still-open version of the original hypothesis, already
   sketched in docs/DESIGN.md.
3. **OpenCodeGo native door** — subagent definitions pinned to OpenCodeGo
   models so councils ride the flat-rate plan inside OpenCode.
4. **Web app** — the plus-button model manager. Deliberately phase 2.
