# mcp-server-operator

Every previous experiment in this series (including the ones where I haven't finished the write-ups yet) gave Claude substantial (often increasing) scaffolding: a detailed `CLAUDE.md` with charm development instructions, custom skills, specific guidance on testing frameworks, code style rules, and so on. The question I kept coming back to (particularly the more I worked with the 4.5 and 4.6 models elsewhere) was: how much of that matters? Are the latest models good enough that they can just ... figure it out? Also, other than the models improving, have the improvements in our docs and the more recent training data (presumably) helped?

This experiment set out to answer that. I gave Claude (Opus 4.6, the latest model at the time) a charm idea and almost nothing else — no `CLAUDE.md` with charm development instructions, no skills, no custom commands, no 'testing sandwich' guidance, no links to Ops or Jubilant documentation. Just the model and whatever it already knows.

The charm itself was deliberately ambitious (there was some other motivation there, related to something else I'm working on when I have time). Not a simple "install a snap and manage a config file" charm like Mosquitto, but something with a lot of moving parts: a subordinate machine charm that deploys an [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server, a separately-packaged charm library, OAuth 2.1, TLS, ingress, full COS observability, OpenTelemetry tracing, Sloth SLOs (the Sloth charm is super new -- it helps to be seeing all the public listing charms!), and a PostgreSQL demo. If Claude was going to fall over, I wanted to see where. (That's where the instructions should focus.)

(MCP is also just interesting as a charm. The idea of letting any principal charm declaratively expose tools, prompts, and resources to LLM agents — without needing to implement the protocol itself — is a compelling use case for subordinates (and an interesting example of what Juju can do). And the PostgreSQL demo, where an LLM can query and analyse a real database through Juju, is the kind of thing that makes for a fun demo.)

## Goals

* Test whether the latest models (Opus 4.6) can develop a charm **without** any custom instructions, skills, or scaffolding beyond what the model already knows.
* Build a charm with extensive integrations — the kind of "best practice" charm with COS, tracing, TLS, OAuth, ingress, and SLOs that we'd want to see from experienced charmers.
* Include a charm library (`charmlibs-interfaces-mcp`) in the modern style — published to PyPI, using dataclasses rather than Pydantic (ok, that's my preferences leaking through, not modern style), with proper provider/requirer classes.
* Produce quality documentation following the Diátaxis framework.
* Produce a compelling demo (particularly the PostgreSQL one).

## Setup

As with recent experiments, Claude Code ran inside a [Multipass](https://canonical.com/multipass) VM with [Concierge](https://github.com/canonical/concierge) providing a bootstrapped Juju environment. I ran Claude in YOLO mode (`--dangerously-skip-permissions`).

The critical difference from every other experiment: **no `CLAUDE.md` with charm development instructions was provided**. There was a `CLAUDE.md`, but it was created *by Claude* during development — a project guide it wrote for itself describing the repository structure, code style, and common commands. It was not seeded with any of the charm-specific guidance (testing frameworks, event handling patterns, import style, and so on) that I've been iterating on since the Mosquitto experiment.

There were also no skills, no custom commands, and no `.claude/commands/` directory.

## Results

The project is in the [mcp-charm repository](https://github.com/tonyandrewmeyer/mcp-charm). The [full transcripts](https://tonyandrewmeyer.github.io/mcp-charm/) are available, made pretty by [Simon Willison's claude-code-transcripts tool](https://simonwillison.net/2025/Dec/25/claude-code-transcripts/). There were three sessions: initial planning and core implementation, refinement and advanced features (observability, demos), and testing and compliance (OAuth, full test suite validation). I think in future I may manage sessions more; I do when working on other projects and using Claude Code. In particular, being more deliberate about starting with a clear context instead of the "do it all in one" approach most of these experiments have leant towards. I think maybe one of the switches here was the automatic one that Claude does these days.

### What Was Built

The project ended up being considerably more complex than any previous experiment, with three separate packages:

```
mcp-charm/
├── charm/                  # Subordinate machine charm (ops framework)
│   ├── src/
│   │   ├── charm.py        # 277 lines — relation handling, lifecycle
│   │   ├── mcp_server.py   # 243 lines — systemd service management
│   │   └── workload_server.py  # Copied from workload/ at build time (I don't love this choice)
│   ├── tests/
│   │   ├── unit/           # 40 test functions
│   │   └── integration/    # Jubilant-based deploy test
│   └── charmcraft.yaml     # 8 relations, 7 config options
├── workload/               # Standalone MCP server (FastMCP + Starlette)
│   ├── src/
│   │   ├── server.py       # 682 lines — MCP protocol, middleware, metrics
│   │   └── token_verifier.py  # 148 lines — JWT + token introspection
│   └── tests/              # 71 test functions (unit + integration)
├── charmlib/               # charmlibs-interfaces-mcp Python package
│   ├── src/                # 515 lines — McpProvider, McpRequirer, models
│   └── tests/              # 23 test functions
├── demo/
│   ├── principal/          # Simple demo charm (system tools)
│   └── postgresql/         # PostgreSQL MCP wrapper
├── docs/                   # Diátaxis: tutorials, how-tos, reference, explanation
└── Makefile                # Build orchestration
```

**134 test functions** across the three packages, covering charm lifecycle events, OAuth, TLS, COS, tracing, MCP protocol compliance, middleware behaviour, security boundaries, and load testing.

### The Charm

The charm itself is reasonably clean. At 277 lines, `charm.py` is well structured: a typed `CharmConfig` dataclass (I did push for that), sensible event observation (non-reconcicle!) using `framework.observe` (not `self.framework.observe`, which was a 'problem' in earlier experiments), and clean separation between the charm and the workload management module (I think the improvements in the `charmcraft` profile are to thank here). It correctly uses `self.load_config` with an `errors="blocked"` parameter, which is a modern Ops pattern I wouldn't have expected the model to know about without being told (I don't think anyone is really using it).

The relation set is substantial:

| Relation | Interface | Direction | Purpose |
|----------|-----------|-----------|---------|
| `mcp` | `mcp` | requires (scope: container) | Principal provides tool definitions |
| `cos-agent` | `cos_agent` | provides | Grafana Agent for observability |
| `sloth` | `sloth` | provides | SLO specifications |
| `oauth` | `oauth` | requires | Identity provider for OAuth 2.1 |
| `reverse-proxy` | `haproxy-route` | requires | HAProxy ingress |
| `certificates` | `tls-certificates` | requires | TLS termination |
| `charm-tracing` | `tracing` | requires | OpenTelemetry (Tempo) |
| `receive-ca-cert` | `certificate_transfer` | requires | CA certificate for tracing |

This is closer to the kind of relation set I'd see on a production charm. I was particularly happy that it used a single `mcp` relation with `scope: container` for both subordinate attachment and data transfer, rather than also requiring `juju-info` (which, honestly, I'm still a bit confused about, but feel like it's an older pattern even though it still works) — although it's interesting to read in `PLAN.md` how Claude worked through this decision, initially proposing `juju-info` and then reasoning its way to the cleaner approach (with some help from me).

### The Charm Library

The `charmlibs-interfaces-mcp` package is probably the most interesting output. It's a proper charm library with:

- `McpProvider` — for principal charms to advertise tools, prompts, and resources
- `McpRequirer` — used internally by the mcp-server charm
- Plain dataclass models (`Tool`, `Prompt`, `Resource`, `ExecHandler`, `HttpHandler`)

No Pydantic, just to make me satisfied (`pydantic` is still a dependency because of `cos` I think). This is what I'd want to see, and the API is ok:

```python
from charmlibs.interfaces import mcp

self.mcp = mcp.McpProvider(self, "mcp")
self.mcp.set_tools([
    mcp.Tool(
        name="list-dbs",
        description="List databases",
        input_schema={...},
        handler=mcp.ExecHandler(command=["psql", "-l", "--csv"]),
    ),
])
```

I don't love "big dumps of config" style relation data, but I'm also not sure whether it would be better to break it out at the relation level. I haven't done much with charm libraries recently, outside of reviewing, so I'm hoping to get some additional input on this.

### Observability

The COS integration is comprehensive — more so than I've seen from any of the previous experiments:

- **Prometheus metrics**: Four metrics (request count, latency histogram, tool calls, active connections) with a custom `MetricsMiddleware`
- **Grafana dashboard**: Request rate, latency percentiles, error rate, tool calls, active connections
- **Alert rules**: `McpServerDown`, `McpServerHighErrorRate`, `McpServerHighLatency`
- **SLOs via Sloth**: 99.9% availability and p99 latency within 5 seconds
- **OpenTelemetry tracing**: Both charm-level (via `ops[tracing]`) and workload-level (ASGI instrumentation with OTLP HTTP export)
- **Structured JSON logging** for Loki integration

### Security

The security model is not terrible:

- All subprocess calls use list args (never `shell=True`) — this was done by design from the start
- Template substitution replaces `{{param}}` in individual argv elements, preventing injection
- Optional command allowlist
- Bearer token auth via config
- OAuth 2.1 resource server mode with JWT validation and token introspection
- Rate limiting middleware

I would want to think this through more and carefully model scenarios out before accepting this as a real charm.

### Documentation

Claude produced documentation following the [Diátaxis](https://diataxis.fr/) framework as asked to. Tutorials, how-to guides, reference, and explanation docs. The demo README is particularly good — step-by-step instructions that actually work, including how to connect Claude Code as an MCP client.

### Tests

The tests are, by and large, well-written. The charm unit tests correctly use `ops.testing` with `Context` and `State` (not Harness), and correctly use `testing.SubordinateRelation` for the `mcp` relation. They use `monkeypatch` rather than `unittest.mock.patch`, and the fixture pattern for patching workload calls is clean.

The workload tests are organised into classes, which I would normally push back on, but in this case there are enough of them (71 functions) that the grouping is reasonable. The integration tests exercise the MCP protocol end-to-end, including authentication, rate limiting, and metrics.

One notable pattern: the OAuth tests generate real RSA key pairs and create proper JWTs for testing, rather than just mocking everything away. This is a better approach than I would have expected.

## Where Claude Struggled

### The `ty` Configuration

Claude had significant trouble with the `ty` type checker configuration. It seems that the `ty` configuration format has changed across recent versions, and Claude tried several variations of `[tool.ty.src]` with different key formats before I suggested simplifying to just `ty check .` with file exclusions. This is a common issue with newer tools — the training data lags behind the current API. Perhaps I should have had it stick with `pyright` as the profile provides, but `ty` is so much faster and that makes it more practicable to be in `pre-commit` checks and keep the agent honest.

### The `ops.testing` API

Claude initially struggled with the `ops.testing.Context` API, particularly around how `relation.save()` and `relation.load()` work with relation data serialisation (we're considering adding a feature to ops to make this simpler (for a while, not because of this experiement)). There was a double-JSON encoding issue where relation data was being JSON-encoded twice. This was resolved through trial and error, but it's the kind of thing that the CLAUDE.md guidance in previous experiments was designed to prevent.

### Namespace Packaging for the Charm Library

Getting `charmlibs-interfaces-mcp` set up as a proper namespace package with the right build backend took several iterations. The `charmlibs` namespace is still quite new, and Claude had to work through the package structure, build configuration, and `__init__.py` handling.

### PyPI Publishing

The initial GitHub Actions workflow for PyPI publishing used the wrong action. I had to correct it to `pypa/gh-action-pypi-publish@release/v1`.

### `except Exception`

There are three instances of `except Exception:` in the codebase (one in `charm.py`, two in `server.py`/`workload_server.py`). In previous experiments, I explicitly instructed against this in `CLAUDE.md`. Without that guidance, it crept back in. The instance in `charm.py` is in `_get_otlp_endpoint()` where it's arguably defensive (the tracing integration shouldn't take down the charm), but it's still not best practice.

## What Went Well

The primary finding is how much the model has improved since the earlier experiments. Without *any* charm-specific instructions:

- It correctly used `ops.testing` (not Harness) for unit tests
- It correctly used `framework.observe` (not `self.framework.observe`)
- It used my preferred import style (`import pathlib` not `from pathlib import Path`) — although this wasn't perfectly consistent
- It followed a sensible development progression (plan → scaffold → implement → test)
- It created a CLAUDE.md for itself to track project conventions
- It correctly used subordinate relations with `scope: container`
- It handled the complexity of three separate packages with shared code (workload source copied into charm at build time)

The code quality is noticeably higher than any previous experiment. The architecture decisions are generally sound — separating the charm, workload, and library was the right call, and the workload sync mechanism (copy at build time, `.gitignore` the copies) is a not-terrible approach.

## What Didn't Go Well

The elephant in the room is that I still had to provide guidance at several points (whereas the hope with the earlier ones was they would be "go build a charm without me"). Claude asked for confirmation on architectural decisions (machine-only vs. K8s, whether to use `juju-info`), which is actually good practice, but also needed correction on tooling (ty config, PyPI publishing). Without the CLAUDE.md guidance, some of the code style issues that I'd previously eliminated came back (`except Exception`, test classes, occasional `from` imports).

The PLAN.md is also interesting as an artefact — you can see Claude 'thinking' through the subordinate relation design, 'changing its mind' several times, and leaving the reasoning trail visible. This is useful as documentation of the decision process, but the final version still contains the earlier (wrong) approaches, which is a bit messy.

## Comparison with Previous Experiments

| Aspect | Mosquitto (Aug 2025) | Beszel (Dec 2025) | SunGather (Dec 2025) | MCP Server (Mar 2026) |
|--------|---------------------|-------------------|---------------------|----------------------|
| Custom CLAUDE.md | Yes | Yes (updated) | Yes (updated) | **No** |
| Skills | No | Yes (unused) | Yes (unused) | **No** |
| Model | Sonnet 4 | Sonnet 4 | Sonnet 4 | **Opus 4.6** |
| Charm type | Machine | K8s | K8s | Machine (subordinate) |
| Tests passing | No | Partially | Mostly | **Yes (134 functions)** |
| COS integration | No | No | No | **Full** |
| Charm library | No | No | No | **Yes (PyPI)** |
| Documentation | Basic | Reasonable | Good | **Diataxis** |
| Integration test | Broken | Partially working | Working | **Working (Jubilant)** |

The progression here is significant. The first experiment with Mosquitto couldn't even run its tests. This one has 134 passing test functions, full observability, a published charm library, and working integration tests — all without the instructions.

Some of this is the model improvement (Opus 4.6 vs. Sonnet 4), some is likely improved training data around Juju and ops (more examples in the training set), and some might just be the nature of this particular charm (luck!). But it strongly suggests that while the CLAUDE.md guidance is still valuable for getting specific things right (avoiding `except Exception`, enforcing import style, ensuring British English), the model is increasingly capable of making ok architectural decisions on its own.

## Thoughts

I'm surprised by how well this went. The charm is closer to production-quality in a way that none of the previous experiments achieved. The architecture is reasonably clean, the testing is much more thorough, the observability is more comprehensive, and the library design is what I'd want to see.

The skills that I spent time building for the SunGather experiment and which were consistently ignored? (I do have more on that in an experiment not fully written up for a few weeks back.) They probably aren't needed any more, at least for the basics. The model knows enough about charming to get the fundamentals right. Where it still needs guidance is on the specific conventions and preferences of a particular team or project — British English, import style, avoiding `except Exception`, and so on. That's what a `CLAUDE.md` should contain: project-specific conventions, not general charm development instructions.

(I did do some recent experimentation with charming using the Canonical inference snaps (particularly `gemma3`) to see how local models would work ... and it was terrible. so something to explore more there).

I'm also interested in the charm library pattern. The `charmlibs` namespace package approach is new, and Claude handled it reasonably well. If we're going to encourage more charms to publish reusable libraries this way, it would be worth making sure there's good documentation and examples available, since Claude did struggle with the packaging setup. I feel like this information *is* all on the `charmlibs` documentation site, and Claude had access to that, but maybe being in the training set is more useful, and it might be too new for that?

## Files of Interest

* [PLAN.md](https://github.com/tonyandrewmeyer/mcp-charm/blob/main/PLAN.md) — The architecture plan, including Claude's visible reasoning about subordinate relations
* [ROADMAP.md](https://github.com/tonyandrewmeyer/mcp-charm/blob/main/ROADMAP.md) — 10-phase development plan (phases 0–9 complete)
* [charm/charmcraft.yaml](https://github.com/tonyandrewmeyer/mcp-charm/blob/main/charm/charmcraft.yaml) — Full relation and config specification
* [charmlib/](https://github.com/tonyandrewmeyer/mcp-charm/tree/main/charmlib) — The reusable charm library
* [demo/](https://github.com/tonyandrewmeyer/mcp-charm/tree/main/demo) — Both demo scenarios (simple + PostgreSQL)
* [docs/](https://github.com/tonyandrewmeyer/mcp-charm/tree/main/docs) — Diataxis documentation
