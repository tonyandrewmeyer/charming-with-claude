# Status — 2026-07-25 (evening), checked over 2026-07-28, 07-30, 07-31, 08-02, 08-09, 08-12, 08-15, 08-17, 08-23, 08-26, 08-27 and 08-30

**2026-08-30: the whole corpus was read a second time, against the source it cites.**
`bin/second-read.py`, output in `audit/20260830/` (one JSON per repo + `ERRATA.md`). It asks
one question per finding -- *does the cited code support this claim* -- and nothing else. It
needs no juju, no `state/lock` and therefore no cron slot, which is why it could run beside
the tail; source comes from the depth-1 clones in `/home/ubuntu/.cache/hyrum/charms`, never
from `work/`, which run-review.sh deletes each slot. Direct HTTPS, no `pi`: the model gets no
tools, so cost is predictable and a second reader cannot mutate the cache prepare.sh clones.

**136 reviews, 2414 findings, $36.98 all in.** supported 1226 (50.8%), contradicted 34 (1.4%),
miscited 184 (7.6%), runtime 257 (10.6%), unverifiable 713 (29.5%). The number that matters:
**of the 1444 findings that could actually be checked against source, 218 -- 15.1% -- are
wrong or miscited.** 35 reviews have no adjudicated error at all.

*Before trusting any of that, two things were measured rather than assumed.* First, the audit
only means anything if the checkout is the code the reviewer read: **136/136 cached HEADs equal
the commit in the review header**, so no line number has drifted. Second, and this is the
lesson worth keeping: **the first pass reported 221 miscited and `sloth-k8s-operator` came back
11-of-15 miscited at high confidence -- and that was my bug, not the review's.** Reviews cite
what the reviewer was looking at, so inside a charm directory that is `charm.py:89`, not
`src/charm.py:89`. Resolving only from the repo root left 250 citations as "no such file", and
with no excerpt to judge against the adjudicator called them *miscited* rather than
unverifiable. sloth's citations are fine: after `find_by_suffix()` it reads **10 supported**.
**A quality gate that cannot find the file reports the author as wrong** -- the same shape as
the 08-02 citation checker that indexed only the repo and scored `single_kernel_*` charms at
zero, and as verify-citations.py's 4x overstatement. Both times the gate's own blindness was
served up as someone else's error.

The other half of that fix is a rule now enforced in code rather than asked for in a prompt:
**no excerpt -> `unverifiable`, always.** The prompt said exactly that and the model ignored it
54 times, and an instruction the output silently violates is not a control.

*Known limits, all of them in ERRATA.md.* 29.5% unverifiable is the method's ceiling -- `deps/`
citations point at PyPI distributions that only ever existed inside a deleted workspace, and
absence claims ("no handler for X") cannot be settled from an excerpt. 40 fallback resolutions
had to CHOOSE between candidates, nearly all in monorepos (mysql-operators 9, testflinger 5,
airflow-core 4, pyroscope 3); the excerpt is labelled `charm.py -> charms/foo/src/charm.py` so
the adjudicator can see what it got, but **an error in a multi-charm repo needs a human before
you act on it.** Three `contradicted` verdicts were hand-checked against source and all three
stand: hive-metastore's `promote_charm.yaml` does have `secrets: inherit` (line 27), catalogue's
nginx config does have `access_log`/`error_log`, and ranger's `ranger-image` is used at
`charmcraft.yaml:85-87`.

**What this changes about requeuing.** Thinness and wrongness are different axes and the corpus
ranks differently on each. The 08-27 requeue picked 62/98/133 on thinness; the audit's worst are
`charmed-etcd-operator` (62% of findings wrong, 8 findings), `superset-k8s-operator` (45%, 9
miscited of 20), `discourse-k8s-operator` (29%), `catalogue-k8s-operator` (33%, 2 contradicted)
and `kafka-operator` (33%). Note 62/98/133 were NOT audited -- their review files are in
`reviews/superseded/20260827/` while they wait to re-run, and the audit reads `reviews/*.md`.
Also confirmed from the audit: **idx 79 identity-saml-provider** (40% error, and its own text
says no deployment was carried out) and **idx 144 self-signed-certificates** (22%, the 07-24
v1-harness review) both belong in the requeue -- see the entry below for why neither can be
reached by the ordinary path.

**2026-08-30: the programme had been dead for 2.5 days, and the log said why in a way that
was entirely wrong.** Last successful review was idx 138 at 08-27 14:15; ~15 slots were lost.
Cursor still 139 with all nine tail charms (139-147) unstarted, and three charms — 62, 98,
133, the ones requeued for quality on 08-27 — sitting with no review file at all, their
originals safe in `reviews/superseded/20260827/`.

*What the log claimed.* From 08-28 every slot printed
`provider refused to bill this account — 403 Org member budget limit exceeded`. That was
false. Billing a real request against both `WORK_MODEL` and `POLISH_MODEL` returned 200 with
`usage.cost_details` populated; the loaned key held $135.26 of $150. **The 08-23 lesson
inverts here: a live billed request is still the honest test, and this time it was the test
that cleared the provider rather than convicting it.**

*Fault 1 — the real one, and it is in the transport.* Every pi turn died in ~16s with
`Request timed out.` (19B `agent.log`), while `curl` to the same endpoint worked. Reproduced
outside the rig, on both models, so not model-specific. node's own `fetch` fails in 0.53s with
`connect ETIMEDOUT 104.18.3.115:443`. Cause: **pi runs on node 22, whose Happy Eyeballs gives
each address `autoSelectFamilyAttemptTimeout` ms to complete the handshake — default 250 — and
connect latency from this box to openrouter.ai has drifted to 287-383ms** (five `curl -w
%{time_connect}` samples, all over the line). openrouter.ai publishes AAAA only and this host
has no IPv6 route, so the v4 attempts are the whole story and there is no second chance behind
them. Nothing in the rig or the account changed; the network path to Cloudflare got slower and
crossed a threshold nobody knew existed. **Fixed in `bin/lib.sh` with
`export NODE_OPTIONS=--network-family-autoselection-attempt-timeout=2000`** (~5x headroom over
the worst sample), which every pi call site inherits by sourcing lib.sh. Verified by running
the real thing: 3.1s with it, 16.6s timeout without.

*Fault 2 — why one dead charm froze the whole queue.* `run-review.sh` called
`check_provider_budget "$LOGDIR"/agent.log "$LOGDIR"/*.log`, and `logs/<repo>/` is per-repo and
never cleared. landscape-server-operator's 08-25 run had hit the **genuine** org-budget wall on
its depth passes, leaving three 104-byte `403 ... budget limit exceeded` logs behind; the review
itself passed the floor, so the charm was accepted and later requeued for quality. Every retry
of it from 08-28 re-read those five-day-old files and called `budget_abort` — which by design
**exits the slot**, and because a deferred charm is picked at the *top* of every slot, the main
queue behind it never ran. Fixed with **`BUDGET_LOG_SINCE`** (exported in `run-review.sh` where
LOGDIR is set; honoured by `provider_budget_block` in `lib.sh`): only logs this run wrote are
eligible. Verified by executing it — stale 403 ignored, fresh 403 still fires, `mtime == since`
counts as fresh, unset keeps the old behaviour, unstattable file is not treated as fresh (6/6).

**The lesson is a new variant of the recurring one.** The old form was *never verify by
measuring a file the failing step overwrites*. This is its mirror: **never diagnose from a file
the failing step does not write.** A stale hit is far worse than an ordinary false positive,
because nothing will ever rewrite the file that produces it — `budget_abort` was designed as a
cheap, self-clearing skip, and reading history turned it into a permanent one.

*Recovery.* 62 and 98 had each burned their single retry on this and been given up on
(`runs.log:5493,5516`); their `retries.tsv` rows were cleared and both were put back on
`state/deferred.tsv` alongside 133 — the proven path. Backups `.bak-20260830` on `lib.sh`,
`run-review.sh`, `retries.tsv`, `deferred.tsv` and this file. All four controllers probed
healthy at 01:10 (lxd 3.6.27, lxd-4 4.0.12, k8s-3 3.6.25, k8s-4 4.0.12) — worth doing because
**98 is k8s kind, so the k8s controllers matter again**, which is the opposite of the 08-27
note. 124G free, 25G memory available. Twelve charms remain (3 deferred + 9 tail) at ~$2.6
mean, ~$31 against $135 on the loaned key — about two days at 6/day, so the tail lands ~09-01,
which is also when our own key at `/home/ubuntu/my-key-pi-auth.json` should be restored and
just before the loaned key expires 09-02T02:06Z. That is tight rather than comfortable: if a
slot is lost, restore the own key on 09-01 regardless and let the tail finish on it.

