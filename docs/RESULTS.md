# Results

> Data lives in `eval/results/` (machine-written: `summary.md`, `summary.csv`,
> `manifest.jsonl`, and raw per-run transcripts under `raw/`, which are
> gitignored). This file is the interpretation. It does not exist yet because
> the pilot has not run — per the pre-registration in
> [EVAL-DESIGN.md](EVAL-DESIGN.md), **a null or negative result will be
> published here exactly as a positive one would be.**

## What will land here when the pilot runs

1. The pre-registered table: arm × mean score, with paired deltas, 95%
   bootstrap CIs, and sign-flip permutation p-values (produced by
   `eval/Invoke-Analyze.ps1` — no hand-typed numbers).
2. Cost and wall-clock per arm, because "better" is only meaningful per
   dollar and per second.
3. The mechanism evidence: which hidden-spec rules each arm's questions
   actually recovered (the per-rule pass matrix), and the council-vs-self
   question-overlap number that decides whether the "different families,
   different blind spots" story survives contact with data.
4. What the numbers support, what they don't, and what would have
   falsified the thesis.
