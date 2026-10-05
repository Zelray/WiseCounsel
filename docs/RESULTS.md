# Results — Wave 2 confirmatory run (2026-10-05)

> Pre-registered protocol: [EVAL-DESIGN.md](EVAL-DESIGN.md), committed at
> `3e273b2` before any data was collected; wave-2 scope, arms, budget, and
> decision rules appended as a dated addendum at `3097b0a`, also before any
> wave-2 model call. Machine-generated tables: `eval/results/summary.md`
> (Track 1, confirmatory) and `summary-t2.md` (Track 2); raw transcripts for
> every run under `eval/results/raw/`. Nothing on this page is hand-typed
> except interpretation. Per the pre-registered honesty commitment, the null
> primary result below is published exactly as a positive one would be.

## Headline

**Wave 2 (300 Track-1 runs, 30 calibrated tasks, 5 arms) tested the
mechanism claim — H2, "the council's questions beat the executor's own
questions" — and it is null. The confirmatory primary comparison came in at
B − C = −0.5 points (95% CI [−5.7, +4.5], p = 0.90, n = 30).** The
pre-registered decision rule — "council earns its keep" = B − C ≥ +5 pp AND
p < 0.05 AND bootstrap CI excludes 0 — **fails on all three conditions**.

What the same run did establish, at the strongest significance this project
has produced: **structured pre-build questions with delivered answers lift
the executor's first-attempt pass rate by ~13 points over the baseline**
(44.8% → 58.0–58.5%, p = 0.0002–0.0011) — but *whose* questions and *what*
extra context those are turns out not to matter:

- The executor's **own** questions, matched and answered exactly like the
  council's (arm C), deliver the same lift: C − A = **+13.7 pp** (p = 0.0011).
- A **sham dossier** — a real council run on a *different* task, fed in
  place of the true one (arm E) — performs identically to the genuine
  article: E − A = +13.7 pp (p = 0.0062), B − E = −0.5 pp (p = 0.94).
- **Compute-matched best-of-3 with selection (arm F) bought nothing at
  all**: F − A = 0.0 pp (p = 1.0) at 4× the executor calls. The "you just
  bought the gain with tokens" objection dies from the other direction —
  the gain is not purchasable with plain executor compute.

The pilot's own falsification criterion — "if a powered run shows
C − A ≈ B − A, then councils are an expensive way to say 'ask clarifying
questions,' and this repo will say so" — is met. The value is in the
question-answer scaffold (forcing the unknowns into the open and answering
them before the build), not in six cheap models picking the questions. The
diversity premise survives only as trivia: council and self questions
overlap just 23.9% (they really do ask different things) while scoring
identically — *different questions, same value*.

## Track 1 — hidden-spec coding tasks (primary, pre-registered)

Executor: `google/gemini-2.5-flash`, single-shot, temp 0. 30 tasks (6 pilot
re-run fresh + 24 new, every new task difficulty-calibrated into the 30–70%
baseline band before the freeze — see `eval/tasks/CALIBRATION-wave2.md`)
× 5 arms × 2 reps = 300 runs. Score = fraction of hidden-rule unit tests
passed. Freeze manifest: `eval/FROZEN-HASHES-wave2.txt` (created before any
wave-2 council/executor call).

| Arm | Mean | Description | Itemized cost/run |
|---|---|---|---|
| A — baseline | 44.8% | brief alone | $0.003 |
| B — council | 58.0% | shipping skill premortem, questions answered | $0.006 |
| C — self-questions | 58.5% | executor asks its own questions | $0.004 |
| E — sham context | 58.5% | council dossier from the WRONG task | $0.006 |
| F — compute-matched | 44.8% | best-of-3 + selection, no answers | $0.009 |

Pre-registered comparisons (paired task-level deltas; **B − C is the
confirmatory primary**, the rest the pre-stated hierarchy, nominal p):

| Comparison | Δ (pp) | 95% CI | p (sign-flip) | Pre-registered verdict |
|---|---|---|---|---|
| **B − C (primary)** | **−0.5** | [−5.7, +4.5] | **0.9007** | **NULL — decision rule fails (needed ≥ +5 pp, p < 0.05, CI excluding 0)** |
| B − A | +13.2 | [7.0, 20.2] | 0.0002 | positive, survives — but not council-specific |
| C − A | +13.7 | [6.2, 21.3] | 0.0011 | positive — self-questioning matches the council |
| B − E | −0.5 | [−8.7, +8.0] | 0.9425 | null — dossier content contributes nothing |
| B − F | +13.2 | [7.0, 20.2] | 0.0003 | positive vs compute-matched control |
| E − A | +13.7 | [5.0, 22.2] | 0.0062 | positive — even a sham dossier carries the lift |
| F − A | −0.0 | [−0.7, +0.8] | 1.0 | null — 4× compute, zero gain |

