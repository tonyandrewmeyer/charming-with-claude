# Experiment Results: llms.txt for Charm Development

**Total sessions:** 432
**Scored sessions:** 366
**Human-reviewed:** 0 (0% of scored)

## Overall Scores by Condition

| Condition | Mean Score (%) | Std Dev | n | Mean Tokens | Mean Cost ($) |
|---|---|---|---|---|---|
| A | 72.0 | 16.4 | 94 | 1530 | 0.1297 |
| B | 72.3 | 16.2 | 92 | 811 | 0.1432 |
| C | 78.3 | 18.7 | 92 | 2070 | 0.2045 |
| D | 74.9 | 19.3 | 88 | 1014 | 0.2073 |

## Scores by Condition × Model

| Condition | Model | Mean Score (%) | Std Dev | n | Mean Tokens |
|---|---|---|---|---|---|
| A | sonnet | 70.4 | 17.4 | 47 | 1813 |
| A | opus | 73.6 | 15.4 | 47 | 1247 |
| B | sonnet | 72.4 | 14.6 | 48 | 850 |
| B | opus | 72.2 | 17.9 | 44 | 768 |
| C | sonnet | 77.2 | 17.5 | 45 | 2194 |
| C | opus | 79.3 | 19.9 | 47 | 1951 |
| D | sonnet | 75.8 | 19.7 | 41 | 972 |
| D | opus | 74.2 | 19.1 | 47 | 1051 |

## Scores by Category

| Category | Cond A | Cond B | Cond C | Cond D |
|---|---|---|---|---|
| ops_api | 82.8% | 83.3% | 84.3% | 88.4% |
| pebble | 67.5% | 80.0% | 82.3% | 78.8% |
| jubilant | 78.2% | 69.8% | 82.1% | 71.0% |
| charmlibs | 60.8% | 61.7% | 51.4% | 55.2% |
| charmcraft | 72.0% | 75.4% | 86.7% | 84.2% |
| synthesis | 66.7% | 60.0% | 81.2% | 56.4% |

## Token Efficiency

Token usage is a key metric — markdown docs should be smaller than HTML.

| Condition | Mean Input Tokens | Mean Output Tokens | Mean Total |
|---|---|---|---|
| A | 26 | 1504 | 1530 |
| B | 5 | 806 | 811 |
| C | 116 | 1954 | 2070 |
| D | 18 | 997 | 1014 |

## Per-Question Scores

| Question | Cond A | Cond B | Cond C | Cond D |
|---|---|---|---|---|
| Q1 | 83.3% | 87.5% | 100.0% | 94.4% |
| Q2 | 77.8% | 73.6% | 83.3% | 88.9% |
| Q3 | 88.9% | 91.1% | 80.0% | 90.3% |
| Q4 | 83.3% | 83.3% | 76.4% | 91.7% |
| Q5 | 75.0% | 77.8% | 79.2% | 75.0% |
| Q6 | 76.4% | 91.7% | 87.5% | 83.3% |
| Q7 | 75.9% | 77.8% | 83.3% | 83.3% |
| Q8 | 58.3% | 58.3% | 69.4% | 58.3% |
| Q9 | 56.9% | 88.9% | 83.3% | 83.3% |
| Q10 | 80.0% | 68.9% | 83.3% | 65.6% |
| Q11 | 66.7% | 66.7% | 79.2% | 77.8% |
| Q12 | 87.5% | 75.0% | 83.3% | 71.1% |
| Q13 | 66.7% | 66.7% | 59.7% | 65.3% |
| Q14 | 43.1% | 55.6% | 23.6% | 34.4% |
| Q15 | 70.8% | 65.3% | 70.8% | 69.4% |
| Q16 | 61.1% | 61.1% | 51.4% | 57.4% |
| Q17 | 80.0% | 78.7% | 86.1% | 88.9% |
| Q18 | 66.7% | 72.2% | 93.3% | 86.7% |
| Q19 | 72.2% | 83.3% | 83.3% | 83.3% |
| Q20 | 69.4% | 66.7% | 83.3% | 75.0% |
| S1 | 76.7% | 77.5% | 88.3% | 62.5% |
| S2 | 35.0% | 67.5% | 77.5% | 68.3% |
| S3 | 75.0% | 31.7% | 76.7% | 32.5% |

## Hallucination Rates

Percentage of responses with score 0 (invented APIs/params).

| Condition | Hallucination Rate |
|---|---|
| A | 1.1% (1/94) |
| B | 1.1% (1/92) |
| C | 7.6% (7/92) |
| D | 5.7% (5/88) |

## Doc Access Patterns (nginx logs)

Metrics from nginx access logs — only available for conditions C/D (local docs with llms.txt). Conditions A/B use real internet so no nginx logs are captured.

### Fetch Summary

| Condition | Mean Fetches | Mean Bytes | Mean Unique Pages | Mean 404s |
|---|---|---|---|---|
| A | - | - | - | - |
| B | - | - | - | - |
| C | 5.5 | 231441 | 5.3 | 1.8 |
| D | 4.4 | 128937 | 4.1 | 1.1 |

### Format Preference (conditions C/D only)

Does the agent prefer llms.txt, llms-full.txt, per-page .md, or HTML?

