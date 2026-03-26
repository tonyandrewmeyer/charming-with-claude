# Experiment Results: llms.txt for Charm Development

**Total sessions:** 20
**Scored sessions:** 20

## Overall Scores by Condition

| Condition | Mean Score (%) | Std Dev | n | Mean Tokens | Mean Cost ($) |
|---|---|---|---|---|---|
| A | 66.1 | 26.8 | 5 | 1598 | 0.1493 |
| B | 78.2 | 9.7 | 5 | 911 | 0.0797 |
| C | 84.7 | 16.9 | 5 | 2694 | 0.3410 |
| D | 84.7 | 12.2 | 5 | 855 | 0.1483 |

## Scores by Condition × Model

| Condition | Model | Mean Score (%) | Std Dev | n | Mean Tokens |
|---|---|---|---|---|---|
| A | sonnet | 66.1 | 26.8 | 5 | 1598 |
| B | sonnet | 78.2 | 9.7 | 5 | 911 |
| C | sonnet | 84.7 | 16.9 | 5 | 2694 |
| D | sonnet | 84.7 | 12.2 | 5 | 855 |

## Scores by Category

| Category | Cond A | Cond B | Cond C | Cond D |
|---|---|---|---|---|
| ops_api | 83.3% | 83.3% | 83.3% | 83.3% |
| pebble | - | - | - | - |
| jubilant | 66.7% | 83.3% | 66.7% | 83.3% |
| charmlibs | - | - | - | - |
| charmcraft | 72.2% | 61.1% | 100.0% | 83.3% |
| synthesis | 25.0% | 80.0% | 90.0% | 90.0% |

## Token Efficiency

Token usage is a key metric — markdown docs should be smaller than HTML.

| Condition | Mean Input Tokens | Mean Output Tokens | Mean Total |
|---|---|---|---|
| A | 5 | 1593 | 1598 |
| B | 6 | 905 | 911 |
| C | 290 | 2404 | 2694 |
| D | 6 | 849 | 855 |

## Per-Question Scores

| Question | Cond A | Cond B | Cond C | Cond D |
|---|---|---|---|---|
| Q1 | 100.0% | 83.3% | 100.0% | 100.0% |
| Q2 | - | - | - | - |
| Q3 | - | - | - | - |
| Q4 | - | - | - | - |
| Q5 | 66.7% | 83.3% | 66.7% | 66.7% |
| Q6 | - | - | - | - |
| Q7 | - | - | - | - |
| Q8 | - | - | - | - |
| Q9 | - | - | - | - |
| Q10 | 66.7% | 83.3% | 66.7% | 83.3% |
| Q11 | - | - | - | - |
| Q12 | - | - | - | - |
| Q13 | - | - | - | - |
| Q14 | - | - | - | - |
| Q15 | - | - | - | - |
| Q16 | - | - | - | - |
| Q17 | 72.2% | 61.1% | 100.0% | 83.3% |
| Q18 | - | - | - | - |
| Q19 | - | - | - | - |
| Q20 | - | - | - | - |
| S1 | 25.0% | 80.0% | 90.0% | 90.0% |
| S2 | - | - | - | - |
| S3 | - | - | - | - |

## Hallucination Rates

Percentage of responses with score 0 (invented APIs/params).

| Condition | Hallucination Rate |
|---|---|
| A | 0.0% (0/5) |
| B | 0.0% (0/5) |
| C | 0.0% (0/5) |
| D | 0.0% (0/5) |

## Doc Access Patterns (nginx logs)

Metrics from nginx access logs — only available for conditions C/D (local docs with llms.txt). Conditions A/B use real internet so no nginx logs are captured.

### Fetch Summary

| Condition | Mean Fetches | Mean Bytes | Mean Unique Pages | Mean 404s |
|---|---|---|---|---|
| A | 1.2 | 579477 | 1.2 | 0.0 |
| B | - | - | - | - |
| C | 8.0 | 222013 | 7.8 | 0.6 |
| D | 4.6 | 91172 | 4.6 | 1.2 |

### Format Preference (conditions C/D only)

Does the agent prefer llms.txt, llms-full.txt, per-page .md, or HTML?

| Condition | llms.txt | llms-full.txt | Per-page .md | HTML | Total |
|---|---|---|---|---|---|
| C | 6 (15%) | 0 (0%) | 15 (38%) | 19 (48%) | 40 |
| D | 3 (13%) | 0 (0%) | 0 (0%) | 20 (87%) | 23 |

### First Page Fetched

What does the agent reach for first?

**Condition C:**
- `/juju/en/latest/llms.txt` (4×)
- `/jubilant/llms.txt` (1×)

**Condition D:**
- `/jubilant/llms.txt` (1×)
- `/charmcraft/llms.txt` (1×)
- `/ops/latest/reference/pebble.html` (1×)
- `/ops/latest/llms.txt` (1×)

### Repos Consulted by Question Category

Does llms.txt help the agent go to the right repo?

| Category | Condition | Repos Visited |
|---|---|---|
| ops_api | C | ops(2) |
| ops_api | D | ops(2), pebble(1) |
| jubilant | C | jubilant(1) |
| jubilant | D | jubilant(1) |
| charmcraft | C | charmcraft(1) |
| charmcraft | D | charmcraft(1) |
| synthesis | C | charmcraft(1), ops(1) |

### Bytes Fetched vs Tokens Consumed

Compares raw bytes from nginx with input tokens billed. Lower bytes/token ratio means the doc format is more efficient.

| Condition | Mean Bytes Fetched | Mean Input Tokens | Bytes/Token |
|---|---|---|---|
| C | 222013 | 290 | 765.6 |
| D | 113965 | 6 | 18994.2 |
