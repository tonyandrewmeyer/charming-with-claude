# Methodology

## Experimental Design

This experiment uses a controlled comparison to evaluate how different levels of AI assistance affect the quality of integration test migrations from `pytest-operator` to `jubilant`.

### Independent Variables

1. **Assistance level** (6 levels) — the amount and type of context provided to Copilot
2. **Model** (2 models) — Claude Sonnet 4.6 and Claude Opus 4.6
3. **Charm complexity** — varying test suite sizes and patterns

### Dependent Variables

Measured using the [evaluation rubric](evaluation-rubric.md):
- Correctness of Jubilant API usage
- Completeness of migration
- Code quality
- Minimality of diff (avoiding unnecessary changes)
- Amount of human review needed

### Controls

- All runs use the same version of GitHub Copilot CLI (v0.0.411)
- All runs use the same charm repository state (pinned to specific commits)
- Each run starts from a clean clone — no prior session state
- Light human supervision is provided consistently: answering direct questions but not volunteering corrections

## Assistance Levels

### Level 1: Bare Prompt

A single instruction with no additional context. Tests the model's baseline knowledge of Jubilant.

```
Migrate this charm's integration tests from pytest-operator (python-libjuju) to
jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.
```

### Level 2: Prompt + Documentation Pointer

Same instruction plus a pointer to the official Jubilant documentation.

```
Migrate this charm's integration tests from pytest-operator (python-libjuju) to
jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.

Before starting, read the jubilant documentation, particularly the migration guide,
at https://documentation.ubuntu.com/jubilant. The reference documentation covers
the full API.
```

### Level 3: Prompt + Source Code Inspection

Instructs the model to install `jubilant` and read the source code directly, rather than relying on documentation or training data.

```
Migrate this charm's integration tests from pytest-operator (python-libjuju) to
jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.

Before starting, install jubilant and pytest-jubilant from PyPI (pip install jubilant
pytest-jubilant) and read the source code to understand the API. The key modules are
the Juju class, wait helpers (all_active, all_blocked, any_error), and the
pytest-jubilant fixtures (pack, get_resources, juju fixture, temp_model_factory).
```

### Level 4: Prompt + Example Charm Reference

Points the model to an already-migrated charm as a working reference, testing the "learning by example" approach.

```
Migrate this charm's integration tests from pytest-operator (python-libjuju) to
jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.

For a working example of what jubilant integration tests look like, clone
https://github.com/canonical/wordpress-k8s-operator and study its tests/integration/
directory. Pay attention to how conftest.py sets up the juju fixture, how tests use
juju.deploy(), juju.wait(), juju.integrate(), and how pytest-jubilant's pack() and
get_resources() are used.
```

### Level 5: Detailed Recipe

Uses the full [charmgpt-recipes migrate-jubilant.md](https://github.com/canonical/charmgpt-recipes) recipe as the instruction. This provides:

- Step-by-step migration process
- API mapping table (OpsTest → Juju)
- Code examples for each pattern
- Quality check validation steps
- State management for tracking progress

(Note that the recipe is in a private repo. If you can't see it, assume a fairly detailed instruction with the above aspects.)

### Level 6: Recipe + Example

Combines the detailed recipe (Level 5) with the example charm reference (Level 4). This represents the maximum level of assistance.

## Charm Selection

### Full Matrix Charm

**saml-integrator-operator** was selected for the full 6-level x 2-model comparison because:
- **Simple complexity** (2 tests, 1 conftest, no helpers) — isolates the effect of assistance level and model choice without confounding complexity
- **Clean pytest-operator patterns** — standard async/await, OpsTest, abort_on_fail
- **Identity team** — represents a common charm domain

### Confirmation Charm

**s3-integrator** was used to verify findings on a more complex charm:
- **Medium complexity** (5 tests, helpers.py with 10 functions, custom action wrappers)
- **Data/storage team** — different domain
- **Poetry-based** dependency management (vs UV for saml-integrator)

### Broader Sample Charms

Five additional charms were selected for increased diversity and confidence:

| Charm | Team | Why Selected |
|-------|------|-------------|
| nginx-ingress-integrator | Networking | Medium complexity, Kubernetes API calls in fixtures |
| content-cache-k8s | Web Infrastructure | Simple-medium, any-charm helper pattern |
| indico | Web App / PaaS | Complex multi-charm deployment (PostgreSQL, Redis, Nginx) |
| loki-k8s | Observability | Large (18 files), cross-model testing, custom helpers |
| hockeypuck-k8s | Security | Multi-model deployment, dependency chains, GPG operations |

All charms were confirmed to still use pytest-operator at the time of testing.

## Execution Protocol

### Environment

- **Machine**: Ubuntu 22.04 sandbox
- **Copilot CLI**: v0.0.411
- **Copilot flags**: `--model <model> --allow-all` (full autonomous mode for the matrix runs; light supervision for broader sample)

### Per-Run Protocol

1. Clone the charm repository to a fresh directory
2. Record the commit hash for reproducibility
3. Run `copilot` with the appropriate prompt and model
4. Save the session transcript (`--share`)
5. Save a diff of all changes
6. Score using the evaluation rubric
7. Record timing, observations, and qualitative notes

### Adaptation During the Experiment

The original plan was 12 runs each on 2 charms (24 total for the matrix). After completing all 12 `saml-integrator` runs, the clear patterns (Sonnet > Opus, L3 best) meant that running the full matrix on `s3-integrator` would add limited value. I instead ran 5 targeted `s3-integrator` experiments (L1, L3, L5, L6 with Sonnet; L1 with Opus) to confirm the findings, then devoted the remaining time (of my self-inflicted budget, and, honestly, patience!) to the 5-charm broader sample.

## Limitations

- **No integration test execution**: I didn't run the actual integration tests in most cases (I've previously found this very arduous, error-prone, and time consuming, as well as demanding on resources -- using CI as set up by the charms was an option but seemed excessive). Evaluation is based on code review only. The migrations may contain subtle runtime errors not caught by static analysis.
- **Autonomous mode for matrix runs**: The full matrix used `--allow-all` (non-interactive), while the broader sample used light supervision. This means the matrix results may understate quality slightly for approaches that benefit from human guidance (particularly the recipe levels).
- **Single operator per run**: Each Copilot session starts fresh, so there is no learning across runs.
- **Sample size**: With 22 total runs, statistical significance is limited. This is an exploratory study (an experiment!), not a formal benchmark :). The consistent patterns across multiple charms and levels do increase confidence in the findings.
- **Evaluator bias**: The same person who designed the experiment also scored the results. Where possible, scoring used objective criteria (correct API calls, presence of hallucinated parameters) to reduce subjectivity.
