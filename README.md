# WiseCounsel

**Before a big task, WiseCounsel makes your frontier model stop and ask you
the questions that change what it builds — then build against your answers.**

Say **"wise counsel"** and your frontier model generates up to 5
build-changing questions about your brief, asks you, and merges your answers
into an enriched brief with a verify-later checklist. That scaffold is the
product, and the lift is measured, not asserted: **+13 points on
first-attempt pass rate**, at **$0 extra cost**, with **no sub-models and no
latency hit**.

[![ci](https://github.com/Zelray/WiseCounsel/actions/workflows/ci.yml/badge.svg)](https://github.com/Zelray/WiseCounsel/actions/workflows/ci.yml)

The multi-model council — 2–6 cheap or free models that fire **in parallel**
and *attack* your brief, surfacing missing rules, ambiguities, and risky
assumptions — is still here, but it is **opt-in**: say **"convene the
council"** when you want that multi-model diversity anyway. A full council
costs **~$0.003** and takes ~15–45 seconds. It also runs **debates** (six
models take positions, then rebut each other anonymously) and **plan
critiques** (cheap models attack your plan before you execute it).

## Evidence

WiseCounsel's improvement claim is tested, not asserted. The full
pre-registered protocol — hypotheses, arms, grading, statistics, and a hard
budget — was committed to this repo **before** any evaluation data was
collected ([docs/EVAL-DESIGN.md](docs/EVAL-DESIGN.md)), and both the pilot
and the wave-2 confirmatory run executed under it. Full numbers and
caveats: [docs/RESULTS.md](docs/RESULTS.md).

**Wave-2 confirmatory result (300 runs, 30 calibrated tasks, 5 arms, ~$2.21
billed, 2026-10-05):** the question-answer scaffold works — briefs enriched
with answered open questions lifted the executor's first-attempt pass rate
**+13.2 points** (44.8% → 58.0%, p = 0.0002) and beat compute-matched
best-of-3-with-selection, which gained **exactly zero** over a single
attempt. But the multi-model council itself — the part the project was
originally built around — **did not earn its keep**: the confirmatory
primary comparison (council vs the executor asking its own questions) came
in at **B − C = −0.5 points (95% CI [−5.7, +4.5], p = 0.90)**, and a sham
dossier built from a *different* task performed identically to the real
one. Per the pre-registered decision rule this is a **null on the council
premium**, published here exactly as a positive would be, per the
commitment made before the data existed.

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
  (they contain unredacted model traffic), and the whole pipeline runs
  offline for zero dollars with `pwsh -File eval/Invoke-DryRunSmoke.ps1`.

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
tight-latency situations. The council is for big, holey, high-stakes work —
opt-in, never always-on.

## Design rationale

Cheap models attack, the frontier model decides: council members never
produce final answers, every uncertain claim is phrased as a "Verify:"
question, and the enriched brief extends the user's words without ever
replacing them. The full rationale — three failure modes and their
mitigations, the synthesis split, the engineering decision log — lives in
[docs/DESIGN.md](docs/DESIGN.md).

**v0.2.0 pivot:** wave-2 measured the scaffold's lift as real and the
council premium as null, so the design followed the data — `clarify` is now
the default and the council is opt-in. That is the point of pre-registering.

## Honest limits

Cheap models hallucinate confidently; WiseCounsel's mitigations (attack-don't-
answer templates, candidates-not-facts framing, verify-later checklists)
reduce but do not eliminate contamination. Six models trained on overlapping
internet data herd toward consensus narratives — especially on finance. This
is a quality amplifier and a cheap re-roll saver, not an oracle. And the
central claim — that the council improves frontier-model output — is exactly
what `docs/EVAL-DESIGN.md` is built to test, with a pre-registered
commitment to publish whatever the data says.

## Roadmap

1. **Track-2 judge re-run** — pending the owner's go-ahead. The judge
   plumbing was fixed in v0.2.0, and a small (<$0.50) re-run would validate
   Track 2; it needs explicit approval plus a pre-registration addendum
   first, so it is **not** committed to here.
2. **OpenCodeGo native door** — subagent definitions pinned to OpenCodeGo
   models so councils ride the flat-rate plan inside OpenCode.
3. **Web app** — the plus-button model manager. Deliberately phase 2.
