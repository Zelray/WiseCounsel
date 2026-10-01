# WiseCounsil Evaluation — Pre-registered Design (v1)

> **Preregistration.** This document was committed to the repository BEFORE any
> evaluation data was collected. It specifies the hypotheses, arms, tasks,
> grading, statistics, and budget in advance; it is never edited after data
> collection begins (corrections, if any, are appended as dated addenda). The
> git history is the timestamp. Commit hash of the data-collection start:
> recorded in `eval/results/manifest.jsonl` at first launch.
>
> **Honesty commitment:** a null or negative result will be published in
> `docs/RESULTS.md` exactly as a positive one would be. Raw transcripts are
> retained for every claim.

## What we are testing

**Hypothesis (H1, product claim):** on spec-gappy coding briefs, a
council-enriched pipeline (cheap models attack the brief → open questions are
answered from a frozen answer sheet → the executor builds with those answers)
raises the frontier executor's first-attempt pass rate on hidden ground-truth
tests, relative to the same executor receiving the brief alone.

**Hypothesis (H2, mechanism claim — the scientifically interesting one):** the
council's question selection beats the executor's *own* question generation
under identical downstream conditions. H2 is the claim that makes WiseCounsil
more than "asking clarifying questions helps" — it is confirmed, if at all,
only in wave 2 (see Statistics).

**What we explicitly do NOT claim:** that councils make frontier models
better in general; that six cheap models substitute for a frontier model; or
anything about tasks outside the hidden-spec coding and decision-task classes
below.

## Arms

All arms share: same executor model, same system prompt scaffold, same task
pack, temperature 0, same run order (interleaved round-robin across arms so
provider-load drift cannot correlate with arm), and a single-shot executor
(no tools, no follow-up turns — the claim is bounded to this setting).

| Arm | Name | Pipeline |
|---|---|---|
| **Arm A** | baseline | Public brief → executor builds the deliverable in one pass. No mention that questions or answers exist. Structurally cannot touch answer-sheet text (separate code path; leakage-checked). |
| **Arm B** | council | Public brief → the **shipping skill** (`wise-counsil/scripts/Invoke-WiseCounsil.ps1 -Mode premortem`) convenes the 6-member council → the executor model itself synthesizes the skill's Step-4 final brief (≤5 open questions, exactly as the product works) → a clerical matcher pairs questions to frozen answer-sheet entries → executor builds with the brief + verbatim matched answers. Unmatched questions get the fixed fallback: "Not specified — use best judgment and state the assumption in a comment." |
| **Arm C** | self-questions | Identical to Arm B **minus the dossier**: the executor generates its own ≤5 questions from the brief alone (same synthesis prompt, empty dossier slot), matched and answered by the same matcher with the same fallback. **B vs C holds everything constant except where the questions came from — this is the ablation that isolates the council.** |
| **Arm D** | single critic (exploratory, pilot only) | Identical to B with a one-member council (single cheap model, same template). Answers "panel vs single critic"; demoted to exploratory so it cannot dilute the hierarchy. |

**Matcher (anti-confound):** the executor-family model at temperature 0,
JSON-only output, maps each question to answer-sheet entry IDs or `NONE`. It
never sees the hidden spec or tests. Only **verbatim** matched entry text is
injected — the matcher cannot paraphrase answers into existence. Sheets
include 1–2 dead entries (out-of-scope topics) so the `NONE`/fallback path is
exercised identically in B, C, D.

**Council-failure rule (pre-stated, no survivorship):** if the council exits
with all members failed, the Arm-B run proceeds without enrichment and is
analyzed exactly as it ran. Council exit codes are logged per run and the
success rate is reported. No council re-rolls.

**Fixed question-sets:** one council dossier and one self-question set per
task, generated once and reused across that task's repetitions.
Repetitions therefore measure build-execution noise only, identically for
every arm. Council-sampling variance is excluded by design and noted as a
limitation.

**Wave-2 arms (pre-announced now, run later, separately budgeted):**
- **Arm E — sham context:** Arm B's pipeline with the dossier replaced by a
  council run on a *different* task, padded to matching length. Separates
  "the council's content" from "extra relevant-looking text in the prompt."
- **Arm F — compute-matched:** executor best-of-N (N samples, self-selected
  best) token-matched to the council pipeline's cost. The literature's
  minimum credible baseline: without it, "you bought the gain with tokens"
  is an unanswerable objection.

## Tasks

Two tracks, all tasks original to this repo (documented provenance per card;
no benchmark items are reused).

**Track 1 — hidden-spec coding tasks (primary metric).** A public brief that
is honest but omits 6–8 unstated rules; a hidden spec fixes the correct
choices; a frozen unit-test file grades implementations rule by rule.
Archetypes: domain-rule calculators, input validators, a state machine,
date logic. Score = passed tests / total tests (partial credit preserved);
per-rule pass/fail is also recorded — that matrix is the mechanism evidence.

**Track 2 — decision tasks (secondary).** Pick/recommend briefs (payment
processor selection; storage architecture decision) withholding 5–6
decision-relevant facts that live in the answer sheet. Graded by the judge
panel on a frozen 6-dimension rubric (0–2 per dimension), see Judge.

**Ground truth freeze order (anti-circularity):** task packs — public brief,
hidden spec, tests, answer sheet — are authored together, hashed (SHA-256,
recorded in the manifest), and committed to git **before any council or
executor call on those tasks**. Nobody inspects council output before the
freeze; any post-freeze pack edit forces all four arms to re-run for that
task. At least half of Track 1 was authored by models instructed to derive
rules from domain conventions only, explicitly blind to this skill's design
and templates (per-card `provenance` records which).

