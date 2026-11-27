# Nine prototype charms for the own-a-charm decision

For the last few months I've been trying to get my team to commit to owning a charm: building it, maintaining it, and carrying the pager for it on our production cloud. Everyone agreed with the principle but nobody agreed on *which* workload, so I was asked to prototype a few and come back with a recommendation.

To make the candidates comparable, I had agents build a real charm for each one. Since I was building nine of them anyway, I also varied the agent harness, the model, and how much supervision each run got. The selection exercise only needed a feel for each workload's shape, but what I ended up with is also a (loosely controlled) experiment in how far different tooling gets with charm authoring. That's what most of this write-up is about.

The team picked HedgeDoc, and the build is now cycle work rather than something in this repository. Charm quality was explicitly not a scoring input (the rubric said so in writing), because I knew the prototypes were built to very different standards and I didn't want that leaking into a decision about workloads. The ranking below had no influence on the pick, which is the main reason I'm comfortable publishing it.

## Goals

* Give each candidate workload a real charm, so the team could poke at something rather than read a paragraph about Pebble layers.
* Deliberately vary the harness and model, and see whether the differences show up in the code.
* Find out what an unattended agent in a VM with a live Juju controller can finish.
* Work out which parts of "is this a good charm?" can be checked automatically and which can't.

## The process

1. I started with fifteen candidates across seven categories, and checked each one for an existing Canonical or community charm. Anything already owned and healthy was dropped.
2. Five filters cut that down to eight: complex enough to be worth doing (so no 12-factor drop-ins), not so complex that it eats the team, plausible production users, no existing owner, and an upstream that won't fight us.
3. For each of the eight, I wrote up a page on the upstream stack, the state of any existing charm, and a realistic estimate of the weekly maintenance.
4. Each survivor got a prototype charm, which is what the rest of this is about. (The ninth, ODK Central, came later. After the shortlisting was done, someone on the team suggested a forms solution, and ODK Central was the one chosen from that category.)
5. The team got a brief with no scores in it, and there were two independent scoring passes (seven axes, ten points each).
6. We had a meeting, and made a decision.

The scores didn't drive the outcome, though. The meeting mostly set both totals aside and argued the pick on dogfooding, which is only one of the seven axes. It landed on the same answer that both score sheets had, so nobody minded, but if the room ends up ignoring the totals and arguing on a single axis, I think the rubric isn't weighting things the way the team does.

## The prototypes

All nine are public in my namespace. Every one has a disclaimer saying that it's AI-generated, unreviewed, and not for production use (and that's true).

