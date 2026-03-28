# Experiment: Do LLM-Friendly Docs Help Agents Write Charms?

**Date:** 2026-03-26 to 2026-03-28
**Status:** Complete (human review in progress)
**Total cost:** ~$99 (sessions) + ~$30 (judge scoring)

## Summary

We tested whether serving documentation in LLM-optimised formats — `llms.txt`, per-page markdown, and HTTP content negotiation — helps AI coding agents answer questions about the Juju charm ecosystem more accurately.

**Result: Yes, meaningfully.** Providing `llms.txt` improved scores from 79.8% (bare agent) to 86.9% — a 7.1 percentage point gain. Content negotiation alone (serving markdown via the HTTP `Accept` header, transparently) improved scores to 83.1%. Curated instructions (CLAUDE.md + skills) improved scores to 82.0% — less than either doc-format intervention.

| Condition | Score | Cost/session | Description |
|---|---|---|---|
| **C** (llms.txt) | **86.9%** | $0.24 | llms.txt index + markdown pages + hint |
| **E** (content negotiation) | 83.1% | $0.27 | Markdown via Accept header, no hint |
| **D** (instructions + llms.txt) | 83.0% | $0.20 | CLAUDE.md + skills + llms.txt |
| **B** (instructions only) | 82.0% | $0.15 | CLAUDE.md + skills |
| **A** (bare agent) | 79.8% | $0.13 | Control — training data only |

## Hypothesis

Providing LLM-optimised documentation formats (`llms.txt`, `llms-full.txt`, per-page markdown via `sphinx-llm`) for the core Juju/charm ecosystem libraries makes agents measurably better at writing charms, compared to relying on standard HTML documentation alone.

**Confirmed**, with nuances: the format helps, the discovery index helps more, and curated instructions help least (though they reduce cost).

## Background

