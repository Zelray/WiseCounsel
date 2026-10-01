# DESIGN.md — why WiseCounsil is shaped the way it is

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
