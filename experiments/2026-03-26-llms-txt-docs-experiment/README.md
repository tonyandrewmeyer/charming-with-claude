# Does llms.txt Actually Help Agents Write Better Code?

There's been a lot of enthusiasm around [llms.txt](https://llmstxt.org/) — the idea that websites should serve a machine-readable index and markdown versions of their pages so that AI agents can consume documentation more effectively. But does it actually make a difference?

I tested this on something concrete: whether Claude Code writes better Juju charms when the ecosystem documentation (ops, Pebble, charmcraft, jubilant, charmlibs, Juju) is served with llms.txt and markdown alongside the normal HTML.

**Short answer: yes, it helps.** Scores improved from 80% to 87% — a meaningful gain, especially for topics where the model's training data is thinner.

## What I Tested

Five conditions, 620 agent sessions, 23 questions spanning API knowledge, configuration, testing, and code generation:

| Condition | What the agent gets | Score | Cost |
|---|---|---|---|
| **A** — bare agent | "You are writing a Juju charm." | 80% | $0.13 |
| **B** — curated instructions | CLAUDE.md with charm dev guidance | 82% | $0.15 |
| **C** — llms.txt | Told docs support llms.txt | **87%** | $0.24 |
| **D** — instructions + llms.txt | Both B and C combined | 83% | $0.20 |
| **E** — content negotiation | Markdown served via `Accept` header, agent unaware | 83% | $0.27 |

Conditions C, D, and E use locally-served docs (nginx + mkcert + `/etc/hosts` redirect) built with [sphinx-llm](https://github.com/NVIDIA/sphinx-llm). Conditions A and B use the real internet.

## Key Findings

**llms.txt is the single most impactful intervention.** It outperforms curated CLAUDE.md instructions (+5pp), and the gap is widest where training data is weakest — Pebble docs (+17pp), charmcraft config (+8pp), and synthesis tasks that combine knowledge from multiple sources (+18pp). For well-covered topics like the core ops API, the agent already knows the answer and docs don't add much.

**Content negotiation is free and worthwhile.** Claude Code already sends `Accept: text/markdown` in its requests. Configuring the server to respond with markdown (condition E) improved scores by 3pp without the agent knowing anything about it. No llms.txt index, no hints — just cleaner content on every page fetch.

**Instructions and llms.txt don't stack well.** Condition D (both) actually scores *below* condition C (llms.txt alone). The instructions make the agent more confident in what it already knows, so it fetches fewer docs and explores less. When the instructions are incomplete, it doesn't cross-check.

**The agent never uses `llms-full.txt`.** It fetches the `llms.txt` index, then follows links to individual pages. The per-page `.html.md` files are what matter — the full concatenation is essentially ignored.

**The agent's first instinct is to go to `/juju/` for everything.** 49 out of 136 sessions in condition C started by fetching `/juju/en/latest/llms.txt`, even for questions about Pebble or charmcraft. The agent associates `documentation.ubuntu.com` with Juju above all else. The `llms.txt` index needs to help with cross-project discovery.

**URL stability matters.** 29% of doc fetches included `/en/` in the path — a URL pattern that hasn't been used by these repos but exists elsewhere on the domain. Without nginx rewrites to handle this, half the doc fetches would have been 404s.

## What This Means in Practice

If you maintain Sphinx documentation and want agents to use it well:

1. Add `sphinx-llm` to your build — it generates `llms.txt`, `llms-full.txt`, and per-page `.html.md` files alongside your existing HTML. It's additive; nothing changes for human readers.
2. Serve markdown via content negotiation — a small nginx or Cloudflare config change that benefits every AI tool that sends `Accept: text/markdown`.
3. Make sure old URLs redirect — agents hallucinate URL patterns from training data. If your docs have moved, redirects are essential.
4. Link to sibling projects in your `llms.txt` — agents struggle to discover what else lives on the same domain.

For people writing CLAUDE.md or similar instructions for charm development: instructions are the cheapest option and help with cost/efficiency, but they're less effective than good docs for accuracy. Name specific doc URLs in your instructions rather than hoping the agent will find them.

## Details

- [WRITEUP.md](WRITEUP.md) — Full experiment report with methodology, infrastructure, per-question results, and detailed analysis of all findings
- [gold-standards.md](gold-standards.md) — The 23 questions and reference answers
- [results/](results/) — Raw data, scorecards, and analysis tables
- [scripts/](scripts/) — Automation pipeline (runner, judge, analysis, review TUI)
- [infra/](infra/) — nginx config, setup script, DNS toggle scripts
- [build-manifest.json](build-manifest.json) — Repo commits and doc build details

Total cost: ~$130 ($99 for 620 agent sessions, ~$30 for judge scoring). Run on an Ubuntu 24.04 VM using Claude Sonnet 4.6 and Opus 4.6.
