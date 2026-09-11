# Model benchmark — 2026-07-24

## Why this shape of test

The OpenRouter key is capped at **$20/day** (`limit: 20, limit_reset: daily`;
~$34k of lifetime credit remains behind that cap). At 8 runs a day that is roughly
$2.50 per charm review, which rules out Claude models for the long agentic loop but
leaves plenty for a short editing pass on one.

Each candidate got the same task in `jnsgruk/zinc-k8s-operator`: use the bash/read
tools to find the Pebble services, list the relation endpoints, and name one real
defect with `file:line`, a quote, a failure mode and a linter rule. Small enough to
be cheap, but it needs genuine tool use and it is checkable — I verified every line
number against the source afterwards, which is what separated the candidates.

## Results

| model | time | cost | citations | finding |
|---|---|---|---|---|
| `deepseek/deepseek-v4-pro` | 468 s | $0.088 | **all correct** — `zinc.py:26`, `charm.py:95`, `zinc.py:83` | `time.sleep(3)` reachable from an event handler; blocks the hook for up to 9 s. Statically traceable, so a strong linter rule. |
| `minimax/minimax-m2.7` | 217 s | $0.034 | **all correct** — `zinc.py:26`, `charm.py:96-97` | `add_layer(combine=True)` + `replan()` does not restart an already-running service when only env changed. Real charm anti-pattern. |
| `z-ai/glm-4.7` | 256 s | $0.026 | **both wrong** — said `zinc.py:22` (is 26), `charm.py:118` (is 94) | vague "password could be empty under a race", hedged to Medium. |
| `minimax/minimax-m3` | 555 s | $0.135 | **mixed** — Python refs correct (`zinc.py:26`, `charm.py:96`, `charm.py:74-76`), but every `charmcraft.yaml` line range was invented (claimed peers 46-47 / metrics 50-51; actually 53-55 / 58-59) | "unit stuck in `WaitingStatus` forever" behind a deferred pebble-ready. Reasoning does not hold: `event.defer()` re-emits on the next hook, so it is not stuck. Confident tone, partly wrong. |
| `qwen/qwen3.7-plus` | — | — | — | unusable: `404 No endpoints available matching your guardrail restrictions and data policy`. The account's privacy settings would need changing. |
| `moonshotai/kimi-k2.7-code` | 600 s | $0.646 | — | **timed out with no output**, having spent 7x what minimax-m3 cost for a complete answer. Rejected. |
| `z-ai/glm-5.2` | 1 s | $0.042 | — | fails immediately with a provider/auth error (`Use /login to log into a provider`). Not reachable on this key. |

## Conclusion

**Work model: `deepseek/deepseek-v4-pro`.** For a two-hour agentic loop the things that
matter are citation accuracy (a review with wrong line numbers is worse than no review),
cheap *output* tokens, and a context window big enough that pi's auto-compaction rarely
fires and throws away detail. deepseek wins all three: perfect citations, $0.43/$0.87 per
M, 1M context. It was the slowest of the three, but at 468 s for this task a 140-minute
budget is not close to binding.

**Runner-up / fallback: `minimax/minimax-m2.7`**, not m3. When m3 was finally tested it
turned out to invent line numbers for YAML files while getting Python files right, and to
argue a confident but incorrect failure mode (it did not know that a deferred event is
re-emitted on the next hook). m2.7 cited perfectly and its finding held up. The 204K
context is the cost of choosing it, but accuracy beats window size here. Treat m3's larger
window as unproven, not as an upgrade.

**glm-4.7 is rejected** despite being cheapest and reasonably fast. Two out of two
fabricated line numbers on a task where the file was open in front of it is exactly the
failure mode that makes an unattended review untrustworthy.

**Polish model: `anthropic/claude-sonnet-5`.** The editing pass sees only the draft and
the notes — tens of thousands of tokens, not millions — so the expensive model is
affordable there and is where the prose quality comes from.

## Caveats

* One task, one repo, one sample per model. This ranks citation discipline, not overall
  charm expertise. Re-run `bin/benchmark-models.sh` against a different charm before
  treating the ordering as settled.
* Costs here are for a 4–8 minute task. A real 140-minute run is maybe 30–50x that, so
  expect roughly $1–3 per review — under the per-run cap, but not by a wide margin.
