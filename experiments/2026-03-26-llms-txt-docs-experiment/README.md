# Does llms.txt Actually Help Agents Write Better Code?

I was nerd-sniped by a (internal Canonical) [post asking for the addition of llms.txt](https://discourse.canonical.com/t/charm-engineering-lt-notes-18-mar-2026/7147?u=tony-meyer). I'd looked into serving Markdown versions of the Charm Tech docs previously (mostly for efficiency), but hadn't got anywhere because we don't have control within our team over the bits of serving the docs that would be needed. I wondered about just using the Sphinx option to serve the source, but wasn't sure whether it would be worth the effort. I'd seen some enthusiasm around [llms.txt](https://llmstxt.org/) — the idea that websites should serve a machine-readable index (that bit is important) and Markdown versions of their pages so that AI agents can consume documentation more effectively. But I wanted some data to back up the request, and when it wasn't immediately forthcoming, I figured that meant it was off to the experiments folder again.

I tested this on something concrete: whether Claude Code writes better Juju charms when the ecosystem documentation (`ops`, Pebble, Charmcraft, Jubilant, charmlibs, Juju) is served with llms.txt and Markdown alongside the normal HTML.

**Short answer: yes, it helps.** Scores improved from 80% to 87% — a meaningful gain, especially for topics where the model's training data is thinner.

## What I Tested

Five conditions, 620 agent sessions, 23 questions spanning API knowledge, configuration, testing, and (a quite small amount of) code generation:

| Condition | What the agent gets | Score | Cost |
|---|---|---|---|
| **A** — bare agent | "You are writing a Juju charm." | 80% | **$0.13** |
| **B** — curated instructions | CLAUDE.md with charm dev guidance | 82% | $0.15 |
| **C** — llms.txt | Told docs support llms.txt | **87%** | $0.24 |
| **D** — instructions + llms.txt | Both B and C combined | 83% | $0.20 |
| **E** — content negotiation | Markdown served via `Accept` header, agent unaware | 83% | $0.27 |

Conditions C, D, and E use locally-served docs (nginx + mkcert + `/etc/hosts` redirect) built with [sphinx-llm](https://github.com/NVIDIA/sphinx-llm). Conditions A and B use the real internet.

## Key Findings

**llms.txt is the single most impactful intervention.** It outperforms curated CLAUDE.md instructions (+5pp), and the gap is widest where training data is weakest — Pebble docs (+17pp), charmcraft config (+8pp), and synthesis tasks that combine knowledge from multiple sources (+18pp). For well-covered topics like the core ops API, the agent already knows the answer and docs don't add much.

(Note that I used the CLAUDE.md I had lying around in this repository, which is missing information about charmlibs, and doesn't explicitly point agents to documentation. In order words, it was a general, mid-quality, slightly dated instructions file, not one tuned to try to win this competition.)

**Content negotiation is free and worthwhile.** Claude Code already sends `Accept: text/markdown` in its requests. Configuring the server to respond with Markdown (condition E) improved scores by 3pp without the agent knowing anything about it. No llms.txt index, no hints — just cleaner content on every page fetch. This could be done without adding the `sphinx-llm` dependency, but would require changes made outside of my team.

**Instructions and llms.txt don't stack well.** Condition D (both) actually scores *below* condition C (llms.txt alone). The instructions make the agent more confident in what it already knows, so it fetches fewer docs and explores less. When the instructions are incomplete, it doesn't cross-check.

(I wonder if a higher-quality instruction file would change this. But not enough to spend several more hours on it...)

**The agent never uses `llms-full.txt`.** It fetches the `llms.txt` index, then follows links to individual pages. The per-page `.html.md` files are what matter — the full concatenation is essentially ignored.

**The agent's first instinct is to go to `/juju/` for everything.** 49 out of 136 sessions in condition C started by fetching `/juju/en/latest/llms.txt`, even for questions about Pebble or charmcraft. The agent associates `documentation.ubuntu.com` with Juju above all else. The `llms.txt` index needs to help with cross-project discovery.

(Maybe the fact that the Juju repository actually has `llms.txt` impacts this, or maybe that the Juju docs have lived at documentation.ubuntu.com a little longer?)

**URL stability matters.** 29% of doc fetches included `/en/` in the path — a URL pattern that hasn't been used by these repos but exists elsewhere on the domain. Without nginx rewrites to handle this, half the doc fetches would have been 404s.

## What This Means in Practice

If you maintain Sphinx documentation and want agents to use it well (and resemble Charm Tech):

1. Add `sphinx-llm` to your build — it generates `llms.txt`, `llms-full.txt`, and per-page `.html.md` files alongside your existing HTML. It's additive; nothing changes for human readers.
2. Serve Markdown via content negotiation — a small nginx or Cloudflare config change that benefits every AI tool that sends `Accept: text/markdown`.
3. Make sure old URLs redirect — agents hallucinate URL patterns from training data. If your docs have moved, redirects are essential.
4. Link to sibling projects in your `llms.txt` — agents struggle to discover what else lives on the same domain.

For people writing AGENTS.md or similar instructions for charm development: instructions are the cheapest option (depending on how one measures the human cost of writing them) and help with cost/efficiency, but they're less effective than good docs for accuracy. Name specific doc URLs in your instructions rather than hoping the agent will find them.

## Details

- [WRITEUP.md](WRITEUP.md) — Full experiment report with methodology, infrastructure, per-question results, and detailed analysis of all findings
- [gold-standards.md](gold-standards.md) — The 23 questions and reference answers
- [results/](results/) — Raw data, scorecards, and analysis tables
- [scripts/](scripts/) — Automation pipeline (runner, judge, analysis, review TUI)
- [infra/](infra/) — nginx config, setup script, DNS toggle scripts
- [build-manifest.json](build-manifest.json) — Repo commits and doc build details

Run on an Ubuntu 24.04 VM using Claude Sonnet 4.6 and Opus 4.6 (there was no significant difference between Sonnet and Opus).