The [llms.txt specification](https://llmstxt.org/) proposes a standardised way to serve documentation in a format optimised for LLM consumption. The `sphinx-llm` extension generates these files from existing Sphinx documentation: an `llms.txt` index, an `llms-full.txt` concatenation, and per-page `.html.md` files alongside the HTML.

None of the target repos currently serve `llms.txt`. All use Sphinx with `canonical_sphinx`, hosted on `documentation.ubuntu.com`.

A separate approach — HTTP content negotiation via the `Accept: text/markdown` header — allows servers to serve markdown to agents transparently. Claude Code already sends `Accept: text/markdown` as its preferred format.

### Key Question

Is the value of better docs *at inference time* significant, or do good upfront instructions (skills, CLAUDE.md, curated prompts) already capture the necessary knowledge more efficiently?

**Answer:** Inference-time docs are more impactful than upfront instructions, but the two serve different purposes. Instructions reduce cost and guide navigation; docs provide accurate, current detail.

## Experimental Setup

### Target Repositories

Six repositories covering the Juju charm development ecosystem:

| Repository | Docs URL | Source | Pages | llms-full.txt |
|---|---|---|---|---|
| canonical/operator (ops) | /ops/ | MyST MD | 62 | 21,815 lines |
| canonical/pebble | /pebble/ | MyST MD | 33 | 4,491 lines |
| canonical/jubilant | /jubilant/ | MyST MD | 10 | 2,135 lines |
| canonical/charmlibs | /charmlibs/ | MyST MD | 174 | 12,282 lines |
| canonical/charmcraft | /charmcraft/ | RST | 134 | 20,902 lines |
| juju/juju | /juju/ | MyST MD | 393 | 38,886 lines |
| **Total** | | | **806** | **100,511 lines** |

Docs were built from tonyandrewmeyer forks using `sphinx-llm` v0.3.0. Commit SHAs are recorded in `build-manifest.json`. The charmlibs build required a two-pass process (per-package autodoc generation via `just`, then combined build with sphinx-llm).

### Conditions

Five experimental conditions in a design that isolates three factors: instructions, llms.txt discovery index, and markdown format.

| Condition | Instructions | llms.txt index | Markdown format | /etc/hosts | Prompt |
|---|---|---|---|---|---|
| **A** (control) | No | No | No | Real internet | "You are writing a Juju charm." |
| **B** (instructions) | Yes | No | No | Real internet | CLAUDE.md + skills |
| **C** (llms.txt) | No | Yes | Yes | Local | "...supports the llms.txt standard." |
| **D** (combined) | Yes | Yes | Yes | Local | CLAUDE.md + skills + llms.txt hint |
| **E** (content negotiation) | No | No | Yes | Local | "...docs at documentation.ubuntu.com." |

**Condition E** was added mid-experiment after discovering that Claude Code sends `Accept: text/markdown, text/html, */*` in its WebFetch requests. nginx was configured to serve `.html.md` files when this header is present, giving the agent markdown transparently — no llms.txt discovery needed.

### Infrastructure

- **Local doc serving:** nginx with HTTPS (mkcert-generated certificate for `documentation.ubuntu.com`)
- **DNS override:** `/etc/hosts` entry redirecting `documentation.ubuntu.com` to `127.0.0.1` for conditions C/D/E; removed for conditions A/B
- **URL rewrites:** nginx rewrites strip version prefixes (`/ops/latest/`, `/charmcraft/stable/`, etc.) and hallucinated `/en/` prefixes to match our flat doc structure
- **Content negotiation:** nginx `map` directive serves `.html.md` files when `Accept: text/markdown` is in the request header
- **WebFetch validation:** Confirmed that Claude Code's WebFetch (Bun-based) resolves DNS via system `getaddrinfo` (respects `/etc/hosts`) and trusts system CA store (mkcert certs work without `NODE_EXTRA_CA_CERTS`)

### Evaluation

**23 items:** 20 information-retrieval questions across 5 categories (ops API, Pebble, jubilant, charmlibs, charmcraft) plus 3 micro-charm synthesis tasks.

**Gold-standard answers** were drafted from the built documentation and reviewed by a domain expert. Multiple corrections were made during the review process (see `gold-standards.md`).

**Scoring:** Each response was scored by a Claude judge on 4 dimensions (0-2 scale each), with weighted aggregation into a percentage. The judge prompt was calibrated after an initial 18% human review revealed systematic over-penalisation of hallucinations — the judge treated extra correct detail not in the gold standard as fabrication. After recalibration, judge-human agreement improved from 69% to 75%.

**Human review:** 114 sessions (18% of scored) were reviewed using a custom Textual TUI tool, with score overrides and notes. Human scores take precedence in the analysis.

### Scale

- **620 total sessions:** 551 for conditions A–D (23 questions × 4 conditions × 3 runs × 2 models) + 69 for condition E (23 questions × 3 runs × Sonnet only)
- **Models:** Claude Sonnet 4.6 and Claude Opus 4.6 (checkpoint after run 1 showed only 2.1pp difference — not significant)
- **618 scored**, 114 human-reviewed
- Sessions run via `claude -p` (non-interactive mode) with `--dangerously-skip-permissions`, `--no-session-persistence`, and `--output-format json`

## Results

### Overall Scores

| Condition | Mean Score (%) | Std Dev | n | Mean Tokens | Mean Cost ($) |
|---|---|---|---|---|---|
| A (control) | 79.8 | 18.3 | 138 | 1,689 | 0.13 |
| B (instructions) | 82.0 | 18.0 | 138 | 833 | 0.15 |
| C (llms.txt) | **86.9** | 15.3 | 136 | 2,229 | 0.24 |
| D (combined) | 83.0 | 19.8 | 137 | 1,029 | 0.20 |
| E (content neg.) | 83.1 | 15.4 | 69 | 2,109 | 0.27 |

### Scores by Category

| Category | A | B | C | D | E |
|---|---|---|---|---|---|
| ops API | 90.0% | 87.8% | 87.2% | 90.9% | 88.1% |
| Pebble | 72.9% | 89.8% | 90.3% | 87.3% | 81.5% |
| jubilant | 83.6% | 83.0% | 92.0% | 82.1% | 87.0% |
| charmlibs | 79.4% | 81.9% | 78.0% | 82.1% | 80.1% |
| charmcraft | 85.4% | 83.6% | 93.8% | 88.4% | 84.7% |
| synthesis | 60.8% | 59.2% | 78.4% | 58.6% | 74.4% |

### Per-Question Scores

| Question | A | B | C | D | E | Topic |
|---|---|---|---|---|---|---|
| Q1 | 86% | 89% | **100%** | 94% | **100%** | Container.add_layer |
| Q2 | **98%** | 93% | 97% | 93% | 91% | Relation data access |
| Q3 | 94% | 94% | 74% | **95%** | 72% | Event list |
| Q4 | 89% | 89% | 82% | 89% | 78% | ActionEvent.fail() |
| Q5 | 82% | 74% | 83% | 83% | **100%** | CollectStatusEvent |
| Q6 | 89% | 94% | **100%** | 97% | 83% | Pebble layer YAML |
| Q7 | 78% | **94%** | **94%** | **94%** | 83% | Pebble notices |
| Q8 | 69% | 76% | **86%** | 71% | 76% | Change/task model |
| Q9 | 57% | **94%** | 81% | 86% | 83% | Log forwarding |
| Q10 | 83% | 77% | **97%** | 85% | 94% | jubilant deploy |
| Q11 | 76% | 89% | 89% | 82% | 78% | jubilant relations |
| Q12 | **92%** | 83% | 90% | 79% | 89% | jubilant actions |
| Q13 | 92% | **94%** | 92% | 89% | **94%** | Ingress library |
| Q14 | 62% | 70% | 64% | **85%** | 63% | TLS certificates |
| Q15 | **94%** | 83% | **94%** | 79% | 87% | pathops library |
| Q16 | 69% | **80%** | 62% | 74% | 76% | Relation provider |
| Q17 | **97%** | 90% | **97%** | 89% | 78% | charmcraft.yaml |
| Q18 | 75% | 77% | **94%** | 79% | 89% | Relation endpoints |
| Q19 | 78% | 83% | **94%** | 89% | 78% | OCI resources |
| Q20 | 92% | 84% | 89% | **97%** | 94% | Multi-base builds |
| S1 | 63% | 55% | **71%** | 51% | 62% | Minimal charm |
| S2 | 51% | 78% | **88%** | 73% | **90%** | Pebble handler |
| S3 | 68% | 44% | **76%** | 53% | 72% | Relation provider |

### Model Comparison (Checkpoint)

After run 1 (181 scored sessions), Sonnet and Opus differed by only 2.1 percentage points (73.1% vs 75.2%), well within one standard deviation. The model dimension was retained for data completeness but is not a significant factor.

### Hallucination Rates

| Condition | Rate |
|---|---|
| A | 1.4% (2/138) |
| B | 0.0% (0/138) |
| C | 1.5% (2/136) |
| D | 1.5% (2/137) |
| E | 0.0% (0/69) |

After judge recalibration, hallucination rates are low and consistent across conditions. The initial v1 scoring showed inflated rates (4–7% for C/D) due to the judge flagging extra correct detail as fabrication.

## Analysis

### Finding 1: llms.txt Provides the Largest Single Improvement

Condition C (llms.txt + hint) outperforms every other condition at 86.9%. The gain over the bare agent (A) is 7.1 percentage points. The gain over curated instructions (B) is 4.9pp.

The biggest wins are in areas where training data is weakest:
- **Pebble:** C=90.3% vs A=72.9% (+17.4pp) — Pebble is a newer, less-trained-on project
- **charmcraft:** C=93.8% vs A=85.4% (+8.4pp) — packaging config changes frequently
- **Synthesis tasks:** C=78.4% vs A=60.8% (+17.6pp) — combining knowledge from multiple sources

For well-known topics (ops API: A=90.0%, C=87.2%), training data is already strong and docs add little.

### Finding 2: Content Negotiation Is Valuable and Zero-Effort

Condition E (markdown via `Accept` header, no llms.txt hint) scores 83.1% — a 3.3pp improvement over the bare agent. The agent doesn't know it's getting markdown; it just makes normal HTML requests and gets cleaner content back.

This decomposes the llms.txt benefit into two parts:
- **Format effect** (A→E): +3.3pp — getting markdown instead of HTML helps
- **Discovery effect** (E→C): +3.8pp — the llms.txt index for navigation helps further

Both matter, but discovery matters slightly more. The format benefit is "free" — it requires only server-side configuration with no agent awareness.

### Finding 3: Instructions Reduce Cost But Not Quality

Condition B (instructions only) scores 82.0% but at only $0.15/session — the cheapest effective option. The instructions help the agent avoid unnecessary web searches and produce more concise answers (833 mean tokens vs 1,689 for condition A).

However, instructions do not improve accuracy for topics they don't explicitly cover. The llms.txt approach is more general — it helps with whatever the docs cover.

### Finding 4: Combining Instructions + llms.txt Underperforms llms.txt Alone

Counterintuitively, condition D (83.0%) scores slightly below condition C (86.9%). The data reveals why: instructions make the agent more confident in its existing knowledge, reducing doc exploration.

| Metric | C | D |
|---|---|---|
| llms.txt fetches | 34% of requests | 15% of requests |
| HTML fetches | 43% | 71% |
| Mean bytes fetched | 249 KB | 126 KB |
| Mean unique pages | 5.3 | 4.3 |

Condition D fetches fewer docs, uses llms.txt less, and relies more on HTML pages it already knows about. When the instructions are incomplete, the agent doesn't cross-check against docs.

### Finding 5: The Agent Never Uses llms-full.txt

Across all conditions, `llms-full.txt` accounts for only 5% of condition C fetches and 0% of D/E fetches. The agent strongly prefers fetching `llms.txt` (the navigation index) and then following links to individual pages.

If a project can only do one thing, generating `llms.txt` as a navigation index with per-page `.html.md` files is far more valuable than a single `llms-full.txt` concatenation.

### Finding 6: The Agent Gravitates to Juju Docs First

In condition C, the agent's first fetch is `/juju/en/latest/llms.txt` **49 times out of 136 sessions** — even for questions about ops, pebble, or charmcraft. The agent strongly associates `documentation.ubuntu.com` with Juju (the most prominent project on the domain in training data).

In condition D, the first fetch is distributed across the correct repos because the CLAUDE.md names them explicitly: charmlibs (22×), charmcraft (19×), pebble (13×), jubilant (12×).

**Implication:** A generic "docs support llms.txt" hint is insufficient. The agent needs to know which sub-sites exist, or the top-level `llms.txt` should link to sibling projects.

### Finding 7: URL Pattern Hallucination

29% of all doc fetches (211/726) included `/en/` in the URL path — a URL pattern from other `documentation.ubuntu.com` sites that is not used by any of the charm ecosystem repos. The breakdown by condition is stark:
- **Condition C:** 50% of fetches use `/en/`, in 68% of sessions
- **Condition D:** only 4% of fetches use `/en/`, in 2 sessions
- **Condition E:** high `/en/` usage (no instructions to correct it)

We added nginx rewrite rules to handle this, but without them, half of condition C's doc fetches would have returned 404s. **URL stability and redirects are a prerequisite for llms.txt adoption.**

The agent also tried hallucinated URLs like `/juju/sdk/howto/manage-relations/llms.txt` and `/charm-tech/howto/manage-tls-certificates/llms.txt` — paths that have never existed. This is a training data artefact from similar URL patterns on other sites.

### Finding 8: Synthesis Tasks Expose a Methodology Artefact

For S3 (write a provider charm), conditions B and D score dramatically lower (44–53%) than A and C (68–76%). Investigation revealed the cause: **the instructed agent describes what code it would write rather than writing it**. It outputs charmcraft.yaml, explains the approach, and references file line numbers, but never actually provides the Python code.

This is an artefact of using non-interactive mode (`-p`). In interactive use, the agent would use Write/Edit tools to create files. The CLAUDE.md instructions trigger a tool-oriented workflow that doesn't work in print mode.

**The synthesis scores for B/D likely understate the real-world value of instructions.** The information-retrieval scores (Q1–Q20) are more representative of the actual quality difference.

## Methodology Notes

### Scoring Calibration

The initial judge prompt was too strict — it treated any detail not in the gold standard as a hallucination. An 18% human review revealed 67% disagreement, with 54 of 55 hallucination overrides being raises (judge too strict). The judge was recalibrated with explicit guidance that:
- Extra correct detail beyond the gold standard is not a hallucination
- The gold standard is a reference, not an exhaustive list
- Deprecated-but-working APIs score 1 for currency, not 0

After recalibration, judge-human agreement improved from 69% to 75%.

### Gold Standard Corrections

During human review, several gold standard answers were corrected:
- Q3: Added deprecated but real events (`add_metrics`, `meter_status_changed`)
- Q14: Added actual TLS certificate event names (`CertificateAvailableEvent`, `CertificateDeniedEvent`)
- Q15: Corrected `ensure_contents` signature and import style (module import preferred)
- Q17: Added legacy `bases` format (still widely used), corrected key list
- Q18: Noted that `scope: container` is only relevant for machine charms
- Q19: Added `upstream-source` as unofficial but widely used field

### Session Isolation

Each session ran in a fresh `/tmp` working directory with no Claude memory, no session persistence, and randomised question order (fixed seed per run). Conditions A/B used the real internet; conditions C/D/E used local nginx. The `/etc/hosts` override was toggled between conditions.

### Limitations

1. **Non-interactive mode**: The `-p` flag prevents tool use (Write, Edit, Bash), penalising conditions B/D whose instructions assume interactive use. Information-retrieval scores are more reliable than synthesis scores for these conditions.

2. **Single domain**: We only intercepted `documentation.ubuntu.com`. The agent could still reach docs via WebSearch (which returns real internet results) or old domains (`juju.is`, `ops.readthedocs.io`), partially bypassing our experimental controls.

3. **Judge accuracy**: Even after calibration, 25% disagreement with human reviewers remains. The analysis uses human scores where available (18% of sessions).

4. **Question selection**: The 23 questions may not be representative of all charm development tasks. They were designed to cover the doc ecosystem broadly, not to test specific difficulty levels.

## Recommendations

### For documentation teams adopting llms.txt

1. **Start with `llms.txt` + per-page `.html.md` files** — the index is more valuable than `llms-full.txt`.
2. **Add content negotiation** (`Accept: text/markdown`) — it's free and Claude Code already supports it.
3. **Ensure URL redirects work** — agents hallucinate old URL patterns. Broken URLs eliminate the benefit.
4. **Cross-link sibling projects** in `llms.txt` — agents don't know the doc domain's structure.
5. **Use `sphinx-llm`** (NVIDIA/jacobtomlinson) — it generates all three outputs and works with `canonical_sphinx`.

### For teams writing agent instructions (CLAUDE.md, skills)

1. **Instructions are cost-effective** ($0.15/session vs $0.24 for llms.txt) but less accurate.
2. **Don't over-specify** — excessive instructions can reduce doc exploration and lower accuracy.
3. **Name specific doc URLs** in instructions — it prevents the agent from guessing wrong paths.
4. **For non-interactive use**, add "output code directly, don't describe it" guidance.

### For the llms.txt specification

1. **Cross-project discovery** is a gap — the spec doesn't address how agents discover sibling projects on the same domain.
2. **`llms-full.txt` is rarely used** — agents prefer the per-page approach. The spec should emphasise `llms.txt` + per-page `.md` over full concatenation.
3. **Content negotiation is complementary** — `llms.txt` handles discovery, `Accept: text/markdown` handles format. Both should be recommended together.

## Files

| File | Description |
|---|---|
| `gold-standards.md` | Gold-standard answers for all 23 items |
| `build-manifest.json` | Doc build details (commits, page counts) |
| `infrastructure.md` | Infrastructure setup details |
| `results/analysis-v2.md` | Full generated analysis tables |
| `results/findings-notes.md` | Detailed observation notes |
| `results/raw/` | Raw session data (JSON + nginx logs) |
| `results/scored/` | Judge scorecards |
| `results/reviewed/` | Human review overrides |
| `scripts/run_experiment.py` | Session runner |
| `scripts/score_responses.py` | Judge scoring |
| `scripts/analyse_results.py` | Analysis + checkpoint |
| `scripts/review_tool.py` | TUI review tool |
| `scripts/questions.json` | Question definitions |

## Running the Experiment

See `scripts/` for the full automation pipeline. Key commands:

```bash
# Run sessions
python3 scripts/run_experiment.py --conditions A,B,C,D,E --models sonnet --runs 3

# Score responses
python3 scripts/score_responses.py

# Human review (33% sample)
source /tmp/llms-experiment-venv/bin/activate
python scripts/review_tool.py --resume

# Analyse
python3 scripts/analyse_results.py --output results/analysis.md
python3 scripts/analyse_results.py --checkpoint  # Sonnet vs Opus comparison
```
