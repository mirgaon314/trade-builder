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

## Round 2 — other people's indicators (same day)

| feature set (weighted model) | SPY | QQQ | TLT | GLD | IWM | mean |
|---|---|---|---|---|---|---|
| hold | 0.86 | 0.94 | 0.23 | 0.55 | 0.57 | 0.63 |
| base (7 indicators) | 0.76 | 0.91 | 0.19 | 0.37 | 0.47 | 0.54 |
| base + Ichimoku (11) | 0.69 | 0.93 | 0.12 | 0.27 | 0.41 | 0.48 |
| base + trend-line angles (13) | 0.50 | 0.81 | 0.02 | 0.54 | 0.54 | 0.48 |
| base + both (17) | 0.53 | 0.67 | 0.10 | 0.52 | 0.43 | 0.45 |
| **Ichimoku only (4)** | 0.84 | 1.01 | 0.16 | 0.62 | 0.60 | **0.65** |
| Ichimoku textbook rule, no learning | 0.56 | 0.78 | 0.01 | 0.38 | 0.05 | 0.36 |

Trend-line angles = annualized slope of a log-price regression over 20/60/120 days plus the residual from the rolling mean. Robustness of Ichimoku-only across training windows is in the README. Lesson: with ~750 training days, four well-chosen features beat seventeen; feature count is the overfitting knob.

## Round 3 — Fibonacci channel ("빗각") features from the `trader` engine

The channel engine from the separate `trader` project (weekly pivots → candidate parallel channels → recency-weighted touch-reversal score → best channel, adaptive lookback) was refit every 10 trading days on data up to that day only, and five per-day features were derived from the current best channel: distance to the nearest level line, distance to the next target level, channel slope (annualized / price), channel score, and lookback window length.

| feature set | SPY | QQQ | TLT | GLD | IWM | mean | 5-asset portfolio |
|---|---|---|---|---|---|---|---|
| hold | 0.86 | 0.94 | 0.22 | 0.49 | 0.55 | 0.61 | 0.96 / dd -25.5% |
| base (7) | 0.75 | 0.88 | 0.30 | 0.53 | 0.21 | 0.53 | 0.85 / dd -18.3% |
| Ichimoku (4) | 0.81 | 0.92 | 0.29 | 0.85 | 0.53 | **0.68** | **1.04** / dd -20.9% |
| channel (5) | 0.74 | 0.70 | 0.04 | 0.31 | 0.19 | 0.40 | 0.67 / dd -24.7% |
| Ichimoku + channel | 0.68 | 0.80 | 0.33 | 0.45 | 0.42 | 0.53 | 0.88 / dd -19.1% |
| base + channel | 0.52 | 0.76 | 0.15 | 0.53 | 0.13 | 0.42 | 0.70 / dd -20.4% |

(Rows differ slightly from Round 2 because the channel needs 300 warm-up days, which shifts the walk-forward folds.)

As daily-direction features the channel does not help and dilutes Ichimoku. That is not surprising: the channel was designed as a **swing tool** — buy at a line touch, target the next level, stop below — and "is tomorrow up?" is the wrong question to ask it. The right test is a trade-level backtest of the actual entry/target/stop rule from `trader/signal/builder.py`, which is a different experiment (next).

## Round 4 — the channel rule as a *swing trade*, not a daily signal

Trade-level simulation of the actual rule in [`fib-channel-trader`](https://github.com/mirgaon314/fib-channel-trader) `signal/builder.py`: scan every 5 days on data up to that day; if the state is `ready` (price within 25% of the support line, above/in the Ichimoku cloud, RSI < 70, reward:risk ≥ 2), place a limit buy at the support line valid 5 days; exit at the next level (target), the swing-low/ATR stop, or after 40 days. One position at a time, 5 bps per side. US ETFs 2010-2026, KRX tick rounding disabled.

| gate | asset | trades | win | avg win | avg loss | CAGR | Sharpe | maxDD | exposure |
|---|---|---|---|---|---|---|---|---|---|
| ready | SPY | 11 | 36% | +4.7% | -1.9% | +0.3% | 0.12 | -8% | 4% |
| ready | QQQ | 23 | 39% | +5.2% | -2.2% | +0.8% | 0.22 | -15% | 6% |
| ready | TLT | 5 | 20% | +1.0% | -2.0% | -0.5% | -0.15 | -9% | 3% |
| ready | GLD | 9 | 22% | +3.8% | -1.8% | -0.4% | -0.12 | -13% | 3% |
| ready | IWM | 21 | 29% | +5.1% | -2.0% | -0.1% | -0.01 | -18% | 5% |
| ready+wait | SPY | 18 | 44% | +5.2% | -2.1% | +1.2% | 0.35 | -9% | 7% |
| ready+wait | QQQ | 32 | 38% | +4.8% | -2.1% | +0.9% | 0.21 | -22% | 9% |
| ready+wait | TLT | 10 | 10% | +1.0% | -2.0% | -1.2% | -0.36 | -17% | 4% |

Requiring `confidence == strong` on top of `ready` changed nothing (the `ready` gate already implies it). Buy & hold over the same span: SPY +14.1% / 0.86, QQQ +18.9% / 0.94.

Reading: the rule is disciplined — wins are about 2.4x the size of losses, exactly the 2:1 gate — but it is in the market only 3-9% of the time, and the hit rate (30-45%) sits right at the breakeven for that payoff, so the equity curve is flat. It never blows up (worst loss -8% to -22% vs -34% to -48% for holding) and it never earns. On trending index ETFs, pullbacks to a channel line are rare and often *are* the start of a breakdown; the rule was designed for KRX single stocks that oscillate inside channels, which is where it should be tested next (data layer for that already exists in `fib-channel-trader`).

Owen's framing, which the numbers support: the channel is one signal among several, closer to a high/low locator than a strategy on its own.
