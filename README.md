# WiseCounsil

**A council of cheap AI models that reads your prompt before your frontier
model does — and makes the frontier model's first try the right one.**

Six cheap or free models fire **in parallel** and *attack* your task brief —
surfacing missing rules, ambiguities, and risky assumptions — before your
frontier model writes a line of code. You answer a handful of build-changing
questions; the frontier model gets an enriched brief instead of guessing in
silence. A full council costs **~$0.003** and takes ~15–45 seconds.

[![ci](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

It also runs **debates** (six models take positions, then rebut each other
anonymously) and **plan critiques** (cheap models attack your plan before you
execute it).

## Evidence

WiseCounsil's improvement claim is being tested, not asserted. The full
pre-registered protocol — hypotheses, arms, grading, statistics, and a hard
budget — was committed to this repo **before** any evaluation data was
collected: see [docs/EVAL-DESIGN.md](docs/EVAL-DESIGN.md).

- **Hypothesis:** on spec-gappy coding briefs, a council-enriched pipeline
  raises the executor's first-attempt pass rate on hidden ground-truth tests.
- **Arms:** baseline (brief alone) · council (the shipping skill) ·
  self-questions (the same executor asks its own questions — the ablation
  that isolates what the council actually adds) · single critic.
- **Grading:** deterministic unit tests authored from hidden specs and frozen
  before any model call — not model opinion. A blind three-judge panel scores
  the decision-track tasks.
- **Pilot:** 6 hidden-spec tasks + 2 decision tasks; a hard $6 spend cap.
  The pilot's job is to prove the harness and size the confirmatory run.
- **You can run the whole pipeline yourself right now, with zero API spend
  and zero keys:** `pwsh -File eval/Invoke-DryRunSmoke.ps1`

**Results are pending. A null or negative result will be published in
[docs/RESULTS.md](docs/RESULTS.md) exactly as a positive one would be.**

## Why not just ask the model to think harder?

That is exactly the question the experiment is built to answer. The
self-questions arm holds everything constant except *where the questions come
from* — if the council's question selection beats the frontier model's own,
the multi-model diversity premise earns its keep; if it doesn't, this README
will say so. Cheap models from differently-trained families carry different
blind spots; coordinated attack-don't-answer templates aim that diversity at
your brief's gaps. Whether it works is an empirical question, and the eval
harness in `eval/` is built to answer it honestly.

## Install

```powershell
git clone <this repo> WiseCounsil
cd WiseCounsil\wise-counsil
pwsh -File scripts\Install-WiseCounsil.ps1
```

The installer validates every roster model against OpenRouter's live catalog,
checks your API key (`env:OPENROUTER_API_KEY` or `~\.openrouter-client.key`),
and copies the skill into `~\.config\opencode\skills\wise-counsil\` and
`~\.claude\skills\wise-counsil\`.

## Use

Say **"wise counsil"** (or "council this") before a big task. Modes are
picked automatically and can be forced: `premortem` (default for builds),
`debate` (research/decision questions, 2 rounds), `critique` (attack an
existing plan).

## Cost

- `balanced-six` (default): **~$0.003 per council** — verified in the
  2026-10-01 smoke test at $0.0015 for a two-member council.
- `free-six`: **$0.00** (subject to your OpenRouter account's privacy
  settings; see Known Constraints in Agents.md).
- OpenCodeGo users: flat-rate plan, so a council costs **$0 extra**.
- Wall time ≈ slowest member (~15–45 s; members fire in parallel).

## When NOT to use it

Quick fixes, typos, well-specified small edits, high-volume routine work,
tight-latency situations. The council is for big, holey, high-stakes work —
opt-in, never always-on.

## Design rationale

Cheap models attack, the frontier model decides: council members never
produce final answers, every uncertain claim is phrased as a "Verify:"
question, and the enriched brief extends the user's words without ever
replacing them. The full rationale — three failure modes and their
mitigations, the synthesis split, the engineering decision log — lives in
[docs/DESIGN.md](docs/DESIGN.md).

## Honest limits

Cheap models hallucinate confidently; WiseCounsil's mitigations (attack-don't-
answer templates, candidates-not-facts framing, verify-later checklists)
reduce but do not eliminate contamination. Six models trained on overlapping
internet data herd toward consensus narratives — especially on finance. This
is a quality amplifier and a cheap re-roll saver, not an oracle. And the
central claim — that the council improves frontier-model output — is exactly
what `docs/EVAL-DESIGN.md` is built to test, with a pre-registered
commitment to publish whatever the data says.

## Roadmap

1. **Pilot eval run** — execute the pre-registered pilot (gated on the $6
   budget cap; see docs/EVAL-DESIGN.md).
2. **Wave-2 confirmatory run** — 30 calibrated tasks, plus the
   compute-matched baseline and sham-context arms the literature expects.
3. **OpenCodeGo native door** — subagent definitions pinned to OpenCodeGo
   models so councils ride the flat-rate plan inside OpenCode.
4. **Web app** — the plus-button model manager. Deliberately phase 2.
