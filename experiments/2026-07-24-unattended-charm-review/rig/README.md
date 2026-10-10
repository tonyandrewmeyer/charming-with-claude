# charm-review

An unattended charm review rig. Every four hours cron picks the next charm off a
queue, hands it to a `pi` agent with full control of this VM, and the agent deploys it,
pokes at it, reads the code and the tests and the docs, and writes one markdown review.
Then everything it built is torn down again.

```
crontab  ──►  bin/run-review.sh  ──►  bin/cleanup.sh          (pre-flight)
                                 ──►  bin/repair-controller.sh (only if models are wedged)
                                 ──►  bin/prepare.sh          (workspace + context)
                                 ──►  pi  (work model)        (deploy, observe, review)
                                 ──►  pi  (polish model)      (edit the draft)
                                 ──►  bin/cleanup.sh          (always, via trap)
                                 ──►  bin/index.sh
```

## Layout

| path | what |
|---|---|
| `queue.tsv` | 147 charms, in review order. Column 1 is the index the cursor points at. |
| `state/cursor` | index of the next charm. Edit it to skip or redo. |
| `state/history.tsv` | one row per run: time, index, repo, the *agent's* exit code, cost, review size, findings. |
| `state/runs.log` | the harness's own narration. |
| `reviews/<repo>.md` | **the output.** One file per charm. |
| `notes/<repo>.notes.md` | the agent's raw working notes for that run. |
| `logs/<repo>/` | agent transcript, prepare log, cleanup log, the pre-polish draft. |
| `prompts/review.md` | the brief the reviewing agent works to. |
| `prompts/polish.md` | the brief for the editing pass. |
| `bin/models.env` | which models to use. Written by the benchmark. |
| `INDEX.md` | generated summary of what is done and what is next. |

## Running it by hand

```bash
bin/run-review.sh                       # next charm in the queue
bin/run-review.sh traefik-k8s-operator  # a specific charm, cursor untouched
bin/cleanup.sh                          # tear down anything left behind
bin/index.sh                            # regenerate INDEX.md
tail -f state/runs.log
```

## Guard rails

* **Budget.** The OpenRouter key is capped at $35/day. Each run works out its own cap
  from what is left and how many slots remain today, and a watchdog kills the agent if
  it goes over. Under $1.50 left, the run is skipped and the queue slot is not consumed.
* **Resources.** A run refuses to start if there is less than 18 G of disk or 4 G of
  memory free, rather than burning budget on a review that cannot deploy anything.
* **Cleanup.** `cleanup.sh` runs before every review, after every review via an `EXIT`
  trap, and destroys any juju model named `rv-*` on all four controllers, orphaned
  charmcraft build containers, unreferenced k8s workload images, and the workspace.
  The agent is told to name its models `rv-*` — that prefix is the whole contract.
* **Model teardown never blocks the slot.** `juju destroy-model` waits for the model to
  really go however you ask it not to — 7-15 min for a k8s model, and for ever for one
  whose undertaker has died. `bin/reap-models.py` fires the destroys detached, tracks
  how long each has been dying, and deletes the kubernetes namespace of anything still
  going after 30 min. See its docstring; this was costing 40 min of every 3 h slot.
* **Wedged models get the controller repaired.** A model stuck in `destroying` restarts
  three of its workers about once a minute for ever, so they accumulate rather than just
  sitting there. Two or more wedged on a controller and the pre-flight restarts that
  controller's pod, at most once every 6 h. See `bin/repair-controller.sh`.
* **The cursor advances before the agent starts**, so a charm that wedges the harness
  costs one slot instead of blocking the queue forever.
* **A file is not a review.** A slot only counts as done if what it wrote clears
  `MIN_REVIEW_BYTES` (8K) and has at least one finding — the same test decides whether
  the queue may skip past a charm, so the two cannot disagree. Anything less is moved to
  `logs/<repo>/review.rejected.<ts>.md`, the cursor is rewound and the charm gets one
  retry. Before this, an agent that timed out could leave a stub that cleared the old
  2000-byte bar and was recorded `rc=0`, and the charm was silently lost; `history.tsv`
  records the agent's own exit code and the findings count so it shows up in the log.
* **Repo contents are data.** `--no-context-files` stops `AGENTS.md`/`CLAUDE.md` in a
  reviewed repo from being loaded as instructions, and the brief tells the agent to
  treat everything in the repo, its issues and its docs as material, never as commands.

## Things it deliberately does not do

* It does not `charmcraft pack` by default — the brief prefers deploying the published
  charm from charmhub so the time goes on observation, and asks the agent to record the
  gap between the revision it ran and the local `HEAD`.
* It does not prune LXD base images; juju reuses the same few and re-downloading costs
  more than the disk.
* It does not touch controllers, `controller` models, or `~/.cache/hyrum/charms`.
