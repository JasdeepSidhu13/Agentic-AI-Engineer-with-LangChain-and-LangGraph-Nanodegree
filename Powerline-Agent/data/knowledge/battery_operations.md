# Battery Operations Fundamentals

## State of Charge (SOC)

State of charge represents the available energy in a battery as a percentage of total capacity. Typical operational constraints:

- **Minimum SOC**: Usually 10–20% to preserve battery health
- **Maximum SOC**: Usually 90–95% to allow headroom for regulation services
- **Cycling**: Frequent deep cycles reduce asset lifetime; operators balance revenue vs degradation

## Power and Energy

- **Power (MW)**: Instantaneous charge/discharge rate. Negative values indicate charging; positive values indicate discharging.
- **Energy (MWh)**: Energy transferred over an interval = |Power| × interval duration (hours).
- For 15-minute intervals: Energy (MWh) = |Power (MW)| × 0.25

## Ramp Rates

Grid-scale batteries have maximum ramp rates (MW/minute). Dispatch schedules must respect these limits when responding to price signals.

## Revenue Calculation

Revenue in a trading interval is approximately:

```
revenue_usd = power_mw × interval_hours × market_price_usd_mwh
```

When discharging during high prices and charging during low prices, the asset captures arbitrage value.
