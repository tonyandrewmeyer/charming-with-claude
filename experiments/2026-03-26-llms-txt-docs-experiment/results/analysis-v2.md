# Experiment Results: llms.txt for Charm Development

**Total sessions:** 620
**Scored sessions:** 618
**Human-reviewed:** 114 (18% of scored)

## Overall Scores by Condition

| Condition | Mean Score (%) | Std Dev | n | Mean Tokens | Mean Cost ($) |
|---|---|---|---|---|---|
| A | 79.8 | 18.3 | 138 | 1689 | 0.1334 |
| B | 82.0 | 18.0 | 138 | 833 | 0.1472 |
| C | 86.9 | 15.3 | 136 | 2229 | 0.2365 |
| D | 83.0 | 19.8 | 137 | 1029 | 0.2022 |
| E | 83.1 | 15.4 | 69 | 2109 | 0.2658 |

## Scores by Condition × Model

| Condition | Model | Mean Score (%) | Std Dev | n | Mean Tokens |
|---|---|---|---|---|---|
| A | sonnet | 81.1 | 18.2 | 69 | 2050 |
| A | opus | 78.4 | 18.5 | 69 | 1328 |
| B | sonnet | 82.0 | 17.4 | 69 | 898 |
| B | opus | 82.0 | 18.8 | 69 | 768 |
| C | sonnet | 86.7 | 13.1 | 69 | 2391 |
| C | opus | 87.1 | 17.4 | 67 | 2061 |
| D | sonnet | 81.6 | 20.3 | 68 | 997 |
| D | opus | 84.3 | 19.2 | 69 | 1061 |
| E | sonnet | 83.1 | 15.4 | 69 | 2109 |

## Scores by Category

| Category | Cond A | Cond B | Cond C | Cond D |
|---|---|---|---|---|
| ops_api | 90.0% | 87.8% | 87.2% | 90.9% | 88.1% |
| pebble | 72.9% | 89.8% | 90.3% | 87.3% | 81.5% |
| jubilant | 83.6% | 83.0% | 92.0% | 82.1% | 87.0% |
| charmlibs | 79.4% | 81.9% | 78.0% | 82.1% | 80.1% |
| charmcraft | 85.4% | 83.6% | 93.8% | 88.4% | 84.7% |
| synthesis | 60.8% | 59.2% | 78.4% | 58.6% | 74.4% |

## Token Efficiency

Token usage is a key metric — markdown docs should be smaller than HTML.

| Condition | Mean Input Tokens | Mean Output Tokens | Mean Total |
|---|---|---|---|
| A | 24 | 1665 | 1689 |
| B | 6 | 827 | 833 |
| C | 108 | 2120 | 2229 |
| D | 17 | 1012 | 1029 |
| E | 49 | 2060 | 2109 |

## Per-Question Scores

| Question | Cond A | Cond B | Cond C | Cond D |
|---|---|---|---|---|
| Q1 | 86.1% | 88.9% | 100.0% | 94.4% | 100.0% |
| Q2 | 98.1% | 92.6% | 97.2% | 92.6% | 90.7% |
| Q3 | 94.4% | 94.4% | 74.1% | 95.4% | 72.2% |
| Q4 | 88.9% | 88.9% | 81.5% | 88.9% | 77.8% |
| Q5 | 82.4% | 74.1% | 83.3% | 83.3% | 100.0% |
| Q6 | 88.9% | 94.4% | 100.0% | 97.2% | 83.3% |
| Q7 | 77.8% | 94.4% | 94.4% | 94.4% | 83.3% |
| Q8 | 68.5% | 75.9% | 86.1% | 71.3% | 75.9% |
| Q9 | 56.5% | 94.4% | 80.6% | 86.1% | 83.3% |
| Q10 | 83.3% | 76.9% | 97.2% | 85.2% | 94.4% |
| Q11 | 75.9% | 88.9% | 88.9% | 82.4% | 77.8% |
| Q12 | 91.7% | 83.3% | 89.8% | 78.7% | 88.9% |
| Q13 | 91.7% | 94.4% | 91.7% | 88.9% | 94.4% |
| Q14 | 62.0% | 70.4% | 63.9% | 85.2% | 63.0% |
| Q15 | 94.4% | 83.3% | 94.4% | 78.7% | 87.0% |
| Q16 | 69.4% | 79.6% | 62.0% | 74.4% | 75.9% |
| Q17 | 97.2% | 89.8% | 97.2% | 88.9% | 77.8% |
| Q18 | 75.0% | 76.9% | 94.4% | 78.7% | 88.9% |
| Q19 | 77.8% | 83.3% | 94.4% | 88.9% | 77.8% |
| Q20 | 91.7% | 84.3% | 88.9% | 97.2% | 94.4% |
| S1 | 63.3% | 55.0% | 70.8% | 50.8% | 61.7% |
| S2 | 50.8% | 78.3% | 87.5% | 72.5% | 90.0% |
| S3 | 68.3% | 44.2% | 76.2% | 52.5% | 71.7% |

## Hallucination Rates

Percentage of responses with score 0 (invented APIs/params).

| Condition | Hallucination Rate |
|---|---|
| A | 1.4% (2/138) |
| B | 0.0% (0/138) |
| C | 1.5% (2/136) |
| D | 1.5% (2/137) |
| E | 0.0% (0/69) |

