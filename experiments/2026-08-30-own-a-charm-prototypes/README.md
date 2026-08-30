# Nine charms, one decision, and what the agents actually built

For the last few months I've been trying to get my team to commit to owning a charm: building it, maintaining it, and carrying the pager for it on our production cloud. Everyone agreed with the principle and nobody agreed on *which* workload, so I was asked to prototype a few and come back with a concrete recommendation.

That's the framing, and the framing is the least interesting part of this. To make the candidates comparable I had agents build a real charm for each one, and because I was building nine of them anyway I varied the agent harness, the model, and how much supervision each run got. The selection exercise wanted a feel for each workload's shape; what I actually ended up with was a natural experiment in how far different tooling gets at charm authoring, with the workload as the variable I couldn't control.

The decision, for completeness: the team picked HedgeDoc, and the build is now cycle work rather than something in this repository. Charm quality was explicitly **not** a scoring input - the rubric said so in writing, precisely because I knew the prototypes were built to wildly different standards and I didn't want that leaking into a decision about workloads. So the ranking below had no influence on the pick, which is the only reason I'm comfortable publishing it.

## Goals

* Give each candidate workload a real charm, so the team could poke at something rather than read a paragraph about Pebble layers.
* Vary harness and model deliberately, and see whether the differences show up in the code.
* Find out what an unattended agent in a VM with a live Juju controller can actually finish.
* Work out which parts of "is this a good charm?" survive automated checking and which don't.

## The process

1. **Category recon.** Fifteen candidates across seven categories, each checked for an existing Canonical or community charm. Anything already owned and healthy was dropped.
2. **Filter pass.** Five filters: complex enough to be worth doing (so no 12-factor drop-ins), not so complex it eats the team, plausible production users, no existing owner, and an upstream that won't fight us. Eight survived.
3. **Desk recon per survivor.** A page each on the upstream stack, the state of any existing charm, and an honest weekly-maintenance estimate.
4. **A prototype per survivor.** This is the part this write-up is about.
5. **A score-free brief to the team, plus two independent scoring passes.** Seven axes, ten points each.
6. **A meeting, and a decision.**

Worth recording, because it's the sort of thing these write-ups usually leave out: the scores didn't drive the outcome. The meeting largely set both totals aside and argued the pick on dogfooding, which is one axis of seven. It happened to land on the same answer both sheets did, so nobody minded, but an axis the room overrides is an axis the rubric isn't capturing.

## The prototypes

All nine are public in my namespace. Every one carries a disclaimer saying it's AI-generated, unreviewed, and not for production, and I mean it.

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