**Watch this one, because the threshold is external.** If connect latency drifts past 2000ms
the same failure returns, and it will look identical: `Request timed out.` in `agent.log` and
nothing wrong anywhere else. The one-line check is
`curl -s -o /dev/null -w '%{time_connect}\n' https://openrouter.ai/api/v1/models` against
`node -e 'fetch("https://openrouter.ai/api/v1/models").then(r=>console.log(r.status))'` — when
curl succeeds and node does not, it is this.


**2026-08-27: three reviews requeued for a re-run, and the mechanism used to do it.**
138/147 done, cursor 139, all nine remaining charms machine kind. All four controllers
probed healthy (lxd 3.6.27, lxd-4 4.0.12, k8s-3 3.6.25, k8s-4 4.0.12) — worth doing
deliberately now, because with only machine charms left the two k8s controllers are no
longer exercised by any run, which is exactly the 08-12 blind spot with the kinds swapped.
The 08-26 budget fixes are confirmed in production: five consecutive `rc=0` runs (134-138),
and idx 134 and 135 — the two charms the org-budget wall ate on 08-26 — came back and
completed **with no intervention**, so `budget_abort` really does return the slot rather
than spend the charm's retry.

Three reviews were judged not good enough and put back for a re-run:

    62   opentelemetry-collector-operator   code-only (machine never provisioned) and
                                            citations-final.log empty — gate died on ENOSPC
    98   penpot-operator                    rc=143, only 2 citations checked vs ~14 for peers
    133  landscape-server-operator          22064B / 8 findings, 8 checked / 5 problems left —
                                            thinnest of the last 20

*How, and why this way.* They were appended to **`state/deferred.tsv`** rather than added as
new rows on the end of `queue.tsv`. A duplicate queue row would have worked, but
`bin/index.sh` walks `queue.tsv` and keys reviews by **repo name**, so each duplicate would
appear twice in INDEX.md's Reviewed table and inflate the denominator to "of 150" — drift in
the one document that reports status. `deferred.tsv` is read by nothing else, and it is the
rig's own proven requeue path (the same one that recovered 78/82/84 on 08-17).

The consequence to know about: a deferred charm is retried at the **top of every slot,
before the cursor pick**, so these three take the next three slots and the tail (139-147)
finishes about half a day later, ~08-30 rather than ~08-29. Still well clear of the loaned
key's 09-02 expiry and the 09-01 restore of our own key. Running them now rather than after
the queue drains is deliberate: if a re-run itself fails there are still slots left to notice,
whereas last-in-queue would put a failure right on top of the key transition.

**The step that is easy to miss: the old review file has to be moved out of the way.**
`run-review.sh:159` skips any charm whose `reviews/<repo>.md` passes `review_is_good`, and it
applies that skip to a deferred pick too — it would have called `defer_undo` and dropped the
charm off the list silently, looking exactly like a completed re-run. The three originals
(plus their notes and per-run logs) are archived at
**`reviews/superseded/20260827/`**; restore any of them with a plain `cp` back to
`reviews/<repo>.md` if the re-run comes out worse. `retries.tsv` had no rows for these three,
so each gets its full one retry.

Verified by executing the rig's own predicate rather than reading it: the deferred pick
resolves `DIDX=62` to a real queue line, and `review_is_good` now returns false for all
three, i.e. they will run rather than be skipped.

*`test-charm-xac2` torn down, and what it exposed.* That model on concierge-k8s-3 (7 apps:
juju-jimm-k8s, hydra, openfga, postgresql, traefik, grafana-agent, self-signed-certificates,
idle since 08-23) was never reaped by cleanup, because `reap-models.py:132` only destroys
models named `rv-*` — a hand-made probe model lives for ever. Destroyed on 08-27 with the
reap-models.py pattern, detached and never in the foreground:

    setsid timeout 3600 juju destroy-model concierge-k8s-3:test-charm-xac2 \
           --force --no-wait --no-prompt --destroy-storage &

Clean in **90 seconds** — 8 pods and 3 PVCs gone, namespace gone, model gone, +3G disk. Judged
on the namespace emptying, not on juju's model doc flipping status.

That teardown doubles as the honest proof that **k8s-3's undertaker is healthy**, which settles
the other loose end: `rv-forgejo-k8s-v3`, stuck `destroying` since 08-19, has **no namespace on
the cluster at all**. It holds nothing; its warning on every cleanup is noise, not a leak.

*A wider blind spot, found while checking that.* **Cleanup enumerates juju *models*, so a
namespace whose model is already gone is invisible to it no matter what it is called.**
`rv-identity-saml-provider` has been Active for 11 days holding a stray `test-image-check` pod
— left behind by idx 79's three `rc=143` attempts on 08-13/08-15. It matches `rv-*` and cleanup
still cannot reach it, because there is no model to enumerate. One pod and no storage, so
nothing is being hurt; the point is the *class*.

*Fixed the same day — `sweep_orphans()` in `bin/reap-models.py`* (backup
`bin/reap-models.py.bak-20260827`, `bin/cleanup.sh.bak-20260827`; new state file
`state/orphan-ns.tsv`, new knob `ORPHAN_AFTER`, default 3600s). It works from the cluster
side: list namespaces, subtract every model name both k8s controllers know, delete what is
left. It lives in reap-models.py rather than cleanup.sh because the juju model list and
`reap_k8s()` were already there, and cleanup.sh logs its output as it does everything else.

This is the only thing in the harness that deletes something juju never told it about, so it
**abstains rather than guesses**, on four guards — each one there because the failure it
prevents would delete a live review's namespace mid-run:

    1. both k8s controllers answered   an unreachable controller returns an empty model
                                       list, and an empty list makes every namespace look
                                       orphaned — the 08-12 blind spot pointed the other way
    2. kubectl answered                None and [] must stay distinguishable: "could not
                                       ask" is not "no namespaces"
    3. rv-* only                       kubeflow, controller-*, kube-system and the
                                       operator's own work are never candidates
    4. old enough AND seen orphaned    ORPHAN_AFTER guards the seconds between juju creating
       on an EARLIER run               a namespace and its model doc; the earlier-run rule
                                       means one bad read can never be enough by itself

