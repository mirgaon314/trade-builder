# Research notes — can the base model be made to *earn*, not just lose less? (2026-09-10)

Setup: same walk-forward (750/250, 5 bps) on SPY, QQQ, TLT, GLD, IWM, 2010-2026. Out-of-sample Sharpe unless noted.

## Variants tried

| variant | SPY | QQQ | TLT | GLD | IWM | mean |
|---|---|---|---|---|---|---|
| buy & hold | 0.87 | 0.95 | 0.12 | 0.61 | 0.54 | 0.62 |
| weighted model (baseline) | 0.76 | 0.90 | 0.19 | 0.37 | 0.47 | 0.54 |
| model, 5-day target + weekly rebalance | 0.75 | 0.90 | 0.05 | 0.53 | 0.45 | 0.54 |
| time-series momentum 12-1, monthly | 0.71 | 1.00 | 0.04 | 0.67 | 0.28 | 0.54 |
| hold + vol targeting (10%, no leverage) | 0.95 | 1.05 | 0.19 | 0.56 | 0.35 | 0.62 |
| model + vol targeting (10%, no leverage) | 0.83 | 0.99 | 0.25 | 0.16 | 0.25 | 0.50 |

Equal-weight 5-asset portfolio, daily rebalanced:

| portfolio | Sharpe | CAGR | maxDD |
|---|---|---|---|
| hold | 0.97 | +11.5% | -25.5% |
| model | 0.89 | +8.7% | -15.8% |
| ts-momentum | 0.87 | +8.6% | -21.1% |
| model + vol target | 0.85 | +4.7% | -8.7% |
| hold + vol target 15%, leverage cap 1.5x | 1.00 | +9.8% | -19.3% |
| model + vol target 15%, leverage cap 1.5x | 0.85 | +7.1% | -12.9% |

## What this says

- No variant beats buy & hold on risk-adjusted return across assets. The best single change was vol targeting on **hold** for SPY/QQQ (0.87→0.95, 0.95→1.05), which is the well-known vol-managed-portfolio effect and has nothing to do with the indicator model.
- Leverage does not turn the model's lower drawdown into higher return: at 1.5x-2x the extra exposure lands mostly in the days the model already gets wrong, and costs rise.
- Predicting a 5-day horizon instead of 1-day changes nothing on average. Classic 12-1 momentum matches the model on average and beats it on GLD/QQQ, loses on IWM/SPY.
- The one robust product of the model is drawdown: portfolio worst loss -25.5% → -15.8% (→ -8.7% with vol targeting), at the cost of about 3 points of CAGR.

## Why, in one paragraph

Daily technical indicators on liquid index ETFs carry almost no predictive information about tomorrow's sign; the 68% hit rate quoted in the README is mostly the market's upward drift, not skill. A long/flat rule built on that can only subtract exposure, so in a 16-year bull market it can only lose return while trimming risk. To actually earn above the index you need a different *source* of edge, not a better classifier on the same inputs: cross-sectional selection across many stocks, volatility forecasting used for sizing (volatility is far more predictable than direction), or data the price series does not already contain.

## What would be worth building next (in order of expected payoff)

1. **Volatility model + sizing** — predict 20-day realized vol from features (this works), size positions by it, and report the leverage-free result. Reuses everything here.
2. **Cross-sectional version** — same features on ~100 stocks, rank daily, hold the top decile long. This is where indicator models have historically shown something.
3. Keep the long/flat model as what it is: a drawdown limiter, and let the personality layer choose how much drawdown protection a user wants to pay for.
