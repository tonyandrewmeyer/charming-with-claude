# Experiment: an agent that reproduces new bug reports (and why I stopped)

**Date:** 2026-11-23
**Agent:** Claude Code built it; the extraction and classification calls were made by DeepSeek V3 (`deepseek/deepseek-chat`) through OpenRouter
**Result:** shelved after a bit over four months, with a working workflow and a PR that was never opened

This is the second of these in a row that didn't work out. The reason is mostly the same as last time, which is the most useful thing about writing it down.

The idea was simple. When someone opens an issue in one of the Charm Tech repos and it looks like a bug, the first job is "can we reproduce this?", and that's entirely manual: read the report, guess what the reporter actually ran, stand up a controller, deploy something that exercises the path, and see. Most of that is mechanical, so an agent could try it when the issue is opened and, if it worked, add a comment with the steps and the output. If the report already had a reproducer, or wasn't a bug, it would do nothing.

I liked it because it's specific to Juju and ops. There are plenty of general-purpose triage bots, but none of them will bootstrap a controller and deploy a scratch charm to check whether a Pebble notice reaches the charm.

## What got built

I started on 2026-07-17 and spent the first week on spikes against real `canonical/operator` issues:

* A deterministic filter (issue type, labels, title patterns, and "does the body already contain something runnable?") so that most issues never reach a model.
* An LLM extraction step that pulls out the versions, the substrate, the commands, and what the reporter expected and saw, plus a second opinion on whether the issue is really a bug at all.
* A single parameterised scratch charm (forked from `charm-ubuntu`) for the cases that need something deployed.
* A runner that executes the commands, either with Scenario in a plain venv or on a Juju substrate set up by concierge.
* A classifier that compares what happened with what the reporter said happened, and decides whether there's anything worth saying.

The comment itself is rendered from the run record with no model call, so it can only show commands that actually ran and output they actually produced. Staying silent is the expected outcome, because a wrong reproducer is worse than none: the maintainer trusts it and skips the check they'd otherwise do.

The final shape was a GitHub Actions workflow on `issues: opened`, split into three jobs so that the one running commands taken from an issue body has no secrets and no write access: `plan` makes the model calls, `reproduce` runs the plan with read-only contents and refuses to start if a key or token is in its environment, and `post` is the only job that can comment. Running on a stock `ubuntu-latest` runner, a whole job (including `concierge prepare` and `charmcraft pack`) took between five and twelve and a half minutes, which was much faster than the same thing in my local VMs. The model calls cost almost nothing: $0.073 for the last 31 test runs.

## What happened

The numbers that should have stopped me were there in the first week. In the first spike, 38 issues had been opened in `operator` in the previous three months, and 6 got past the filter. In the second, 67 issues over six months gave 18 past the filter and 4 that were actually bugs in scope. Of those 4, one reproduced (`#2639`, a Pebble notice recorded as a non-root user never reaching the charm). Two of the others had already been fixed by the time I tried.

I read that as a result about the filter rather than about the size of the problem. It's both, and the second one matters more: the filter dropped 7 of the 11 issues typed as bugs because the reporter had already included a reproducer. People filing bugs against ops are mostly charmers and the team itself, and they already know how to write a Scenario test.

Most of August went into measuring the pipeline against exit criteria I wrote for it. That kept running into the same wall from a different side. I couldn't find enough real bugs to measure recall: the largest corpus I could label had 150 issues and 21 true positives, and showing the recall bar I'd set needed at least 36 consecutive hits with no misses. I retired that criterion as unpassable, and later did the same to the false-comment criterion, because there weren't enough live cases that reached the comment step to measure it either. The comment-usefulness score had to be assembled from recorded output (partly synthetic) because live traffic produced nothing to rate. (I rated five of those comments blind, and all five were usable, but that says the composer works, not that anyone needs it.)

The first live run against a real substrate, on 2026-08-18, composed zero comments with the production settings. Loosening the gates to get some output produced two false ones.

From September the workflow ran from my fork against real `operator` issues with posting turned off. In one round, 16 issues were dispatched and none reached the composer: most were tasks, docs, CI failures in the repo itself, or already had a reproducer. The OpenRouter budget ran out in late September, which paused things for a week. The final round before the PR was 16 runs against `#2045` (a Scenario issue about the working directory during a hook), with 11 correct comments and no incorrect ones, and 17 other open issues, none of which reached a comment.

Meanwhile, the one Juju reproduction stopped reproducing. `#2639` reproduced on Juju 4.0.5 and doesn't on 4.0.14 or 3.6, so the substrate half of the project, which is most of its complexity, has no live case at all.

When I put it all into PR form, it was 150 files and about 33,000 lines, of which about 19,000 were tests and fixtures. That's never going into `operator`, and it's too big for our shared tooling repo too. And `operator` has 9 open issues typed as bugs right now (`charmlibs` has 5), so pointing it at the backlog instead of new issues doesn't change the arithmetic.

## What I learnt

### Look at your traffic before you build (again)

This was the main lesson from the Dependabot agent, and I repeated the mistake here. The traffic numbers were in the first two spikes, and they were small. The question I should have asked at that point was "how many comments a year would this post?" and the honest answer was "a handful".

### If you can't get enough cases to measure it, that's the answer

I spent a long time treating the lack of test cases as a measurement problem: bigger corpora, reconstructed open-time labels, confidence bounds, retired and replaced criteria. It wasn't a measurement problem. The reason I couldn't find enough real bugs without reproducers to evaluate against is the same reason the tool wouldn't have anything to do in production.

### The cheap path was the useful one

Every reproduction that worked on a live issue was Scenario-shaped: no controller, no packing, no channel matrix, just a test in a venv. The Juju substrate path is the part I was most excited about and the part that made the project specific to charming, and it was justified by a single case. A version that only did the Scenario path would have been a few thousand lines and could have shipped months ago. I'm still not sure it would have been worth running, though.

### Some of the pieces are worth keeping

Rendering the comment from the run record rather than asking a model to write it was a clear improvement: once that changed, the comments stopped being able to claim anything that hadn't happened. And splitting the workflow so the job that runs untrusted commands holds nothing worth taking is the shape I'd use for any workflow that executes something from an issue body. Neither of those depends on this project.

## What's next

I've shelved it. The [fork branch](https://github.com/tonyandrewmeyer/operator/tree/add-reproducer-workflow) stays where it is, and the workflow runs if anyone wants to try it against an issue.

I do think there's a version of this that has the traffic. The hundreds of charm repos across Canonical get bug reports that are much rougher than the ones filed against ops, from people who aren't going to write a Scenario test, and reproducing those needs exactly the Juju-specific work that general triage bots don't do. But that means deploying the real charm with real relations, in repos other teams own, and very little of what I built here would carry over. If I come back to it, it'll be as a new project, and the first thing I'll do is count the issues.
