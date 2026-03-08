# Evaluation Rubric

Each Copilot migration run is scored on these dimensions, each rated 1-5.

## Dimensions

### 1. Correctness (weight: 30%)

Does the migrated code use the `jubilant`/`pytest-jubilant` API correctly?

| Score | Description |
|-------|-------------|
| 5 | All API calls correct, proper argument names, correct types |
| 4 | Minor issues (such as slightly wrong argument order) but would likely work |
| 3 | Some incorrect API usage that would cause test failures |
| 2 | Significant API misuse, invented methods or arguments |
| 1 | Fundamentally wrong - uses old API, hallucinates `jubilant` API |

Note that I did not run all the integration tests in all evaluations, as doing so is not as simple as one would hope for many charms. Ideally, that would actually be part of the scoring here ("`charmcraft test` succeeds" or similar, maybe 25% weight).

### 2. Completeness (weight: 25%)

Were all files and patterns migrated?

| Score | Description |
|-------|-------------|
| 5 | All test files, conftest, helpers, and dependencies fully migrated |
| 4 | One or two minor items missed (e.g. a helper function, a dependency) |
| 3 | Most files migrated but some significant gaps |
| 2 | Only partially migrated - mix of old and new patterns |
| 1 | Only superficial changes, most code still uses old framework |

### 3. Code Quality (weight: 15%)

Is the migrated code clean, idiomatic, and well-structured?

(Obviously a bit subjective, but, hey, it's my experiment, and I would hope that Charm Tech would recognise idiomatic Jubilant.)

| Score | Description |
|-------|-------------|
| 5 | Clean, idiomatic Jubilant usage; good fixture design; minimal unnecessary changes |
| 4 | Good quality with minor style issues |
| 3 | Functional but messy - unnecessary variables, poor naming, etc. |
| 2 | Significant quality issues - copy-paste artifacts, dead code |
| 1 | Poor quality - hard to read, lots of unnecessary changes |

### 4. Minimal Diff (weight: 15%)

Did the model avoid unnecessary changes outside the migration scope?

| Score | Description |
|-------|-------------|
| 5 | Only migration-related changes; test logic preserved exactly |
| 4 | Very minor extraneous changes (whitespace, import ordering) |
| 3 | Some unnecessary refactoring or reformatting |
| 2 | Significant unnecessary changes mixed with migration |
| 1 | Wholesale rewrite rather than targeted migration |

Note that the extra changes might be good, but for this tech debt task we want a really tight PR.

### 5. Human Review Needed (weight: 15%)

How much human intervention would be needed before merging?

| Score | Description |
|-------|-------------|
| 5 | Could merge as-is after a quick scan |
| 4 | Minor tweaks needed (typos, small fixes) |
| 3 | Moderate review and fixes needed |
| 2 | Substantial rework required |
| 1 | Easier to redo from scratch than fix |

I am assuming that the person who runs the AI migration would do suitable due-diligence. This is not a recommendation to skimp on review from humans!

## Composite Score

Weighted average: `(correctness * 0.30) + (completeness * 0.25) + (quality * 0.15) + (minimal_diff * 0.15) + (review * 0.15)`

## Additional Observations (qualitative)

For each run, also note:
- Time taken (wall clock)
- Number of copilot turns/interactions
- Whether copilot asked clarifying questions
- Any hallucinated APIs or patterns
- Whether it correctly handled edge cases (abort_on_fail, multi-model, complex fixtures)
- Comparison to gold standard diff
