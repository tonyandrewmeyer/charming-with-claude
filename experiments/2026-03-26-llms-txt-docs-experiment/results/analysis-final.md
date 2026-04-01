# Experiment Results: llms.txt for Charm Development

**Total sessions:** 551
**Scored sessions:** 493
**Human-reviewed:** 0 (0% of scored)

## Overall Scores by Condition

| Condition | Mean Score (%) | Std Dev | n | Mean Tokens | Mean Cost ($) |
|---|---|---|---|---|---|
| A | 71.9 | 17.3 | 127 | 1636 | 0.1385 |
| B | 73.3 | 16.7 | 123 | 815 | 0.1472 |
| C | 77.2 | 18.8 | 124 | 2088 | 0.2131 |
| D | 74.4 | 19.3 | 119 | 1035 | 0.2059 |

## Scores by Condition × Model

| Condition | Model | Mean Score (%) | Std Dev | n | Mean Tokens |
|---|---|---|---|---|---|
| A | sonnet | 69.9 | 17.6 | 63 | 1953 |
| A | opus | 73.9 | 16.8 | 64 | 1324 |
| B | sonnet | 73.0 | 15.3 | 63 | 887 |
| B | opus | 73.7 | 18.2 | 60 | 740 |
| C | sonnet | 76.6 | 17.3 | 61 | 2202 |
| C | opus | 77.8 | 20.2 | 63 | 1977 |
| D | sonnet | 73.4 | 20.1 | 57 | 988 |
| D | opus | 75.3 | 18.6 | 62 | 1079 |

## Scores by Category

| Category | Cond A | Cond B | Cond C | Cond D |
|---|---|---|---|---|
| ops_api | 84.5% | 83.0% | 83.0% | 86.5% |
| pebble | 67.5% | 82.2% | 82.1% | 79.2% |
| jubilant | 77.2% | 73.8% | 81.5% | 68.2% |
| charmlibs | 60.6% | 62.3% | 52.2% | 58.6% |
| charmcraft | 72.5% | 73.1% | 85.0% | 82.9% |
| synthesis | 64.3% | 61.9% | 81.7% | 59.5% |

## Token Efficiency

Token usage is a key metric — markdown docs should be smaller than HTML.

| Condition | Mean Input Tokens | Mean Output Tokens | Mean Total |
|---|---|---|---|
| A | 21 | 1615 | 1636 |
| B | 6 | 810 | 815 |
| C | 97 | 1991 | 2088 |
| D | 18 | 1018 | 1035 |

## Per-Question Scores

| Question | Cond A | Cond B | Cond C | Cond D |
|---|---|---|---|---|
| Q1 | 86.1% | 86.1% | 100.0% | 94.4% |
| Q2 | 81.5% | 79.6% | 86.1% | 84.3% |
| Q3 | 90.7% | 90.7% | 77.8% | 88.9% |
| Q4 | 86.1% | 83.3% | 73.1% | 91.7% |
| Q5 | 75.0% | 73.3% | 76.7% | 75.0% |
| Q6 | 78.7% | 95.8% | 91.7% | 83.3% |
| Q7 | 75.6% | 79.2% | 83.3% | 83.3% |
| Q8 | 58.3% | 61.1% | 68.5% | 61.1% |
| Q9 | 52.8% | 87.5% | 76.4% | 83.3% |
| Q10 | 77.8% | 71.3% | 83.3% | 65.7% |
| Q11 | 67.6% | 69.4% | 75.0% | 69.4% |
| Q12 | 86.1% | 80.6% | 86.1% | 69.4% |
| Q13 | 65.7% | 65.7% | 60.2% | 64.8% |
| Q14 | 48.1% | 55.6% | 30.6% | 36.1% |
| Q15 | 69.4% | 65.7% | 72.2% | 74.1% |
| Q16 | 59.3% | 62.0% | 44.4% | 59.7% |
| Q17 | 83.3% | 78.7% | 86.1% | 88.9% |
| Q18 | 64.8% | 69.4% | 91.7% | 81.5% |
| Q19 | 72.2% | 83.3% | 83.3% | 83.3% |
| Q20 | 69.4% | 61.1% | 78.7% | 77.8% |
| S1 | 73.8% | 80.0% | 87.0% | 62.5% |
| S2 | 41.2% | 56.7% | 80.0% | 68.0% |
| S3 | 73.3% | 47.0% | 76.2% | 47.5% |

## Hallucination Rates

Percentage of responses with score 0 (invented APIs/params).

| Condition | Hallucination Rate |
|---|---|
| A | 1.6% (2/127) |
| B | 0.8% (1/123) |
| C | 7.3% (9/124) |
| D | 5.0% (6/119) |

## Doc Access Patterns (nginx logs)

Metrics from nginx access logs — only available for conditions C/D (local docs with llms.txt). Conditions A/B use real internet so no nginx logs are captured.

### Fetch Summary

| Condition | Mean Fetches | Mean Bytes | Mean Unique Pages | Mean 404s |
|---|---|---|---|---|
| A | - | - | - | - |
| B | - | - | - | - |
| C | 5.5 | 248727 | 5.3 | 1.8 |
| D | 4.6 | 125655 | 4.3 | 1.2 |

### Format Preference (conditions C/D only)

Does the agent prefer llms.txt, llms-full.txt, per-page .md, or HTML?

