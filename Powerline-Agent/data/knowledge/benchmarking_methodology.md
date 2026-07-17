# Powerline Benchmarking Methodology

## Powerline-Perfect Benchmark

The Powerline-perfect benchmark represents the **maximum achievable revenue** for a battery asset given:

- Actual market prices observed in each interval
- Asset physical constraints (power limits, SOC bounds, ramp rates)
- Perfect foresight of prices within the interval

This benchmark is **not** a forecast — it is a retrospective upper bound used to identify missed opportunities.

## Benchmark Revenue Calculation

For each interval, the benchmark optimizer determines the ideal charge/discharge decision. Benchmark revenue is the sum of optimal interval revenues over the analysis window.

## Performance Gap Analysis

```
revenue_gap = benchmark_revenue - actual_revenue
gap_pct = revenue_gap / benchmark_revenue × 100
```

Common causes of performance gaps:

| Cause | Indicator | Recommendation |
|-------|-----------|----------------|
| SOC constraints | Low SOC during price spikes | Adjust SOC targets before peak windows |
| Suboptimal bidding | High gap during volatile periods | Review bid-spread parameters |
| Missed arbitrage | Negative revenue during low-price intervals | Increase charging during negative prices |
| Ramp limits | Gap concentrated in fast price transitions | Evaluate dispatch latency |

## Fleet Benchmarking

When comparing multiple assets:

- Rank by average capture rate over the analysis period
- Normalize by asset capacity (MW) for fair comparison
- Segment by market region if assets operate in different markets

## Continuous Benchmarking

Battery Co-Pilot runs continuous benchmarking to:

1. Detect performance drift before it compounds
2. Identify asset-specific vs fleet-wide issues
3. Quantify ROI of strategy changes after implementation
