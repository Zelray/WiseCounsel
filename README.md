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

WiseCounsil's improvement claim is tested, not asserted. The full
pre-registered protocol — hypotheses, arms, grading, statistics, and a hard
budget — was committed to this repo **before** any evaluation data was
collected ([docs/EVAL-DESIGN.md](docs/EVAL-DESIGN.md)), and the pilot ran
under it. Full numbers and caveats: [docs/RESULTS.md](docs/RESULTS.md).

**Pilot result (48 runs, $0.24, hidden-spec coding tasks):** council-enriched
briefs improved the executor's first-attempt pass rate by a mean **+15.8
points** (24.2% → 40.0%) at ~$0.005 extra per task — **a promising signal,
not yet a confirmed finding** (95% CI [3.3, 35.8], p = 0.125 on 6 tasks; the
pre-registered confirmatory bar was p < 0.05). The strongest mechanistic
finding: the council's questions overlapped only **21.6%** with the
questions the frontier model asked itself — differently-trained families
really do surface different gaps. The self-questions control also improved
(+11.7 pp), so the council's *unique* premium (+4.2 pp) is not yet
distinguishable from noise at this scale. A null or negative wave-2 result
will be published here exactly as a positive one would be.

- **Arms:** baseline (brief alone) · council (the shipping skill) ·
  self-questions (the same executor asks its own questions — the ablation
  that isolates what the council actually adds) · single critic.
- **Grading:** deterministic unit tests authored from hidden specs and frozen
  before any model call — not model opinion.
- **Reproducibility:** raw transcripts for all 56 runs ship in the repo
  audit trail (`eval/results/`), and the whole pipeline runs offline for
  zero dollars with `pwsh -File eval/Invoke-DryRunSmoke.ps1`.

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
