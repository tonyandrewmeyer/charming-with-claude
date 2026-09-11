#!/bin/bash
# Benchmark candidate OpenRouter models for the charm-review agent.
export PATH="/home/ubuntu/.local/share/pi-node/node-v22.23.1-linux-x64/bin:$PATH"
KEY=$(python3 -c "import json;print(json.load(open('/home/ubuntu/.pi/agent/auth.json'))['openrouter']['key'])")
OUT="${BENCH_OUT:-/home/ubuntu/charm-review/state/bench-outputs}"
mkdir -p "$OUT"
REPO=/home/ubuntu/.cache/hyrum/charms/jnsgruk/zinc-k8s-operator

usage() { curl -sS -H "Authorization: Bearer $KEY" https://openrouter.ai/api/v1/key | python3 -c "import json,sys;print(json.load(sys.stdin)['data']['usage'])"; }

PROMPT='You are reviewing a Juju charm. Working directory is the charm repo. Using ONLY the bash/read tools, investigate the code and answer.

Produce EXACTLY this markdown, no preamble:

## Services
Pebble layer/service names the charm defines, each with `file:line`.

## Endpoints
The charm relation endpoints, split into provides and requires, from metadata/charmcraft yaml.

## Finding
ONE concrete correctness, robustness or performance defect in the charm code. Give `file:line`, quote the offending line, explain the failure mode in 2-3 sentences, and state how a charm linter could detect it. Do not invent code that is not there.

## Confidence
One line: how confident you are and why.'

for M in ${BENCH_MODELS:-"z-ai/glm-4.7" "minimax/minimax-m2.7" "deepseek/deepseek-v4-pro"}; do
  SLUG=$(echo "$M" | tr '/' '_')
  B=$(usage)
  S=$(date +%s)
  (cd "$REPO" && timeout 600 pi -p --no-session --no-approve --model "$M" "$PROMPT" < /dev/null) > "$OUT/$SLUG.md" 2> "$OUT/$SLUG.err"
  RC=$?
  E=$(date +%s)
  sleep 4
  A=$(usage)
  python3 -c "print(f'$M\trc=$RC\tsecs={$E-$S}\tcost=\${$A-$B:.4f}')" >> "$OUT/results.tsv"
  echo "done $M rc=$RC"
done
cat "$OUT/results.tsv"
