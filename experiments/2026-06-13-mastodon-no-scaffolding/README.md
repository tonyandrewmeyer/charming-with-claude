# Experiment: A Mastodon charm with no scaffolding at all

**Date:** 2026-06-13
**Agent:** Claude Code, Claude Fable 5
**Result:** [tonyandrewmeyer/mastodon-operator](https://github.com/tonyandrewmeyer/mastodon-operator)
**Build transcripts:** [docs/transcripts](https://github.com/tonyandrewmeyer/mastodon-operator/tree/main/docs/transcripts) in that repo

It's been ten months since the [mosquitto experiment](../2025-08-01-mosquitto-operator/README.md), and quite a lot has happened in between: Fable (arriving and, at time of writing, leaving...), Opus 4.x, Sonnet 4.x, Haiku 4.5, skills, MCP, content negotiation for docs, [`pytest-jubilant`](https://pypi.org/project/pytest-jubilant/) 2.0, [charmlibs](https://github.com/canonical/charmlibs), and (somewhat ironically) a lot of writing here in `charming-with-claude` about how to *help* the agent do this kind of work.

I also spent a lot of time playing with building [cantrip](https://tonyandrewmeyer.github.io/cantrip), a day on ["-craft"](https://github.com/canonical/-craft) insanity, and a chunk of time over the last few weeks looking into getting Pi/Opencode able to write and improve a charm with only models that I can run locally. More on the latter later.

I wanted to set all of that aside for one experiment and ask a much narrower question: with none of the help we've been building -- no `CLAUDE.md`, no skills, no `.claude/commands`, no curated MCP servers, no llms.txt-aware doc server (llms.txt is coming to Ops, Jubilant, and most of the Canonical docs any day now), no priming, and only minimal nudging after the initial build -- how far can a recent agent actually get on its own, from a one-line prompt, with a small number of follow-ups that a non-expert user might plausibly write?

The aim isn't really to compare Fable to Sonnet 4 from August: that comparison is unfair in several directions (different workload, different sandbox, different host OS, different mood). The aim is to set a baseline for "what does the floor look like now". When someone who has never written a charm sits down with Claude Code and types "build me a Mastodon charm", what do they get?

## Setup

The whole experiment ran in a throwaway sandbox VM with network access and `sudo`, and nothing else: no `charmcraft`, no `juju`, no `lxd`, no `concierge`, no Python deps, no vendored libs. I gave the agent:

* A one-sentence task in the first turn.
* Nothing in `~/.claude/`, no project `CLAUDE.md`, no skills.
* Permission to run anything it wanted in the VM (it's disposable).
* A handful of follow-up prompts over the session.

That's it. No instructions on how to structure a charm, no link to Ops docs, no warning that `charmcraft pack` is slow, no "use Jubilant for integration tests", no "use `charmlibs`", no "don't catch `Exception`". I was deliberately curious about what would emerge unprompted.

I counted the human turns afterwards: 19, give or take, depending on whether you count "logged in" and "fix the issues" as separate prompts. The full unedited transcript is in the result repo. The actual prompts are roughly:

1. Build a Mastodon charm. (initial)
2. Same again (I cancelled the first one in under a minute — probably it shouldn't count), but mentioning the sandbox VM.
3. Fix the issues.
4. Are there integration tests? Observability integrations?
5. Yes, add `cos-agent`.
6. Use the `uv` plugin rather than `charm`.
7. Yes, add TLS.
8. A charm should encapsulate best practice for day-2 ops -- please research Mastodon's operator practices and make sure the charm does this.
9. Should `nginx`/`web`/`sidekiq`/`streaming` really all be one charm, or split into a collection? Would that be more "Juju"?
10. Yes, implement the role option.
11. Add an honest experimental/alpha warning to the README, and export the build transcripts somewhere readable on GitHub.
12. Push it to `github.com/tonyandrewmeyer/mastodon-operator`, configure the repo appropriately. (And I logged in to `gh`.)
13. Yes, update copyright headers.
14. Add a Dependabot config (non-security updates).
15. Set a 7-day cooldown on it.
16. Update `CONTRIBUTING.md` for the uv/tox-uv workflow.
17. Switch CI to use `concierge`.
18. Re-export the transcripts to pick up the extra work.

Most of those are one-liners. There's nothing in there about architecture, code style, testing approach, or any of the things we'd normally script into a `CLAUDE.md`. The agent did all of that itself, or didn't.

## What it built

A working machine charm for Mastodon v4.5.11 on Ubuntu 24.04, packed for amd64 and arm64. It:

* Installs Ruby (via `rbenv`, with jemalloc, matching the release's `.ruby-version`), Node.js 24 from Nodesource, and the various system packages Mastodon needs.
* Fetches the official Mastodon release tarball, builds it on the unit, and manages the long-lived secrets (`SECRET_KEY_BASE`, `OTP_SECRET`, VAPID, Active Record encryption keys) as a shared Juju app secret.
* Runs Puma (port 3000), Sidekiq, and the Node streaming API (port 4000) as `systemd` services, with `nginx` in front terminating TLS and serving static assets.
* Integrates with `postgresql` (required), optionally with an external Redis provider, an `s3`-compatible object store, Elasticsearch for full-text search, an `smtp` integrator, and a `tls-certificates` v4 provider. Without the optional integrations it runs a colocated `redis-server` and stores media on a Juju storage volume.
* Provides `cos-agent` for COS observability, with bundled alert rules and Mastodon's native Prometheus exporters wired up.
* Supports asymmetric scale-out via a `role` config and a peer-ish `primary`/`cluster` relation, so you can deploy extra applications running `sidekiq`-only or `streaming`-only that follow the primary's version and config.
* Coordinates upgrades following Mastodon's documented procedure (pre-deployment migrations against the old code, symlink swap, restart, post-deployment migrations once every aux unit has caught up).
* Has a daily systemd timer that prunes cached remote media per Mastodon's storage optimisation guidance, plus `tootctl`, `create-admin`, and `media-cleanup` actions.

It deployed cleanly on local LXD against the real `postgresql` charm, came up `active`, and a second `role=sidekiq` application joined and reached `active` too. I did not run it federating, I did not push real traffic at it, and I have not security-reviewed any of the code. The README in the result repo is appropriately loud about this.

By the numbers: `src/charm.py` is 743 lines, `src/mastodon.py` is 959 lines, `charmcraft.yaml` is 278 lines, and there are around 900 lines of unit tests plus a thin integration suite. CI is `tox -e lint`, `tox -e unit`, a `uv.lock` sync check, packing through `concierge`, and Zizmor on the workflows.

## What was good

* **It just worked.** That's the headline. The mosquitto experiment in August produced something that didn't deploy, and I noted then that "I would rather start from scratch than start from this". This time the charm deployed, integrated with `postgresql`, came up active, and -- crucially -- did so as part of the same session, with the agent watching the unit status and fixing the things that broke. The "agent" part of "agentic" is doing real work here in a way it visibly wasn't ten months ago.
* **Unprompted use of Ops correctly.** No `Harness`, no `ops.main(MyCharm)` with positional args, no obviously dated patterns. It used Scenario for unit tests, including `Context`/`State` properly, without being told to. This is a real change: in August, Scenario v7 was almost invisible to the agent.
* **Unprompted use of `jubilant` for integration tests.** Again, without being told. The mosquitto attempts produced fake-async imaginings of Jubilant; this attempt produced something that actually looks like Jubilant code, including `pytest-jubilant` fixtures. I expect the work that's gone into Jubilant docs and the charmcraft profiles is what makes the difference here.
* **Unprompted use of charm libs.** It vendored `data_platform_libs`, `operator_libs_linux` (unfortunately not the newer charmlibs versions), `tls_certificates_interface` v4, `cos_agent`, and `smtp_integrator` directly from the canonical repos, and used them more-or-less correctly. The mosquitto run had to be told about `operator-libs-linux` and then ignored the instruction.
* **Sensible architectural questions.** When I asked "should this really be one charm?", the agent gave a 'thoughtful' answer about Mastodon's components scaling at different rates, sketched what splitting would look like, then proposed and implemented the asymmetric `role` option as a middle path. That feels more like a conversation with a colleague than with a stochastic parrot.
* **Day-2 operations.** The "please research Mastodon's operator practices" prompt produced material gains: pre/post-deployment migration ordering, media pruning timers, append-only Redis, the `tootctl` action, a backup-and-restore section in the README that names exactly which secrets are load-bearing. Some of that came from real Mastodon docs; I'm sure some of it came from the training set. Either way, it's substantially more grown-up than the mosquitto output.
* **Decent docs.** The README is long but readable, the `CONTRIBUTING.md` describes the actual workflow (rather than a fantasy one), there's a `SECURITY.md`, and the `transcripts/` directory has both a single Markdown file and an HTML export with a working index. It even worked around GitHub-renders-HTML-as-source by pointing at `htmlpreview.github.io`.
* **Self-correcting on real signal.** During the deploy, the first attempt hit `hook failed: "storage-attached"` and then `hook failed: "install"`. The agent watched the logs, found the actual problem, and fixed it -- this is the kind of loop the mosquitto run couldn't really close because `charmcraft pack` and the integration tests were both too slow for the model's 'patience' at the time. Faster packing and the `uv` plugin help, but I think the bigger change is that the agent is willing to wait, and uses `Monitor` to react to unit-status transitions rather than polling.
* **It pushed the result and configured the repo.** Dependabot, cooldowns, copyright headers, transcripts, an honest warning in the README. Bookkeeping that I'd usually do at the end and grumble about.

## What was bad, or at least worth flagging

* **Charm size and surface area.** Two files, 1,700 lines of Python, 278 lines of `charmcraft.yaml`, six integrations, one storage volume, roles, asymmetric upgrades, COS, TLS via three different mechanisms, daily timers. This is large for a charm built in a single sitting from one prompt. Some of that is Mastodon being genuinely complex, but some of it is the agent's tendency to want to do everything. A human starting from scratch would possibly have stopped after "Puma + Sidekiq + Postgres" and shipped that first.
* **One charm doing everything.** I asked about splitting it; the agent considered it and then talked us both out of it. That's *probably* the right call given the deep coupling between Mastodon's components and the shared release tree on disk (I use Mastodon but have never hosted it, so don't know for sure), but it's also a charm doing four daemons in one unit, which is the thing we usually try to avoid. I'd want to revisit this if it were going anywhere real.
* **Integration tests are still thin.** 101 lines for one test file. They check the happy path -- deploy, relate, get to active -- and not much else. That's better than the mosquitto runs (which were imagined), but it's not the red/green approach we'd want for something this load-bearing. The agent didn't write integration tests first, and I didn't ask for it to.
* **Vendored libs vs `charm-libs:`.** It pulled libs by `curl`ing them from `main`, instead of declaring `charm-libs:` and using `charmcraft fetch-libs`. The result works, but it pins to `main` at the moment of build, and it doesn't track lib versions the way `charmcraft fetch-libs` does. It's interesting given that charm libs in this form are on the way out.
* **No `pytest-jubilant` for the integration suite either.** It used `jubilant` directly. Again, fine, but the wrapper exists and is what I'd reach for first.
* **The "role" option is clever but bespoke.** It invented a `primary`/`cluster` relation pair to share config and version between applications. That's a reasonable shape, but it's not a documented Juju pattern that I know of -- closer to a peer relation across applications. I'd want a charmer to look hard at this before depending on it.
* **Lots of low-confidence detail in the README.** The `extra-env` table, the `MASTODON_PROMETHEUS_EXPORTER_WEB_DETAILED_METRICS=true` advice, the `ES_USER`/`ES_PASS`/`ES_CA_FILE` notes -- I have no way of being sure those are right without running them, and I haven't.
* **No formal review of the code.** I read enough to write this up and to be happy that the shape is right, but I didn't do a line-by-line review. The README warning in the result repo reflects that honestly.

## Other observations

* **The number of prompts is the point.** Nineteen-ish messages, almost all of them under 20 words. No template, no examples, no skills, no scaffolding. The cumulative time I spent typing was well under ten minutes. That's a very different mode to where we are when we're carefully crafting `CLAUDE.md` files, and it's worth holding both shapes in mind.
* **The agent volunteered structure I would have asked for.** A `pyproject.toml`, a `tox.ini`, `ruff` + `pyright`, a `uv.lock`, a `CONTRIBUTING.md`, GitHub Actions CI, `concierge.yaml`, Zizmor, copyright headers. These are the things our `claude-instructions/CLAUDE.md` says to do; they emerged partly unprompted. Some of that is probably training data catching up, some is definitely `charmcraft init`, and some is probably the model being more confident about scaffolding conventions in general.
* **Skill-shaped behaviour without skills.** It used `claude-transcript` and `claude-code-transcripts` to export the session, sensibly (I did point it there). It used `concierge prepare -p dev` when asked. It used `Monitor` to watch unit status. These are all things that *could* be a skill, and the agent is increasingly capable of figuring them out on its own when the task makes it obvious which tool fits.
* **Where help still wins.** I am unsure if this means that `CLAUDE.md` and skills don't matter. The llms.txt experiment showed that inference-time docs add ~7pp to a different evaluation; instructions still bring down cost meaningfully; skills still encode hard-won shape. But a lot of what we used to write into `CLAUDE.md` is becoming default behaviour. The marginal value of a `CLAUDE.md` line that says "always use Jubilant for integration tests" is much lower in June 2026 than it was in August 2025.
* **`Monitor` and background tasks changed the feel.** A lot of the build transcript is the agent watching a long task in the background while doing something else. The "agent gives up because `charmcraft pack` is slow" failure mode from the mosquitto experiment has effectively been engineered away.
* **It thinks about itself.** When I asked for the README disclaimer, it wrote one that's more honest than I would have expected -- "has not had a security review, and is not maintained or endorsed by anyone. Treat it as a reference/prototype". This is good. Less impressively, the changelog still has that I-am-pitching-to-a-VP tone in places.

## So how far have things actually come?

Quite a long way, mainly in the agent's *behaviour* rather than in any individual capability:

* It will wait for slow things now.
* It will react to real signal (failing hooks, unit-status transitions) and not just to its own predictions.
* It will pick the modern tool unprompted more often than not.
* It will hold a multi-step plan across an hour and a half of real work.
* It will ask reasonable architectural questions when given the opening, and answer reasonable architectural questions when asked.

What hasn't changed: it still over-builds, it still writes thinner tests than it should, it still wants to write code more than it wants to read it, and it still produces some prose that reads like it's trying too hard. But the gap between "what you get with no scaffolding" and "what you get with our best scaffolding" has narrowed considerably, and the floor has risen.

Some of this is that the harness is better and the model is better. Some will definitely be a combination of improved documentation on our side and the training window capturing more of that. I think a lot is better scaffolding from `charmcraft init`, even though I didn't do that for the agent, or even mention it, just getting the latest version does a lot.

For the question I actually care about -- can someone new to charming get a usable starting point out of an agent with no help -- the answer is now closer to "yes" than it was. Not "yes, ship this", but "yes, you have something concrete to read, learn from, and improve". That feels like real progress.

## Next

* Re-run with `CLAUDE.md` + skills + llms.txt available, on the same workload, and compare. The most interesting question is no longer "does scaffolding help" but "what's the marginal effect now". I suspect a lot smaller than it used to be, and concentrated in code quality rather than getting-to-active. I've been doing a lot with much simpler harnesses and local models, trying to find the right sort of assistance, and this is a valuable data point.
* Try the same one-line-prompt experiment with a Kubernetes charm. I expect the gap to widen there -- Pebble events are harder to reason about from training data alone.
* Have a real charmer review `mastodon-operator`'s charm code and write up the actual technical-debt list. The README warning is honest, but it would be more useful if it were specific. Tricky to do without loading someone up with a review they didn't ask for.
