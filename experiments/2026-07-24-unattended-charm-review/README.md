# What Happens If You Review Every Charm We Ship, Unattended, For Six Weeks?

Charm Tech gets asked a lot of variations on "what's actually wrong with charms?", and the honest answer has always been anecdotal. We know the patterns we personally trip over, and we know what shows up in the issues people bother to file, but nobody has sat down and deployed 147 charm repositories, broken each one on purpose, and written up what happened. That's several months of work for a person, which is why it has never been done.

So I built something to do it instead, pointed it at every charm repository I could find, and went away for a fortnight. It was sized for exactly that fortnight: one charm every four hours, six a day, 147 charms, done by the time I got back. I started it about ten days early to convince myself it worked before I stopped watching it, and it finished about two weeks late, for reasons covered at length below.

**Claude Code wrote and debugged all of the infrastructure, but it didn't write the reviews.** A 3-hour agentic loop on a Claude model, 147 times over, was never going to fit the budget I had. The reviews were written by cheaper models through OpenRouter (`deepseek-v4-pro`, and then `minimax-m2.7` after deepseek's price moved), driven by [`pi`](https://www.npmjs.com/package/@earendil-works/pi) rather than Claude Code, with Claude Sonnet doing the short editing pass at the end of each run, the weekly cross-charm synthesis, and the audit. Claude Code was the thing that built the rig, diagnosed it every time it broke, and wrote the operational log. That split was a budget decision rather than a considered one, but it turned out to be a reasonable shape: expensive model for judgement and synthesis, cheap model for the long grind.

## The numbers

| | |
|---|---|
| Charm repositories reviewed | 147 of 147 |
| Findings | 2,618 |
| Runs (including retries and failures) | 183 |
| Total spend on models | $569.70 |
| Mean cost per review | ~$3.10 |
| Elapsed | 2026-07-24 to 2026-09-02 (planned for the fortnight of 08-03 to 08-17) |
| Hardware | one 260 GB Multipass VM, four Juju controllers (3.6 and 4.x, LXD and Kubernetes) |

Every four hours, cron took the next charm off a priority-ordered queue, gave an agent full control of the VM, and let it deploy the charm, relate it to real partners, break it deliberately, read the code and the tests and the docs, and write one markdown review. Then everything it built was torn down again. 135 of the 136 charms in the first audited batch were genuinely deployed, not just read.

## What it found

The full synthesis is in [results/THEMES.md](results/THEMES.md). The headline defects, in rough order of frequency times severity:

**Invalid config crashes the hook instead of producing `BlockedStatus` (42 of 136 charms).** By a distance the most common defect in the corpus. A bad YAML value, an out-of-range int, a malformed secret URI goes straight into `yaml.safe_load()` or a pydantic model with no `try`/`except`, the hook raises, and Juju then holds every subsequent hook - including the `config-changed` that would fix it - until someone runs `juju resolve`. Several of these crash in `__init__`, so the charm is unrecoverable by ordinary means. traefik does this on a typo in `routing_mode`, confirmed on both Juju versions.

There's a nice detail buried in that one: two reviews independently noticed that `ops.testing.Harness` is what *hides* this class of bug, because it reuses one charm instance across events, where a Scenario-style test constructs a fresh charm per event and would have caught it immediately. That's the strongest argument for the Harness-to-Scenario migration I've seen, and it came out of the data rather than out of me wanting it to be true.

**`postgresql-k8s` gates the ecosystem on Juju 3.6 (33 of 136).** Every channel declares `assumes: juju < 4.0.0`. A third of the corpus could not be exercised end-to-end on Juju 4.x, not because of anything those charms did, but because their only database option refuses to deploy there. No dependent charm can fix this.

**The charm reports `active` while the workload is dead (about 22 of 136).** `pebble stop` the workload and the charm sits at `active/idle` indefinitely. This is the gap between "deploys cleanly" and "survives being operated", and the corpus clears the first bar much more consistently than the second.

**Relation departure is the untested half (about 20 of 136).** `relation-joined` and `relation-changed` get wired up first and get all the test coverage; `relation-departed` and `relation-broken` are missing, or present and a no-op, or (in two cases) present and crashing. Stale credentials survive relation removal.

**Bare `except Exception` (35 of 136)**, and `ruff`'s `BLE001` mostly not enabled in CI.

The synthesis also ranks the lint rules worth actually building, weighted by charms caught, false positive risk, and whether they're mechanically checkable at all. That list is the part I most want to do something with: "no `try`/`except` around a parse fed by `self.config` or relation data, with no path to `BlockedStatus`" would fire on 42 charms and looks cheap to write.

And it's honest about what it doesn't cover, which I asked for explicitly: no public cloud substrates, no cross-model relations, no soak testing, no dedicated security pass, and a heavy skew towards k8s charms (92 of 136) relative to how much of the real ecosystem is machine-based.

## The reviews are wrong about 15% of the time, and I can prove it

Near the end I had the whole corpus read a second time against the source it cites, asking one question per finding: *does the cited code support this claim?* ([results/ERRATA.md](results/ERRATA.md), and `rig/bin/second-read.py`.)

Of 2,414 findings, 1,226 are supported, 34 are contradicted, 184 are miscited, and 713 are unverifiable from an excerpt alone. Of the 1,444 that could actually be checked, **218 (15.1%) are wrong or miscited**. 35 reviews have no adjudicated error at all; the worst is `charmed-etcd-operator` at 62%.

I'd rather publish that number than not have it. But the more useful thing I learnt was from getting it wrong first. The initial audit pass reported 221 miscitations and scored `sloth-k8s-operator` at 11 wrong out of 15 - and that was my bug. Reviews cite what the reviewer was looking at, so inside a charm directory that's `charm.py:89` and not `src/charm.py:89`. Resolving only from the repository root left 250 citations as "no such file", and with no excerpt to judge against, the adjudicator called them *miscited* rather than *unverifiable*. sloth's citations were fine.

**A quality gate that cannot find the file reports the author as wrong.** That happened three separate times in this project, in three different gates, and each time the gate's own blindness was served up to me as somebody else's error. The fix that stuck was making it a rule in code rather than an instruction in a prompt: no excerpt means `unverifiable`, always. The prompt already said exactly that, and the model ignored it 54 times. An instruction that the output can silently violate is not a control.

## What actually went wrong, which is the interesting bit

The full operational log is [operations-log.md](operations-log.md), and I think it's more valuable than the reviews are. It's 1,100 lines of "here is a way an unattended agent programme fails that I did not think of", written as it happened. A selection:

* **A charm filled the disk at 120 MB/s.** `opentelemetry-collector` is configured to scrape `/var/log/syslog` and also writes its own progress to syslog, so every line it read produced another line to read. One container held 177 GB. The stall was self-sustaining, which is the part worth remembering: a full disk stops the Juju API answering, so the cleanup that would have destroyed the offending model couldn't list models, so it skipped exactly the containers that were filling the disk. Twenty-five slots and four days, every one of them running a cleanup that could not help itself.

* **Both LXD controllers were gone for six days and nothing noticed**, because the twelve charms reviewed in that window were all Kubernetes ones and the substrate guard only probes the controllers the current charm needs. A guard that only checks what this slot needs cannot see a substrate that nothing has needed for a week.

* **The work model was silently repriced 2.7x mid-programme**, and it presented as ordinary cost. Same code, same charms, same logs, same exit paths - but the first pass now exhausted the work cap on its own and the watchdog killed it mid-review. Throughput went 6 reviews a day to 1 for three days before I spotted it, and two truncated reviews were *accepted* because they cleared the size floor. What identified it was cost against wall-clock rather than cost alone: one charm ran a 46-minute pass for $4.07 and finished, another was killed at 12 minutes having spent $4.71. Twelve minutes of identical work cannot cost more than forty-five. (The obvious fix, pinning the dated snapshot advertised at the old price, is also wrong: it bills at more than double what the listing says. Price a model by billing a real request and reading `usage.cost_details`, never by reading `/models`.)

* **The transport broke on a threshold nobody knew existed.** Every agent turn started dying in 16 seconds while `curl` to the same endpoint worked fine. `pi` runs on node 22, whose Happy Eyeballs implementation gives each address 250 ms to complete a handshake, and connect latency from that box to OpenRouter had drifted to 287-383 ms. Nothing in the rig or the account changed; the network path to Cloudflare just got slower and crossed a line. One `NODE_OPTIONS` setting fixed it.

* **A stale log file froze the queue permanently.** The budget check globbed `logs/<repo>/*.log`, which is per-repo and never cleared, so a five-day-old 403 from a genuine outage made every retry of that charm abort the slot - and because deferred charms are picked before the cursor, the whole queue behind it stopped. The old lesson here was *never verify by measuring a file the failing step overwrites*; this is its mirror, *never diagnose from a file the failing step doesn't write*. A stale hit is worse than an ordinary false positive, because nothing will ever rewrite the file that produces it.

* **A reclaim that matched nothing still exited 0.** The first version of the disk-reclaim script iterated an LXD pool directory that's root-only, so the glob expanded to nothing under the cron user and it reported success every time. Same shape as a citation gate that checks zero citations, and the same shape as the build-container cleanup that ran every cycle for a week and had never deleted a single container, because `lxc list` only shows the `default` project and charmcraft builds in its own. **Test a cleanup by making it find something.**

The thread running through all of those is one thing: a guard that reads a field the failing path never writes is not a guard, it's a decoration. I now have quite a lot of respect for the discipline of verifying every fix by executing it against a real fault rather than by reading the diff, because in this project reading the diff was wrong about half the time.

## Would I do it again

Yes, and roughly the same way. Some things I'd change:

Reviews are cheap and audits are cheaper. The second read cost about $37 to adjudicate 2,414 findings, against $570 to produce them, and it's the thing that makes the corpus usable by someone other than me. I'd build it in from the start rather than bolting it on at the end.

The quality floor was the weakest part. "At least 8 KB and one finding" is trivially satisfied by a truncated review, which is exactly how the repricing incident got two bad reviews accepted. `citations checked:` turned out to be the metric that exposes a shallow run, and I only worked that out afterwards.

I'd also stop trying to make one review both broad and deep. Splitting into a cheap deployability sweep across everything and an expensive deep pass on a shortlist would probably have got more useful output for the same money, although I'm not certain - the deep passes are where the good findings came from, and I don't know in advance which charms deserve one.

The thing I keep coming back to, though, is that none of this was blocked on the models being good enough. Every serious failure in six weeks was infrastructure: a disk, a controller, a stale file, a price change, a TCP timeout. The reviewing worked, unattended, for six weeks, on a $3 budget per charm. The hard part was keeping the box alive around it.

## What's here

* [operations-log.md](operations-log.md) - the running log, written as each fault was diagnosed and fixed. The most transferable part of this experiment.
* [results/THEMES.md](results/THEMES.md) - cross-charm synthesis: recurring defects with per-charm citations, lint rules worth building, patterns worth copying, where practice diverges, and what the programme didn't cover.
* [results/INDEX.md](results/INDEX.md) - all 147 charms with findings count and cost.
* [results/ERRATA.md](results/ERRATA.md) - the second-read audit, per-review and per-finding.
* [reviews/](reviews/) - all 147 reviews, one file per repository, plus the superseded originals of the four that were re-run. [traefik-k8s-operator.md](reviews/traefik-k8s-operator.md) is a representative one if you just want to see the shape. Read [results/THEMES.md](results/THEMES.md) first: the individual reviews are the raw material, and about 15% of their checkable findings are wrong.
* [rig/](rig/) - the harness, with its own [README](rig/README.md). `bin/run-review.sh` is the whole run; `bin/lib.sh` holds the guards; `prompts/review.md` is the brief the reviewing agent works to; `crontab` and `bin/models.env` carry a lot of the reasoning in comments. `rig/state/history.tsv` has one row per run if you want the raw cost and size data.

A handful of test-model credentials that turned up in captured `juju run` output have been replaced with `REDACTED`. The models they came from were destroyed weeks ago, but there's no reason to publish them.
