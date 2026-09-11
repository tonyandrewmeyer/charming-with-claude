You are writing the cross-charm synthesis for a running charm review programme.

`/home/ubuntu/charm-review/reviews/` holds one review per charm, written by an agent
that deployed each charm, exercised it, and read its code, tests and docs. Read all of
them (they are the only source you may use — do not go and re-review the charms) and
write `/home/ubuntu/charm-review/THEMES.md`.

What the reader wants out of this file: to know what is systematically wrong across the
charm ecosystem, what to build tooling for, and what good work to copy. Structure it:

```markdown
# Cross-charm themes

_N reviews as of <date>._

## Recurring defects
For each pattern seen in two or more charms: what it is, how many charms, which ones
(with the `file:line` from their reviews), why it keeps happening, and what would stop it.
Most frequent and most severe first.

## Linter rules worth building
The concrete ruleset this programme has earned so far. For each: the rule, what it fires
on, how many charms in the corpus it would have caught, false-positive risk, and whether
it is mechanically checkable or needs judgement. Rank by (charms caught x severity).

## Patterns worth copying
Good work found in specific charms that others should adopt, with the charm and file
reference, and a note on what makes it better than the common approach.

## Divergence in common practice
Places where charms disagree with each other about how to do the same thing — status
handling, config validation, library layout, testing style, upgrade paths. Say which
approach the evidence favours, or say that the evidence does not settle it.

## Deployability
What fraction deployed cleanly, what the common failure modes were, what that says about
the state of the ecosystem's docs and defaults.

## What the reviews are not covering
Gaps in this programme itself — kinds of charm, substrate, or failure mode that the
corpus so far has not touched.
```

Rules: every claim traces to at least one review, named. Count things — "6 of 19 charms"
beats "many charms". Do not repeat a per-charm review; this file is only for what emerges
across them. If only a handful of reviews exist, say so and keep it short rather than
inflating thin evidence.
