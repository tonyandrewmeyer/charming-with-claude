# Model Checkpoint: Sonnet vs Opus (Run 1)

**Scored run 1 sessions:** 181

## Overall

| Model | Mean Score (%) | Std Dev | n |
|---|---|---|---|
| sonnet | 73.1 | 17.9 | 90 |
| opus | 75.2 | 19.0 | 91 |

## By Condition

| Condition | Sonnet | Opus | Difference |
|---|---|---|---|
| A | 70.9% | 72.1% | +1.1 |
| B | 71.3% | 73.5% | +2.2 |
| C | 76.7% | 77.1% | +0.3 |
| D | 73.8% | 78.3% | +4.5 |

## Per Question

| Question | Sonnet (mean across conds) | Opus (mean across conds) | Diff |
|---|---|---|---|
| Q1 | 100.0% | 83.3% | -16.7 |
| Q10 | 75.0% | 73.6% | -1.4 |
| Q11 | 70.8% | 79.2% | +8.3 |
| Q12 | 77.8% | 91.7% | +13.9 |
| Q13 | 72.2% | 55.6% | -16.7 |
| Q14 | 36.1% | 50.0% | +13.9 |
| Q15 | 70.8% | 73.6% | +2.8 |
| Q16 | 61.1% | 61.1% | +0.0 |
| Q17 | 72.2% | 87.5% | +15.3 |
| Q18 | 83.3% | 73.6% | -9.7 |
| Q19 | 83.3% | 83.3% | +0.0 |
| Q2 | 80.6% | 79.2% | -1.4 |
| Q20 | 83.3% | 73.6% | -9.7 |
| Q3 | 77.8% | 88.9% | +11.1 |
| Q4 | 75.0% | 100.0% | +25.0 |
| Q5 | 83.3% | 79.2% | -4.2 |
| Q6 | 76.4% | 87.5% | +11.1 |
| Q7 | 73.6% | 83.3% | +9.7 |
| Q8 | 70.8% | 51.4% | -19.4 |
| Q9 | 77.8% | 79.2% | +1.4 |
| S1 | 78.8% | 67.5% | -11.2 |
| S2 | 43.8% | 80.0% | +36.2 |
| S3 | 55.0% | 43.8% | -11.2 |

## Recommendation

Difference (2.1pp) is within 1 standard deviation (17.9pp). **Consider dropping the model dimension** for runs 2-3 to save cost.