*Verified by executing every guard against real objects, not by reading them.* A real live
`rv-guard-probe` model was created on concierge-k8s-3 and was **not** swept even at
`ORPHAN_AFTER=0` (guard 3's `known` set). A bogus controller name and a stubbed failing
`kubectl` each made it abstain, also at `ORPHAN_AFTER=0`. A stub returning `{"items":[]}`
swept nothing rather than everything. A freshly created `rv-age-probe` namespace was spared
at the default threshold and seen at `ORPHAN_AFTER=0`. Then the real thing: two live runs
took `rv-identity-saml-provider` from "watching it" to
`deleted orphaned namespace rv-identity-saml-provider (283h old, no juju model)`, and the
namespace really did terminate — judged on `kubectl get ns` going empty, not on rc=0 — after
which the `orphan-ns.tsv` record pruned itself. The cluster is now down to its own
namespaces plus kubeflow.


**2026-08-26 (evening): unblocked on a colleague's key — and the budget arithmetic had to
change shape to match it.** A colleague lent their own OpenRouter key to cover the gap until
the org budget resets on **2026-09-01**. It is in `/home/ubuntu/.pi/agent/auth.json` as usual,
and it bills: confirmed by billing a real request against **both** `WORK_MODEL`
(minimax/minimax-m2.7, $0.00017) and `POLISH_MODEL` (anthropic/claude-sonnet-5, $0.000096)
and reading `usage.cost_details`, not by trusting the 200 from `/api/v1/key`.

*The new key is a different shape from every key this rig has run on.*

    ours (saved)        limit 35   limit_reset daily   expires 2026-09-22T09:38Z
    colleague's (live)  limit 150  limit_reset null    expires 2026-09-02T02:06Z

`limit_reset: null` means the $150 is a **flat pot, not a daily allowance** — it never
refills. That broke the budget maths, which computed `REMAIN = limit - usage_daily`: correct
for a daily key, and wrong here in the dangerous direction, because `usage_daily` returns to
0 at 00:00 UTC while the pot does not. The rig would have read a spent-down key as a full
$150 every single morning, never skipped a slot for budget, and discovered the truth only by
being refused mid-run — the same silent-loss shape as the org-budget fault above, and this
time `provider_budget_block` would not even have matched, since a key wall says "key limit
exceeded" and not "budget limit exceeded".

*Fix (`bin/lib.sh`, `bin/run-review.sh`, `bin/themes.sh`; backups `.bak-20260826b`).* New
`budget_remaining()` asks the provider for **`limit_remaining`**, which is right for both
shapes of key, and keeps `limit - usage_daily` only as the fallback for a key that reports no
`limit_remaining`. A key with no limit at all reads as unlimited, not as broke — returning 0
there would skip every slot for ever. `usage_today` is untouched and still carries the
within-run spend delta for the cap and the liveness signal. `provider_budget_block` also now
matches "key limit exceeded". The three log lines that said "left today" no longer do, because
on this key it is not true.

Verified by executing, not by reading: `budget_remaining` returns 149.9997 live against the
real key (the 0.0003 being the two probe requests), the fallback returns 28.00 for a
`limit 35 / usage_daily 7` key, an unlimited key returns 1e9 rather than 0, an unreachable
provider returns empty and leaves the existing "cannot reach openrouter" abort in charge, and
the full budget block computes `CAP=$5.50 WORK_CAP=$4.50` — unchanged from the healthy
baseline, so nothing is throttled — while a $0.90 pot correctly skips the slot without
consuming it.

*Headroom is not a concern.* 14 charms remain (idx 134-147). At the last-16 mean of $2.59
that is ~$36, and $77 even if every one hit the full $5.50 cap, against a $150 pot. At 5-6
slots a day the queue should finish around **2026-08-29**, comfortably before both the
2026-09-01 reset and the key's 2026-09-02 expiry. No extra pacing was added, deliberately:
the per-slot `min(MAX_RUN_BUDGET, REMAIN/SLOTS_LEFT)` still caps a slot at $5.50, and the
$150 only has to cover a fortnight's worth of work that will actually take three days.

*Two things to do by hand, neither of them the rig's job.* (1) **Our own key is NOT lost** —
it is saved at `/home/ubuntu/my-key-pi-auth.json`, mode 600, valid JSON, `type: api_key`
present. On or after 2026-09-01 put it back with
`cp /home/ubuntu/my-key-pi-auth.json /home/ubuntu/.pi/agent/auth.json`; cron re-reads it next
slot and nothing needs restarting. (2) That has to happen before **2026-09-02T02:06Z**, when
the colleague's key expires — although if the queue finishes on 08-29 as projected, it is
moot. Do not leave the old key in the file commented out: JSON has no comments and the whole
file fails to parse, which gives "Missing Authentication header" rather than a 401.

*Unchanged and still true:* `/api/v1/key` cannot see the org-member budget. The saved key
still reports `limit_remaining: 35` and `usage_daily: 0` today despite being refused all
morning. `budget_remaining()` is a guard against a wall the key can see; `provider_budget_block`
remains the only thing that catches the one it cannot.


**2026-08-26: the OpenRouter account hit its $500/month org-member budget, and the rig was
eating the queue rather than waiting for it.** 133 of 147 reviewed. Three slots since
midnight died in about one second each with

    403: {"message":"Org member budget limit exceeded (monthly limit). Contact your org admin.","code":403}

in a 104-byte `agent.log`. The budget resets **2026-09-01**. Nothing is wrong with the rig,
the charms, the substrate or the daily cap — the account simply cannot be billed until then.

*Why it was destructive rather than merely idle.* An empty review plus a non-zero rc is
indistinguishable, to `retry_or_give_up`, from a charm that cannot be reviewed. So each
charm got its one retry and was then abandoned with the cursor past it and no row in
`deferred.tsv`. **idx 134 `parca-scrape-target-operator` was already permanently lost and
135 `prometheus-scrape-target-k8s-operator` was one slot from the same fate.** At two slots
per charm and six slots a day, the remaining 13 charms would all have been abandoned by
about 08-29 — the programme would have ended at 133/147 having written nothing further.

*Why the existing guard did not catch it.* `run-review.sh` already aborts a slot without
consuming it when openrouter is unreachable, but that test is `usage_today` coming back
empty, and `/api/v1/key` answered 200 throughout: `limit_remaining` $28.94, `usage_monthly`
$36.86, `limit` 35. **That key's own counters know nothing about the org budget enforced
above it.** Same trap as the pgid CPU sum and as `last-connection` — the guard was reading a
field the failing path never writes. There is no way to pre-empt this by asking the API; the
only honest signal is what the provider said when a real request was billed.

*Fix (`bin/lib.sh` + `bin/run-review.sh`, backups `.bak-20260826`).* `provider_budget_block`
classifies a turn's log on **message text, never on a bare status code** — a 403 is also what
moderation returns, and that one *is* the charm's problem. It matches "budget limit
exceeded", "insufficient credits", "requires more credits", "negative credit balance",
"out of credits". `budget_abort` then treats the slot the way the substrate guard treats a
dead controller: cursor back onto the charm (or its deferred row restored), **no retry
spent, no `history.tsv` row written**, exit 0. Checked immediately after the first pass, so
a refused account does not go on to pay for deploys and a citation gate that cannot run,
and again at the no-usable-review block to catch a budget that runs out mid-run.

Deliberately **not** `defer_charm`: that execs on to the next charm in the same slot, which
is right for a substrate only one *kind* needs and catastrophic here — an account with no
money would defer the entire remaining queue in one slot. And `finish()` skips the history
row for such a slot, or six phantom `rc=1 bytes=0` rows a day would bury the corpus stats.

*Verified by executing it, twice over.* 17 unit assertions (real captured 403s match; **zero
false positives across all 124 successful runs' `agent.log`**; a moderation 403 and a generic
provider error do not match; cursor/retries/deferred effects correct for both the cursor
charm and a deferred one) plus 3 on the history suppression. Then **end-to-end against the
live fault at 11:15**, which is the only test that matters: the run picked 134, prepared it,
was refused, and gave the slot back in 30 seconds — cursor still 134, and `retries.tsv`,
`history.tsv` and `deferred.tsv` all byte-identical (md5 unchanged) afterwards.

*Repair.* Cursor rewound 135 -> 134; the `parca-scrape-target-operator` and
`prometheus-scrape-target-k8s-operator` rows dropped from `retries.tsv` (backup
`.bak-20260826`), so both charms have their full two attempts again. Neither had written a
review file, so nothing was skipped as "already reviewed". Cron is **on**: every slot until
09-01 now costs about 30 seconds and $0, and the queue resumes by itself the moment the
budget resets. **Nothing to do on 09-01.**

*One loose end.* `bin/themes.sh` runs Monday 08-31 02:30, still inside the outage, and will
fail both attempts. It is honest about it — it logs `FAILED rc=N — THEMES.md is UNCHANGED`
and leaves the old file rather than truncating it — but THEMES.md then stays stale until
09-07 unless it is run by hand after the reset. The 13 remaining charms need ~$33 at the
current ~$2.5/review, so the tail is about 2.5 days of slots once billing works again.


**2026-08-15 check, mid-absence. 82 of 147 reviewed (81 on disk after two were pulled for
re-run); the programme has been failing ~3 runs in 4 since 08-13 without ever looking
broken.** Nothing crashed, no substrate was down, no slot was skipped, `deferred.tsv` was
empty and the disk had 184G free. Every guard built for the 08-05 and 08-12 faults did its
job. The run log reads normally throughout. Completed reviews per day: 6, 6, 6 through
08-10/11/12, then **1, 1, 1** on 08-13/14/15 — fourteen slots for four reviews.

*Cause: the work model was silently repriced.* `bin/models.env` pinned the unversioned
alias `deepseek/deepseek-v4-pro`, and its output price rose from the **$0.870/Mtok** the
2026-07-24 benchmark recorded to **$2.262/Mtok measured live on 08-15 — 2.685x** — around
2026-08-12. Every budget number in the rig (`MAX_RUN_BUDGET`, the $4.50 work cap, the
citation reserve) was sized against the old price. So the first pass now exhausts the work
cap on its own and `start_spend_watchdog` SIGTERMs it mid-review: `rc=143`, and either a
0-byte review or a truncated one.

*Why it was invisible.* The failure presents as ordinary cost. `agent.log` is 0B on the
killed runs, which looks like the agent produced nothing — it is actually just pi's
block-buffered stdout lost to the SIGTERM, so it is a symptom of the kill, not a cause.
**The measurement that identified it was cost against wall-clock, not cost alone**: notary
ran a 45.8-minute first pass for $4.07 total and finished fine, while litmus was killed at
12.0 minutes having spent $4.71. Twelve minutes of identical work cannot cost more than
forty-five — that discrepancy is the whole diagnosis. Per-run cost alone hides it, because
the cap censors the data: every run now lands at $4.6-5.9 because that is where it is
killed, not what it wanted to spend.

*Damage.* Three charms abandoned outright after two attempts each — **80 litmus-operators,
82 jimm-k8s-operator, 84 gatus-k8s-operator**. Worse, two were *accepted while truncated*:
**78 hive-metastore** (24KB, 10 findings, `citations checked: 8`) and **79
identity-saml-provider** (27KB, 9 findings) cleared the 8K/1-finding floor while having had
zero depth passes and no citation correction. 85 postgresql landed the same way (20KB, 9
findings, 8 citations). Healthy 08-10 runs check 27-34 citations and carry 12-25 findings.
**The quality floor cannot see this**: it tests the artefact's size, and a first pass killed
at the cap still writes a plausible 24KB document. `citations checked:` is the metric that
exposes it, exactly as the 08-02 note predicted — a low count is the alarm.

*Fixes.* Work model switched to **`minimax/minimax-m2.7`**, the 2026-07-24 runner-up and
already the designated fallback: $0.380 in / $1.700 out measured live, ~3x cheaper on the
input term that dominates an agentic loop. Verified end-to-end — `pi -p --model
minimax/minimax-m2.7 --thinking high` with real tool use returned a correct `file:line`
citation. The five damaged charms (78, 79, 80, 82, 84) are requeued via `state/deferred.tsv`
with their `retries.tsv` counters cleared, and the two truncated reviews moved to
`logs/<repo>/review.truncated-20260815.md` so `review_is_good` cannot skip straight past
them. **The trade is context: 205K against deepseek's 1M**, so pi's auto-compaction will
fire much harder on the large charms — litmus (48K py_lines), postgresql (42K), kfp at idx
88 (54K). That is the first thing to check if quality drops; compare against the 08-10
baseline, not against the 08-13..15 runs, which are all truncated.

*A trap worth recording.* The obvious fix — pin the GA snapshot `deepseek-v4-pro-0813`,
advertised in OpenRouter's `/models` listing at the original $0.435/$0.870 — is wrong. It
actually bills **$1.320/$3.960**, worse than the alias on output. The listing price and the
billed price disagree. **Price a model by billing a real request and reading
`usage.cost_details`, never by reading `/models`.** Both figures in this section were
measured that way.

*The general lesson.* Every fault found in this programme so far has been something inside
the rig — a disk, a controller, a guard, a stale file. This one was entirely outside it and
changed nothing observable: same code, same charms, same logs, same exit paths. **A
dependency can be repriced under a running programme, and a fixed-dollar budget silently
converts that into truncated work.** The rig's caps are denominated in dollars but its real
constraint is tokens, and nothing was watching the exchange rate between them.

**2026-08-12 check, mid-absence. 74 of 147 reviewed; the programme had been stopped dead
for 17 hours and would not have restarted on its own.** Reviews 63-74 all completed
normally (08-09 15:02 to 08-11 17:59, healthy sizes and finding counts). Then every slot
from 08-11 20:00 onward logged `no machine controller reachable after 15min (tried:
concierge-lxd-4 concierge-lxd) — skipping slot without consuming it`. Five slots, cursor
pinned at 75. **Nothing was lost or corrupted** — an unconsumed slot leaves the queue
intact, exactly as designed — but nothing would ever have run again either.

*Cause.* Both LXD controllers were **gone**, not wedged: LXD's instance table held one row
(a charmcraft base instance), `storage-pools/*/containers/` held no `juju-*` directory, and
the `juju-controller-17c6ca`/`-93e000` profiles were orphaned at `USED BY 0` while their
custom volumes survived. LXD itself was healthy throughout — daemon up, `lxdbr0` addressed,
default profile intact — so this was not an LXD failure but the loss of two containers.

They went during the **2026-08-05 ENOSPC event**: `cleanup: could not list models on
concierge-lxd` first appears at 08-05 05:32 and never stops (92 occurrences). Exact
mechanism is not recoverable — the persistent journal was vacuumed during that same event,
so the deletion is not in `journalctl` (boot -1 retains 90 seconds). Ruled out by reading
the code: `cleanup.sh` only ever deletes in the `charmcraft`/`rockcraft` projects, and
`logcap.sh` stops containers, never deletes them.

*Why it stayed hidden for six days.* Reviews 63-74 were **all k8s charms**. The substrate
guard only probes the controllers the current charm's `kind` needs, so a dead machine
substrate is invisible until a machine charm comes up. Idx 75 (cos-proxy) was the first
since 08-04. **A guard that only checks what the current slot needs cannot notice a
substrate that nothing has needed for six days** — the corollary of the 08-09 lesson.

*Why it could never recover.* Two independent gaps, both fixed:

1. **No repair path for LXD.** `repair-controller.sh` deletes `controller-0` in a
   controller namespace — k8s only, as the 08-09 audit noted and left unaddressed. No
   restart fixes a container that does not exist anyway; only a re-bootstrap does. New
   `bin/repair-lxd-controller.sh` re-bootstraps a missing LXD controller with the matching
   client (`juju_3` for concierge-lxd, `juju` for concierge-lxd-4), behind a 12h cooldown
   whose **stamp is written before the attempt** so a hung bootstrap still counts. It
   refuses to run unless the daemon answers, `lxdbr0` has an address and the default
   profile has a root disk — bootstrapping into a sick LXD would burn a slot and leave
   debris. The substrate guard now dispatches to it by controller name.
2. **The guard pinned the cursor.** Skipping the slot protects the queue but stops
   *everything*, including the 39 runnable k8s charms sitting behind the one unrunnable
   machine charm. The guard now calls `defer_charm`: the charm moves to
   `state/deferred.tsv`, the cursor advances past it, and the slot carries on with the next
   charm. Deferral is not a drop — one deferred charm is retried at the top of every later
   slot, ahead of the cursor pick, so the tail returns by itself if its substrate does. A
   kind that has already failed its probe this slot is fast-forwarded without a second
   15-minute wait (`DEAD_KINDS`, exported across the `exec`). Charms that come off the list
   and then fail go back onto it rather than rewinding the cursor behind itself.

*Verified by execution, not by reading* — six scenarios in a sandboxed copy of the rig
(`ROOT` repointed, substrate and budget stubbed): defer + fast-forward, re-defer on a later
slot, recovery when the substrate returns, all-substrates-dead terminating cleanly instead
of looping, an exhausted queue still retrying its deferred tail, and a deferred charm whose
prepare fails going back on the list with the cursor untouched. The first attempt at that
sandbox silently tested the **live** rig — the copied scripts source `lib.sh` by absolute
path, so repointing `ROOT` in the copy changed nothing. It was the real lock that stopped
it. Same shape as the 08-09 reclaim that matched nothing: *a test that cannot fail is not
a test.*

*Restored.* Both controllers re-bootstrapped by hand on 08-12 (~4min each), under
`flock state/lock` so the 16:00 slot could not collide. Versions moved with the current
snaps: **concierge-lxd 3.6.23 → 3.6.27**, **concierge-lxd-4 4.0.5 → 4.0.12**. Reviews 1-74
were done against the older pair; the queue's remaining machine charms will be reviewed
against these. Idx 75 (cos-proxy) is unreviewed and next.

**2026-08-09 check, mid-absence, after a four-day stall.** 62 of 147 reviewed. Work stopped
after idx 62 at 05:38 on 08-05 with the disk full, and every slot from 08:00 on 08-05 to
08:00 on 08-09 logged `only 0G disk free (need 18G) — skipping slot without consuming it`.
**25 slots and four days lost, but nothing was corrupted or dropped**: a skipped slot is not
consumed, so the cursor stayed at 63 and the queue is intact. The operator added 20G, which
changed nothing — `resize2fs` reports the filesystem already spans the whole disk, so the new
space had already been absorbed and eaten.

*Cause.* `opentelemetry-collector` (idx 62) is configured to scrape `/var/log/syslog` and
also writes its own progress lines to syslog, so every line it read produced another line to
read. Measured while still running on 08-09: **~120MB/s**, which fills this 260G box in about
half an hour. Two leftover otelcol containers (`juju-c79b67-0` in `rv-otelcol`, `juju-68c03b-0`
in `rv-otelcol2`) had been doing this since 08-05; one alone held 177G of syslog.

*Why it did not recover on its own — the part worth remembering.* The stall was
self-sustaining. A full disk stops the juju API answering, so `reap-models.py` could not
list the models it needed to destroy, and cleanup skipped the exact containers that were
filling the disk. The one action that would have freed space was the one the full disk
prevented. Every one of those 25 slots ran a cleanup that could not help itself. Confirmed
by the fact that all four controllers answered normally the moment space was freed — they
were never independently broken.

*Fixed.* `bin/logcap.sh` does only filesystem work — no juju, no LXD API on the common path
— because those are precisely what stop working when it is needed. It truncates container
logs over 1G and stops a container that offends three times (truncation alone only mops up;
an offender refills within minutes). Juju controllers are protected by looking for
`juju-db`/`agents/controller-*` rather than by name, so it holds if a controller is rebuilt.
It runs on a **1-minute cron**, not from cleanup: a 30-minute fill cannot be contained by a
check that only runs at 4-hourly slot boundaries. The disk guard in `run-review.sh` now
escalates to that reclaim and re-checks before skipping, instead of halting for ever.

Verified end-to-end by creating a real runaway in a throwaway container: truncation, the
three-strike stop, and the controller exemption all fire. The first version was a silent
no-op — the LXD pool directory is root-only, so `for cdir in "$POOL"/*` expanded to nothing
as the `ubuntu` user cron runs as, and the script still exited 0. **A reclaim that reports
success without having matched anything is the same class of fault as a citation gate that
checks zero citations: test it by making it find something.**

*Still exposed.* cos-proxy (75), parca-agent (106), otel-ebpf-profiler (112) and
hardware-observer (139) all forward logs the same way and are still queued.

*Known-bad artefact.* Review idx 62 cleared the 8K/1-finding floor (32936B, 18 findings) but
is **code-only**: its own Deployment log says the machine never finished provisioning, and
`logs/opentelemetry-collector-operator/citations-final.log` is empty because the citation
gate died on ENOSPC mid-run. Re-run it if slots allow.

*Audit of the other skip paths (08-09).* The disk guard was not the only place that halted
without repairing. All 1727 lines of `bin/` were checked; four defects found and fixed, and
`bin/run-review.sh.bak-20260809` is the pre-change copy.

1. **Substrate guard never attempted repair** (`run-review.sh`, substrate wait). It skipped
   the slot for ever while `repair-controller.sh` — written for exactly a wedged controller
   — was only reachable from the wedged-destroying-models pre-flight. Now tried once before
   skipping, relying on that script's own 6h cooldown. Note it is **k8s-only**: it deletes
   `controller-0` in the controller namespace, so an unreachable `concierge-lxd`/`-lxd-4`
   still just skips. That gap is real and unaddressed. — **It cost six days.** Both LXD
   controllers were already missing when this was written on 08-09; nothing needed them
   until 08-11. Closed on 08-12 by `bin/repair-lxd-controller.sh` and `defer_charm`; see
   the 08-12 section at the top.
2. **Memory guard had no reclaim** — the disk guard's exact sibling. Since the lock is held
   at that point, no legitimate review is in flight, so any surviving agent process is an
   orphan; it now reaps those and re-checks. Not hypothetical: killing a run's parent on
   08-09 left its `timeout`/`pi` child alive holding its memory.
3. **A wedged run held the lock for ever.** Nothing bounded a run's wall-clock — the agent
   is capped, but `finish()` shells out to `lxc`/`juju` with no timeout and a wedged LXD
   hangs there still holding it. Every later slot would log "another review is still going"
   until someone logged in, with no recovery path at all — strictly worse than the disk
   stall, which at least recovered once space was freed from outside. A lock held beyond
   `STALE_LOCK_SECS` (8h, against real runs of 1.5-5h) is now treated as wedged and broken.
   `state/lock.acquired` records the acquisition time.
4. **A prepare failure silently dropped the charm.** The cursor advances before the work,
   and `exit 1` on prepare goes straight to the `finish` trap, which does not rewind — so
   the charm was written to history with `bytes=0` and never revisited. Same silent-loss
   class as the rc=0 stub and the no-op citation gate. Nothing had been lost to it yet;
   that was luck. The rewind rule now lives in one `retry_or_give_up` helper shared by this
   path and the no-usable-review path, rather than two copies that can drift.

Two things the testing caught that reading did not. The stale-lock breaker's first version
**killed itself**: `exec 9>` opens the lock before the `flock` attempt, so `fuser` reports
the taking-over process too, and the process-group kill took out cron's shell with it. It
now skips its own PID and signals PIDs individually. And `pkill -f` matches *any* process
whose command line contains the pattern, which is worth remembering when testing near it.

Left alone deliberately: `exit 1` on OpenRouter unreachable leaves the cursor untouched, so
nothing is lost — though note that after the key expires on **08-23** every slot will fail
in exactly that way. Budget exhaustion self-corrects at the daily reset, and the one-retry
cap is intended.

*Corpus quality check (08-09), over all 62 completed reviews.* Healthy, and not drifting.
1093 findings, **100% carrying both `**Where**` and `**Evidence**`**, 99.7% a `**Fix**`,
83% a `file:line`; no review under the 8K floor, none with fewer than 5 findings; median
33KB. Findings per review rose slightly (16.0 → 18.9, first third vs last) and size was
flat at 34KB, so the late reviews are if anything denser than the early ones. Deployment
is the strong signal against code-only drift: **every** charm was actually deployed bar
karapace (partial, and it says so), and 47 of 63 were exercised on *both* Juju 3.6 and 4.0.

The headline citation number is misleading and should not be quoted as-is. 1189 citations
checked, 152 unresolved — but classifying them: **75 are false positives from the checker
itself**, 25 are the known pre-08-02 dependency blindness, and only ~35 are candidate
genuine errors, i.e. **~2.9%**, and spot-checks show some of those are near-misses too
(alertmanager `charm.py:717` is inside the method starting at 711, just past `NEAR = 5`).
The false-positive mode is in `verify-citations.py`: it pairs citations to quotes at
*finding* granularity, then tests **every citation against every quote**, so in a
`**Where**` line listing several locations each quote flags all the others. Verified
against source: kyuubi `charm.py:56` really is `class KyuubiCharm(TypedCharmBase...)`,
alertmanager `charm.py:472-480` really is the key-path mapping, k6 `k6.py:52-55` really is
`resume()`. Worth fixing the checker (pair positionally, or skip quote-checking when a
Where line has multiple citations) so the residual number means something.

*One real gap found and fixed.* **THEMES.md was six weeks and 49 reviews out of date.** The
08-03 weekly run did fire across 50 reviews but the agent died with
`Provider finish_reason: error`, leaving THEMES.md untouched from 07-27 — and it logged
`done rc=1 (34671 bytes)`, a healthy-looking size that was just the stale file measured by
`wc`. Nothing retried. Same class as the 0-byte review that passed `[ -s ]`: the check
tested a file the agent *overwrites*, so size proves nothing. `themes.sh` now compares
content against `logs/THEMES.prev.md`, retries once, and says FAILED plainly when the file
did not change. The next scheduled run (Mondays 02:30) will regenerate it across ~64
reviews.

*Projection.* Restarted by hand at 12:41 on 08-09 on idx 63 (vault-k8s-operator). 85 left
and about 48 slots to the operator's return on 08-17, so expect roughly 110 of 147 done and
a low-priority tail (remaining scores 57-91 against 105-167 for the finished half). The
OpenRouter key expiring **2026-08-23** is now the binding constraint on the tail.

**2026-08-02 check, the evening before the two-week absence.** 48 of 147 reviewed, six
slots a day for three days running, $24-27/day against the $35 cap, disk flat at ~139G
free. No crashes since the host-side fix. Review quality is not drifting — mongodb-k8s
reproduces a real crash-loop (exit 48 on `/tmp` permissions), ties it to upstream issue
\#467, and enumerates the caught-exception list to prove `ShardingMigrationError` is
missing. The quality floor did its job once: opensearch-operator wrote a 0-byte review at
12:27 on 08-01, was rejected, and the retry at 18:08 landed 34831B/17 findings.

One real fault found and fixed — see "The citation checker was blind to dependency code"
under Known residuals. Projection: 99 left, ~Aug 19 at 6/day or ~Aug 21 at the 10-day
average of 5.3/day, against the OpenRouter key expiring Aug 23. The remaining queue scores
78-105 where the finished half scored 105-167, so anything that slips is the low-priority
tail.

**2026-07-30 check, after the VM was killed.** 31 of 147 reviewed. The VM died hard at
03:27 and stayed down until 12:14 — **three slots lost** (04:00, 08:00, 12:00). Nothing
needed restoring: the kyuubi run had finished cleanly at 01:28, so no run was in flight,
and the state came back consistent (cursor 30, no retries pending, no leftover review
models, namespaces or PVCs, all four controllers up, both LXD containers running). A
catch-up run on #30 was started by hand at 12:22.

The shutdown was **not** the guest's doing and not a resource problem — no OOM, no
ext4 error, 176G free. From 02:55 the kernel logged escalating `soft lockup` warnings
across many CPUs, including `swapper` (the idle task), while etcd failed its readiness
probe; the journal then stops mid-line with no shutdown sequence. That signature — the
guest stalling for half an hour and then being cut off — is the **host**, not this box.
If it recurs there is nothing to fix in here.

Cron self-heals after a reboot, but only at the next 4-hourly boundary, so a boot at
12:14 leaves the box idle until 16:00 — about one review per outage. An `@reboot`
catch-up entry was considered on 07-30 and **deliberately declined**: cron already
resumes on its own, and a catch-up firing against a half-booted cluster could spend a
slot producing a shallow review. The idle window is an accepted loss, not an oversight.

The real find was not the reboot: **the cost/citation squeeze had come back**, and the
2026-07-28 fix was treating a symptom. Two mechanism bugs found and fixed — see Budget.

## The rig is LIVE

Cron has been live since 07:23 on 2026-07-25. It fired every 3 hours until the evening of
2026-07-25, when the cadence was slowed to **every 4 hours (6 runs/day)** to buy each run
more wall-clock — see Cadence below. The first day's slots at 09:00,
12:00, 15:00 and 18:00 all fired. Five reviews exist; four are good
(`temporal`, `grafana-agent`, `catalogue`, `self-signed-certificates`, plus `traefik`
in progress), and the findings hold up on inspection — the traefik run found a charm
that dies permanently in `__init__` on an invalid `routing_mode`, confirmed on both
Juju versions.

To pause it:
```bash
crontab -l | sed 's#^\(.*run-review\|.*themes\)#\##' | crontab -   # comment both out
# or just: crontab -r    (removes all cron; keeps the harness and reviews)
```

Watch it:
```bash
tail -f ~/charm-review/state/runs.log
cat ~/charm-review/INDEX.md
```

## What the first half-day of unattended running exposed

Five real faults, all now fixed. If something looks wrong later, read this first.

### 1. Cleanup blocked on model teardown and was eating the slot

`juju destroy-model --force --no-wait` does **not** return promptly. It waits for the
model to actually go — 7-15 minutes for a k8s model, and *for ever* for one whose
undertaker worker has died. Re-issuing destroy against an already-`destroying` model
blocks for ever too, so one stuck model poisoned every later cleanup.

Cleanup runs three times per review, so by the 18:00 slot three stuck models were
costing **42 minutes before the agent even started**, and it was growing.

Fixed: `bin/reap-models.py` now fires every destroy off detached and returns in under a
second. It records how long each model has been dying and, past 30 minutes, deletes the
model's kubernetes namespace directly to get the pods and PVCs back. `cleanup.sh` just
calls it.

### 2. A wedged model degrades the controller for ever

This is the one that would have killed the programme. Force-destroying a k8s model on
juju 4.0.5 sometimes tears down the model's `modeloperator` before its units are
removed, so the model can never finish destroying — the agents that would confirm the
removal are already gone. `rv-ga-deep` and `rv-ga-j4` are both in that state with empty
namespaces.

A model in that state is not inert. Its dependency engine keeps restarting
`valid-credential-flag`, `migration-master` and `migration-inactive-flag`, each failing
instantly with `watcher registry closed`, **about 60 times an hour, for ever**. Three
wedged models were producing ~180 restarts an hour, starting at exactly the moment the
grafana-agent run wedged them. At 3-4 wedged models per run and several runs a day that
compounds until the controller is unusable — and it had already started costing
coverage: the grafana-agent review records "Juju 4 deploy attempted on concierge-k8s-4
but failed due to broken controller (no modeloperator pods)".

Fixed: `bin/repair-controller.sh` restarts the controller pod to clear the wedged
in-memory engines. Pre-flight calls it when two or more models on a controller have
been dying longer than 30 minutes, at most once every 6 hours, while the lock is held
and nothing is deployed.

**Verified by hand on 2026-07-25 at 20:04.** The controller came back in 41 seconds, all
three wedged models were reaped by the revived undertaker, and the crash-loop rate went
from ~180/hour to **zero**. Note `juju destroy-model --force --timeout 0` does *not*
clear a wedged model — that was tested for 11 minutes and failed. Restarting the
controller is the only repair that works.

### 3. The overnight half of every day was reviewing on a starvation budget

The OpenRouter allowance resets at **00:00 UTC** — 12:00 local, confirmed when spend
went back to $0 at noon. But the per-slot cap divided what was left by the number of
slots to *local* midnight. So the four afternoon slots each got the full $3.00 cap and
the four overnight slots got squeezed to $1.25, $1.07, $0.83 and $0.50 — the watchdog
would have killed those agents almost immediately.

Fixed: `SLOTS_LEFT` now counts against the UTC day. Every slot gets a flat $2.50.

### 4. The rig was filling its own disk, via fault 2

Free space fell 205G → 186G in the first day. The cause was not what it looked like.
Ruled out by measurement: PVCs are tracked one-for-one with their models, LXD is stable
at two controller containers with no orphans, and containerd is not accumulating
garbage — removing an image really does free its overlayfs snapshots (tested: 2 images
freed 140MB and 7 snapshot dirs), so `cleanup.sh`'s image pruning works.

The actual cause: **the juju controllers' k8s volumes are sparse files behind a loopback
ext4, and deleting data inside them never shrinks the backing file.** The k8s-4
controller had grown to **8.7G of backing file for 877M of live data — 7.9G of pure
ratchet** — while the healthy k8s-3 controller had only 0.7G of ratchet with *more* live
data. The difference is write volume, and the write volume was the log flood from fault
2's crash-looping workers. So fault 2 was also the disk leak.

Fixed twice over: the repair stops the write flood, and `cleanup.sh` now runs `fstrim`
over the CSI mounts every cycle, which punches the freed blocks back out of the sparse
files. The first run reclaimed **7.7G**; free space went 186G → 197G. Cleanup also now
logs per-component sizes (`cleanup: usage — containerd … lxd … k8s-volumes …`) so any
future growth is attributable from the log instead of guessed at.

### 5. Build containers were never cleaned up — the worst leak of the lot

`charmcraft` and `rockcraft` build containers are 1.3-2.8G each, and cleanup's loop had
**never deleted a single one**. They live in their own LXD *projects* (`charmcraft`,
`rockcraft`), and a bare `lxc list` only shows the `default` project — so the loop looked
correct, ran every cycle, and silently matched nothing. `lxc storage volume list` is
project-scoped too, which is why an earlier sweep for orphans came up clean and LXD was
wrongly written off as stable.

The rig had produced five of them in one day (~9G). At that rate it would have filled the
disk around the middle of the programme. Fixed: the loop now iterates the projects
explicitly with `sudo lxc list --project`. Two things are deliberately spared —
`base-instance-*` (the cached buildd base each tool clones from, expensive to rebuild) and
anything created before `state/epoch`, because this box had the operator's own charmcraft
work on it before the harness existed.

Reclaimed 9G on the first run; LXD went 25.9G → 16.7G, free space 187G → 196G.

**This was found by the per-component `cleanup: usage` line added for fault 4** — LXD
jumped 17.2G → 25.9G across one review and the log made it obvious. Without that line it
would have surfaced as an unexplained disk-full a fortnight later.

### Also fixed

* A run that produced no review (`datahub-k8s-operator`, 12:00) still ran both citation
  passes against a file that did not exist, burning 15 minutes and ~$0.5 being told so.
  Those passes are now skipped when there is no review.
* That run also consumed its queue slot silently. The cursor is now rewound so the charm
  is retried in the next slot — once only, tracked in `state/retries.tsv`, so a charm
  that genuinely cannot be reviewed cannot wedge the queue.

## Cadence

**Every 4 hours, 6 runs/day** (was every 3h / 8 runs/day until the evening of 2026-07-25).
The change was made because *every* run was ending on the harness's own depth ceiling —
55% of a 2h budget, or 3 passes — rather than because the agent had run out of work, while
finishing in 32-112 minutes of a 180-minute slot. So the slot was never the constraint; my
ceilings were.

Now: 3h agent budget, depth passes until 60% of it, up to 4 passes. Worst case is roughly
170min of agent time plus ~45min of citations and polish, which fits a 4h slot with ~25min
to spare; the `flock` means an overrun just skips the next slot rather than overlapping.

`SLOT_HOURS` in `bin/lib.sh` and the `*/4` in the crontab **must stay in sync** — the
per-slot budget maths counts remaining slots in the UTC day from `SLOT_HOURS`.

Coverage arithmetic, against the stated target of **the morning of 2026-08-17**: 143
charms left (142 unreviewed + datahub reclaimed) at 6/day needs ~24 days, so the queue
finishes **around 2026-08-18 if every slot lands a review, more realistically 2026-08-20**
once some slots are lost to failures, retries and the resource guard. That overshoot was
accepted deliberately in preference to a shallower 3h cadence.

There is no hard "finish" event — the harness just works down a priority-ordered queue, so
the practical reading is: ~130 of 147 done by the morning of 08-17, and the remaining
(lowest-priority) tail trickles in over the following few days. If the date ever becomes
hard, the lever is simply to stop it: whatever is done is done, and what is left is the
least valuable part of the queue.

**Re-measured 2026-07-30**, replacing the estimate above. Throughput has held at the full
6/day on every complete day (07-26, 07-27, 07-28; 07-25 and 07-29 lost one slot each), and
in 32 runs the queue has lost **nothing** to the resource guard, the budget skip or the
lock — one no-review run (datahub) and the rest to host reboots. So the nominal rate is
the real rate, and the only leak is the host.

116 charms remain. At 6/day that is ~19 days: the queue finishes **around 2026-08-18-19**,
and roughly **137 of 147 are done by the morning of 08-17** — about ten short, all from the
bottom of the priority order. The three slots lost on 07-30 cost half a day; the projection
is a little *better* than the 07-28 one only because throughput held.

## The four controllers

| controller | juju | substrate | health |
|---|---|---|---|
| `concierge-k8s-4` | 4.0.5 | Kubernetes | the unstable one — see fault 2 |
| `concierge-k8s-3` | 3.6.25 | Kubernetes | fine |
| `concierge-lxd-4` | 4.0.12 | LXD | re-bootstrapped 2026-08-12, was 4.0.5 |
| `concierge-lxd`   | 3.6.27 | LXD | re-bootstrapped 2026-08-12, was 3.6.23 |

## How a run works

1. `cleanup` pre-flight (now sub-second) + controller repair if models are wedged +
   resource guard (skips the slot if <18G disk or <4G mem).
2. `prepare` — working copy with 400 commits of history, charmhub metadata, the raw
   Discourse docs, open issues, test/CI inventory.
3. **First pass** — the agent deploys, observes, reviews code/tests/docs (cap 3h, and it
   is told that figure in its brief so it paces against it).
4. **Depth passes** — the agent stops early on its own, so the harness hands the review
   back with a prioritised "what you skipped" list and repeats until 60% of the budget
   is used or 4 passes. Took catalogue from 8 findings to 18, traefik from ~10 to ~18.
   Note a 0-byte `deepen-N.log` does NOT mean a wasted pass — it means the agent ended by
   writing files rather than printing a summary. Catalogue's 8→18 pass logged 0 bytes.
5. **Citation correction** — `verify-citations.py` checks every `file:line` against the
   source. About half of first-draft citations are wrong; the agent is fed the
   mismatches, up to twice. Residual is ~1 bad citation per review.
6. **Polish** — a short Claude-sonnet pass.
7. `cleanup` via EXIT trap, then `index`.

## Budget

Resets to **$35** at 00:00 UTC / 12:00 local (raised from $20 on 2026-07-25).
`MAX_RUN_BUDGET` is $5.50, so every slot gets a $5.50 cap — $4.50 for the exploring
passes and a $1.00 `CITE_RESERVE` that guarantees the citation-correction passes still
run. 6 slots × $5.50 = $33 of $35, leaving room for the weekly themes run. Under $1.50
left, a slot is skipped without consuming the queue.

**Money became the binding constraint on 2026-07-28** — the line that used to sit here
saying it never had was written when runs cost $2.4-3.2. See below.

### The cost/citation squeeze (found 2026-07-28, fixed)

Reviews grew as the rig went: mean cost $3.17 → $4.51 and mean review 32.1K → 37.8K
between the first ten runs and the last ten. The depth loop began consuming the entire
work cap, so the citation-correction pass — the thing that makes `file:line` references
trustworthy — got skipped on **3 of 12 runs** with *"already at its $5.00 cap"*.

Residual bad citations went from ~1 per review to **5-8**: postgresql shipped 8 of 25
wrong, blackbox 6 of 28, alertmanager 17 of 51. The old $0.35 reserve did not cover even
one correction pass ($0.30-0.50), let alone the two the loop can run.

Fixed by raising `MAX_RUN_BUDGET` $5.00 → $5.50 *and* `CITE_RESERVE` $0.35 → $1.00, so
the reserve comes out of new headroom and the work cap stays at ~$4.50 — depth is
unchanged. Day total is now at most $33 of $35 against $26-28/day observed. Both live in
`bin/lib.sh`. If a day does run hot the per-slot `min(MAX, REMAIN/SLOTS_LEFT)` squeezes
the late slots, and the `CAP*0.5` floor stops the reserve from ever exceeding half a
squeezed slot's budget.

**This is the failure mode to re-check first if reviews start looking untrustworthy**,
because it is self-reinforcing: bigger review → more citations → more errors → less
budget left to fix them. The one-line check is
`grep -c "skipping fix-citations" state/runs.log`.

### It came back, and raising the numbers was the wrong fix (2026-07-30)

That check read 5, not 3: it recurred on **k6** and **kyuubi** (2026-07-29/30), which
shipped **9 bad citations of 19 and 9 of 20** — 45%, against a residual of 0-2 on the
eight healthy runs either side of them. Both overran the $5.50 cap, at $5.768 and
$6.515, and both had citation correction skipped. Raising `MAX_RUN_BUDGET` and
`CITE_RESERVE` on 07-28 bought two clean days and then the growth in review size ate
the new headroom too. Money was never the bug. Two mechanism bugs were:

1. **Only the first pass was watchdogged.** The spend watchdog wrapped the opening
   agent invocation and nothing else. The depth passes went through `agent_turn`, which
   checked the cap *before* starting a pass and never again — so a pass beginning at
   $4.49 of a $4.50 work cap ran unbounded to its 40-minute timeout and spent straight
   through the reserve sitting behind it. Fixed: the watchdog is now a function,
   `start_spend_watchdog`, and **every** turn gets one.

2. **The reserve was not a floor.** The citation passes were gated at the absolute
   `$CAP`, so once the work phase reached the cap there was nothing left for them —
   precisely the case the reserve exists to prevent. Fixed: their cap is now measured
   from where the work phase actually stopped (`CITE_CAP = max(CAP, spent + RESERVE)`),
   so the correction always gets its reserve and never less than before.

The two are a pair, and fix 1 is what bounds the cost — fix 2 alone would just let runs
spend more. Together: when the work phase behaves, `CITE_CAP` is exactly $5.50 and
nothing changes; when it overruns, the ceiling lifts only for the cheap pass that makes
citations trustworthy. Expect run cost to *fall* back to ~$5.00-5.50 from the $5.6-6.5
of the last four runs, because the depth passes can no longer overshoot.

Verified before shipping: `wait` still blocks on a turn started with `exec setsid`
(the depth loop would silently collapse to one pass if it did not — a background job in
a non-interactive shell is not a process-group leader, so `setsid` does not fork and
`$!` stays valid), the group kill takes pi down with its timeout wrapper and leaves no
strays, and the `CITE_CAP` arithmetic is a no-op for a work phase that stays in budget.

**If citations look bad again, do not raise the numbers.** Check first whether a turn
overran its cap — `cat logs/<repo>/watchdog.log` — and whether the log says
`work phase overran, citation cap raised to $N`.

## Models (see state/benchmark.md)

- Work: `deepseek/deepseek-v4-pro` — best citation accuracy, cheap output, 1M context.
- Fallback: `minimax/minimax-m2.7` (NOT m3 — m3 invents YAML line numbers).
- Polish + weekly themes: `anthropic/claude-sonnet-5`.
- Unusable on this key: qwen/* (privacy 404), z-ai/glm-5.2 (auth error), kimi-k2.7-code.

## Known residuals / where to look first

- **Citation accuracy is the weak point of the base model**, but the reported
  `problems: N` overstated it — see below. `logs/<repo>/citations-final.log` records what
  survived. Note the correction pass gets steadily *less* effective the more there is to
  correct — alertmanager's two passes only took 22 problems to 17, where parca's took 10
  to 2 — so the reserve keeps a small problem small rather than rescuing a large one.

### A wedged turn burned 2h08 for 1 second of CPU (fixed 2026-08-04)

The spend watchdog cannot see a turn that has stopped working. It polls OpenRouter usage,
so a turn blocked on a provider call that never returns spends nothing, never approaches
the cap, and is stopped only by its wall-clock timeout — at the full length of the turn.

Caught live: `hook-service-operator`'s `deepen-2` on 2026-08-04 started at 08:40 and used
**1 second of CPU in 2h08**, with a 0-byte log and no write to the review or the notes,
before dying on its 7816s timeout having contributed nothing. The review was safe — 30748B
and 19 findings from the first pass and `deepen-1`, comfortably over the floor — so this
costs *depth*, not charms. That is why it is easy to miss: `history.tsv` shows rc=0 and a
healthy byte count, and nothing anywhere says the slot did two-thirds of nothing.

`start_spend_watchdog` now watches liveness as well as spend, on the same 90s poll, and
stops a turn that has made no progress for `LIVENESS_STALL` (1800s). Progress is any of:

- **bytes written to the turn's log**, or
- **a write to `$REVIEW_FILE` or `$NOTES_FILE`** (mtime), or
- **`LIVENESS_MIN_CPU` (5) CPU seconds** accumulated by the turn's whole *process group* —
  pi shells out to juju and kubectl, so the group is the unit of work, not the pid.

The clock resets only on *meaningful* progress rather than on any change at all, so a
wedged client ticking the odd CPU second still trips it.

**Do not drop the artifact-mtime signal and rely on the log.** 53 of the 247 pass logs
across the first 57 runs are 0 bytes — 21%, on runs that finished perfectly well (hydra,
istio-ingress, mysql-operators, mongodb-k8s). A pass that writes nothing to stdout for
half an hour is normal pi behaviour, so log growth alone would kill working turns.

Thresholds have a wide margin: the bar is 5 CPU seconds per 1800s, or 0.28% utilisation,
against the wedged turn's 1s in 7680s (0.013%) — about 20x. A false positive costs one
killed pass, not a charm, since the review is already on disk and the pass dies exactly as
the timeout would have killed it. Note the depth loop's `|| break` is unchanged, so a
liveness kill of a *depth* pass ends the depth loop and hands the time to citations and
polish rather than to another depth pass; a liveness kill of the *first* pass still leaves
the depth passes to run.

`WATCHDOG_POLL` (default 90) exists so this can be exercised in seconds rather than
half-hours. Tested against six cases: wedged (killed), CPU-busy (survives), log-writing
(survives), review-writing (survives), true hang (killed), and over-cap (still killed, so
the original spend behaviour is intact).

### The resource guard never checked whether anything could be deployed (fixed 2026-08-04)

`run-review.sh` refused to start a slot on low disk or low memory, but nothing asked
whether the *substrate* was up. A run that cannot deploy does not fail — it writes a
code-only review, which clears the 8K/1-finding floor, is recorded as done and is never
revisited, because the cursor advanced before the work started. Exactly the silent-drift
shape the quality floor was built to catch, arriving by a route the floor cannot see.

The way in is a host reboot. Cron resumes at the next 4-hourly boundary regardless of
whether k8s and LXD have finished coming up — and on 2026-07-30 a run started at 12:22,
eight minutes after the 12:14 boot, and spent its full 3h producing a 3.6K review with
`citations checked: 0`. (That run is also the `rc=124` case from the same day, so a cold
substrate is not *proven* to be the cause — but it is the reason not to find out.)

The guard now probes the controllers the charm's `kind` needs — `concierge-k8s-4/3` for
k8s, `concierge-lxd-4/concierge-lxd` for machine — via `juju status -m <ctl>:controller`
(`controller_ready` in `lib.sh`, ~200ms, exits 2 rather than hanging when unreachable).
One API call covers both layers: the k8s controllers are pods and the LXD ones are
containers, so a controller that answers proves the substrate under it is up. Probing
`kubectl`/`lxc` as well would only add ways to get a false negative.

Behaviour, in order of preference:

- **Both up** — proceed silently.
- **One up** — proceed, and log it. One Juju version is enough to review on; the
  cross-version comparison the brief asks for is the part that is lost.
- **Neither** — re-probe every `SUBSTRATE_PROBE_INTERVAL` (60s) for up to
  `SUBSTRATE_WAIT_MAX` (900s), then **skip the slot without consuming it**. The expected
  case is transient, so wait it out rather than skipping on the first miss; 15 min is
  nothing against a 4h slot, and the wait holds the flock so it cannot overlap the
  next slot.

There is deliberately **no "waited long enough, proceed anyway" valve**. If the substrate
is genuinely dead, an unspent slot leaves the queue intact and recoverable, whereas a
queue burned through with code-only reviews is neither — the cursor has moved past every
one of them. Halting is the recoverable error, so the guard biases to it. The cost of the
guard being wrong in the other direction is one lost slot, which the rig already absorbs.

This also removes the objection recorded against an `@reboot` catch-up entry on 07-30
("a catch-up firing against a half-booted cluster could spend a slot producing a shallow
review"). The entry is still **not** added — that decision stands on its own.

**Rebooting the host safely.** A reboot *mid-run* silently costs that charm: the cursor
advanced at the top of the run, and the `review_is_good` rewind at the bottom never
executes, because SIGTERM kills the script at its `wait`. The EXIT trap does still fire,
so cleanup and a `history.tsv` row happen — but not the rewind, and `index.sh` counts any
review over 500B as done. So reboot only between runs, and let the lock arbitrate rather
than the clock:

```bash
flock -n /home/ubuntu/charm-review/state/lock -c 'sudo systemctl reboot'
```

That refuses if a run is in flight. Prefer early in the gap after a run finishes (runs
have all landed within ~2h05 of their slot) over the last minutes before the next one, so
the cluster has time to settle — the guard will now wait for it either way.

### The citation checker was blind to dependency code (found and fixed 2026-08-02)

`verify-citations.py` indexed only `$WS/repo`. Canonical's data-platform charms have moved
to the "single kernel" pattern — opensearch-dashboards' `kubernetes/src/charm.py` is 22
lines of imports and the real logic ships as the PyPI distribution
`opensearch-dashboards-charms-single-kernel`. So every citation into the code actually
worth reviewing read as `no such file in the repo`, and the run on 08-02 scored
**`citations checked: 0, problems: 9` with all nine citations correct**.

The damage was not wrong reviews — the correction agent went and read the pip-installed
package itself and fixed eight genuinely wrong line numbers, removing no findings, and the
mongodb-k8s review honestly labelled its citations `(installed library
mongo-charms-single-kernel 1.8.52, not in this repo)`. The damage was that the gate
contributed nothing on those runs while two correction passes (~13 min, ~$0.50-1.00 each
run) were spent re-deriving what the checker should have confirmed — and that the model
learned to stop emitting line numbers at all, which is why mongodb-k8s and opensearch have
zero checkable citations.

Fixed in three places:

* `bin/fetch-deps.py` (new) unpacks the repo's **direct** declared dependencies into
  `$WS/deps`. Wheels first — both single-kernel packages ship `py3-none-any`, so nothing
  is built or executed on the normal path; an sdist is only accepted when no wheel exists.
  Bounded hard because it runs unattended: `--no-deps`, 25 packages, 200MB, 90s per
  package, 300s overall, `--retries 2 --timeout 15`, and every failure non-fatal. Measured
  cold: 5s for the heaviest repo (9 deps, 15MB); an unreachable index gives up in 12s.
* `verify-citations.py` takes extra roots and searches the repo **first**, so a name in
  both resolves to the copy under review. Dependency hits are labelled `(dependency)`.
* `prompts/review.md` and `prompts/fix-citations.md` tell the agent `$WS/deps` exists and
  that citations into it are checked like any other — without this the model keeps
  omitting line numbers it thinks will be rejected.

Regression-tested across all 49 existing reviews: repo-only output is **byte-identical**
to the old checker. With deps indexed, four reviews improve and none get worse —
opensearch-dashboards `0 checked/8 problems → 8/0`, pyroscope `13/7 → 19/1`, tempo
`11/3 → 14/0`, spark-integration-hub `22/0 → 24/0`. Note pyroscope and tempo were affected
too and their problem counts looked ordinary, so the blind spot was wider than the
data-platform charms it was found on. At least mongos-k8s (#65), litmus (#80) and
pgbouncer (#91) are still to come in the queue.

### `problems: N` was inflated by the checker (fixed 2026-07-28)

Verified by hand against upstream source at the reviewed commits: **the findings are
real and the citations are mostly right.** Six of postgresql-k8s's eight reported
problems were the checker's fault, not the model's.

Two false-positive mechanisms in `verify-citations.py`:

1. **Definition vs call site (fixed).** A quote like `` `update_config()` `` substring-
   matches the *call* `self.update_config()` but not the *definition*
   `def update_config(self, ...)`. So a finding that correctly cited where a method is
   defined got reported as wrong and pointed at its caller. `quotes_in()` now drops lone
   undotted names — the asymmetry can't arise for a dotted chain like
   `self.ingress.on.ready`, so those stay checked. Measured, at the reviewed commits:
   postgresql 6→2 problems, alertmanager 12→9, loki 5→4, parca 3→3 (no instances), with
   `citations checked` unchanged in all four. The filter was validated against 10 known
   false positives and 9 known-genuine catches before shipping.

2. **Prose bleed (still present).** `quotes_in()` pools every backtick span in the whole
   **Evidence** section and tests each against every citation in **Where**, so a token
   from the surrounding narrative (`juju resolve`, `config-changed`) gets matched against
   a citation pointing at different, correct code. Both of postgresql's two remaining
   problems are this. Fixing it means preferring fenced code blocks over inline spans and
   pairing each quote to its own citation; not attempted yet because it is harder to make
   safe than mechanism 1 was.

Reassuringly, **the correction agents largely defend against this themselves** — they
re-read the source and push back rather than deleting findings. loki, parca and
prometheus all logged "0 findings removed", and prometheus and alertmanager independently
diagnosed the checker as being at fault in their `fix-citations-*.log`. So the false
positives cost budget and noise, not correctness.

**Read `problems: N` as a noisy upper bound, not a defect count.**
- A charm that genuinely cannot be deployed finishes fast and shallow — expected, and
  the review says so.
- Some observability charms need `ubuntu@26.04`, which this cluster does not offer, so
  those integrations get skipped. The traefik review records this.
- `state/cursor` is the next queue index; the harness skips charms already reviewed, so
  editing the cursor or deleting a review file both work as you'd expect.
- `state/destroying.tsv` is the reaper's memory of what is still tearing down.
- Weekly `themes.sh` (Mon 02:30) writes `THEMES.md` — first fire is 2026-07-27.

## Environment gotchas

- `pi` hangs forever without `--no-approve` non-interactively.
- Charmhub info API needs `fields=...,result.publisher`; docs are at
  `https://discourse.charmhub.io/raw/<topic-id>`.
- `k8s ctr` doesn't exist; use `/snap/k8s/current/bin/ctr --address
  /run/containerd/containerd.sock -n k8s.io`.
