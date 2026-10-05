# Track-1 wave-2 calibration (suite construction record — NOT experiment data)

Generated 2026-10-05 — one executor call (google/gemini-2.5-flash, temperature 0.0) per task on the PUBLIC BRIEF ALONE, arm-A-identical scaffold, graded by the task's frozen checker. Tasks outside the 30-70% band are rewritten or discarded BEFORE the wave-2 freeze (docs/EVAL-DESIGN.md, Difficulty calibration + wave-2 addendum).

## Final suite state (all 24 new tasks in the 30-70% band)

| task file | task_id | archetype | final baseline % | round-1 % | action history |
|---|---|---|---|---|---|
| task-10-electricity-tier-bill.json | T1-electricity-tier-bill | domain-rule-calculator | 30% | 0% | Rev2 brief (error path + rate card public) |
| task-11-taxi-fare.json | T1-taxi-fare | domain-rule-calculator | 30% | 0% | Rev2 brief (error path + rate card public) |
| task-12-hotel-stay-total.json | T1-hotel-stay-total | domain-rule-calculator | 70% | 0% | Rev2+Rev3 brief/tests (rate card, season calendar, clean cases); Rev4: integer-month format made explicit + 12.50 guest fee published (round-3 run misread month as string, scored 1/10) |
| task-13-baggage-fees.json | T1-baggage-fees | domain-rule-calculator | 40% | 10% | Rev2 brief (error path + rate card public) |
| task-14-license-plate.json | T1-license-plate | input-validation | 60% | 20% | Rev2: error path public, tests de-coupled |
| task-15-coupon-code.json | T1-coupon-code | input-validation | 30% | 10% | Rev2: ValueError contract public, tests de-coupled |
| task-16-postal-code.json | T1-postal-code | input-validation | 30% | 30% | kept as authored |
| task-17-hex-color.json | T1-hex-color | input-validation | 50% | 50% | kept as authored |
| task-18-seat-map.json | T1-seat-map | input-validation | 30% | 30% | kept as authored |
| task-19-subscription-lifecycle.json | T1-subscription-lifecycle | state-machine | 40% | 40% | kept as authored |
| task-20-vending-session.json | T1-vending-session | state-machine | 50% | 50% | kept as authored |
| task-21-turnstile-gate.json | T1-turnstile-gate | state-machine | 70% | 70% | kept as authored |
| task-22-clinic-appointment.json | T1-clinic-appointment | state-machine | 50% | 50% | kept as authored |
| task-23-kyc-verification.json | T1-kyc-verification | state-machine | 60% | 60% | kept as authored |
| task-24-warranty-expiry.json | T1-warranty-expiry | date-aggregation | 60% | 60% | kept as authored |
| task-25-pay-period-split.json | T1-pay-period-split | date-aggregation | 70% | 70% | kept as authored |
| task-26-invoice-aging.json | T1-invoice-aging | date-aggregation | 70% | 80% | Rev2+completion: R8 error-path rule completed (prior agent died mid-edit), tests merged |
| task-27-recurrence-clip.json | T1-recurrence-clip | date-aggregation | 70% | 90% | Rev2: half-open window convention pinned, adversarial enumeration removed from brief |
| task-28-retention-expiry.json | T1-retention-expiry | date-aggregation | 60% | 0% | Rev2 brief (error/return paths public); confirmed adequate, verified |
| task-29-cart-promotions.json | T1-cart-promotions | mixed | 60% | 10% | repair (dead agent left a stale expected value, ref 9/10) + Rev2 de-coupling + Rev3/4: promo face values + gate published, clean cases added |
| task-30-refund-eligibility.json | T1-refund-eligibility | mixed | 30% | 30% | Rev2 test de-coupling only |
| task-31-badge-eligibility.json | T1-badge-eligibility | mixed | 40% | 40% | kept as authored |
| task-32-loan-payoff-quote.json | T1-loan-payoff-quote | mixed | 60% | 10% | Rev2 brief (return shape, rate units, error path public), tests de-coupled |
| task-37-dryclean-order.json | T1-dryclean-order | domain-rule-calculator | 40% | (new) | REPLACEMENT — see below |

## Discarded task

**task-09-courier-rates** (round-1 0%, round-2 0%, round-3 0%, round-4 80% — DISCARDED).
Four revision rounds could not land it in band: with the 5 kg tier break hidden, every
multi-kilogram total cascades to failure (a plausible implementer guessed a 1 kg break and
scored 0/10 while producing well-engineered code); with the break published, the task is
bimodal and overshot to 80%. Discarded per the pre-registered rule ("rewritten or
discarded") and replaced by task-37-dryclean-order (same archetype), authored with the
calibration lessons baked in (full public rate card, explicit input formats, clean
isolation cases, no composed-total cascade) and landing in band at 40% on its first run.
Round transcripts for every calibration run are preserved under
eval/results/raw/calibration-wave2/ (round-1 copies suffixed -round1).

## Summary

24 new tasks calibrated across up to 4 rounds; 23 kept in band after revision, 1 discarded
and replaced (also in band). Final suite: 30 Track-1 tasks (6 pilot re-run + 24 new), every
new task inside the 30-70% baseline band. Total calibration spend: ~$0.09. Rewrite
outcomes are documented above per round; raw transcripts retained per run.
