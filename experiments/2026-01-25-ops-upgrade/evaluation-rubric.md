# Evaluation Rubric

## Scoring Dimensions

### 1. Correctness (30%)

| Score | Description |
|-------|-------------|
| 5 | All API calls correct. Code compiles, tests pass, no regressions introduced. |
| 4 | Minor issues that wouldn't cause runtime failures (e.g. slightly non-ideal parameter choice). |
| 3 | One or two incorrect API usages that would cause test failures or runtime issues, but are easy to fix. |
| 2 | Several incorrect usages or a fundamental misunderstanding of the new API. |
| 1 | Completely wrong approach; the "upgrade" introduces bugs or breaks the charm. |

### 2. Completeness (25%)

| Score | Description |
|-------|-------------|
| 5 | Every instance of the old pattern found and updated. All related files (tests, config, dependencies) updated. |
| 4 | Most instances updated; one or two minor locations missed (e.g. a test helper, a less-visited code path). |
| 3 | Core instances updated but several secondary locations missed. |
| 2 | Only the most obvious instances updated; significant gaps. |
| 1 | Barely started; most of the old pattern remains. |

### 3. Code Quality (15%)

| Score | Description |
|-------|-------------|
| 5 | Idiomatic use of the new feature. Code reads as if a knowledgeable charmer wrote it. |
| 4 | Correct and clean, but misses some idiomatic touches (e.g. doesn't use a convenience method). |
| 3 | Functional but clunky; mixes old and new patterns or uses the new API in an unusual way. |
| 2 | Works but clearly doesn't understand the intent behind the new feature. |
| 1 | Cargo-culted or copy-pasted without understanding. |

### 4. Minimal Diff (15%)

| Score | Description |
|-------|-------------|
| 5 | Only the necessary changes made. No reformatting, no unrelated refactoring, no unnecessary imports. |
| 4 | One or two minor unnecessary changes (e.g. reordering imports, trivial whitespace). |
| 3 | Several unnecessary changes that clutter the diff but don't break anything. |
| 2 | Significant unrelated changes mixed in with the upgrade. |
| 1 | Extensive rewrite far beyond what the upgrade requires. |

### 5. Human Review Needed (15%)

| Score | Description |
|-------|-------------|
| 5 | Merge-ready. A reviewer would approve with no changes. |
| 4 | One or two small fixes needed (typo, minor style issue). |
| 3 | Needs moderate attention -- a few fixes and some manual verification. |
| 2 | Substantial rework needed; useful as a starting point but not close to mergeable. |
| 1 | Easier to redo from scratch than to fix. |

## Composite Score

Weighted sum: (Correctness × 0.30) + (Completeness × 0.25) + (Quality × 0.15) + (Minimal Diff × 0.15) + (Review Needed × 0.15) = score out of 5.

Multiply by 5 for the 25-point scale used in the results tables.

## Additional Observations

For each run, also record qualitative notes on:

* **Feature detection** (for the single-skill/generic-prompt approaches): Did the agent correctly identify which changes apply?
* **False positives**: Did the agent try to apply changes that aren't relevant?
* **Exemplar usage**: When given an exemplar reference, did the agent visibly consult it? Did it help or lead to copy-paste issues?
* **Explanation quality**: Did the agent explain *why* it was making each change?
* **Dependency handling**: Did the agent update `pyproject.toml` / `requirements.txt` / `tox.ini` as needed?
* **Test updates**: Were tests updated to match the new code patterns?
* **CI**: Does linting (format, lint, type check) pass? Do the unit tests pass, assuming they do on main?
