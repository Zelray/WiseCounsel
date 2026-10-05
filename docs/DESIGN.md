# DESIGN.md — why WiseCounsel is shaped the way it is

## The thesis

A single frontier model is a single point of training, architecture, bias,
and failure. Cheap models from *differently-trained families* (DeepSeek,
Qwen, Mistral, Google, Meta, NVIDIA...) carry different priors and different
blind spots. Coordinated well, their diversity becomes a quality signal —
the same "diversity trumps ability" logic behind Ailin's Collective
Intelligence Engine, scaled down to a harness-native skill and a flat-rate
budget.

The idea is NOT to replace the frontier model. It is to make the frontier
model's **first attempt** land on a complete spec instead of silent guesses,
and to save expensive re-rolls. Where it pays: spec-gappy prompts (most
non-coders' prompts), domain-rule-heavy builds, research/decision debates.
Where it doesn't: quick fixes and tight-latency work.

## Three failure modes, three mitigations

1. **Hallucination contamination** — a cheap model states a wrong "fact"
   (misremembered statute, invented API) and the frontier model inherits it.
   → Mitigation: templates demand *attack, don't answer*; every uncertain
   claim must be phrased as a "Verify:" question; the frontier model's
   protocol forbids citing council members as authorities; the enriched
   brief is additive and the user's words win conflicts.

2. **Herding** — six models trained on overlapping data converge on the
   same consensus narrative (worst on finance).
   → Mitigation: debate rounds force each member to name what would change
   its mind and to rebut the *strongest* peer argument; anonymity in round 2
   prevents status effects; dissent notes survive to the final brief.

3. **Context pollution** — dumping six full transcripts into the frontier
   context costs more than the calls saved.
   → Mitigation: per-member visible output capped (~300 words / 1200-token
   budget); the frontier model synthesizes a ~600-word brief; raw dossiers
   stay on disk (`runs/`) as the audit trail, cited but not pasted.

## Who synthesizes, and why

Round 1 fires in parallel (wall time = slowest member). Debate round 2 runs
sequentially because each member must see anonymized peers first. The
*frontier model* — not a cheap aggregator — performs the final synthesis:
judging candidate evidence is exactly the judgment frontier models are best
at, and it costs nothing extra in tokens the user wasn't already spending.

## Engineering decisions (log)

| Decision | Why |
|---|---|
| Prompt templates live in SKILL.md, plumbing in the script | Models judge; script only collects. Keeps the smart part reviewable in markdown. |
| `reasoning.exclude` + 1200-token budget | Smoke test 2026-10-01: a thinking model (qwen3.8) returned empty content after hidden reasoning consumed a 400-token budget. Budget now absorbs reasoning; template still caps visible length. |
| Empty successful responses → visible failures | Silent-empty is the worst failure mode; normalize-then-report makes it diagnosable. |
| Roster validated against live catalog at install time | Model IDs rot; the installer catches dead IDs before first use. |
| Roster hard-capped at 6, min 2 | Beyond ~6, disagreement stops adding signal and latency/cost keep growing; below 2 there is no dissent. |
| Presets instead of hardcoded defaults | Switching the whole council is one flag (`-Preset free-six`). |
| `runs/` gitignored | Dossiers contain the user's raw prompts (privacy). |

## Known constraints

- **ZDR**: Mike's OpenRouter account privacy setting excludes endpoints not
  meeting its data policy — several `:free` models 404 with
  "zdr-violation-by-account" (observed 2026-10-01). Paid models route fine.
  Adjustable at https://openrouter.ai/settings/privacy (Mike's call).
- **OpenCodeGo door** requires generated model-pinned subagent definitions
  inside OpenCode; designed in SKILL.md Step 3 (Door B), untested.

## What wave 2 taught us

Wave 2 (2026-10-05) was the confirmatory eval: 300 Track-1 runs over 30
difficulty-calibrated tasks, 5 arms, decision rules pre-registered before any
model call, ~$2.21 all-in. It tested this document's thesis directly and split
it. Full numbers live in [RESULTS.md](RESULTS.md); what follows is only what
the design takes from them.

**The question-answer scaffold is confirmed.** Forcing the unknowns into the
open and answering them before the build lifts the executor's first-attempt
pass rate from 44.8% to 58.0% (B − A = +13.2 pp, p = 0.0002) — the strongest
significance this project has produced. The same run killed the cheapest
objection from the other side: compute-matched best-of-3 with selection (arm
F) scored exactly the baseline (F − A = 0.0 pp, p = 1.0) at 4× the executor
calls. The gain is not purchasable with plain compute; it comes from asking.

**The council premium is refuted.** The confirmatory primary — council
questions (B) vs the executor's own questions, matched and answered the same
way (C) — came in at B − C = −0.5 pp (95% CI [−5.7, +4.5], p = 0.90, n = 30).
The pre-registered rule ("council earns its keep" = ≥ +5 pp AND p < 0.05 AND
CI excluding 0) fails on all three conditions, and the CI rules out any
council advantage larger than +4.5 pp. A sham dossier — a real council run on
the *wrong* task — matched the genuine article (B − E = −0.5 pp, p = 0.94):
the diversity premise did not pay on this task class. Published as the null it
is, per the pre-registration.

**The design lesson:** the lift comes from the *question-asking discipline* —
build-changing questions surfaced before the build, answered before coding —
not from who generates the questions. Council and self questions overlap just
23.9% (they really do ask different things) yet score identically: different
questions, same value. So the cheap version is the product. v0.2.0 makes
`clarify` — the arm-C shape, $0, the frontier agent interrogating its own
brief — the **default**, and demotes the council to explicit opt-in ("convene
the council").

**Why the council is kept at all:** it remains the measured arm-B path
(+13.2 pp over baseline); the machinery is built, validated (60/60 councils
returned), and already measured; the untested task classes — long research and
decision briefs, the territory Track 2 was meant to cover — are exactly where
model diversity is still a live hypothesis; and some users simply want a
plurality of voices. Premortem, debate, and critique keep working as today,
opt-in only.

**The Track-2 failure is an engineering lesson, not a results problem.** The
LLM-judged decision track mechanically failed — 50 of 75 judge slots (67%)
returned unparseable output — from three compounding causes:

1. every judge wrote its response to the same file, so each judge overwrote
   the previous one's output and the failures could not be inspected post-hoc;
2. the judges' 512-token output cap truncated the 6-dimension rubric (0–2 per
   dimension, plus totals) mid-JSON;
3. the prompt never demanded strict JSON-only output, so two of the three
   judge models (claude-haiku-4.5, gpt-5-mini) free-formed; only the gemini
   judge scored reliably.

The v0.2.0 fix bundles per-judge response files, a strict JSON-only
instruction, and maxTokens above the truncating 512 — code-only, no re-run.
Track 2 carries no evidentiary weight this wave, and any re-run is gated on
owner approval plus a fresh dated prereg addendum before data, same as every
measured claim here.

## Roadmap rationale

**Web app (phase 2, deferred on purpose):** the plus-button model manager is
a product-quality UX, but the MVP question is whether councils earn their
keep on real tasks. A config file answers that in days; the web app answers
it after weeks. Build it after 2–3 weeks of real use, once the config
surface shows which knobs people actually touch.

**God-king experiment:** feed the merged brief to a mid-tier model as the
primary executor and benchmark it against the same model without the brief.
Realistic expectation (from cascade research): mid-tier + great context ≈
frontier on *bounded* tasks (calculators, form apps), not on novel
debugging or large refactors. If it holds, "frontier-adjacent quality at
flat-rate cost" becomes the headline claim.