Every one of these ran in a disposable multipass VM with a bootstrapped controller. Mastodon, Sentry, DependencyTrack and HedgeDoc were interactive, with me steering. The four GLM and oh-my-pi runs and ODK Central were unattended: a long self-contained build prompt, one round of questions at the start, and no checkpoints after that. (Windmill's opencode run also used Haiku 4.5 as its small model for one call, and GLM 5.2 for the other 413.)

Provenance took longer to reconstruct than it should have, because I recorded it in VM names rather than in the repositories. The oh-my-pi session exports turned out to carry the model in a base64 blob, and the rest came out of the VMs themselves: Tracecat's build ran under oh-my-pi at 09:43 on 23 June after an opencode session was started and abandoned twelve minutes earlier, one prompt into the build. Its main session is 563 entries and 49.6M tokens over 1h35m, which lines up exactly with the commit span.

## How I evaluated them

I cloned all nine, ran every unit suite myself, and read the charm code. All nine suites pass, which turns out to be the least informative thing in this write-up (see below). Beyond that I looked at the things I'd look at in a review: whether there's a reconciler or a pile of per-event handlers, whether status is computed in `collect-status` or assigned imperatively, whether relation removal is handled at all, whether `StoredState` and `defer()` show up, which versions of the charm libraries were reached for, and whether the tests test the charm or a stub of it.

## The ranking

My honest order, best-built first. I'm ranking construction quality, not how impressive the workload is.

**1. ODK Central (Opus 5, Claude Code).** Three charms plus two charm libraries the agent wrote itself to bind them together, because Juju has no shared volume between applications and upstream's one-shot secrets container has no charm equivalent. Backup and restore to S3, secret rotation made visible across a relation, migration gating, and 180 unit tests behind a 95% coverage gate. It's the only prototype where the agent hit a genuine architectural mismatch with upstream and designed around it rather than through it. The one thing I'd push back on is status: 21 imperative `self.unit.status = ...` assignments across the group and no `collect-status` handler anywhere, which is the current recommended shape and is what most of the other prototypes did.

**2. Sentry (Opus 4.8, Claude Code).** The hardest workload by a distance - Kafka, ClickHouse, Snuba, Relay, a taskbroker, and five stateful backends - and it got the furthest, because it had a live model and kept deploying into it. Five charms, `collect_unit_status` in all of them, zero imperative status assignments, a hand-written `sentry_dsn` charm library, and a demo application charm built specifically to prove that library works end to end. It processed a real Sentry event on a live stack. That's a much higher bar than "the tests pass".

**3. Mastodon (Fable 5, Claude Code).** The best single charm in the set, and the most current: `tls-certificates` v4, `charmlibs` packages rather than the deprecated Charmhub `operator_libs_linux`, an `ops` floor of 3.8.1, no `defer()`, no `StoredState`, and a reconciler funnelling every event. A machine charm that builds Ruby via rbenv and manages five long-lived secrets as Juju secrets is not a small ask, and it read as though someone who knew the framework wrote it.

**4. Flagsmith (Opus 4.8 via oh-my-pi, finished with Claude Code on Opus 4.7).** Four charms, one workload each, `collect_unit_status` throughout, `tls-certificates` v4. It's here rather than higher because of what happened when it was deployed, which is the most useful thing in this whole experiment and gets its own section.

**5. HedgeDoc (Opus 4.8, Claude Code, 16 subagents).** Right shape, wrong body. The reconciler pattern, the pure-logic split, the `collect-status` handler and a 240-line config surface mapping every option to its upstream variable are all correct and all expensive to redo. But removing the database relation silently drops the charm back to an empty SQLite file and reports `active`, the user-management actions exec without `service_context` so they talk to a different database than the service does, the single-unit guard blocks in status while every unit still starts, and about a third of the charm tests monkeypatch the method they're named for. It's the one I reviewed hardest, because it's the one the team picked.

**6. DependencyTrack (Opus 4.8, Claude Code).** Competent and small. Two charms plus a rock for the frontend, sensible decomposition, 66 tests. Nothing wrong with it and nothing especially ambitious in it.

**7. Windmill (GLM 5.2 via opencode).** The thinnest of the nine: 17 unit tests across two charms, five distinct relations across the pair, no `collect-status`, and one outright bug - `windmill-worker` sets `ops.ErrorStatus` when a Pebble layer update fails, which Juju will not accept from a charm. It was live-validated against a model, which is more than some managed, and the code is otherwise unobjectionable. There just isn't much of it.

**8. Tracecat (GLM 5.2 via oh-my-pi).** The largest single `charm.py` in the set at 899 lines, nine day-2 actions, six secret labels, and 74 unit tests - all of them written against `Harness`, which is deprecated, while seven of the other eight prototypes used Scenario. It also reached for `tls-certificates` v3, has no `collect-status` handler, and observes no `relation-broken` or `relation-departed` events at all, so removing the PostgreSQL, Redis, Temporal or S3 relation leaves the workload running against credentials it no longer has. Lots of code, dated shape.

**9. Zammad (GLM 5.2 via oh-my-pi).** `StoredState` holding the PostgreSQL password and the Redis URL in plaintext, an `ops` floor of 2.10, `tls-certificates` v3, no `collect-status`, and status assigned imperatively in fourteen places across per-event handlers. This is roughly how you'd have written a charm in 2022, and it's the only prototype in the set with `StoredState` in it at all.

## The comparison that actually isolates the model

Two of these runs are a proper controlled pair, which I didn't plan and am pleased about. Zammad and Flagsmith were both built by oh-my-pi, in the same shape of disposable VM, through OpenRouter, five days apart. The only meaningful difference is the model: `z-ai/glm-5.2` for Zammad, `anthropic/claude-opus-4.8` for Flagsmith.

| | Zammad (GLM 5.2) | Flagsmith (Opus 4.8) |
|---|---|---|
| Status | imperative, 14 sites | `collect_unit_status`, all four charms |
| `StoredState` | yes, holding credentials | none |
| `tls-certificates` | v3 | v4 |
| Test framework | `Harness` | Scenario |
| `ops` floor | 2.10 | ~3.7 |

Same harness, same week, same operator, opposite ends of every axis I care about.

The set happens to contain the other half of that experiment too. All three GLM runs are the same model (5.2, through OpenRouter) across two different harnesses - Windmill under opencode, Zammad and Tracecat under oh-my-pi - and they land in the same place as each other: no `collect-status` anywhere, imperative status throughout, `tls-certificates` v3 in the two that use it, `Harness` rather than Scenario in the two that have enough tests to tell. Holding the harness fixed and changing the model moves everything; holding the model fixed and changing the harness moves nothing I can see in the code.

My read is that the harness barely matters for the shape of the charm you get, and the model matters enormously - specifically, how recent its sense of "how you write a charm" is. Charm idiom has moved a long way since 2022, and a model that learnt the old shape confidently produces a great deal of clean, well-organised, well-tested code in the wrong pattern.

That is a somewhat uncomfortable conclusion for a team that writes documentation for a living, because it means the thing determining charm quality is largely outside our control. Although it also means llms.txt and good docs are worth more than they look, since that's the lever we do have (and the [llms.txt experiment](../2026-03-26-llms-txt-docs-experiment/) found the gains were biggest exactly where training data is thinnest).

## Green tests tell you almost nothing

All nine unit suites pass. I ran them.

Flagsmith's four suites were green when the agent ran out of budget, and three of its four workloads were broken on a live deploy:

* `flagsmith-frontend` used a hard-coded `working-dir: /app` when the upstream image's WORKDIR is `/srv/bt`, so Pebble failed with `fork/exec /usr/bin/node: no such file or directory`.
* `flagsmith-task-processor` crash-looped because the Pebble HTTP probes hit `localhost` and Django returned 400 `DisallowedHost`, with no `DJANGO_ALLOWED_HOSTS` set.
* `flagsmith-edge-proxy` blocked because `ALLOW_ORIGINS=*` isn't valid for a setting upstream parses as a JSON list.

None of the three is catchable by a unit test, in principle rather than by omission. All three are facts about someone else's container image. The oh-my-pi run spent roughly $200 and several hours of live debugging without finding any of them, because it stayed in the charm-side error (`relation-changed` failing) and never sampled the workload container's logs, where all three errors were sitting in plain text. Finishing it off from Claude Code took a single turn: read the last messages, pull the unit's logs once, three distinct error lines, three fixes, repack, refresh, all units active.

The lesson isn't "Claude is faster". oh-my-pi did the bulk of the work and was on the right track. It's that the last 5% of a charm lives in the workload container, the charm-side error message looks nothing like the cause, and an agent that plateaus will plateau there. If I were writing the build prompt again, the one instruction I'd add is: when a unit errors, read the workload container's log before you read the charm's.

The same point in a different shape: HedgeDoc's most substantial bespoke artefact is a 154-line Node Prometheus exporter, pushed into the container at reconcile time, run as a second Pebble service with its own health check, with a Grafana dashboard and two alert rules built on top of it. Its premise - "HedgeDoc 1.x does not expose Prometheus metrics natively" - is wrong. Upstream has exposed `hedgedoc_notes`, `hedgedoc_online_users` and friends on the main port for years, behind the same flag the charm already forces on. The exporter is careful, well-written code that degrades properly when the endpoint is unavailable, and it should never have existed. The integration test asserts the exporter's own metric names, so it confirms the workaround works rather than asking whether it's needed.

Agents will write you an excellent solution to a problem you don't have, and nothing in a test suite is going to tell you.

## Does workload difficulty explain any of it?

Less than I expected. My prior was that the hard workloads would produce the worse charms, and it went the other way: Sentry is the most complicated thing here and is second on the list, while Windmill (two stateless services and a Postgres queue, which is about as easy as this set gets) is second to last. Zammad and Mastodon are near-identical in shape - a Rails app, background workers, Postgres, Redis, Elasticsearch, on a machine - and sit at opposite ends of the ranking.

What difficulty did change is how much *live* iteration happened. The heavy k8s workloads forced the agent to keep deploying, because nothing about a Kafka-plus-ClickHouse stack comes up first try, and every deploy cycle bought a class of bug that unit tests structurally cannot reach. The easy workloads came up quickly, looked fine, and stopped. Difficulty didn't make the agent better; it made it iterate, and iteration made it better.

## Caveats

* Nine data points, and the variables aren't cleanly crossed. Only the Zammad/Flagsmith pair isolates one thing.
* Workload, harness, model, supervision level and my own attention are all confounded outside that pair. The Claude Code runs got more of my time, and that will be worth something.
* I built the ranking myself, after the decision, knowing which model built what. I did the measurements first and the ranking second, but I can't claim I was blind.
* All of this is June to August 2026. Model versions move; the specific ordering will not hold.

## What I'd do differently

Record the harness and model in the repository at build time, in a file, not in a VM name. I got all nine in the end, but only by decoding session exports and booting VMs months later, and that is not a thing I should have had to do to answer "what built this?".

And make the build prompt end with a deploy, an integration test that writes something, and a `juju refresh` that checks the something is still there. Every prototype here has a test suite. Only the ones that were made to deploy have any evidence that the charm works.