## Doc Access Patterns (nginx logs)

Metrics from nginx access logs — only available for conditions C/D (local docs with llms.txt). Conditions A/B use real internet so no nginx logs are captured.

### Fetch Summary

| Condition | Mean Fetches | Mean Bytes | Mean Unique Pages | Mean 404s |
|---|---|---|---|---|
| A | - | - | - | - |
| B | - | - | - | - |
| C | 5.5 | 248727 | 5.3 | 1.8 |
| D | 4.6 | 125655 | 4.3 | 1.2 |
| E | 4.1 | 71888 | 4.0 | 1.3 |

### Format Preference (conditions C/D only)

Does the agent prefer llms.txt, llms-full.txt, per-page .md, or HTML?

| Condition | llms.txt | llms-full.txt | Per-page .md | HTML | Total |
|---|---|---|---|---|---|
| C | 253 (34%) | 37 (5%) | 139 (18%) | 325 (43%) | 754 |
| D | 95 (15%) | 3 (0%) | 84 (13%) | 447 (71%) | 629 |
| E | 0 (0%) | 0 (0%) | 0 (0%) | 281 (100%) | 281 |

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

**Condition E:**
- `/juju/en/latest/` (6×)
- `/jubilant/reference/jubilant/` (4×)
- `/juju/en/latest/reference/relation/` (4×)
- `/juju/en/latest/reference/charm-resources/` (3×)
- `/juju/en/latest/reference/ops/` (3×)
- `/juju/en/latest/reference/hook/` (3×)
- `/jubilant/` (2×)
- `/juju/en/latest/reference/charm-libraries/` (2×)
- `/pebble/en/latest/reference/log-forwarding/` (2×)
- `/juju/en/latest/reference/pebble/` (2×)
- `/juju/en/latest/reference/relation-endpoints/` (1×)
- `/charmlibs/` (1×)
- `/charmlibs/reference/charmlibs/pathops/` (1×)
- `/juju/en/latest/reference/libraries/pathops/` (1×)
- `/juju/en/latest/reference/charm-architecture/` (1×)
- `/juju/en/latest/reference/charmcraft-yaml/` (1×)
- `/juju/en/latest/reference/files/charmcraft-yaml/` (1×)
- `/juju/en/latest/reference/charm-metadata/` (1×)
- `/juju/en/latest/reference/charm-taxonomy/` (1×)
- `/juju/en/latest/reference/charmcraft/charmcraft-yaml/` (1×)
- `/juju/en/latest/reference/charm-files/charmcraft-yaml/` (1×)
- `/charmcraft/en/latest/reference/charmcraft-yaml/` (1×)
- `/juju/en/latest/reference/relation-and-event-lifecycle/` (1×)
- `/juju/en/latest/reference/hook-tools/` (1×)
- `/juju/en/latest/reference/juju-charm-sdk/actions/` (1×)
- `/juju/en/latest/reference/ops/collect-status-event/` (1×)
- `/juju/en/latest/reference/charm-anatomy/` (1×)
- `/rockcraft/en/latest/reference/pebble-layers/` (1×)
- `/pebble/en/latest/reference/notices/` (1×)
- `/juju/en/latest/reference/pebble-notices/` (1×)
- `/pebble/en/latest/reference/changes-and-tasks/` (1×)
- `/rockcraft/en/latest/explanation/pebble/` (1×)
- `/pebble/en/latest/` (1×)
- `/rockcraft/en/latest/reference/pebble/` (1×)
- `/juju/en/latest/reference/charm-sdk/ops/` (1×)

### Repos Consulted by Question Category

Does llms.txt help the agent go to the right repo?

| Category | Condition | Repos Visited |
|---|---|---|
| ops_api | C | juju(26), ops(3), pebble(1) |
| ops_api | D | ops(16), pebble(2), juju(1) |
| ops_api | E | juju(12), ops(7) |
| pebble | C | pebble(24), juju(9), ops(5) |
| pebble | D | pebble(20), ops(12) |
| pebble | E | pebble(9), juju(5), ops(4) |
| jubilant | C | jubilant(18), juju(10), ops(2) |
| jubilant | D | jubilant(18), ops(2), juju(1) |
| jubilant | E | jubilant(6), ops(2) |
| charmlibs | C | juju(23), charmlibs(7), ops(4), charmcraft(1) |
| charmlibs | D | charmlibs(23), ops(3) |
| charmlibs | E | juju(10), charmlibs(8), ops(6), charmcraft(2) |
| charmcraft | C | charmcraft(24), juju(13) |
| charmcraft | D | charmcraft(20), ops(1) |
| charmcraft | E | charmcraft(12), juju(11), ops(1) |
| synthesis | C | juju(17), charmcraft(5), ops(5), pebble(5) |
| synthesis | D | ops(4), pebble(2) |
| synthesis | E | juju(4), ops(4), pebble(3), charmcraft(1) |

### Bytes Fetched vs Tokens Consumed

Compares raw bytes from nginx with input tokens billed. Lower bytes/token ratio means the doc format is more efficient.

| Condition | Mean Bytes Fetched | Mean Input Tokens | Bytes/Token |
|---|---|---|---|
| C | 258078 | 108 | 2385.2 |
| D | 170442 | 17 | 10323.0 |
| E | 88576 | 49 | 1796.0 |
