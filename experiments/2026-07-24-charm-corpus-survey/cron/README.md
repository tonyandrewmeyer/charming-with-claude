# The cron setup

Five jobs on the [Hermes](https://github.com/hermes-agent/hermes) cron scheduler, created 2026-07-24 and staggered so the two that call the GitHub API never overlap. The three shell wrappers here ran with `no_agent: true`, meaning Hermes executed the script directly with no model in the loop. The other two are agent jobs, and their prompts are in `prompts/`.

| Job | Schedule (NZ) | Runs | What it did | State at the end |
|---|---|---|---|---|
| `rq-static-daily` | `0 5 * * *` | 34 | refresh clones, then RQ-2, RQ-9, RQ-11, RQ-7 | paused 2026-08-26 |
| `rq4-health-daily` | `0 6 * * *` | 34 | ~60-repo round-robin GitHub health batch | still running |
| `rq6-issues-daily` | `0 7 * * *` | 34 | alternating fetch and classify phases | paused 2026-08-26 |
| `rq6-llm-classify` | `30 7 * * *` | 34 | LLM pass over the classifier's residue | deleted 2026-08-26 |
| `rq-digest-weekly` | `0 9 * * 0` | 5 | weekly prose digest into `digests/` | still running |

There are six files in `data/digests/` against five scheduled runs: the first was a manual run on the day the jobs were created, to check the prompt did something sensible before leaving it alone.

`rq6-llm-classify` was deleted rather than paused because it had nothing left to do: the backlog it was draining hit zero, after which it kept firing against an empty queue until it started failing on an org monthly budget limit. Its last useful run wrote six records.

## Things the wrappers had to learn

`rq-static-daily.sh` is much longer than the other two, and every extra section is scar tissue:

- **Step 1 reverts dependency files** before anything else. hyrum's `ops` patcher writes to the same shared corpus and does not always revert `pyproject.toml` / `uv.lock` / `poetry.lock` / `requirements.txt`, which are exactly the files RQ-2 reads. It skips the cleanup entirely if a hyrum run is in flight, so it never fights a live patch.
- **Step 2 refreshes the clones**, which the original version did not do at all. That omission is why the corpus sat frozen from 2026-07-10 to 2026-08-16 while the job reported success every night. It also probes each host before refreshing: `git.launchpad.net` has been unreachable from this machine since at least 2026-08-17, each dead connection hangs for about 270 seconds, and because `get-charms` shares one worker pool across all rows, 119 Launchpad rows were starving the ~520 reachable ones. Probing rather than hardcoding an exclusion means they come back on their own if the host does.
- **Step 3 skips any pass that already has rows for the current UTC date.** The passes stamp rows in UTC and blindly append, while cron fires at 05:00 NZ (17:00 UTC the day before), so a manual run and the next cron fire collide easily. That is why 2026-07-23 is five times too wide.

There is a comment in the wrapper naming `$HOME/multipass-mounts/hyrum` as a trap: it is a separate tree stuck at 2026-07-04, with an old charm list and a `get-charms` whose CLI rejects `--workers`. It fails loudly rather than falling back to it.

## The agent prompts

`prompts/rq6-llm-classify.md` and `prompts/rq-digest-weekly.md` are the prompt fields of the two agent jobs, verbatim as they ran during the experiment.

The digest prompt has since been narrowed to RQ-4 only, because that is the only pass still collecting: the version here still asks for the RQ-6 cross-cutting section and the static-pass one-liners, which would now be read off frozen files. The copy is kept as it ran rather than updated.

Both are mostly guard rails, and both sets of guard rails were added after a failure rather than designed up front. The classify prompt's are about blast radius (write only to your own file, never touch the deterministic output, cap the batch size so each write stays atomic). The digest prompt's are about budget - an early run spent its entire tool budget on analysis nobody asked for and wrote no file, which is why it now says to write a complete-but-thin digest after the first pass and improve it from there.

The digest prompt's honesty rules are the part I would carry into anything similar:

> A metric that did not move is only a trend if it was actually collected. Check that the underlying pass ran and that the corpus was refreshed before reporting anything as "stable" or "flat".

That rule exists because a digest reported the frozen-corpus flat line as ecosystem stability, and I would rather the next one caught it than that I did.