**Verdict, applied verbatim from the pre-registration:** H1-family claim
(structured question-answering helps) **confirmed, p = 0.0002**. H2 (the
council's question *selection* is the active ingredient) **refuted at n =
30** — the council premium over self-questioning is −0.5 pp with a CI that
rules out any council advantage larger than +4.5 pp.

### Known artifacts, disclosed

- **Four zeroed runs (0.7% of 600), all on one task (username-validator),
  arms A and F, both reps:** the baseline/best-of-3 executor emitted
  syntactically broken Python (`SyntaxError: '{' was never closed`), the
  grader correctly failed the file, and the run scored 0. Per the
  pre-registered no-exclusions rule these zeros stand in the official
  numbers; they mechanically favor B over A/F on that task. Labeled
  post-hoc sensitivity check (NOT part of the confirmatory table):
  excluding that task entirely, B − A = +10.9 pp and **B − C = −0.5 pp,
  still null** (n = 29). No verdict changes.
- **Cost accounting, three numbers, honestly:** the manifest's itemized
  per-run costs sum to **$1.92** for all 325 runs (per-run entries verified
  against their parts); OpenRouter's authoritative key-usage delta for the
  whole wave-2 day (calibration + both tracks) is **$2.27**; the launch
  log's running counter printed **$3.95** and is superseded — a harness
  accounting quirk (council-internal calls and intermittent provider
  cost fields are not fully itemized per run). The ~13% itemization gap
  does not touch per-arm *ratios*, which is what the cost discussion uses.
  Absolute claim to trust: **the whole confirmatory run cost about $2.21
  in provider billing**, inside the $2.50–4.00 estimate and far under the
  $8.00 hard cap.

### Integrity checks (all pre-registered)

- **Leakage:** all 60 baseline prompts vs answer sheets: verdict OK on
  every run (threshold 0.4 overlap).
- **Council reliability:** 60/60 Track-1 councils (and 5/5 Track-2)
  returned successfully; zero re-rolls, per the no-survivorship rule.
- **Diversity audit:** mean B-vs-C question-token overlap (Jaccard) =
  **23.9%** — the council asks genuinely different questions than the
  executor asks itself. In the pilot this was read as mechanistic support
  for the product; wave 2 shows different questions scoring identically,
  so diversity of questioning does not translate into value at this
  task class.
- **Arm-detectability probe:** constant (24/25 runs got exactly 2-of-3
  "enriched" votes across ALL arms including the un-enriched baseline).
  Interpreted per protocol as uninformative, not as blindness.

## Track 2 — decision tasks (secondary) — UNRELIABLE, not evidence

4 new harder decision tasks + payment-processor kept, 3-judge panel as
pre-registered. **The panel mechanically failed: 50 of 75 judge slots
(67%) returned unparseable output** (two of the three judge models —
claude-haiku-4.5 and gpt-5-mini — failed to emit parseable JSON on most
runs; only the gemini judge scored reliably, and each judge's response
overwrites the same log so the failures cannot be inspected post-hoc).
Headline scores are therefore mostly single-judge means near ceiling
(A = 0.80, B = 1.0, C = 0.85, E = 0.95, F = 0.80 of max), B − C = +15 pp
at p = 0.25 on n = 5, and the pre-registered reliability bar (panel
agreement, detectability) is not met. **Track 2 is reported as
unreliable and carries no evidentiary weight this wave.** Root cause is
diagnosed and fixable (stronger JSON-only instruction, larger
max_tokens, or structured output mode) — recorded for a future wave.

## What this means for the product

The shipping skill's premortem council, as measured, adds nothing over
asking the executor to enumerate its own questions — but the *scaffold
around* the council (surface the open questions, answer them from an
answer sheet, build once with the answers) is worth ~+13 points and beats
spending 4× the compute on best-of-3 selection. Honest framing: WiseCounsil
the scaffold works; WiseCounsil the multi-model council is, on this task
class, undifferentiated from a mirror. Owner decisions that follow —
(e.g. ship the scaffold with self-questions as the default and the council
as an opt-in; or target task classes where diversity might matter, like
the research/decision briefs Track 2 was meant to test once its judges
work) — are product calls, not eval calls.

## Pilot (2026-10-01) — history

The pilot (6 tasks × 4 arms × 2 reps + 2 decision tasks, $0.61 total, 56
runs) found B − A = +15.8 pp (p = 0.125, not confirmed at its bar),
question-overlap 21.6%, and 12/12 council reliability. Its full writeup is
preserved in git history (this file at commit `00d961b`) and its numbers
are superseded by wave 2 per the pre-registered supersession clause: the
pilot's 6 Track-1 tasks were re-run fresh inside wave 2 with the same
hidden tests. Pilot-era artifacts: `eval/FROZEN-HASHES.txt` (historical
freeze), `summary-t2.md` (wave-2 Track 2).
