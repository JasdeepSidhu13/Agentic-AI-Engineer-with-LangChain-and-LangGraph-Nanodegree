# Electricity Market Trading Basics

## Spot Markets

Spot markets (e.g., Australia's NEM, CAISO, ERCOT) clear energy at locational marginal prices (LMP) for each trading interval. Battery assets participate by:

1. **Charging** when prices are low (or negative)
2. **Discharging** when prices spike
3. **Providing ancillary services** (FCAS, regulation) when profitable

## Price Spikes

Price spikes occur during:

- Evening demand ramps (typically 5–8 PM)
- Renewable generation drop-offs (cloud cover, calm wind)
- Transmission constraints or generator outages

Battery assets maximize revenue by maintaining SOC headroom before anticipated spikes.

## Bidding Strategy

Effective bidding strategies include:

- **Bid-spread optimization**: Widen spreads during volatile periods
- **SOC-aware dispatch**: Reserve capacity for known peak windows
- **Portfolio coordination**: Avoid simultaneous discharge across correlated assets

## Capture Rate

Capture rate measures how much of the theoretically optimal revenue an asset achieved:

```
capture_rate = actual_revenue / benchmark_revenue
```

A capture rate of 0.85 means the asset captured 85% of the Powerline-perfect benchmark opportunity.
