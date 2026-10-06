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

**Postscript, day two (2026-10-06): the market ran my control arm.**

The day after publishing this, while closing out a repo audit, I reached for
a grilling skill and noticed something I had not thought about when I set
the $8 cap: the most popular questioning skill in the AI ecosystem right
now — Matt Pocock's "grilling" — is my experiment's winning arm, built as
craft. One model stops. It interviews you relentlessly. Every question
carries a recommended answer. Nothing gets built until the two of you agree
on what is being built. That is arm C: the scaffold that lifted
first-attempt pass rate 13.2 points, while my council of six models added
nothing over it and three-times-the-compute best-of-3 gained exactly zero.

Be clear about what this is and isn't. I did not design the experiment
around grilling — I found the connection the day after publishing, and
nothing in my data measures his skill. What it is, is demand-side evidence
for the pattern my data isolated: the industry's favorite prompting tool
works because questions-before-building is the active ingredient — the
conclusion I had to spend $2.21 and 325 runs to earn, the market arrived at
by shipping and watching what people adopt.

Credit where due, too: as questioning craft, grilling is ahead of my
clarify mode. It asks in dependency order — foundations first, only
questions answerable now — across multiple rounds, until the decision tree
has no unsettled frontier. My clarify is a single pass of five questions.
That structure is copyable for free, and it is the obvious chapter-two
experiment: single-pass clarify against rounds-based clarify, one model,
pre-registered, pennies. It is written down as a candidate, not committed
to. I know what happens to my untested favorite ideas now: sometimes
they're placebos with good formatting. The difference is that checking
costs almost nothing — and the checking is the product.
