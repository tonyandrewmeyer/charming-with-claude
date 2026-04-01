# Experiment Results: llms.txt for Charm Development

**Total sessions:** 284
**Scored sessions:** 265
**Human-reviewed:** 0 (0% of scored)

## Overall Scores by Condition

| Condition | Mean Score (%) | Std Dev | n | Mean Tokens | Mean Cost ($) |
|---|---|---|---|---|---|
| A | 71.7 | 16.2 | 70 | 1654 | 0.1407 |
| B | 72.3 | 16.8 | 67 | 800 | 0.1280 |
| C | 78.5 | 17.9 | 66 | 2128 | 0.2003 |
| D | 75.0 | 18.5 | 62 | 1036 | 0.2149 |

## Scores by Condition × Model

| Condition | Model | Mean Score (%) | Std Dev | n | Mean Tokens |
|---|---|---|---|---|---|
| A | sonnet | 71.1 | 16.8 | 34 | 2026 |
| A | opus | 72.3 | 15.9 | 36 | 1303 |
| B | sonnet | 71.6 | 15.2 | 35 | 846 |
| B | opus | 73.1 | 18.7 | 32 | 749 |
| C | sonnet | 77.9 | 16.7 | 33 | 2158 |
| C | opus | 79.0 | 19.2 | 33 | 2097 |
| D | sonnet | 74.9 | 19.3 | 30 | 960 |
| D | opus | 75.1 | 18.1 | 32 | 1107 |

## Scores by Category

| Category | Cond A | Cond B | Cond C | Cond D |
|---|---|---|---|---|
| ops_api | 84.7% | 81.9% | 80.6% | 88.1% |
| pebble | 67.5% | 80.0% | 82.3% | 78.8% |
| jubilant | 77.8% | 71.6% | 81.7% | 74.1% |
| charmlibs | 63.4% | 61.5% | 55.0% | 57.2% |
| charmcraft | 69.4% | 75.0% | 87.9% | 83.3% |
| synthesis | 66.7% | 60.0% | 81.2% | 56.4% |

## Token Efficiency

Token usage is a key metric — markdown docs should be smaller than HTML.

| Condition | Mean Input Tokens | Mean Output Tokens | Mean Total |
|---|---|---|---|
| A | 30 | 1624 | 1654 |
| B | 5 | 794 | 800 |
| C | 106 | 2021 | 2128 |
| D | 22 | 1014 | 1036 |

## Per-Question Scores

| Question | Cond A | Cond B | Cond C | Cond D |
|---|---|---|---|---|
| Q1 | 94.4% | 87.5% | 100.0% | 91.7% |
| Q2 | 77.8% | 75.9% | 69.4% | 92.6% |
| Q3 | 80.6% | 88.9% | 75.9% | 96.3% |
| Q4 | 88.9% | 77.8% | 76.4% | 91.7% |
| Q5 | 75.0% | 77.8% | 79.2% | 75.0% |
| Q6 | 76.4% | 91.7% | 87.5% | 83.3% |
| Q7 | 75.9% | 77.8% | 83.3% | 83.3% |
| Q8 | 58.3% | 58.3% | 69.4% | 58.3% |
| Q9 | 56.9% | 88.9% | 83.3% | 83.3% |
| Q10 | 79.2% | 69.4% | 83.3% | 66.7% |
| Q11 | 66.7% | 66.7% | 77.8% | 81.5% |
| Q12 | 87.5% | 77.8% | 83.3% | 74.1% |
| Q13 | 66.7% | 66.7% | 59.7% | 66.7% |
| Q14 | 51.9% | 54.2% | 16.7% | 40.7% |
| Q15 | 72.2% | 64.8% | 72.2% | 70.4% |
| Q16 | 61.1% | 61.1% | 61.1% | 52.8% |
| Q17 | 74.1% | 72.2% | 88.9% | 83.3% |
| Q18 | 61.1% | 69.4% | 100.0% | 83.3% |
| Q19 | 70.8% | 83.3% | 83.3% | 83.3% |
| Q20 | 72.2% | 72.2% | 83.3% | 83.3% |
| S1 | 76.7% | 77.5% | 88.3% | 62.5% |
| S2 | 35.0% | 67.5% | 77.5% | 68.3% |
| S3 | 75.0% | 31.7% | 76.7% | 32.5% |

## Hallucination Rates

Percentage of responses with score 0 (invented APIs/params).

| Condition | Hallucination Rate |
|---|---|
| A | 0.0% (0/70) |
| B | 1.5% (1/67) |
| C | 4.5% (3/66) |
| D | 4.8% (3/62) |

## Doc Access Patterns (nginx logs)

Metrics from nginx access logs — only available for conditions C/D (local docs with llms.txt). Conditions A/B use real internet so no nginx logs are captured.

### Fetch Summary

