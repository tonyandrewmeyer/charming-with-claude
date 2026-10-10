#!/bin/bash
# One-shot: put the user's own OpenRouter key back in ~/.pi/agent/auth.json, replacing the
# colleague's loaned key that has been in there since 2026-08-26.
#
# It waits for `state/lock` first, so the swap lands BETWEEN slots. A mid-slot swap is not
# safe: `pi` re-reads auth.json at every turn, but run-review.sh captures OR_KEY once when
# lib.sh is sourced, so the turns would start billing the new key while the watchdog kept
# polling the old key's usage_daily. That reads as "no spend", and spend is the primary
# liveness signal since 2026-08-17 — through a long deploy, where the log, the review and
# the notes all go quiet too, the watchdog would kill a perfectly healthy turn at
# LIVENESS_STALL and burn the charm's one retry. The end-of-run cost row would be wrong and
# the work cap unenforced for the rest of the slot as well.
#
# Holding the lock cannot cost a slot: a run that finds it held logs "another review is
# still going" and skips WITHOUT consuming the queue, and this holds it for about a second.
set -u
ROOT=/home/ubuntu/charm-review
SRC=/home/ubuntu/my-key-pi-auth.json
DST=/home/ubuntu/.pi/agent/auth.json
LOG=$ROOT/state/keyswap.log
say() { echo "[$(date -Is)] keyswap: $*" | tee -a "$LOG" >> "$ROOT/state/runs.log"; }

fp() { python3 -c "import json,sys;k=json.load(open('$1'))['openrouter']['key'];print(k[:12]+'...'+k[-4:])" 2>/dev/null; }

[ "$(fp "$SRC")" = "$(fp "$DST")" ] && { say "own key already in place — nothing to do"; exit 0; }

exec 9>"$ROOT/state/lock"
say "waiting for state/lock (current key $(fp "$DST"), restoring $(fp "$SRC"))"
if flock -w "${KEYSWAP_WAIT:-21600}" 9; then
  say "lock acquired, no slot in flight"
else
  # Six hours is past any real run (1.5-5h) and past the point the stale-lock breaker would
  # fire, so the holder is wedged. The loaned key expires 2026-09-02T02:06Z; a swap under a
  # dead run beats waking up to a key that no longer bills.
  say "WARNING could not get the lock in ${KEYSWAP_WAIT:-21600}s — swapping anyway"
fi

# Validate before overwriting, and write-then-rename so no reader ever sees a partial file:
# a truncated auth.json fails to parse and pi answers "Missing Authentication header",
# which looks nothing like a key problem (2026-08-23).
python3 - "$SRC" <<'PY' || { say "ABORT source file is not valid pi auth JSON"; exit 1; }
import json,sys
d=json.load(open(sys.argv[1]))
o=d["openrouter"]
assert o["type"]=="api_key", o.get("type")
assert o["key"].startswith("sk-or-v1-") and len(o["key"])>40
PY

install -m 600 /dev/null "$DST.new" && cat "$SRC" > "$DST.new" && mv -f "$DST.new" "$DST" \
  || { say "ABORT could not write $DST"; rm -f "$DST.new"; exit 1; }

NOW=$(fp "$DST")
if [ "$NOW" = "$(fp "$SRC")" ]; then
  say "restored own key $NOW (mode $(stat -c %a "$DST")); loaned key backed up at /home/ubuntu/loaned-key-pi-auth.json"
  say "$(curl -sS --max-time 20 -H "Authorization: Bearer $(python3 -c "import json;print(json.load(open('$DST'))['openrouter']['key'])")" \
        https://openrouter.ai/api/v1/key | python3 -c "
import json,sys
d=json.load(sys.stdin)['data']
print(f\"provider says limit=\${d['limit']} reset={d['limit_reset']} remaining=\${d['limit_remaining']:.2f} expires={d['expires_at']}\")" 2>/dev/null || echo "provider check failed")"
else
  say "ABORT verification failed — $DST holds $NOW"; exit 1
fi