| Charm | Built | Harness | Model | Charms | `src` LOC | Unit tests |
|---|---|---|---|---|---|---|
| [mastodon-operator](https://github.com/tonyandrewmeyer/mastodon-operator) | 11 Jun | Claude Code | Fable 5 | 1 (machine) | 1,702 | 51 |
| [sentry-operators](https://github.com/tonyandrewmeyer/sentry-operators) | 14 Jun | Claude Code | Opus 4.8 | 5 + demo app (k8s) | 3,532 | 96 |
| [dependencytracker-operators](https://github.com/tonyandrewmeyer/dependencytracker-operators) | 14 Jun | Claude Code | Opus 4.8 | 2 + a rock (k8s) | 902 | 66 |
| [hedgedoc-operator](https://github.com/tonyandrewmeyer/hedgedoc-operator) | 15 Jun | Claude Code (16 subagents) | Opus 4.8 | 1 (k8s) | 836 | 38 |
| [zammad-operator](https://github.com/tonyandrewmeyer/zammad-operator) | 18 Jun | oh-my-pi | GLM 5.2 (OpenRouter) | 1 (machine) | 1,157 | 29 |
| [windmill-operators](https://github.com/tonyandrewmeyer/windmill-operators) | 20 Jun | opencode | GLM 5.2 (OpenRouter) | 2 (k8s) | 1,239 | 17 |
| [tracecat-operator](https://github.com/tonyandrewmeyer/tracecat-operator) | 23 Jun | oh-my-pi | GLM 5.2 (OpenRouter) | 1, 2 containers (k8s) | 972 | 74 |
| [flagsmith-operators](https://github.com/tonyandrewmeyer/flagsmith-operators) | 23 Jun | oh-my-pi, then Claude Code | Opus 4.8, then Opus 4.7 | 4 (k8s) | 1,486 | 60 |
| [odk-central-operators](https://github.com/tonyandrewmeyer/odk-central-operators) | 26 Aug | Claude Code | Opus 5 | 3 + 2 charm libs (k8s) | 2,535 | 180 |

All of these ran in a disposable Multipass VM with a bootstrapped controller. Mastodon, Sentry, DependencyTrack, and HedgeDoc were interactive, with me steering. The four GLM and oh-my-pi runs and ODK Central were unattended: a long self-contained build prompt, one round of questions at the start, and no checkpoints after that. (Windmill's opencode run also used Haiku 4.5 as its small model for one call, and GLM 5.2 for the other 413.)

Working out the provenance took longer than it should have, because I recorded it in VM names rather than in the repositories. The oh-my-pi session exports have the model in a base64 blob, and the rest came out of the VMs themselves. For example, Tracecat's build ran under oh-my-pi at 09:43 on 23 June, twelve minutes after an opencode session was started and then abandoned one prompt into the build. Its main session is 563 entries and 49.6M tokens over 1h35m, which lines up with the commit span.

## How I evaluated them

I cloned all nine, ran every unit test suite myself, and read the charm code. All nine suites pass, which turns out to tell you very little (more on that below). Beyond that, I looked at the things I'd look at in a review: whether there's a reconciler or a pile of per-event handlers, whether status is computed in `collect-status` or set imperatively, whether relation removal is handled at all, whether `StoredState` and `defer()` show up, which versions of the charm libraries were used, and whether the tests test the charm or a stub of it.

## The ranking

This is my order, best-built first. I'm ranking how well each charm is built, not how impressive the workload is.

### 1. ODK Central (Opus 5, Claude Code)

Three charms, plus two charm libraries that the agent wrote itself to tie them together, because Juju has no shared volume between applications and upstream's one-shot secrets container has no charm equivalent. There's backup and restore to S3, secret rotation that's visible across a relation, migration gating, and 180 unit tests behind a 95% coverage gate. It's the only prototype where the agent hit a real architectural mismatch with upstream and designed around it rather than forcing its way through. The one thing I'd push back on is status: there are 21 imperative `self.unit.status = ...` assignments across the charms and no `collect-status` handler anywhere, even though that's the currently recommended approach and most of the other prototypes used it.

### 2. Sentry (Opus 4.8, Claude Code)

By far the hardest workload (Kafka, ClickHouse, Snuba, Relay, a taskbroker, and five stateful backends), and it got the furthest, I think because it had a live model and kept deploying into it. Five charms, `collect_unit_status` in all of them, no imperative status assignments, a hand-written `sentry_dsn` charm library, and a demo application charm built specifically to show that the library works end to end. It processed a real Sentry event on a live stack, which is a much higher bar than passing tests.

### 3. Mastodon (Fable 5, Claude Code)

The best single charm in the set, and the most up to date: `tls-certificates` v4, `charmlibs` packages rather than the deprecated Charmhub `operator_libs_linux`, an `ops` floor of 3.8.1, no `defer()`, no `StoredState`, and a reconciler that every event goes through. A machine charm that builds Ruby with rbenv and manages five long-lived secrets as Juju secrets is not a small ask, and it reads as though it was written by someone who knows the framework.

### 4. Flagsmith (Opus 4.8 via oh-my-pi, finished with Claude Code on Opus 4.7)

Four charms, one workload each, `collect_unit_status` throughout, and `tls-certificates` v4. It's here rather than higher because of what happened when it was deployed, which was the most useful part of the whole exercise and has its own section below.

### 5. HedgeDoc (Opus 4.8, Claude Code, 16 subagents)

The overall shape is right, but a lot of the detail is wrong. The reconciler pattern, the split into pure logic, the `collect-status` handler, and a 240-line config surface that maps every option to its upstream variable are all correct, and would all be expensive to redo. However:

* Removing the database relation silently drops the charm back to an empty SQLite file and reports `active`.
* The user-management actions exec without `service_context`, so they talk to a different database than the service does.
* The single-unit guard sets blocked status, but every unit still starts.
* About a third of the charm tests monkeypatch the method they're named for.

I reviewed this one the most carefully, because it's the one the team picked.

### 6. DependencyTrack (Opus 4.8, Claude Code)

Small and competent. Two charms plus a rock for the frontend, a sensible split, and 66 tests. There's nothing wrong with it, although there's nothing especially ambitious in it either.

### 7. Windmill (GLM 5.2 via opencode)

The thinnest of the nine: 17 unit tests across two charms, five distinct relations across the pair, no `collect-status`, and one outright bug (`windmill-worker` sets `ops.ErrorStatus` when a Pebble layer update fails, which Juju won't accept from a charm). It was validated against a live model, which is more than some of the others managed, and the rest of the code is fine. There's just not much of it.

### 8. Tracecat (GLM 5.2 via oh-my-pi)

The largest single `charm.py` in the set at 899 lines, with nine day-2 actions, six secret labels, and 74 unit tests. All of those tests use `Harness`, which is deprecated, while seven of the other eight prototypes used Scenario. It also uses `tls-certificates` v3, has no `collect-status` handler, and doesn't observe any `relation-broken` or `relation-departed` events, so removing the PostgreSQL, Redis, Temporal, or S3 relation leaves the workload running with credentials it no longer has. It's a lot of code, but in an old style.

### 9. Zammad (GLM 5.2 via oh-my-pi)

`StoredState` holding the PostgreSQL password and the Redis URL in plain text, an `ops` floor of 2.10, `tls-certificates` v3, no `collect-status`, and status set imperatively in fourteen places across per-event handlers. This is roughly how you'd have written a charm in 2022, and it's the only prototype with `StoredState` in it at all.

## Harness or model?

I didn't plan it, but two of these runs make a reasonable controlled pair. Zammad and Flagsmith were both built with oh-my-pi, in the same kind of disposable VM, through OpenRouter, five days apart. The only meaningful difference is the model: `z-ai/glm-5.2` for Zammad and `anthropic/claude-opus-4.8` for Flagsmith.

| | Zammad (GLM 5.2) | Flagsmith (Opus 4.8) |
|---|---|---|
| Status | imperative, 14 sites | `collect_unit_status`, all four charms |
| `StoredState` | yes, holding credentials | none |
| `tls-certificates` | v3 | v4 |
| Test framework | `Harness` | Scenario |
| `ops` floor | 2.10 | ~3.7 |

The same harness, in the same week, run by the same person, and they're at opposite ends of everything I was looking at.

The set also happens to have the reverse comparison. All three GLM runs are the same model (5.2, through OpenRouter) across two different harnesses: Windmill under opencode, and Zammad and Tracecat under oh-my-pi. They all end up in the same place: no `collect-status` anywhere, imperative status throughout, `tls-certificates` v3 in the two that use it, and `Harness` rather than Scenario in the two that have enough tests to tell. So with the harness fixed, changing the model changed everything, and with the model fixed, changing the harness didn't make any difference that I can see in the code.

I think the harness barely matters for the shape of the charm you get, and the model matters a lot - specifically, how recent its idea of "how you write a charm" is. Charm idioms have changed a lot since 2022, and a model that learnt the old way will confidently produce plenty of clean, well-organised, well-tested code that uses the wrong patterns.

That's a somewhat uncomfortable conclusion for a team that writes documentation for a living, since it means the thing that most determines charm quality is largely out of our control. On the other hand, it also means llms.txt and good docs are probably worth more than they look, since that's the lever we do have (and the [llms.txt experiment](../2026-03-26-llms-txt-docs-experiment/) found the gains were biggest where training data is thinnest).

## Passing unit tests don't mean much

All nine unit test suites pass (I ran them).

Flagsmith's four suites were passing when the agent ran out of budget, but three of its four workloads were broken when deployed:

* `flagsmith-frontend` used a hard-coded `working-dir: /app` when the upstream image's WORKDIR is `/srv/bt`, so Pebble failed with `fork/exec /usr/bin/node: no such file or directory`.
* `flagsmith-task-processor` crash-looped because the Pebble HTTP probes hit `localhost` and Django returned 400 `DisallowedHost`, with no `DJANGO_ALLOWED_HOSTS` set.
* `flagsmith-edge-proxy` blocked because `ALLOW_ORIGINS=*` isn't valid for a setting that upstream parses as a JSON list.

None of these could be caught by a unit test, even in principle, since they're all facts about someone else's container image. The oh-my-pi run spent roughly US$200 and several hours of live debugging without finding any of them. It stayed focused on the charm-side error (`relation-changed` failing) and never looked at the workload container's logs, where all three errors were in plain text. Finishing it off with Claude Code took a single turn: read the last few messages, pull the unit's logs once, find three distinct error lines, make three fixes, repack, refresh, and all the units were active.

I don't think the takeaway is that Claude is faster. oh-my-pi did most of the work and was on the right track. The problem is that the last 5% of a charm is in the workload container, the charm-side error looks nothing like the cause, and an agent that gets stuck is likely to get stuck there. If I were writing the build prompt again, the one instruction I'd add is: when a unit errors, read the workload container's log before you read the charm's.

HedgeDoc has a similar story. Its biggest bespoke piece is a 154-line Node Prometheus exporter that gets pushed into the container at reconcile time and run as a second Pebble service with its own health check, with a Grafana dashboard and two alert rules built on top of it. The premise ("HedgeDoc 1.x does not expose Prometheus metrics natively") is wrong. Upstream has exposed `hedgedoc_notes`, `hedgedoc_online_users`, and others on the main port for years, behind the same flag that the charm already forces on. The exporter is careful, well-written code that degrades properly when the endpoint is unavailable, but it shouldn't exist. The integration test checks the exporter's own metric names, so it confirms that the workaround works rather than whether it's needed, and nothing in a test suite was ever going to flag that.

## Does workload difficulty explain any of it?

Less than I expected. I assumed the hard workloads would produce worse charms, but it went the other way: Sentry is the most complicated workload here and is second on the list, while Windmill (two stateless services and a Postgres queue, which is about as easy as this set gets) is second to last. Zammad and Mastodon are very similar in shape (a Rails app, background workers, Postgres, Redis, and Elasticsearch, on a machine) and are at opposite ends of the ranking.

What difficulty did change is how much live iteration happened. The heavy k8s workloads forced the agent to keep deploying, because nothing about a Kafka-plus-ClickHouse stack comes up first time, and each deploy cycle turned up a class of bug that unit tests can't reach. The easy workloads came up quickly, looked fine, and the agent stopped there. I don't think difficulty made the agents better directly, but it made them iterate, and the iteration helped.

## Caveats

* Nine data points, and the variables aren't cleanly crossed. Only the Zammad/Flagsmith pair (for the model) and the three GLM runs (for the harness) isolate one thing each.
* Outside those, the workload, harness, model, level of supervision, and my own attention are all confounded. The Claude Code runs got more of my time, and that probably counts for something.
* I did the ranking myself, after the decision, knowing which model built what. I did the measurements first and the ranking second, but it wasn't blind.
* All of this is from June to August 2026. Models change, and the specific ordering won't hold.

## What I'd do differently

I'd record the harness and model in the repository at build time, in a file, rather than in a VM name. I did get all nine in the end, but only by decoding session exports and booting VMs months later, and I shouldn't have had to do that to answer "what built this?".

I'd also make the build prompt end with a deploy, an integration test that writes some data, and a `juju refresh` that checks the data is still there. Every prototype here has a test suite, but only the ones that were pushed to deploy have any evidence that the charm works.