| Condition | Mean Fetches | Mean Bytes | Mean Unique Pages | Mean 404s |
|---|---|---|---|---|
| A | - | - | - | - |
| B | - | - | - | - |
| C | 5.0 | 254875 | 5.0 | 1.5 |
| D | 4.9 | 109597 | 4.7 | 1.3 |

### Format Preference (conditions C/D only)

Does the agent prefer llms.txt, llms-full.txt, per-page .md, or HTML?

| Condition | llms.txt | llms-full.txt | Per-page .md | HTML | Total |
|---|---|---|---|---|---|
| C | 127 (36%) | 23 (6%) | 79 (22%) | 127 (36%) | 356 |
| D | 50 (15%) | 2 (1%) | 45 (13%) | 239 (71%) | 336 |

### First Page Fetched

What does the agent reach for first?

**Condition C:**
- `/juju/en/latest/llms.txt` (27×)
- `/pebble/en/latest/llms.txt` (3×)
- `/jubilant/en/latest/llms.txt` (2×)
- `/juju/sdk/jubilant/llms.txt` (2×)
- `/jubilant/llms.txt` (2×)
- `/llms.txt` (2×)
- `/juju/sdk/howto/manage-interfaces/llms.txt` (2×)
- `/juju/sdk/howto/manage-the-workload-container/llms.txt` (2×)
- `/juju/en/latest/llms-full.txt` (2×)
- `/pebble/en/latest/reference/changes-and-tasks/` (2×)
- `/pebble/en/latest/reference/log-forwarding/` (2×)
- `/juju/sdk/howto/manage-the-lifecycle-of-a-charm/llms.txt` (1×)
- `/juju/sdk/dev/llms-full.txt` (1×)
- `/juju/sdk/jubilant/llms-full.txt` (1×)
- `/charm-tech/howto/manage-tls-certificates/llms.txt` (1×)
- `/charm-tech/reference/files/charmcraft-yaml/` (1×)
- `/charmcraft/en/latest/reference/files/charmcraft-yaml/` (1×)
- `/juju/en/stable/llms-full.txt` (1×)
- `/llmstxt/juju/` (1×)
- `/juju/sdk/howto/manage-the-pebble-layer/llms.txt` (1×)
- `/charmcraft/en/stable/llms.txt` (1×)
- `/juju/3.6/llms-full.txt` (1×)
- `/juju/sdk/howto/manage-actions/llms.txt` (1×)
- `/charm-tech/howto/manage-status/llms.txt` (1×)
- `/charm-tech/howto/manage-the-status-of-a-charm/llms.txt` (1×)
- `/pebble/reference/layer-specification/` (1×)
- `/pebble/reference/layer-specification` (1×)
- `/pebble/en/latest/reference/layer-specification/` (1×)
- `/llmstxt/juju/en/latest/llms.txt` (1×)
- `/juju/sdk/howto/manage-the-lifecycle/llms.txt` (1×)
- `/juju/3/en/llms-full.txt` (1×)
- `/juju/sdk/howto/manage-relations/llms.txt` (1×)

**Condition D:**
- `/charmlibs/llms.txt` (13×)
- `/charmcraft/llms.txt` (9×)
- `/pebble/llms.txt` (7×)
- `/jubilant/llms.txt` (6×)
- `/ops/llms.txt` (3×)
- `/ops/latest/reference/ops.html` (3×)
- `/jubilant/reference/jubilant/` (2×)
- `/ops/latest/reference/pebble.html` (2×)
- `/pebble/reference/layer-specification/` (2×)
- `/jubilant/.llms.txt` (1×)
- `/traefik-k8s-charm/` (1×)
- `/charmcraft/latest/reference/files/charmcraft-yaml/` (1×)
- `/ops/latest/llms.txt` (1×)
- `/pebble/reference/changes-and-tasks/` (1×)

### Repos Consulted by Question Category

Does llms.txt help the agent go to the right repo?

| Category | Condition | Repos Visited |
|---|---|---|
| ops_api | C | juju(15), ops(1) |
| ops_api | D | ops(8), juju(1) |
| pebble | C | pebble(13), juju(4), ops(2) |
| pebble | D | pebble(9), ops(5) |
| jubilant | C | jubilant(10), juju(6), ops(1) |
| jubilant | D | jubilant(9), ops(1) |
| charmlibs | C | juju(12), charmlibs(4), ops(3) |
| charmlibs | D | charmlibs(14), ops(2) |
| charmcraft | C | charmcraft(11), juju(7) |
| charmcraft | D | charmcraft(10), ops(1) |
| synthesis | C | juju(8), charmcraft(3), ops(3), pebble(2) |
| synthesis | D | ops(2), pebble(1) |

### Bytes Fetched vs Tokens Consumed

Compares raw bytes from nginx with input tokens billed. Lower bytes/token ratio means the doc format is more efficient.

| Condition | Mean Bytes Fetched | Mean Input Tokens | Bytes/Token |
|---|---|---|---|
| C | 262263 | 106 | 2465.0 |
| D | 145426 | 22 | 6748.8 |
