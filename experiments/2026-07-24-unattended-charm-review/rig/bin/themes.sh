#!/bin/bash
# Weekly cross-charm synthesis. Cheap: it reads the reviews already written and
# writes THEMES.md, no deploying, no charm code.
. /home/ubuntu/charm-review/bin/lib.sh
set -u

N=$(ls "$ROOT/reviews"/*.md 2>/dev/null | wc -l)
if [ "$N" -lt 3 ]; then log "themes: only $N reviews, too early"; exit 0; fi

SPENT=$(usage_today); LIMIT=$(daily_limit)
REMAIN=$(budget_remaining)
[ -z "$REMAIN" ] && REMAIN=$(python3 -c "print(f'{max(0.0,$LIMIT-${SPENT:-0}):.2f}')")
REMAIN=$(python3 -c "print(f'{float(\"$REMAIN\"):.2f}')")
if python3 -c "import sys; sys.exit(0 if $REMAIN < 1.50 else 1)"; then
  log "themes: only \$$REMAIN of budget left, skipping"; exit 0
fi

[ -f "$ROOT/THEMES.md" ] && cp "$ROOT/THEMES.md" "$ROOT/logs/THEMES.prev.md"

# Test the artifact, not the exit code — and here the artifact is a file the agent
# *overwrites*, so "it is big enough" proves nothing: on 2026-08-03 the agent died with
# "Provider finish_reason: error" after 5 minutes, THEMES.md was left untouched from
# 07-27, and the run logged `done rc=1 (34671 bytes)` — a healthy-looking size that was
# simply the stale file measured by wc. Nothing retried, so the synthesis silently stayed
# six weeks and 49 reviews out of date. Compare the content instead, and say plainly when
# it did not change. Same lesson as the 0-byte review that cleared an `[ -s ]` test.
themes_attempt() {  # themes_attempt <n>
  log "themes: synthesising across $N reviews with $THEMES_MODEL (attempt $1)"
  cd "$ROOT" && timeout 2400 pi -p --no-session --no-approve --no-context-files \
    --model "${THEMES_MODEL:-$POLISH_MODEL}" --thinking high \
    "$(cat "$ROOT/prompts/themes.md")" </dev/null > "$ROOT/logs/themes.log" 2>&1
}
themes_changed() {  # themes_changed -> 0 if THEMES.md differs from the pre-run copy
  ! cmp -s "$ROOT/THEMES.md" "$ROOT/logs/THEMES.prev.md"
}

themes_attempt 1; RC=$?
if [ "$RC" -ne 0 ] || ! themes_changed; then
  log "themes: attempt 1 produced nothing (rc=$RC, THEMES.md unchanged) — retrying once"
  themes_attempt 2; RC=$?
fi
if [ "$RC" -eq 0 ] && themes_changed; then
  log "themes: done rc=0 ($(wc -c <"$ROOT/THEMES.md" 2>/dev/null || echo 0) bytes, updated)"
else
  log "themes: FAILED rc=$RC — THEMES.md is UNCHANGED and still reflects an older set of reviews"
fi
