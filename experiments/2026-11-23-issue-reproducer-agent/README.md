# Experiment: an agent that reproduces new bug reports (and why I stopped)

**Date:** 2026-11-23
**Agent:** Claude Code built it; the extraction and classification calls were made by DeepSeek V3 (`deepseek/deepseek-chat`) through OpenRouter
**Result:** shelved after a bit over four months, with a working workflow and a PR that was never opened

This is the second of these in a row that didn't work out, and mostly for the same reason as the [Dependabot agent](../2026-11-12-dependabot-review-agent/), which I think makes it more worth writing down.

When someone opens an issue in one of the Charm Tech repos and it looks like a bug, the first job is to try to reproduce it. That's entirely manual: we read the report, guess what the reporter actually ran, stand up a controller, deploy something that exercises that code, and see what happens. A lot of that is mechanical, so my idea was that an agent could try it as soon as the issue is opened and, if it reproduced, add a comment with the steps and the output. If the report already had a reproducer, or wasn't a bug, it would do nothing.

I liked it because it's specific to Juju and ops. There are plenty of general-purpose triage bots, but as far as I know none of them will bootstrap a controller and deploy a scratch charm to check whether a Pebble notice reaches the charm.

## What got built

I started on 17 July and spent the first week on spikes against real `canonical/operator` issues:

* A deterministic filter (issue type, labels, title patterns, and "does the body already contain something runnable?") so that most issues never reach a model.
* An LLM extraction step that pulls out the versions, the substrate, the commands, and what the reporter expected and saw, plus a second opinion on whether the issue is really a bug at all.
* A single parameterised scratch charm (forked from `charm-ubuntu`) for the cases that need something deployed.
* A runner that executes the commands, either with Scenario in a plain venv or on a Juju substrate set up by concierge.
* A classifier that compares what happened with what the reporter said happened, and decides whether there's anything worth saying.

The comment itself is rendered from the run record with no model call, so it can only show commands that actually ran and output they actually produced. I expected it to stay silent most of the time, because a wrong reproducer is worse than none. A maintainer will trust it, and skip the check they'd otherwise do.

The final version was a GitHub Actions workflow triggered on `issues: opened`. It's split into three jobs so that the one that runs commands taken from an issue body has no secrets and no write access. The `plan` job makes the model calls. The `reproduce` job runs the plan with read-only access to the contents, and refuses to start if there's a key or token in its environment. The `post` job is the only one that can comment. On a stock `ubuntu-latest` runner, a whole run (including `concierge prepare` and `charmcraft pack`) took between five and twelve and a half minutes, which was much faster than the same thing in my local VMs. The model calls cost almost nothing ($0.073 for the last 31 test runs).

I compared models once, in early August, and none of the three I tried beat DeepSeek V3 on deciding whether an issue was a real bug (GPT-4.1 came closest, at about 19 times the cost). The Claude models were left out because the harness couldn't cope with them wrapping JSON in code fences, which was a harness problem rather than a model one. I never ran the comparison again, though, and given how much models changed over those four months, I should have.

## What happened

The numbers that should have stopped me were there in the first week. In the first spike, 38 issues had been opened in `operator` in the previous three months, and 6 got past the filter. In the second, 67 issues over six months gave 18 past the filter and 4 that were actually bugs in scope. Of those 4, one reproduced ([#2639](https://github.com/canonical/operator/issues/2639), a Pebble notice recorded as a non-root user never reaching the charm). Two of the others had already been fixed by the time I tried.

At the time, I read that as a result about the filter rather than about the size of the problem. It was really both, and the size of the problem matters more. The filter dropped 7 of the 11 issues typed as bugs because the reporter had already included a reproducer. Most of the people filing bugs against ops are charmers or the team itself, and they already know how to write a Scenario test.

I spent most of August measuring the pipeline against the exit criteria I'd written for it, and kept running into the same problem. I couldn't find enough real bugs to measure recall. The largest corpus I could label had 150 issues with 21 true positives, and showing that it met the recall bar I'd set needed at least 36 hits in a row. I retired that criterion as unpassable, and later did the same to the false-comment criterion, because there weren't enough live cases that reached the comment step to measure that either. I had to assemble the comment-usefulness score from recorded output (partly synthetic), because live traffic produced nothing to rate. (I rated five of those comments blind, and all five were usable. That shows the composer works, but says nothing about whether anyone needs it.)

The first live run against a real substrate, on 18 August, didn't compose any comments with the production settings. When I loosened the gates to get some output, it produced two false ones.

From September I ran the workflow from my fork against real `operator` issues, with posting turned off. In one round, I dispatched 16 issues and none of them reached the composer. Most were tasks, docs, or CI failures in the repo itself, or already had a reproducer. The OpenRouter budget ran out in late September, which paused things for a week. The final round before the PR was 16 runs against [#2045](https://github.com/canonical/operator/issues/2045) (a Scenario issue about the working directory during a hook), which gave 11 correct comments and no incorrect ones, and 17 other open issues, none of which reached a comment.

Meanwhile, the one Juju reproduction stopped reproducing. #2639 reproduced on Juju 4.0.5 and doesn't on 4.0.14 or 3.6, so the substrate half of the project, which is most of its complexity, has no live case at all.

When I put it all into PR form, it was 150 files and about 33,000 lines, of which about 19,000 were tests and fixtures. That's never going into `operator`, and it's too big for our shared tooling repo too. And `operator` has 9 open issues typed as bugs right now (`charmlibs` has 5), so pointing it at the backlog instead of new issues wouldn't give it much more to do.

## What I learnt

### Count the issues before you build (again)

This was one of the lessons from the Dependabot agent, and I made the same mistake here. The numbers were in the first two spikes, and they were small. The question I should have asked at that point was "how many comments a year would this post?", and the honest answer was "a handful".

### If you can't get enough cases to measure it, that's the answer

I spent a long time treating the lack of test cases as a measurement problem, with bigger corpora, reconstructed open-time labels, confidence bounds, and retired and replaced criteria. The reason I couldn't find enough real bugs without reproducers to evaluate against is the same reason that the tool wouldn't have had anything to do in production.

### The cheap path was the useful one

Every reproduction that worked on a live issue was a Scenario test in a venv, with no controller, packing, or channel matrix. The Juju substrate path is the part I was most excited about, and it's what made the project specific to charming, but only one case ever needed it (and that one stopped reproducing). A version that only did the Scenario path would have been a few thousand lines and could have shipped months ago. I'm still not sure it would have been worth running, though.

### Some of the pieces are worth keeping

Rendering the comment from the run record, rather than asking a model to write it, was a clear improvement. Once I changed that, the comments couldn't claim anything that hadn't happened. I'd also split any workflow that runs something from an issue body the same way, so that the job running untrusted commands has no secrets or write access.

## What's next

I've shelved it. The [fork branch](https://github.com/tonyandrewmeyer/operator/tree/add-reproducer-workflow) stays where it is, and the workflow still works if anyone wants to try it against an issue.

I do think there's a version of this that would have enough to do. The hundreds of charm repos across Canonical get bug reports that are much rougher than the ones filed against ops, from people who aren't going to write a Scenario test, and reproducing those needs exactly the Juju-specific work that general triage bots don't do. But that means deploying the real charm with real relations, in repos other teams own, and very little of what I built here would carry over. If I come back to it, it'll be as a new project, and the first thing I'll do is count the issues.
