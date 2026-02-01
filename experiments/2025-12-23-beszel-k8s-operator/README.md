# beszel-k8s-operator

In this experiment, I had Claude Code build a charm for [beszel](https://www.beszel.dev), a simple monitoring utility.

## Goals

* Determine how much Claude has progressed since the earlier [mosquitto experiment](../2025-08-01-mosquitto-operator/).
* Develop a Kubernetes charm, rather than a machine one.
* Run Claude in YOLO mode (`--dangerously-skip-permissions`) inside of a [Multipass](https://canonical.com/multipass) virtual machine. It seems like this is the best way to run Claude Code for anything other than trivial work.
* To see how much could be accomplished with minimal input - basically give an initial, very basic, instruction to build the charm (I literally gave it only `Build a charm for beszel. https://www.beszel.dev/`) and see how far Claude could get without help.

## Setup

Inside of the VM, I installed Claude Code itself, and also [Concierge](https://github.com/canonical/concierge), and ran `sudo concierge prepare -p dev` so that Claude was starting with a completely bootstrapped Juju (with both K8s and machine controllers).

The [CLAUDE.md](./CLAUDE.md) file had a few updates from the one used with the `mosquitto` experiment.

```diff
5,6d4
< Note that to run `charmcraft` on macOS, you will need to run `uvx charmcraft`.
< 
9c7
< We are building a *charm* to be deployed on a *Juju* controller. All the information you need about Juju can be found at https://juju.is/docs
---
> We are building a *charm* to be deployed on a *Juju* controller. All the information you need about Juju can be found at https://documentation.ubuntu.com/juju/latest/
28c26
< * State transition tests, which we refer to as unit tests. These use [ops.testing](https://documentation.ubuntu.com/ops/latest/reference/ops-testing.html). Each test prepares by creating an `testing.Context` object and a `testing.State` object that describes the Juju state when the event is run, then acts by using `ctx.run` to run an event, then asserts on the output state, which is returned by `ctx.run`.
---
> * State transition tests, which we refer to as unit tests. These use [ops.testing](https://documentation.ubuntu.com/ops/latest/reference/ops-testing.html)'s `Context` and `State`, **not Harness**. Each test prepares by creating an `testing.Context` object and a `testing.State` object that describes the Juju state when the event is run, then acts by using `ctx.run` to run an event, then asserts on the output state, which is returned by `ctx.run`.
38c36
< Integration tests can be run with `tox -e integration`, but also with `charmcraft test`.
---
> Integration tests can be run with `tox -e integration`.
54c52
< At this point, you should ultrathink about a plan for the charm. Use the research from the first step and plan what config, actions, storage, resources, secrets, and so on it should use, and how it will scale and interact with other charms. Do *not* start implementing the charm until you have confirmed that the plan is acceptable. You'll want to document this plan in a markdown file so that it can be referred to later.
---
> At this point, you should ultrathink about a plan for the charm. Use the research from the first step and plan what config, actions, storage, resources, secrets, and so on it should use, and how it will scale and interact with other charms. Do *not* start implementing the charm until you have confirmed that the plan is acceptable. You'll want to document this plan in a markdown file so that it can be referred to later. Update this file (CLAUDE.md) to include specifics about the charm being developed, rather than a generic set of instructions for building a charm.
96a95,96
> * Comments are for explaining *why* a decision was made, not *what* the code is doing. If a reader cannot understand *what* the code is doing, it probably needs to be simplified.
> * Don't use `type: ignore` unless there is no other reasonable option.
```

Key Changes

 * Tooling & Commands: Removed the specific instruction to run charmcraft via uvx on macOS and removed charmcraft test as a suggested way to run integration tests, leaving tox -e integration as the primary method. (Because I moved off macOS to Ubuntu).
 * Documentation Links: Updated the Juju documentation URL from the legacy juju.is domain to the new documentation.ubuntu.com path.
 * Testing Guidance: Explicitly clarified that unit tests should use ops.testing's Context and State patterns rather than the older Harness method.
 * Process Updates: Added a requirement to update the CLAUDE.md file with project-specific details during the planning phase, rather than keeping it as a template of generic instructions.
 * Coding Standards: Introduced two new "Best Practice" rules:
 * Comments should explain why, not what (favouring self-documenting code).
 * The use of # type: ignore is discouraged unless absolutely necessary.

I also added a few subagents, based on the [GitHub recommendations](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/), and two skills, one [Armin's tmux skill](https://github.com/mitsuhiko/agent-stuff/tree/main/skills/tmux) and a custom Juju skill.

There was also an initial `settings.json`, but this mostly has some initial permissions approval, and since I was running with permission-checking off, this probably did little to help, if anything. It did have setup for auto-formatting Python code, but something was wrong and that continually failed, which confused Claude, and it couldn't fix it itself.

## Results

The [full transcript](https://tonyandrewmeyer.github.io/beszel-k8s-operator/) is available, made pretty by [Simon Willison's claude-code-transcripts tool](https://simonwillison.net/2025/Dec/25/claude-code-transcripts/). It includes links to the commits that Claude did as it worked. The final result is available in the [beszel-k8s-operator repository](https://github.com/tonyandrewmeyer/beszel-k8s-operator).

## Lessons

### Plan mode

Plan mode existed in Claude Code in the last experiment, but has been significantly upgraded since then. The first steps Claude took were the "research your workload" and "design the charm" ones, and did this in plan mode. I was then presented with options for the development, which I mostly accepted as-is. I did point out that there was a local `juju` and that Claude was in a sandbox.

### `charmcraft init`

Claude correctly used Charmcraft to get an initial charm state, and I feel this did a good job of getting this going well. It did need to 'figure out' that `--force` was needed, since the agent instruction files were already present. That should probably be in the instructions.

### Starting with integration tests

Claude paid attention to the instructions to start with integration tests. These weren't terrible: they use [Jubilant](https://documentation.ubuntu.com/jubilant/) and get parts correct (most noticeably running actions and ssh commands are wrong).

### Code of Conduct

Claude still seems to get stuck trying to create a code of conduct file, so I again interrupted things here and told it to skip that step. This likely needs to either become part of the Charmcraft profile, or get removed as an instruction from CLAUDE.md. Interestingly, the transcript shows it can download the template, it just can't create the file itself with that content.

### Trust

Charms requiring `--trust` is so common that Claude did it here, without even needing it. It would be great to try to reduce that.

### `tox-uv` is the default but unintuitive

Charmcraft installs `tox.ini` in a way that requires installing [tox](https://tox.wiki/en/4.32.0/) with [tox-uv](https://pypi.org/project/tox-uv/). This is not obvious, and Claude missed it and this meant it didn't run the commands as often as it should, or benefit from the tooling being set up (I eventually did the install myself). This is also a challenge when setting up the CI.

We should improve this somehow, without waiting for `uv` to add a task runner system.

### Juju skill ignored

There were several interactions with Juju, as expected, including adding a model. The skill was ignored, as far as I can tell. I do not know why this is, but need to figure it out before investing any more time into skills.

### CI is configured but not tested

I had to help considerably with this. I wonder if I told Claude the repository address (it could get it from `git remote` but that wasn't in place at the very start) if it would do better, or maybe some instructions about how to check this (with [gh](https://cli.github.com), probably, or maybe [Ned Batchelder's watchgha](https://nedbatchelder.com/blog/202303/watchgha.html)) would encourage Claude to verify that it was correct.

It also installed Charmcraft to pack the charm, but didn't install or bootstrap Juju, and I helped explain what to do. I wonder if having this set up initially didn't help, because there was an assumption the CI environment would be similar to the dev one.

### Claude is better with slow tasks
 
In the previous experiment, Claude struggled with tasks (like packing and integration tests) that were very slow (over 10 minutes). Since then, Claude has gained the ability to work with background tasks and handle long-running work much more smoothly, and I didn't see any issues with that this time.

### Integrations

Claude did a reasonable job of integrations (for identity, for S3, for ingress). I feel like some documentation pointing to [charmlibs](https://documentation.ubuntu.com/charmlibs) including how to use libraries, what libraries are available, and so on, might work better than the web searches that land on Charmhub.

### Minimal containers

The (upstream) Beszel container uses a [scratch image](https://hub.docker.com/_/scratch), so there's no shell in the workload container (and also no tools like `curl`, which Claude tried to use). A [chiselled Rock](https://documentation.ubuntu.com/rockcraft/latest/explanation/chisel/#explanation-chisel) would have similar issues.

It might be worth giving Claude instructions or even a skill to deal with this. Perhaps even with [Cascade](https://github.com/tonyandrewmeyer/cascade]!

### Unit tests

These were immediately Scenario tests, but Scenario 6 from the look of it. I think the "use scenario via ops.testing" decision was a terrible one for agents, although it should resolve itself over time. The agent struggled pulling usage documentation and examples, so more of that would be good (we have plenty already, so just helping it know what to fetch).

## Spread

At this point, we're a bit over a third of the way down page eight of the first transcript. I then asked Claude to use [spread](https://github.com/canonical/spread) for the integration tests, since this is what Charms should do now, and since there is better scaffolding in Charmcraft now (which I installed for Claude at this point). This stage seemed to take forever... (there are 7 more pages of transcript, so it's about half of the effort).

Partly this is because I couldn't guide Claude the right way, and partly this is because this is new, and partly this is because our documentation is terrible (mostly: missing). It will be interesting to use Claude to try out the new documentation later this cycle.

## Final notes

It's taken me a month to write this up properly (I did a bit earlier, but to finish). I need to figure out how to do that more promptly and concisely and efficiently.

I felt this went vastly better than the last experiment, right up until spread. Some of the issues were also my fault (the bad tool config). I'm looking forward to trying more out, and also seeing if I can get skills working usefully.
