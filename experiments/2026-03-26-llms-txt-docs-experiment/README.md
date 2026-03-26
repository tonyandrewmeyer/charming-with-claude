# Experiment: Do LLM-Friendly Docs Help Agents Write Charms?

**Date:** 2026-03-26
**Status:** Planning

## Hypothesis

Providing LLM-optimised documentation formats (`llms.txt`, `llms-full.txt`, per-page markdown via `sphinx-llm`) for the core Juju/charm ecosystem libraries makes agents measurably better at writing charms, compared to relying on standard HTML documentation alone.

## Background

The [llms.txt specification](https://llmstxt.org/) proposes a standardised way to serve documentation in a format optimised for LLM consumption. The `sphinx-llm` extension can generate these files from existing Sphinx documentation. None of the target repos currently serve `llms.txt`.

All five target repos use Sphinx with `canonical_sphinx`, hosted on `documentation.ubuntu.com`. Four use MyST Markdown source; charmcraft uses RST. This makes them good candidates for `sphinx-llm` integration.

### Key Question

Is the value of better docs *at inference time* significant, or do good upfront instructions (skills, CLAUDE.md, curated prompts) already capture the necessary knowledge more efficiently?

## Target Repositories

| Repository | Docs URL | Source Format | Fork |
|---|---|---|---|
| canonical/operator (ops) | documentation.ubuntu.com/ops/ | MyST Markdown | tonyandrewmeyer/operator |
| canonical/pebble | documentation.ubuntu.com/pebble/ | MyST Markdown | tonyandrewmeyer/pebble |
| canonical/jubilant | documentation.ubuntu.com/jubilant/ | MyST Markdown | tonyandrewmeyer/jubilant |
| canonical/charmlibs | documentation.ubuntu.com/charmlibs/ | MyST Markdown | tonyandrewmeyer/charmlibs |
| canonical/charmcraft | documentation.ubuntu.com/charmcraft/ | reStructuredText | tonyandrewmeyer/charmcraft |

## Experimental Conditions

### Condition A: Bare Agent (Control)
- Fresh Claude Code session, no CLAUDE.md, no skills
- Initial prompt includes only: "You are writing a Juju charm."
- `/etc/hosts` is **not** modified — agent accesses the real `documentation.ubuntu.com` (standard HTML, no llms.txt)
- Agent may discover docs on its own via WebSearch/WebFetch if it chooses to
- Tests: what can the agent do with just its training knowledge + real web access?

### Condition B: Curated Instructions (Skills Baseline)
- Claude Code with charm-development CLAUDE.md and skills from `claude-instructions/`
- `/etc/hosts` is **not** modified — real docs, no llms.txt
- Represents "best current practice" for guided charm development
- Tests: how much do good upfront instructions improve over bare agent?

### Condition C: LLM-Optimised Docs Only
- Fresh Claude Code session, no CLAUDE.md, no skills
- Initial prompt includes: "You are writing a Juju charm. Documentation is available at documentation.ubuntu.com and supports the llms.txt standard."
- `/etc/hosts` **is** modified — agent hits local nginx serving enhanced docs (HTML + llms.txt + llms-full.txt + per-page .md)
- Tests: does the llms.txt ecosystem alone (with a hint) help as much as curated instructions?

### Condition D: Curated Instructions + LLM-Optimised Docs
- Full skills/instructions from Condition B
- `/etc/hosts` **is** modified — enhanced docs from Condition C
- Skills/CLAUDE.md also mention that docs support llms.txt
- Tests: does the combination outperform either alone?

### Condition Matrix

| | No llms.txt (real docs) | llms.txt (local enhanced docs) |
|---|---|---|
| **No instructions** | A (bare + real web) | C (bare + llms.txt hint) |
| **Curated instructions** | B (skills + real web) | D (skills + llms.txt) |

This 2×2 design lets us isolate the effect of each factor and measure interaction effects.

## Infrastructure: Local Doc Serving

### Approach: Local Build + nginx + /etc/hosts

This VM has passwordless sudo, so the `/etc/hosts` approach is straightforward.

#### Step 1: Clone and Build Enhanced Docs

```bash
# Working directory for doc builds
mkdir -p ~/llms-txt-experiment/docs-build

# For each fork:
for repo in operator pebble jubilant charmlibs charmcraft; do
    git clone https://github.com/tonyandrewmeyer/${repo}.git \
        ~/llms-txt-experiment/docs-build/${repo}
done

# Install sphinx-llm
pip install sphinx-llm

# For each repo, add sphinx_llm.txt to conf.py extensions and build
# (detailed per-repo build scripts in scripts/ directory)
```

#### Step 2: Serve via nginx

```nginx
server {
    listen 80;
    server_name documentation.ubuntu.com;

    # ops docs
    location /ops/ {
        alias /home/ubuntu/llms-txt-experiment/docs-output/operator/;
        try_files $uri $uri/ =404;
    }

    # pebble docs
    location /pebble/ {
        alias /home/ubuntu/llms-txt-experiment/docs-output/pebble/;
        try_files $uri $uri/ =404;
    }

    # jubilant docs
    location /jubilant/ {
        alias /home/ubuntu/llms-txt-experiment/docs-output/jubilant/;
        try_files $uri $uri/ =404;
    }

    # charmlibs docs
    location /charmlibs/ {
        alias /home/ubuntu/llms-txt-experiment/docs-output/charmlibs/;
        try_files $uri $uri/ =404;
    }

    # charmcraft docs
    location /charmcraft/ {
        alias /home/ubuntu/llms-txt-experiment/docs-output/charmcraft/;
        try_files $uri $uri/ =404;
    }
}
```

#### Step 3: DNS Override

```bash
# Enable (before conditions C/D runs):
echo "127.0.0.1 documentation.ubuntu.com" | sudo tee -a /etc/hosts

# Disable (before conditions A/B runs):
sudo sed -i '/documentation.ubuntu.com/d' /etc/hosts
```

#### HTTPS Consideration

The real `documentation.ubuntu.com` serves over HTTPS. Claude Code's WebFetch will likely request `https://` URLs. Options:
1. **Self-signed cert + nginx SSL** — may cause certificate verification failures in WebFetch
2. **mkcert** — generate a locally-trusted CA and cert for `documentation.ubuntu.com`
3. **HTTP-only** — if WebFetch follows redirects or tries HTTP fallback, this might just work
4. **Proxy approach** — use a local HTTPS proxy that terminates TLS and forwards to nginx on HTTP

**Recommendation:** Use `mkcert` to generate a trusted local cert. This is the cleanest approach and avoids certificate errors.

```bash
# Install mkcert
sudo apt install -y libnss3-tools
curl -JLO "https://dl.filippo.io/mkcert/latest?for=linux/amd64"
chmod +x mkcert-v*-linux-amd64
sudo mv mkcert-v*-linux-amd64 /usr/local/bin/mkcert

# Create local CA and cert
mkcert -install
mkcert documentation.ubuntu.com

# Use the generated cert in nginx SSL config
```

## Evaluation Design

### Approach: Information Retrieval + Micro-Tasks

20 questions across five categories, plus 3 micro-charm synthesis tasks. Each question has a gold-standard answer prepared in advance. This avoids the cost and variability of building full charms while still testing real capability.

### Question Set

#### Category 1: ops API Knowledge (5 questions)

| # | Question | Tests | Gold Standard Source |
|---|---|---|---|
| Q1 | "What parameters does `Container.add_layer` accept and what does each do?" | API detail retrieval | ops API reference |
| Q2 | "How do you access relation data for a specific remote unit? Show the code." | Relation data access pattern | ops how-to guides |
| Q3 | "What is the full list of hook events a charm can observe? List them all." | Comprehensive API enumeration | ops reference |
| Q4 | "What's the difference between `ActionEvent.fail()` and raising an exception in an action handler?" | Nuanced API behaviour | ops reference + guides |
| Q5 | "How do you use `ops.CollectStatusEvent` to set charm status? Show a complete example." | Recent API feature | ops how-to / reference |

#### Category 2: Pebble Knowledge (4 questions)

| # | Question | Tests | Gold Standard Source |
|---|---|---|---|
| Q6 | "Write a complete Pebble layer YAML that defines a service with an HTTP health check, custom environment variables, and a log target." | Layer format synthesis | Pebble reference |
| Q7 | "How do Pebble notices work? What types are there and how does a charm observe them via ops?" | Cross-project knowledge (Pebble + ops) | Pebble + ops docs |
| Q8 | "What is the Pebble change/task model? How do you check if a long-running operation has completed?" | Pebble internal concepts | Pebble reference |
| Q9 | "How do you configure Pebble log forwarding to Loki? Show the layer YAML and explain the protocol options." | Specific feature detail | Pebble reference |

#### Category 3: Testing with jubilant (3 questions)

| # | Question | Tests | Gold Standard Source |
|---|---|---|---|
| Q10 | "How do you deploy a charm and wait for it to reach active/idle using jubilant? Show complete test code." | Basic jubilant usage | jubilant docs |
| Q11 | "How do you add a relation between two applications and verify data was exchanged, using jubilant?" | Relation testing pattern | jubilant docs |
| Q12 | "How do you run a Juju action on a unit and check its results using jubilant?" | Action testing | jubilant docs |

#### Category 4: Charm Libraries — charmlibs (4 questions)

| # | Question | Tests | Gold Standard Source |
|---|---|---|---|
| Q13 | "How do you use the ingress library to provide ingress to your charm? Show the requires side." | Library usage pattern | charmlibs docs |
| Q14 | "What events does the TLS certificates library emit, and when should a charm request a new certificate?" | Library event model | charmlibs docs |
| Q15 | "How do you use the database_requires library to connect to a PostgreSQL database?" | Database relation pattern | charmlibs docs |
| Q16 | "What is the correct way to implement a provider side of a relation using charmlibs?" | Provider pattern | charmlibs docs |

#### Category 5: Charmcraft & Packaging (4 questions)

| # | Question | Tests | Gold Standard Source |
|---|---|---|---|
| Q17 | "What is the structure of a `charmcraft.yaml` file for a Kubernetes charm? Show a complete example with all required fields." | Packaging config | charmcraft docs |
| Q18 | "How do you declare a relation endpoint in `charmcraft.yaml` and what fields does it support?" | Config detail | charmcraft docs |
| Q19 | "How do you configure resource declarations for OCI images in `charmcraft.yaml`?" | Resource config | charmcraft docs |
| Q20 | "What bases/platforms does charmcraft support and how do you specify multi-base builds?" | Build config | charmcraft docs |

#### Synthesis Tasks (3 micro-charm builds)

| # | Task | Tests | Scoring |
|---|---|---|---|
| S1 | "Write a minimal K8s charm (`src/charm.py` + `charmcraft.yaml`) that sets ActiveStatus on install and WaitingStatus if a 'name' config option is empty." | Basic charm structure | Diff against gold standard |
| S2 | "Write a charm handler for `_on_pebble_ready` that configures a workload container with: the command from a config option, environment variables from a database relation, and an HTTP health check." | Multi-source synthesis | Correctness of Pebble layer + relation data access |
| S3 | "Write a complete charm class that provides data over a custom relation interface. When a remote app joins the relation, set the 'endpoint' key in the relation data to the unit's FQDN." | Relation provider pattern | Correct relation data handling |

### Scoring Rubric

#### Per-Question Scoring (Q1–Q20)

| Dimension | 0 | 1 | 2 | Weight |
|---|---|---|---|---|
| **Correctness** | Wrong or fabricated answer | Partially correct (right concept, wrong details) | Fully correct, matches gold standard | 3× |
| **Specificity** | Vague/generic (could apply to any framework) | Some framework-specific details | Precise API names, parameters, patterns | 2× |
| **Hallucination** | Invented APIs, parameters, or classes | Minor inaccuracies (e.g., wrong default value) | No hallucinations — all facts verifiable | 3× |
| **Currency** | Uses deprecated/removed APIs | Uses older but still valid APIs | Uses current recommended APIs | 1× |

**Max score per question:** (2×3) + (2×2) + (2×3) + (2×1) = 18 points
**Max total (Q1–Q20):** 360 points

#### Per-Task Scoring (S1–S3)

| Dimension | 0 | 1 | 2 | Weight |
|---|---|---|---|---|
| **Runs correctly** | Syntax errors or missing imports | Minor issues (would work with small fixes) | Would run correctly as-is | 3× |
| **Idiomatic** | Not recognisable as an ops charm | Some charm patterns but non-standard | Follows ops conventions and patterns | 2× |
| **Complete** | Missing major components | Has the structure but missing details | All requested features implemented | 2× |
| **Hallucination-free** | Uses invented APIs | Minor API inaccuracies | All API usage is correct | 3× |

**Max score per task:** (2×3) + (2×2) + (2×2) + (2×3) = 20 points
**Max total (S1–S3):** 60 points

#### Efficiency Metrics (automated, per session)

| Metric | How to Capture |
|---|---|
| **Total tokens** (input + output) | Claude Code session metadata / API logs |
| **Tool calls** | Count of WebFetch, WebSearch, Read calls |
| **Web fetches** | Count and URLs of all WebFetch calls (did it find llms.txt? llms-full.txt? .md pages?) |
| **Time to answer** | Wall-clock time from prompt to final response |
| **Docs discovered** | Which doc URLs the agent accessed (nginx access log analysis) |

### Automated Scoring Approach

To score 240 sessions consistently, we use a two-layer approach:

1. **Automated pre-scoring:** A separate Claude instance (the "judge") scores each response against the gold standard, producing a JSON scorecard. The judge prompt includes the gold standard answer, the scoring rubric, and the agent's response.

2. **Human spot-check:** Manually review a random 10-20% sample to calibrate the judge and catch systematic errors. Adjust judge prompt if needed.

3. **Efficiency metrics:** Fully automated — parse from session logs and nginx access logs.

## Automation: Running the Experiment

### Session Runner Script

A Python script that:
1. Sets up the environment for the condition (enable/disable `/etc/hosts`, set up CLAUDE.md)
2. Launches Claude Code in headless/API mode with the appropriate prompt
3. Sends each question, captures the full response
4. Records token usage, tool calls, timing
5. Saves raw session data to `results/raw/`

```
scripts/
├── run_experiment.py       # Main runner — iterates conditions × questions × runs
├── setup_condition.sh      # Toggles /etc/hosts, CLAUDE.md, skills per condition
├── build_docs.sh           # Builds all 5 doc sets with sphinx-llm
├── serve_docs.sh           # Starts/stops nginx
├── score_responses.py      # Judge script — sends responses to Claude for scoring
├── analyse_results.py      # Aggregates scores, generates tables and charts
├── gold_standards.json     # All gold-standard answers
└── nginx.conf              # nginx configuration for local doc serving
```

### Session Isolation

Each session must be fully isolated:
- Fresh `/tmp` working directory
- No `.claude/` directory (no memory persistence between sessions)
- Condition A/C: no CLAUDE.md in the working directory
- Condition B/D: CLAUDE.md + skills copied into the working directory
- Separate nginx access log per session (for doc access analysis)

### Run Order

Randomise the order of conditions and questions within each run to avoid systematic bias from model warm-up, caching, or temporal effects. Use a fixed random seed per run for reproducibility.

## Practical Considerations

### Repeatability
- 3 runs per condition per question (720 total sessions across all questions)
- Wait — that's 20 questions + 3 tasks = 23 items × 4 conditions × 3 runs = 276 sessions
- Use the same model (claude-sonnet-4-6 for cost efficiency, or claude-opus-4-6 for capability — decide before starting)
- Pin doc builds to specific commits of the forks (record commit SHAs)

### Cost Estimate
- Info retrieval questions: ~5K tokens input + ~2K tokens output each ≈ $0.05/session (Sonnet)
- Synthesis tasks: ~10K tokens input + ~5K tokens output each ≈ $0.15/session (Sonnet)
- Total estimate (Sonnet): ~240 × $0.05 + ~36 × $0.15 ≈ $17
- Scoring (judge): ~276 judge calls ≈ $15
- **Total estimate: ~$32** (Sonnet) or ~$160 (Opus)
- This is very affordable — run with both models if budget permits

### What sphinx-llm Produces

The `sphinx-llm` (`sphinx_llm.txt` extension) generates:
- `llms.txt` — index file with links and descriptions (markdown)
- `llms-full.txt` — all docs concatenated into one markdown file
- Per-page `.html.md` files — markdown version of each HTML page

This is strictly additive — all existing HTML docs remain unchanged.

### Which sphinx-llm?

Two options:
- **`sphinx-llm`** (NVIDIA/jacobtomlinson) — generates markdown output, per-page `.md` files, `llms.txt`, `llms-full.txt`
- **`sphinx-llms-txt`** (jdillard) — generates `llms.txt` and `llms-full.txt` only, in RST format, more configuration options

**Decision:** Use `sphinx-llm` since it produces per-page markdown files (which is part of what we want to test) and outputs markdown (more natural for LLMs than RST). Note: charmcraft uses RST source, but sphinx-llm converts to markdown output regardless.

### Potential Complications

1. **`canonical_sphinx` compatibility with `sphinx-llm`:** The Canonical Sphinx theme may have custom directives or builders that interact poorly with sphinx-llm's markdown builder. Test early.

2. **charmcraft RST source:** sphinx-llm should handle RST→markdown conversion, but the output quality may differ from MyST→markdown. Worth checking.

3. **Large llms-full.txt:** If the concatenated docs exceed Claude's practical context window for a single WebFetch, the agent may need to use per-page .md files instead. This is itself an interesting finding.

4. **WebFetch vs WebSearch:** The agent might WebSearch for docs rather than directly fetching URLs. WebSearch results come from the real internet, not our local server. Only WebFetch is affected by the DNS override. This means conditions C/D still have access to real search results — the llms.txt files are an *additional* resource, not a replacement.

5. **HTTPS/TLS:** Must get mkcert working properly so WebFetch doesn't reject the self-signed cert. Test this before running any sessions.

## Expected Outcomes & What We Learn

### Possible Results

| Outcome | Implication |
|---|---|
| **D >> B > C > A** | Both help, instructions matter more, combination is best. Invest in both. |
| **B ≈ D >> C ≈ A** | Instructions are what matter; llms.txt adds nothing on top. Focus on skills/CLAUDE.md. |
| **C ≈ D >> A ≈ B** | llms.txt is transformative; instructions add little on top. Push for llms.txt adoption in Canonical docs. |
| **B >> D > A > C** | Instructions help, but llms.txt actively hurts (e.g., context pollution). Investigate why. |
| **A ≈ B ≈ C ≈ D** | Neither approach makes a significant difference. Training data already captures most of what's needed. |

### Secondary Findings

Regardless of the main result, we'll learn:
- **Does the agent discover and use llms.txt?** If not, the spec needs better agent integration.
- **Which doc pages does the agent fetch?** Informs which docs are most valuable.
- **Does llms-full.txt get used, or per-page .md?** Informs whether full-context or targeted retrieval is preferred.
- **Which questions are hardest?** Identifies gaps in current docs or training data.
- **Does the RST-sourced charmcraft behave differently?** Informs whether source format matters.

## Resolved Decisions

- ✅ Agent is told llms.txt exists (conditions C/D get a hint in their prompt)
- ✅ Condition A gets "You are writing a Juju charm" as minimal context
- ✅ Condition A uses real internet (no /etc/hosts override)
- ✅ Include charmcraft (RST source — interesting comparison)
- ✅ Use `/etc/hosts` + nginx + mkcert (VM with passwordless sudo)
- ✅ Full 240+ sessions, 3 runs per condition

## Next Steps

1. **Review this plan** — align on any remaining questions
2. **Fork setup** — ensure tonyandrewmeyer forks are up to date, record commit SHAs
3. **Build enhanced docs** — install sphinx-llm, test with each repo, resolve any build issues
4. **Set up infrastructure** — nginx, mkcert, /etc/hosts toggle script
5. **Write gold-standard answers** — Q1–Q20 + S1–S3, sourced from actual current docs
6. **Build the runner** — session runner, judge script, analysis script
7. **Pilot run** — 2-3 questions × 4 conditions × 1 run to validate the setup
8. **Full run** — all 276 sessions
9. **Score and analyse** — automated + human spot-check
10. **Write up results** — findings, recommendations, artefacts for the community