**Difficulty calibration (documented, control-arm only):** during suite
construction, the executor model runs each public brief alone once; tasks
outside the 30–70% baseline pass band are rewritten before the freeze. This
uses only control-arm behavior, cannot bias the B−A direction, and is
disclosed as a suite-construction step.

## Judge (Track 2 only)

Three-judge ensemble, each from a model family absent from the council
roster (roster families: DeepSeek, Alibaba/Qwen, Mistral, OpenAI-open
gpt-oss, Meta-Llama, Google-Gemma). Headline score = mean of the three;
all three reported individually. Judge hygiene: blind to arm labels;
randomized presentation order (seeded, logged); anchored rubric frozen
before runs; executors are instructed (per the shipping skill's own
directives) to never reference the council, and a regex audit flags any
output containing council traces (flagged runs are excluded from judged
scoring, with the exclusion count reported).

Known judge limitations, disclosed: position and verbosity bias exist; we
mitigate (blinding, rubric anchoring, multi-judge panel, length-vs-score
correlation reported) but do not run human raters — a solo project cannot.
An **arm-detectability probe** asks each judge to guess which arm produced
each output; if judges beat chance, Track 2 is reported as contaminated,
not as evidence. Judge-panel agreement (Spearman) is reported; below 0.5,
Track 2 is reported as unreliable. Track 1's hidden tests are the primary
metric precisely because they need no judge.

## Statistics

Pilot: 6 Track-1 tasks × 4 arms × 2 reps, plus 2 Track-2 tasks × 4 arms ×
1 rep. **The pilot is a signal-detection and power-estimation run, not a
publication-grade trial.** With 8 paired task-level deltas, it can only
detect large effects (≥ ~15 points at typical noise); its deliverables are
the harness itself, a noise estimate (σ of task deltas) that sizes wave 2,
and a go/no-go signal.

- **Unit of analysis:** per task, mean over reps → paired task-level deltas.
- **Primary comparison (pilot): B vs A** (the product claim; the largest
  expected effect). Secondary, in a pre-stated hierarchy with nominal
  p-values only: C vs A, then B vs C. Exploratory: D vs B. No other
  comparisons are made.
- **Test:** exact paired sign-flip permutation test on task deltas
  (2⁸ = 256 flips; p floor ≈ 0.008). **Effect size:** mean delta in
  percentage points + 95% percentile bootstrap CI (10,000 task resamples)
  + standardized effect (mean/SD of deltas). Cost and latency per arm
  reported alongside — a claim is only meaningful per dollar and per second.
- **Pre-stated decision rules (pilot):** "council helps" = B−A ≥ +5 points,
  p < 0.05, CI excludes 0. "Council hurts" = B−A ≤ −5 points, p < 0.05.
  Everything else is null — including "significant but < 5 points," which
  is not practically meaningful against a $0.003, ~40-second council.
- **Wave-2 gate:** pilot B−A ≥ +10 points with p < 0.10 scales the suite to
  30 tasks (calibrated), adds Arms E and F, and re-runs the confirmatory
  test — where **B vs C becomes the primary comparison**, powered from the
  pilot's measured σ. H2 is claimed, if ever, only from wave 2.
- **Blinded analysis:** during analysis, arms are referred to by neutral
  codenames; the analysis script is committed before arm labels are
  revealed. All reps are reported, including failures; no post-hoc task or
  run exclusions except the pre-stated rules above.
- **Diversity audit (reported regardless of outcome):** fraction of Arm-C
  self-questions duplicated by the council's questions. If overlap is high,
  the "different families, different blind spots" story is dead no matter
  what the scores say — and we will say so.

## Leakage and validity checks

1. **Answer-sheet leakage into Arm A/C:** automated pre-flight check — for
   every Arm-A prompt, word-overlap against every sheet entry must stay
   below threshold; the check's output is saved per run as `leak-check.txt`.
   Hidden specs and tests never enter any prompt in any arm.
2. **Question-phrasing leakage:** council questions can smuggle answers
   ("Verify: is overtime 1.5× after 40 h?" *is* the spec). The per-task
   **spec-coverage audit** reports, for each arm's pre-build material, what
   fraction of hidden-spec dimensions are stated or strongly implied —
   BEFORE execution. This number is reported as a first-class result, not a
   footnote, because question *selection* quality is exactly what H2 claims.
3. **Test-gaming audit:** tests split into sheet-mapped vs generic smoke;
   both sub-scores reported; solutions are manually audited for hardcoded
   test-visible constants at pilot scale.
4. **Reproducibility pack:** per experiment, `eval/results/` holds the
   manifest (one JSON row per run: arm, task, rep, model ids incl.
   OpenRouter's served-model string, temperatures, seeds, hashes of brief/
   tests/sheet/templates, score, cost, latency, flags) plus per-run
   directories with exact request bodies, raw responses, delivered answer
   mappings, and score JSONs. A stranger can recompute every number from
   these files alone.

## Budget

Worst-case pilot math (padded token estimates, gemini-class executor
pricing; ~$20 key headroom): 22 executor runs per arm ≈ $0.99/arm; councils
≈ $0.005 each ≈ $0.11 (Arm B) + $0.04 (Arm D); matcher ≈ $0.02/arm (treated
arms); judge share ≈ $0.18/arm. **Pilot worst case ≈ $4.89; hard cap $6.00**
(including a re-run reserve). The harness aborts (exit 4) the moment
cumulative spend crosses the cap. Wave 2 (~30 tasks × 5 arms × 2–3 reps +
judging) is separately estimated and separately approved before launch.

*Model IDs named in `eval/config.json` are validated against OpenRouter's
live catalog at launch; any ID drift re-opens this document as a dated
addendum before data collection.*

## Preregistration addenda

(none yet — this section records any post-freeze, pre-launch changes with
dates and reasons; after data collection begins, no edits.)