| Condition | llms.txt | llms-full.txt | Per-page .md | HTML | Total |
|---|---|---|---|---|---|
| C | 253 (34%) | 37 (5%) | 139 (18%) | 325 (43%) | 754 |
| D | 95 (15%) | 3 (0%) | 84 (13%) | 447 (71%) | 629 |

### First Page Fetched

What does the agent reach for first?

**Condition C:**
- `/juju/en/latest/llms.txt` (49×)
- `/llms.txt` (9×)
- `/pebble/en/latest/llms.txt` (6×)
- `/jubilant/en/latest/llms.txt` (4×)
- `/juju/sdk/jubilant/llms.txt` (4×)
- `/jubilant/llms.txt` (3×)
- `/juju/sdk/howto/manage-the-workload-container/llms.txt` (3×)
- `/juju/sdk/howto/manage-the-pebble-layer/llms.txt` (3×)
- `/juju/en/latest/llms-full.txt` (3×)
- `/pebble/en/latest/reference/changes-and-tasks/` (3×)
- `/juju/sdk/dev/llms-full.txt` (2×)
- `/juju/sdk/howto/manage-interfaces/llms.txt` (2×)
- `/juju/sdk/howto/manage-tls-certificates/llms.txt` (2×)
- `/charmcraft/en/latest/reference/files/charmcraft-yaml/` (2×)
- `/llmstxt/juju/` (2×)
- `/charmcraft/en/stable/llms.txt` (2×)
- `/juju/sdk/howto/manage-actions/llms.txt` (2×)
- `/pebble/en/latest/reference/layer-specification/` (2×)
- `/pebble/en/latest/reference/log-forwarding/` (2×)
- `/juju/sdk/howto/manage-the-workload/interact-with-pebble/llms.txt` (2×)
- `/juju/sdk/howto/manage-relations/llms.txt` (2×)
- `/juju/sdk/howto/manage-the-lifecycle-of-a-charm/llms.txt` (1×)
- `/juju/sdk/howto/manage-the-deployed-lifecycle/llms.txt` (1×)
- `/juju/sdk/jubilant/llms-full.txt` (1×)
- `/juju/sdk/howto/llms-ctx.txt` (1×)
- `/charm-tech/howto/manage-tls-certificates/llms.txt` (1×)
- `/charm-tech/llms-full.txt` (1×)
- `/charm-tech/reference/files/charmcraft-yaml/` (1×)
- `/juju/en/stable/llms-full.txt` (1×)
- `/charmcraft/en/stable/reference/files/charmcraft-yaml/` (1×)
- `/charmcraft/en/latest/llms.txt` (1×)
- `/juju/3.6/llms-full.txt` (1×)
- `/juju/en/latest/reference/hook/` (1×)
- `/charm-tech/howto/manage-status/llms.txt` (1×)
- `/charm-tech/howto/manage-the-status-of-a-charm/llms.txt` (1×)
- `/juju/sdk/howto/manage-the-unit-status/llms.txt` (1×)
- `/pebble/reference/layer-specification/` (1×)
- `/pebble/reference/layer-specification` (1×)
- `/pebble/en/latest/reference/layer-specification` (1×)
- `/llmstxt/juju/en/latest/llms.txt` (1×)
- `/pebble/llms-full.txt` (1×)
- `/rockcraft/en/latest/llms.txt` (1×)
- `/juju/sdk/howto/manage-the-lifecycle/llms.txt` (1×)
- `/juju/3/en/llms-full.txt` (1×)
- `/juju/sdk/llms.txt` (1×)

**Condition D:**
- `/charmlibs/llms.txt` (22×)
- `/charmcraft/llms.txt` (19×)
- `/pebble/llms.txt` (13×)
- `/jubilant/llms.txt` (12×)
- `/ops/latest/reference/pebble.html` (6×)
- `/ops/latest/reference/ops.html` (6×)
- `/pebble/reference/layer-specification/` (6×)
- `/jubilant/reference/jubilant/` (5×)
- `/ops/llms.txt` (4×)
- `/pebble/reference/changes-and-tasks/` (3×)
- `/ops/latest/llms.txt` (2×)
- `/jubilant/.llms.txt` (1×)
- `/traefik-k8s-charm/` (1×)
- `/charmcraft/latest/reference/files/charmcraft-yaml/` (1×)

### Repos Consulted by Question Category

Does llms.txt help the agent go to the right repo?

| Category | Condition | Repos Visited |
|---|---|---|
| ops_api | C | juju(26), ops(3), pebble(1) |
| ops_api | D | ops(16), pebble(2), juju(1) |
| pebble | C | pebble(24), juju(9), ops(5) |
| pebble | D | pebble(20), ops(12) |
| jubilant | C | jubilant(18), juju(10), ops(2) |
| jubilant | D | jubilant(18), ops(2), juju(1) |
| charmlibs | C | juju(23), charmlibs(7), ops(4), charmcraft(1) |
| charmlibs | D | charmlibs(23), ops(3) |
| charmcraft | C | charmcraft(24), juju(13) |
| charmcraft | D | charmcraft(20), ops(1) |
| synthesis | C | juju(17), charmcraft(5), ops(5), pebble(5) |
| synthesis | D | ops(4), pebble(2) |

### Bytes Fetched vs Tokens Consumed

Compares raw bytes from nginx with input tokens billed. Lower bytes/token ratio means the doc format is more efficient.

| Condition | Mean Bytes Fetched | Mean Input Tokens | Bytes/Token |
|---|---|---|---|
| C | 258078 | 97 | 2668.6 |
| D | 170442 | 18 | 9626.3 |
