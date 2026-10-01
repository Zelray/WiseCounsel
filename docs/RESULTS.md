# Results — Pilot (2026-10-01)

> Pre-registered protocol: [EVAL-DESIGN.md](EVAL-DESIGN.md), committed at
> `3e273b2` before any data was collected. Machine-generated tables:
> `eval/results/summary.md` (Track 1) and `summary-t2.md` (Track 2); raw
> transcripts for every run under `eval/results/raw/`. Nothing on this page is
> hand-typed except interpretation.

## Headline

**In the pre-registered pilot, the council-enriched pipeline improved
first-attempt pass rate on hidden-spec coding tasks by a mean +15.8 points
(24.2% → 40.0%), for ~$0.005 extra and ~40 s per task. The improvement is
NOT a confirmed finding at the pre-registered bar** — 6 tasks is too few
(p = 0.125; the protocol required p < 0.05). It is a promising, honestly
bounded signal, plus real mechanistic support for the diversity premise:

- **Council questions were materially different questions.** Mean token
  overlap between the council's questions and the executor's own: **21.6%**
  — the council surfaced content the executor did not ask itself about.
- **The council ran 12/12 without a single failure** (all 6 members, every
  task), and its full pipeline cost was ~$0.005/task.

## Track 1 — hidden-spec coding tasks (primary, pre-registered)

Executor: `google/gemini-2.5-flash`, single-shot, temp 0. 6 tasks × 4 arms
× 2 reps = 48 runs. Score = fraction of hidden-rule unit tests passed.

| Arm | Mean | Description | Cost/task |
|---|---|---|---|
| A — baseline | 24.2% | brief alone | $0.002 |
| B — council | 40.0% | shipping skill, questions answered | $0.007 |
| C — self-questions | 35.8% | executor asks its own questions | $0.004 |
| D — single critic | 41.7% | one cheap model's questions | $0.005 |

Pre-registered paired comparisons (task-level deltas):

| Comparison | Δ (pp) | 95% CI | p (sign-flip) | Pre-registered verdict |
|---|---|---|---|---|
| **B − A** (primary) | **+15.8** | [3.3, 35.8] | 0.125 | **Not confirmed** (rule required p < 0.05; CI excluding 0 and Δ ≥ +5 both met) |
| C − A | +11.7 | [−15.0, 42.5] | 0.625 | null — but same direction as B − A |
| B − C (mechanism) | +4.2 | [−10.8, 20.8] | 0.750 | null at this n — council premium over self-questioning is not distinguishable |
| D − B | +1.7 | [−4.2, 7.5] | 0.8125 | null — single critic ≈ full council on scores |

**Reading this honestly:** much of the gain comes from *asking questions and
getting answers at all* (arm C also improved +11.7 pp). The specifically
council-flavored claim — that six cheap models pick better questions than the
frontier model picks for itself — shows only +4.2 pp at a sample size this
pilot was pre-declared unable to resolve. The wave-2 scale gate (Δ ≥ +10 and
p < 0.10) did **not** fire by its letter (p = 0.125); scaling to a powered
run is a fresh spend decision, not an automatic continuation.

### Known artifact, disclosed

Two baseline runs (username-validator, both reps) scored 0 on a **harness
extraction bug**: the executor omitted its closing code fence, the fallback
saved an unparsable file, and the grader failed. Per the pre-registered
no-exclusions rule these zeros stand in the official numbers — and readers
should note the artifact *favors* the council comparison (it penalized arm A
on one of six tasks; the same task's B/C/D runs extracted cleanly). The
parser is hardened before any wave-2 run. This is exactly the kind of wart
pre-registration exists to force into the open.

### Integrity checks (all pre-registered)

- **Leakage:** all 12 baseline prompts vs answer sheet: max overlap 0.148
  (threshold 0.4) — the answer sheet never leaked into the baseline.
- **Council reliability:** 12/12 councils returned full rosters; zero
  re-rolls (per the no-survivorship rule).
- **Judge arm-detectability probe:** judges answered "enriched" for every
  output regardless of arm — a constant response: no detectable arm bias,
  but the probe is uninformative as designed and Track 2 stays secondary.

## Track 2 — decision tasks (secondary)

2 tasks × 4 arms, judged by a 3-judge panel (claude-haiku-4.5, gpt-5-mini,
gemini-2.5-flash), rubric 6×0–2. **Uninformative at this size:** one task
(storage ADR) hit the ceiling — every arm scored 1.0 — and the payment task
n=2 CIs span ±25 pp. Council arm trended *lower* than baseline (−12.5 pp)
but this is noise on two tasks and should not be read as either harm or
help. Lesson recorded: wave 2 needs harder, non-ceiling decision tasks.

## Diversity audit

The pre-registered question-overlap audit came back at **21.6% (Track 1)**:
~78% of the council's question content was not duplicated by the executor's
own questions. This is the pilot's strongest piece of evidence *for* the
product's core premise — differently-trained families surface different
gaps — and it is independent of the noisy score comparison.

## What would falsify the thesis

If a powered run shows B − A ≈ 0 with C − A ≈ B − A, then councils are an
expensive way to say "ask clarifying questions," and this repo will say so.

## Next step (owner decision, new spend)

Wave 2 per the pre-registration: ~30 calibrated tasks (incl. fixing the
ceiling Track-2 task), hardened parser, arms A/B/C/D (+E sham-context,
+F compute-matched for the literature-grade claim). Estimated ~$2–5 total
on the same key, ~2–4 h wall clock. The pilot's job — proving the harness
and sizing the effect — is done; the confirmatory run is what the Evidence
section can cite.
