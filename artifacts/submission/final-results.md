# Final numerical result

**1475731.79 INR** — total wasted spend, 13 of 800 ads.

| Partition | Ads | Exact contribution (INR) |
|---|---:|---:|
| Google | 5 | 429321.93 |
| Instagram | 5 | 576898.53 |
| Meta | 1 | 143760.62 |
| YouTube | 2 | 325750.71 |
| Reconciliation total | 13 | 1475731.79 |

Official scored category: wasted spend. These platform partitions are disjoint. Every qualifying ad passes all three checks and contributes full spend once.

Internal total: 1475731.79 exactly. Required reporting: two decimal places. Reporting choice: ROUND_HALF_UP, since the official page specifies no tie mode. Half-even, half-up, final-total rounding and per-ad rounding all agree on these cent-precision inputs. Residual: 0.00.

Independent Python Decimal and JavaScript BigInt computations agree on all qualifying IDs, platform counts and monetary contributions. A second interpretation using revenue/spend instead of supplied rounded ROAS also totals 1475731.79. No private answer-key match is claimed.
