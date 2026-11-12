# Experiment: an agent that reviews Dependabot PRs (and why I stopped)

**Date:** 2026-11-12
**Agent:** Claude Code built it; the reviews themselves were written by Llama 3.3 70B through OpenRouter
**Result:** dropped after five months, with the runtime half carrying on as its own project

This one didn't work out, but I think a couple of the reasons are worth writing down, partly because a lot of people (inside Canonical and out) are building review agents right now, and partly so I remember them next time.

I started with two goals that were fairly separate. The first was "given a PR for a charm, work out what the charm actually *does*, whether that's different from before, and report it in the PR". The second was about Dependabot. We get a lot of Dependabot PRs, and they're mostly accepted on the strength of the compatibility score and a skim of the release notes. It would be better to know how a change affects *our* use of the dependency: mostly runtime dependencies, maybe test ones, and arguably tooling too.

The two ended up joined, and I think that was the first mistake.

## What got built

The plan (May 2026) had three layers:

* Layer A looked at what changed upstream: the actual commit range between the old and new version (not just the release notes), plus advisories from deps.dev and `pip-audit`.
* Layer B looked at how the consuming repo uses the dependency: imports, call sites, and whether those intersect with what changed.
* Layer C handed both reports to an LLM, which wrote a PR comment with a label (`no-impact`, `possible-impact`, `clear-impact`) and a recommendation.

The "deploy the charm with the new dependency and watch what it does" part was split out into a separate runtime-monitoring project, which became the Dependabot comment's runtime section.

From mid-June it ran every two hours from cron on my laptop, against four personal repos ([shimmer](https://github.com/tonyandrewmeyer/shimmer), [cascade](https://github.com/tonyandrewmeyer/cascade), [cantrip](https://tonyandrewmeyer.github.io/cantrip), and [borescope](https://github.com/tonyandrewmeyer/borescope)) plus my `*-operator` charm repos, posting a comment on every Dependabot PR. I deliberately used a cheap model, because a bot that comments on every dependency bump in every repo needs to be cheap to run.

## What happened

The first self-audit, in June, graded 21 comments. The label was right in three of them. One said that a starlette bump "does not affect our subprocess usage; safe to merge" (starlette is a web framework, and the pipeline had found no evidence of how we used it at all). Another put "Human review needed" on a PyJWT bump that fixed a HIGH-severity advisory, when the rules said that should be "Do not merge".

Most of the next four months went into making the comments *correct*. There were three bug investigations, a series of evaluation windows, and eventually a "claims audit": a deterministic check, run before anything is posted, that fails if the comment asserts something its own reports can't support. That worked, in the sense that the obviously wrong comments mostly stopped. In the last window (25 October to 10 November) the pilot posted 107 comments: 46 `no-impact`, 43 `possible-impact`, 10 `clear-impact`, and 8 lockfile-only.

`possible-impact` is 40% of that, and it tells the reviewer nothing they didn't know before opening the PR.

The runtime side fared worse. Tied to Dependabot bumps, it only ran for `ops` and PyYAML bumps against one small charm, plus open PRs on public machine charms. Merged PRs, private repos, Kubernetes charms, and GitHub Actions bumps all skipped it. After a restart in mid-October it didn't complete for a single real PR.

## What I learnt

### "Found nothing" isn't "no impact"

Nearly every bad comment came from turning an absence into a confident verdict: no imports found became "doesn't touch the changed code", which became "safe to merge". The same shape showed up in the plumbing, where a failed `gh` call to list a repo's PRs was logged as "0 recently-merged Dependabot PRs". Most of the real engineering was keeping "we couldn't tell" separate from "it doesn't matter", all the way through to the rendered comment. If I were starting again, I'd make that distinction a first-class value in every layer from day one, rather than finding each place it leaked one at a time.

### Measuring correctness doesn't tell you whether it's useful

Every evaluation I ran scored whether the comments were right. None of them asked whether a comment had changed what I did with the PR, and looking back, I can't point to one that did. That's the question I should have asked in June. (The claims audit is a decent piece of work, but it's a verifier that grew to be a big chunk of the system just to keep a cheap model honest, and it's solving the wrong problem if the honest output isn't worth reading.)

### Look at your traffic before you build

Most of the PRs the pilot reviewed were ruff, ty, tox, `setup-uv`, and `codeql-action` bumps. "How does this change affect our use of it?" barely applies to a linter or a GitHub Action, and the runtime dependency bumps I actually cared about were a small slice. The idea makes sense for that slice, and a bot that comments on every bump is mostly noise.

### Don't make the speculative part depend on the narrow part

Making the runtime monitor a component of the Dependabot comment meant it only ever saw dependency bumps, which is about the least interesting input for a "what does this charm actually do" tool. It deserves to be judged on ordinary charm PRs.

## What's next

I've dropped the Dependabot agent. General-purpose review agents are everywhere now, and any of them will review a Dependabot PR at least as well as this did. Once one of them is clearly established, the charm-specific part ("check how this repo actually uses the package; don't bother for tooling bumps") is probably a few lines of instructions or a small skill, rather than a pipeline that I have to keep running.

The runtime monitor carries on, without the Dependabot framing. Deploying a charm under Juju, driving its hooks, and comparing what it does before and after a change is something I haven't seen anyone else doing, so that's the part I think is still worth exploring.
