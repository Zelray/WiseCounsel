# Decision memo: why this product looks like this

*Mike — repo owner — 2026-10-05*

**The bet.** I bet that a council of 3–6 cheap AI models, attacking your
prompt before a frontier model starts work, would make the frontier model's
first try better. It made sense: different training data means different
blind spots, and attack-don't-answer templates aim that diversity right at
the gaps in a brief. The cost was about three-tenths of a cent per council.
If it worked, it was a cheap quality multiplier on every big task I run.

**What I did about the bet.** I don't trust "it worked on my machine"
stories — mine or anyone else's. So before running anything, I committed
the whole experiment design to this repo: the arms, the grading, the
statistics, the decision rules, and a hard $8 budget. The task graders were
written from hidden specs and frozen before any model call saw them. And I
committed in advance, in public, to publish whatever the data said —
including if it said my favorite idea was worthless.

**What the data said.** Two things, pointing in opposite directions. The
question-answer scaffold — the model stops, asks you up to five questions
that would actually change what gets built, and works from your answers —
lifted first-attempt pass rate by 13.2 points over 300 runs. That is real:
p = 0.0002, and it beat spending three times the compute on "try three
times and keep the best," which gained exactly zero. But the council added
nothing over the model asking its own questions: −0.5 points, p = 0.90.
The kicker: a sham dossier, generated from a completely different task,
performed identically to the real council. The expensive part of my product
was a placebo with good formatting.

**The decision.** Kill the default, keep the evidence. v0.2.0 ships the
scaffold as the default and the council as opt-in. That is not a
consolation prize — the scaffold is the part that worked, it costs
nothing, and the whole experiment that separated the two cost $2.21.

**What I'd do differently.** Two things. First, I'd have tested the
judge-scored decision-brief track as carefully as the coding track before
launch — a logging bug let three judges overwrite each other's output, we
caught it in the autopsy, fixed it, and left that track honestly marked
"unvalidated" instead of quietly re-running it and hoping. Second, I'd
have mapped the boundary conditions on day one: my null covers frontier
models on short, self-contained coding tasks, and nothing else. The
question is still open for weaker executors, knowledge-heavy work, and
long research briefs — that's written down in the design doc, not buried
in a drawer.

**The part I won't pretend away.** AI agents wrote every line of code in
this repo. I told them what to build, set the approval gates, capped and
audited every dollar, made the kill call, and wrote this memo. If you are
hiring for judgment under uncertainty, that division of labor is the
résumé — not a confession.
