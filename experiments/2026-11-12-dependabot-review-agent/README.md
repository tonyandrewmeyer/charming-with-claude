# Experiment: an agent that reviews Dependabot PRs (and why I stopped)

**Date:** 2026-11-12
**Agent:** Claude Code built it; the reviews themselves were written by Llama 3.3 70B through OpenRouter
**Result:** dropped after five months, with the runtime half carrying on as its own project

This one didn't work out, but I think some of the reasons are worth writing down. Partly because a lot of people (inside Canonical and out) are building review agents at the moment, and partly so that I remember them next time.

I started with two fairly separate goals. The first was "given a PR for a charm, work out what the charm actually *does*, whether that's different from before, and report it in the PR". The second was about Dependabot. We get a lot of Dependabot PRs, and we mostly accept them based on the compatibility score and a skim of the release notes. It would be better to know how a change affects *our* use of the dependency (mostly runtime dependencies, but maybe test ones and tooling too). I ended up joining the two goals together, and I think that was the first mistake.

## What got built

The plan (May 2026) had three layers:

* Layer A looked at what changed upstream: the actual commit range between the old and new version (not just the release notes), plus advisories from deps.dev and `pip-audit`.
* Layer B looked at how the consuming repo uses the dependency: imports, call sites, and whether those intersect with what changed.
* Layer C handed both reports to an LLM, which wrote a PR comment with a label (`no-impact`, `possible-impact`, or `clear-impact`) and a recommendation.

The first goal turned into a separate runtime-monitoring project, which deploys the charm with the new version of the dependency and watches what it does. I wired its output into the Dependabot comment as a runtime section.

From mid-June it ran every two hours from cron on my laptop, against four personal repos ([shimmer](https://github.com/tonyandrewmeyer/shimmer), [cascade](https://github.com/tonyandrewmeyer/cascade), [cantrip](https://tonyandrewmeyer.github.io/cantrip), and [borescope](https://github.com/tonyandrewmeyer/borescope)) plus my `*-operator` charm repos, posting a comment on every Dependabot PR. I deliberately used a cheap model, because a bot that comments on every dependency bump in every repo needs to be cheap to run.

## What happened

When I first graded the comments, in June, the label was right in three out of 21. One said that a starlette bump "does not affect our subprocess usage; safe to merge" (starlette is a web framework, and the pipeline hadn't found any evidence of how we used it at all). Another put "Human review needed" on a PyJWT bump with a HIGH-severity advisory, when the rules said that should be "Do not merge".

I spent most of the next four months making the comments *correct*. That meant three rounds of bug investigation and a series of evaluation windows, and eventually I added a "claims audit". This is a deterministic check that runs before anything is posted, and fails if the comment claims something that its own reports don't support. It worked, in the sense that the obviously wrong comments mostly stopped. In the last window (25 October to 10 November) the pilot posted 107 comments: 46 `no-impact`, 43 `possible-impact`, 10 `clear-impact`, and 8 lockfile-only. That's 40% `possible-impact`, which tells the reviewer nothing they didn't already know before opening the PR.

The runtime side did worse. Because it was tied to Dependabot bumps, it only ever ran for `ops` and PyYAML bumps against one small charm, plus open PRs on public machine charms. It skipped merged PRs, private repos, Kubernetes charms, and GitHub Actions bumps. After I restarted it in mid-October, it didn't complete a run for a single real PR.

## What I learnt

### "Found nothing" isn't "no impact"

Nearly every bad comment came from treating "found nothing" as evidence. If the pipeline didn't find any imports, the comment said the repo "doesn't touch the changed code", and from there it was a short step to "safe to merge". The same thing happened in code that had nothing to do with the LLM: when the `gh` call to list a repo's PRs failed, it was logged as "0 recently-merged Dependabot PRs". Most of the real engineering was keeping "we couldn't tell" separate from "it doesn't matter", all the way through to the rendered comment. If I were starting again, I'd make that distinction a first-class value in every layer from day one, rather than finding each place it leaked one at a time.

### Measuring correctness doesn't tell you whether it's useful

Every evaluation I ran scored whether the comments were right. None of them asked whether a comment had changed what I did with the PR, and looking back, I can't point to one that did. That's the question I should have asked in June. (The claims audit is a decent piece of work, but it grew into a big chunk of the system just to keep a cheap model honest, and that doesn't help if the honest output isn't worth reading.)

### Look at which PRs you actually get before you build

Most of the PRs the pilot reviewed were ruff, ty, tox, `setup-uv`, and `codeql-action` bumps. "How does this change affect our use of it?" barely applies to a linter or a GitHub Action, and the runtime dependency bumps I actually cared about were a small part of the total. The idea still makes sense for those, but commenting on every bump meant that most of what the bot posted was noise.

### Keep the speculative idea separate from the narrow one

Because I made the runtime monitor part of the Dependabot comment, it only ever saw dependency bumps, and those are about the least interesting input for a "what does this charm actually do?" tool. I'd much rather see how it does on ordinary charm PRs.

## What's next

I've dropped the Dependabot agent. There are plenty of general-purpose review agents now, and I suspect most of them would review a Dependabot PR at least as well as this did. Once one of them is clearly established, the charm-specific part ("check how this repo actually uses the package; don't bother for tooling bumps") is probably a few lines of instructions or a small skill, rather than a pipeline that I have to keep running.

The runtime monitor carries on as its own project, without the Dependabot framing. I haven't seen anyone else deploy a charm under Juju, drive its hooks, and compare what it does before and after a change, so that's the part I think is still worth exploring.