| Condition | llms.txt | llms-full.txt | Per-page .md | HTML | Total |
|---|---|---|---|---|---|
| C | 195 (33%) | 28 (5%) | 117 (20%) | 250 (42%) | 590 |
| D | 72 (15%) | 2 (0%) | 52 (11%) | 344 (73%) | 470 |

### First Page Fetched

What does the agent reach for first?

**Condition C:**
- `/juju/en/latest/llms.txt` (39×)
- `/llms.txt` (5×)
- `/jubilant/en/latest/llms.txt` (4×)
- `/pebble/en/latest/llms.txt` (4×)
- `/juju/sdk/jubilant/llms.txt` (3×)
- `/juju/sdk/howto/manage-the-pebble-layer/llms.txt` (3×)
- `/pebble/en/latest/reference/changes-and-tasks/` (3×)
- `/jubilant/llms.txt` (2×)
- `/juju/sdk/howto/manage-interfaces/llms.txt` (2×)
- `/juju/sdk/howto/manage-the-workload-container/llms.txt` (2×)
- `/charmcraft/en/latest/reference/files/charmcraft-yaml/` (2×)
- `/llmstxt/juju/` (2×)
- `/charmcraft/en/stable/llms.txt` (2×)
- `/juju/en/latest/llms-full.txt` (2×)
- `/pebble/en/latest/reference/log-forwarding/` (2×)
- `/juju/sdk/howto/manage-relations/llms.txt` (2×)
- `/juju/sdk/howto/manage-the-lifecycle-of-a-charm/llms.txt` (1×)
- `/juju/sdk/dev/llms-full.txt` (1×)
- `/juju/sdk/howto/manage-the-deployed-lifecycle/llms.txt` (1×)
- `/juju/sdk/jubilant/llms-full.txt` (1×)
- `/charm-tech/howto/manage-tls-certificates/llms.txt` (1×)
- `/juju/sdk/howto/manage-tls-certificates/llms.txt` (1×)
- `/charm-tech/llms-full.txt` (1×)
- `/charm-tech/reference/files/charmcraft-yaml/` (1×)
- `/juju/en/stable/llms-full.txt` (1×)
- `/charmcraft/en/latest/llms.txt` (1×)
- `/juju/3.6/llms-full.txt` (1×)
- `/juju/en/latest/reference/hook/` (1×)
- `/juju/sdk/howto/manage-actions/llms.txt` (1×)
- `/charm-tech/howto/manage-status/llms.txt` (1×)
- `/charm-tech/howto/manage-the-status-of-a-charm/llms.txt` (1×)
- `/pebble/reference/layer-specification/` (1×)
- `/pebble/reference/layer-specification` (1×)
- `/pebble/en/latest/reference/layer-specification` (1×)
- `/pebble/en/latest/reference/layer-specification/` (1×)
- `/llmstxt/juju/en/latest/llms.txt` (1×)
- `/rockcraft/en/latest/llms.txt` (1×)
- `/juju/sdk/howto/manage-the-lifecycle/llms.txt` (1×)
- `/juju/3/en/llms-full.txt` (1×)
- `/juju/sdk/howto/manage-the-workload/interact-with-pebble/llms.txt` (1×)
- `/juju/sdk/llms.txt` (1×)

**Condition D:**
- `/charmcraft/llms.txt` (16×)
- `/charmlibs/llms.txt` (15×)
- `/pebble/llms.txt` (11×)
- `/jubilant/llms.txt` (8×)
- `/ops/latest/reference/pebble.html` (6×)
- `/pebble/reference/layer-specification/` (6×)
- `/jubilant/reference/jubilant/` (5×)
- `/ops/latest/reference/ops.html` (4×)
- `/ops/llms.txt` (3×)
- `/ops/latest/llms.txt` (2×)
- `/pebble/reference/changes-and-tasks/` (2×)
- `/jubilant/.llms.txt` (1×)
- `/traefik-k8s-charm/` (1×)
- `/charmcraft/latest/reference/files/charmcraft-yaml/` (1×)

### Repos Consulted by Question Category

Does llms.txt help the agent go to the right repo?

| Category | Condition | Repos Visited |
|---|---|---|
| ops_api | C | juju(21), ops(2) |
| ops_api | D | ops(13), pebble(2), juju(1) |
| pebble | C | pebble(18), juju(7), ops(3) |
| pebble | D | pebble(17), ops(10) |
| jubilant | C | jubilant(14), juju(8), ops(1) |
| jubilant | D | jubilant(14), ops(1) |
| charmlibs | C | juju(15), charmlibs(4), ops(3) |
| charmlibs | D | charmlibs(16), ops(2) |
| charmcraft | C | charmcraft(21), juju(12) |
| charmcraft | D | charmcraft(17), ops(1) |
| synthesis | C | juju(14), pebble(5), charmcraft(4), ops(4) |
| synthesis | D | ops(4), pebble(2) |

### Bytes Fetched vs Tokens Consumed

Compares raw bytes from nginx with input tokens billed. Lower bytes/token ratio means the doc format is more efficient.

| Condition | Mean Bytes Fetched | Mean Input Tokens | Bytes/Token |
|---|---|---|---|
| C | 238117 | 116 | 2053.7 |
| D | 170325 | 18 | 9695.1 |
