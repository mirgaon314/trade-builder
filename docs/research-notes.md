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

Without any confirmation gate (limit buy at the support line whenever one exists):

| asset | trades | win | avg win | avg loss | CAGR | Sharpe | maxDD | exposure | hold CAGR / Sharpe / maxDD |
|---|---|---|---|---|---|---|---|---|---|
| SPY | 140 | 62% | +2.7% | -2.9% | +4.0% | 0.48 | -18% | 34% | +14.1% / 0.86 / -34% |
| QQQ | 153 | 55% | +3.4% | -2.8% | +5.4% | 0.52 | -16% | 33% | +18.9% / 0.94 / -35% |
| TLT | 158 | 55% | +2.4% | -2.4% | +1.4% | 0.20 | -34% | 44% | +2.2% / 0.22 / -48% |
| GLD | 143 | 50% | +3.0% | -2.6% | +1.0% | 0.16 | -32% | 44% | +7.1% / 0.49 / -46% |
| IWM | 166 | 47% | +3.6% | -2.9% | +0.4% | 0.09 | -50% | 33% | +10.2% / 0.55 / -41% |

Dropping the Ichimoku/RSI/reward-risk gate multiplies trades by ~8 and turns the flat curve into a small positive one on the equity ETFs, but the payoff ratio collapses toward 1:1 and the drawdown protection is gone on IWM (-50%). The gate trades away almost all the return to keep the losses small; without it the rule is an ordinary mean-reversion entry with no edge over holding.

## Round 5 — the channel rule on 20 single stocks (US + KRX), three entry/stop variants

Same swing simulator as Round 4, on 10 US stocks (2010-2026) and 10 KRX stocks (2015-2026, KRX tick rounding on). Each cell is **CAGR / Sharpe / max drawdown (trades, win rate)**.

- **June rule**: limit buy at the support line, swing-low/ATR stop capped 2-7%, Ichimoku + RSI + reward:risk ≥ 2 gate, scan every 5 days.
- **Owen, limit**: same scan, stop = recent 10-bar low clamped to 3-5% below entry, gate = not below cloud, RSI < 70, lower 80% of the channel, reward:risk ≥ 1; limit buy at the line.
- **Owen, bounce**: same, but only buy at the next open after a day that touched the line and closed back above it ("it stopped at support and looks like it will turn").

| | hold CAGR / Sharpe / maxDD | June rule (limit @ line, 2:1 gate) | Owen: stop 3-5%, limit @ line | Owen: stop 3-5%, buy after bounce |
|---|---|---|---|---|
| AAPL | +25% / 0.92 / -44% | +3% / 0.42 / -14% (48t, 40%) | +1% / 0.17 / -21% (86t, 42%) | +3% / 0.39 / -16% (59t, 54%) |
| MSFT | +23% / 0.92 / -37% | +1% / 0.12 / -16% (31t, 32%) | +0% / 0.09 / -26% (70t, 43%) | +1% / 0.13 / -18% (53t, 51%) |
| NVDA | +50% / 1.13 / -66% | +0% / 0.09 / -38% (52t, 33%) | +4% / 0.32 / -39% (109t, 42%) | +0% / 0.07 / -39% (83t, 41%) |
| AMD | +31% / 0.75 / -82% | -0% / 0.05 / -47% (50t, 30%) | +2% / 0.20 / -38% (94t, 34%) | -1% / 0.02 / -31% (63t, 38%) |
| TSLA | +44% / 0.93 / -74% | +3% / 0.29 / -43% (41t, 39%) | +2% / 0.21 / -39% (101t, 37%) | +3% / 0.28 / -28% (72t, 46%) |
| AMZN | +25% / 0.83 / -56% | +1% / 0.24 / -16% (32t, 38%) | +5% / 0.44 / -32% (87t, 49%) | +3% / 0.36 / -28% (55t, 53%) |
| META | +25% / 0.78 / -77% | +7% / 0.76 / -15% (44t, 48%) | +10% / 0.79 / -24% (69t, 52%) | +6% / 0.56 / -19% (45t, 60%) |
| INTC | +14% / 0.53 / -71% | -3% / -0.44 / -44% (34t, 18%) | -1% / -0.05 / -43% (71t, 32%) | +1% / 0.11 / -26% (47t, 47%) |
| BA | +9% / 0.41 / -78% | -2% / -0.23 / -42% (26t, 27%) | -2% / -0.16 / -49% (69t, 38%) | -3% / -0.34 / -44% (43t, 42%) |
| XOM | +9% / 0.45 / -62% | +1% / 0.17 / -23% (29t, 28%) | +1% / 0.19 / -26% (51t, 43%) | -0% / -0.00 / -32% (35t, 46%) |
| 삼성전자 | +26% / 0.84 / -45% | +3% / 0.41 / -18% (23t, 43%) | n/a / 0.00 / -12% (43t, 51%) | n/a / -0.20 / -14% (22t, 55%) |
| SK하이닉스 | +50% / 1.10 / -55% | +2% / 0.21 / -39% (33t, 39%) | +3% / 0.28 / -37% (61t, 41%) | -0% / 0.04 / -26% (43t, 47%) |
| 현대차 | +9% / 0.42 / -61% | -0% / 0.03 / -28% (20t, 25%) | +2% / 0.19 / -25% (56t, 38%) | +2% / 0.27 / -15% (35t, 49%) |
| 한화에어로 | +25% / 0.68 / -82% | -7% / -0.45 / -61% (32t, 25%) | -10% / -0.61 / -72% (70t, 23%) | -4% / -0.27 / -35% (46t, 30%) |
| 한화오션 | +39% / 0.91 / -78% | n/a / 0.00 / -23% (25t, 44%) | n/a / 0.00 / -55% (68t, 37%) | n/a / 0.23 / -36% (49t, 47%) |
| NAVER | +5% / 0.31 / -66% | -4% / -0.36 / -41% (16t, 6%) | -5% / -0.34 / -49% (41t, 24%) | -3% / -0.30 / -36% (23t, 35%) |
| LG화학 | -1% / 0.19 / -82% | +0% / 0.08 / -26% (25t, 32%) | -5% / -0.31 / -52% (49t, 29%) | -0% / 0.01 / -28% (30t, 43%) |
| 셀트리온 | +9% / 0.41 / -65% | -4% / -0.40 / -37% (20t, 20%) | -4% / -0.25 / -54% (56t, 32%) | -6% / -0.61 / -53% (39t, 31%) |
| KB금융 | +18% / 0.66 / -62% | +1% / 0.15 / -32% (28t, 32%) | +7% / 0.49 / -32% (61t, 51%) | +3% / 0.27 / -29% (50t, 56%) |
| 기아 | +9% / 0.43 / -58% | -1% / -0.13 / -25% (20t, 25%) | -3% / -0.16 / -41% (46t, 30%) | -4% / -0.50 / -37% (31t, 29%) |
| **mean** | +22% / 0.68 / -65% | +0% / 0.05 / -31% | +0% / 0.07 / -38% | -0% / 0.03 / -29% |

Summary across the 20 stocks:

| | June rule | Owen, limit | Owen, bounce |
|---|---|---|---|
| mean win rate | 31% | 38% | **45%** |
| mean trades | 31 | 68 | 46 |
| mean Sharpe (hold 0.68) | 0.05 | 0.07 | 0.03 |
| mean max drawdown (hold -65%) | -31% | -38% | **-29%** |
| stocks where Sharpe > hold | 0 / 20 | 1 / 20 (META) | 0 / 20 |

What Owen's rules do: the bounce-confirmed entry lifts the hit rate from 31% to 45% and gives the smallest drawdowns of any variant — exactly the "buy when it has stopped and looks like it will go up" intent. What they do not do: earn. Winners shrink (you buy a day later and higher, the target does not move), so the equity curve stays flat and no variant beats holding the stock on a risk-adjusted basis, in either market. The stocks where the rule looked best (META, KB금융, AMZN) are the ones that oscillated inside a channel for years; the ones where it lost (한화에어로, NAVER, 셀트리온, BA) trended hard in one direction and the "support" kept breaking.

Honest conclusion for the whole day: a single-stock swing rule built on channel touches is a **risk-control tool, not a return engine**. Its real product is a smaller worst-case loss at the price of sitting out most of the up-move. Entry timing is the right knob to work on (it moved win rate 14 points), but the next gain has to come from *which* stocks to apply it to — channel-bound names — which is a selection problem this repo does not solve yet.

## Round 6 — can a model pick *which* touches to take? (2026-09-11)

Why this question: the swing rule's ceiling on a single stock is set by exposure (~16% of days in the market) and a fixed target, so even a perfect touch-picker cannot beat holding a stock that trended (with every trade a winner, mean CAGR would be +19.7% vs +22.1% for holding; 9 of 20 stocks would need a win rate above 100%). As one book across many stocks, exposure fills in (about 3 positions open on average) and per-trade expectancy becomes the only lever, so touch selection is worth testing there.

Setup (`scripts/touch_dataset.py`, `scripts/touch_model.py`, simulator now in `tradebuilder/swing.py`): every touch of a proposed support line on the same 20 stocks, no entry gate, overlapping events allowed — **3,789 touches, 2011-2026**. Each row: what the touch day looked like at its close (wick ratio, close/low vs the line, gap, volume ratio, 5/20-day return, RSI, ATR, range) plus the builder's own read at order time (state, cloud, RSI flag, channel position, reward:risk, channel score/reversal rate/touch count) and the label: buy the next open, exit at target / stop (3-5%, lifted to ≥5% below the fill) / 40 days. Walk-forward by year, 3 years minimum training, 60-day embargo before each test year, pooled across stocks; out-of-sample 2014-2026, 3,420 touches.

| take which touches | n / yr | win | mean ret / trade | sum of trade returns / yr |
|---|---|---|---|---|
| all | 263 | 36.8% | +0.1% | +13.7% |
| Owen's gate (cloud, RSI, lower 80%, rr ≥ 1) | 104 | 33.3% | +0.1% | +9.6% |
| **bounce-confirmed** (closed back above the line) | 121 | **47.3%** | +0.2% | +23.6% |
| gate + bounce (= round 5's best variant) | 46 | 43.8% | +0.2% | +9.3% |
| logistic, P(win) > 0.5 | 72 | **54.8%** | +0.2% | +12.8% |
| logistic, top 30% by P(win) per year | 79 | 51.7% | −0.0% | −3.1% |
| logistic, E[ret] = p·target − (1−p)·stop > 0 | 124 | 44.6% | **+0.3%** | **+28.6%** |
| gradient boosting, E[ret] > 0 | 132 | 43.3% | +0.2% | +28.1% |
| ridge / GBM regression on the return itself, top 30% | 79 | 35-37% | +0.0-0.2% | +1.8% / +14.2% |

Out-of-sample AUC for P(win): 0.686 (logistic) / 0.685 (GBM), positive in 13 of 13 years; the bounce flag alone scores 0.603. Largest logistic weights: `target_pct` −0.42, `low_vs_line` +0.40, `close_vs_line` +0.26, `stop_pct` −0.16, `wick` +0.12, `rsi_14` −0.12.

What this says:

- **The classifier's headline is a tautology.** Its strongest signal is "the target is close", which raises the hit rate to 55% while the money per trade stays where it was — it is picking easy small wins. Ranking by P(win) alone actually loses money (top 30%: −3.1%/yr). Any "predict the bounce" model has to be scored on expected return, not accuracy.
- **After correcting for payoff, the model's edge over the one-line bounce rule is within noise.** E[ret] > 0 takes about the same number of touches as the bounce rule (124 vs 121 per year) and earns +28.6% vs +23.6% summed per-trade return per year — but it beats the bounce rule in only **7 of 13 years**, and the yearly sums swing from −1.7 to +2.1 with the market (2016, 2023 good; 2018, 2022, 2024 bad for every rule). Pooled US touches are better than KRX (win 47% vs 42%, mean +0.3% vs +0.1%).
- **Owen's gate hurts** on this dataset (33% vs 37% for all touches): the cloud/RSI/position filters remove touches without improving the ones that remain. The bounce confirmation is the only hand rule that does anything, and the model mostly re-learns it (`low_vs_line`, `close_vs_line`, `wick`).
- Mean return per trade is +0.2-0.3% at best against 10 bps round trip, with 46% of exits at the target and 45% at the stop. That is the whole edge: about a quarter of a percent per touch, unstable year to year.

Honest conclusion: touch-day information separates bounces from breakdowns a little (AUC 0.69, every year), but not enough to change the economics — the model turns 47% → 55% hit rate into the *same* money, and once you score it on money it is a coin flip against "did it close back above the line". The channel touch is not where the return lives. If this line is pursued further, the two things not yet tried are (1) a market-regime input (index 5/20-day return — every rule's bad years are the same years) and (2) letting winners run past the fixed target, since the target cap is what turns better picks into no extra money.

Bookkeeping from porting the simulator: the round-5 "June rule" column was run with the `ready+wait` gate (not `ready` only); the `n/a` CAGR cells for 삼성전자 and 한화오션 were caused by zero-price rows FinanceDataReader returns on halted days (2018 split), now dropped in `fetch_krx`. Re-running round 5 with the ported code on 2026-09-11 reproduces every US cell within ±1 trade (yfinance re-adjusts the whole series on each dividend); KRX cells move by up to ~9 trades because the zero-price rows (삼성전자, 한화오션, NAVER) also distorted the channel scale for a year and because KRX tick rounding makes the one-position-at-a-time path sensitive to any data revision. Old and new code give identical results on identical data. The summary row is unchanged: mean win 32% / 38% / 45%, Sharpe above hold in 0 / 1 / 0 of 20.

## Round 7 — release the target cap (2026-09-11)

Round 6 ended on: better picks do not turn into money because the fixed target (the next channel line, about +5%) caps every winner. So keep the entries and change only the exit. `scripts/touch_exits.py` re-labels the same 3,787 touches under exits that let winners run (`label_trailing` in `tradebuilder/swing.py`); `scripts/touch_book.py` then runs them as **one book across all 20 stocks** — take a touch if a slot is free, size 1/N, mark to market daily — against holding the same 20 stocks equal-weight.

Per touch (buy the next open; initial stop as before, 3-5% below the line and at least 5% below the fill):

| bounce-confirmed touches, exit = | win | avg win | avg loss | mean ret / trade | hold days | years > 0 |
|---|---|---|---|---|---|---|
| next channel line, 40 days (rounds 5-6) | 48% | +4.6% | −3.8% | +0.2% | 5 | 10 / 16 |
| hold through target, then trail 2 ATR | 38% | +6.1% | −3.1% | +0.4% | 7 | 11 / 16 |
| no target, trail 2 ATR below the highest high | 36% | +6.7% | −3.2% | +0.4% | 7 | 11 / 16 |
| no target, trail 3 ATR | 34% | +10.2% | −3.7% | +1.0% | 13 | 10 / 16 |
| **no target, trail 8%** | 34% | **+10.8%** | −3.8% | **+1.3%** | 18 | **12 / 16** |

Mean return per touch goes from +0.2% to +1.3% — the first change all day that moved the per-trade economics rather than the hit rate. It moves the same way for all touches and for gate + bounce. The cost is the hit rate (48% → 34%) and three times the holding period.

As one book (2011-2026, 5 bps per side, trailing 8% exit):

| slots (size 1/N) | selection | CAGR | Sharpe | maxDD | avg open | trades |
|---|---|---|---|---|---|---|
| 8 | bounce, fixed target | +2.9% | 0.43 | −22% | 2.2 | 1,567 |
| 8 | bounce, trail 8% | +9.9% | 0.88 | −22% | 4.5 | 1,197 |
| 8 | all touches, trail 8% | +11.9% | 0.91 | −32% | 5.8 | 1,934 |
| 4 | bounce, trail 8% | +14.8% | 0.90 | −32% | 3.0 | 770 |
| 3 | all touches, trail 8% | +17.8% | 0.93 | −32% | 2.5 | 785 |
| — | **equal-weight hold of the 20** | **+27.3%** | **1.37** | −37% | — | — |

What this says:

- **The exit was the bottleneck, not the entry.** Same touches, same stops: replacing the fixed target with a trailing stop takes the book from Sharpe 0.43 to about 0.9 at the same drawdown (−22%), and CAGR from +3% to +10%. Nothing on the entry side today (Owen's gate, a classifier, expected-return ranking) moved anything by a comparable amount.
- **Once winners run, touch selection stops mattering.** All touches and bounce-confirmed touches land at the same Sharpe (0.91 vs 0.88); the gate + bounce subset is worse only because it takes too few trades to fill the book. The return is coming from *being long a single stock with a trailing stop while it trends*, not from reading the touch.
- **It still loses to holding these stocks, and that benchmark is rigged.** The 20 names were picked in 2026 knowing they were AAPL, NVDA, TSLA, SK하이닉스 and so on; equal-weight hold of that list has Sharpe 1.37, which no long-only rule on those names is going to beat. The fair test is a universe chosen without hindsight (all S&P 500 / KOSPI 200 members as of each year). The rule's Sharpe of about 0.9 with a third less drawdown is the number to carry forward, not the gap to +27%.
- Concentrating (3-4 slots) buys CAGR (+15-18%) with the same Sharpe and a deeper worst loss (−32%); 8 slots leave about half the capital idle because only 2-5 positions are open on average. Sizing by the number of live signals rather than a fixed 1/N is the obvious next fix.

Honest conclusion for the day: the channel touch is a decent *place to enter with a tight stop*, and the fixed target was what made it look like it could not earn. With winners allowed to run, the swing rule becomes an ordinary trend-following book on single stocks — Sharpe about 0.9, worst loss about a third less than holding — which is respectable and not special. What is still untested: a hindsight-free universe, sizing by live signal count, and a market-regime filter (every rule's bad years are 2018, 2022, 2024).

## Round 7 — adversarial review (same day)

Three independent reviewers (one defending round 7, one attacking it, one judging and re-running the numbers) were given the code, `data/touches_exits.csv`, and the book backtest. Everything below was re-run by the judge and spot-checked again afterwards (hold20 +2.01% / fix20 +0.54% / trail8 +1.07% on 3,761 touches; hold20 − trail8 = +0.94%, t = 4.98).

**Placebo entries.** Enter every 5th trading day on the same 20 stocks with no channel at all, same initial stop, same 8% trailing exit: +1.53% per trade (n = 12,755). Channel touches: +1.05% (all), +1.26% (bounce-confirmed). In the US the bounce-confirmed touch and the placebo are a dead heat (+1.84% vs +1.85%); in KRX the touch is clearly worse (+0.34% vs +1.06%). As a 3-slot book the placebo and the touch rule land on the same Sharpe (0.84 vs 0.93, CAGR +17.2% vs +17.8%). **The channel line carries no entry information in the US and negative information in KRX.**

**"The exit was the bottleneck" was the wrong reading.** Per-trade return under each rule, and the same trades normalised by capital-days (return per day of capital tied up, annualised):

| rule on the same 3,787 touches | mean / trade | hold days | per capital-day | annualised |
|---|---|---|---|---|
| fixed target (rounds 5-6) | +0.2% | 5 | — | — |
| stop only, exit after 20 days (`fix20`) | +0.55% | 9 | 0.058% | +14.7% |
| touch + trail 8% (round 7) | +1.05% | 15 | 0.068% | +17.2% |
| placebo entry + trail 8% | +1.53% | 18 | 0.083% | +21.0% |
| **no rules: buy next open, sell close 20 days later** | **+2.01%** | 20 | **0.100%** | +25.3% |
| equal-weight hold of the 20 | — | — | 0.099% | +27.3% |

The ladder from +0.2% to +1.3% per trade in rounds 5-7 is a *holding-period* ladder: every rule earns less per day of capital than simply being long, and the fewer rules, the closer to the drift. Matched holds (same entry, same number of days as the trailing exit, no rule) return +1.14% vs +1.05% for the trailing stop with correlation 0.98 — the trailing stop is a holding-period extender, not a source of return. The initial stop is a net cost: same 20-day window, +0.55% with the 3-5% stop vs +2.01% without it. As a 3-slot book, "buy any touch, hold 20 days, no stop" gives +22.0% / Sharpe 0.94 / −36%, above touch + trail (+17.8% / 0.93 / −32%) and the placebo (+17.2% / 0.84 / −39%).

**Other findings.** Return is concentrated: the top 1% of trades are 46% of the total and dropping the top 5% turns the mean negative. Removing MSFT, AAPL and BA cuts every rule by roughly half but leaves the ranking intact. Effective sample size is far below 3,787 (adjacent touches on the same stock correlate +0.3; about 267 stock-year blocks). Rounds 1-7 tried about 95 configurations with one walk-forward (round 6, verdict: no edge). Look-ahead, the `path[-1]` rescaling in `touch_book.py`, and slot management were checked and are fine. The paired exit comparison in round 7 is correct as a calculation (+0.98% / trade, t = 8.0); what it shows is that the rules *subtract* less when the target is removed, not that the touch or the exit adds anything.

**What survives:** the gate buys drawdown with return (round 4-5); bounce confirmation raises the hit rate (round 5); the touch-selection classifier is a tautology once scored on money (round 6); the hand-picked 20-stock benchmark is contaminated (round 7). **What dies:** "the exit is the bottleneck"; "the touch is a good place to enter with a tight stop"; keeping the current structure and adding universe, sizing and regime layers on top.

**Next round, one hypothesis at a time, block-bootstrapped by stock-year, nothing else added:**

1. A hindsight-free universe (each year's S&P 500 / KOSPI 200 members, random 40): does anything — touch + trail, or plain 20-day holds — earn more per capital-day than the universe drift once the 2026 selection is gone? This is the only unresolved variable.
2. Price the stop: same entries, `owen_stop` on/off, how much drawdown does the −1.46% per trade actually buy?
3. One regime filter (index 20-day return > 0): are 2018 / 2022 / 2024 a rule failure or plain beta?

If 1 fails, this repo resets to a "rule-free N-day long book" and the channel engine stays what round 4 already suggested: a chart annotation, not a signal.

**Regime check (Owen's question: is hold winning only because 2011-2026 was a bull market?).** Partly yes. SPY was down in only 2 of the 16 sample years, and in those two (2018, 2022) the rules did not beat holding either: per touch, hold20 −1.0% / −0.6% vs stop-only −1.0% / −1.3% vs trail 8% −0.6% / −1.2%. Across the five weak years the mean is hold20 +0.7% vs about −0.5% for both rules; what the stop buys per trade is the tail (5th percentile −5% vs −14%), not the year. To see a real bear regime the same three exits were run with placebo entries (every 5th day) on SPY / QQQ / IWM over 2000-2010 vs 2010-2026:

| | hold 20 days | stop only, 20 days | trail 8% (avg hold) | 5th pct hold / trail |
|---|---|---|---|---|
| SPY 2000-2010 | +0.01% | −0.03% | **+0.33%** (47 d) | −8.5% / −4.8% |
| QQQ 2000-2010 | −0.23% | −0.16% | **+0.60%** (34 d) | −16.4% / −5.1% |
| IWM 2000-2010 | +0.36% | +0.38% | +0.37% (35 d) | −10.7% / −5.1% |
| SPY 2010-2026 | +1.06% | +0.66% | +2.12% (62 d) | −6.0% / −4.8% |
| QQQ 2010-2026 | +1.42% | +0.85% | +1.90% (48 d) | −7.1% / −5.1% |

In the flat decade the trailing exit is the only rule with a positive mean and it cuts the worst trades by two thirds; in the bull decade holding earns more per day of capital (SPY: 0.053% vs 0.034%). So "the rules only subtract" is a bull-market statement. The cost of the stop is paid every year; its protection shows up only when the drift is gone. That makes the regime question the first thing to settle, and it means any rule here has to be scored on both a bull and a flat span, never on 2010-2026 alone.

## Round 8 — one regime filter (2026-09-11)

Pre-registered: enter only when the index's 20-day return is positive (SPY for US, KOSPI for KRX). Nothing else changes. `scripts/regime_filter.py`, two panels, same three exits as the regime check above. A 200-day-MA version is printed once as a sanity variant, not as a second hypothesis.

| | filter on | hold 20d, no stop: sum / yr | trail 8%: sum / yr | trail 8% mean / trade |
|---|---|---|---|---|
| SPY 2000-2010, no filter | — | +0.5% | +16.6% | +0.33% |
| SPY 2000-2010, r20 > 0 | 57% of days | +1.5% | +19.8% | +0.69% |
| SPY 2010-2026, no filter | — | +53.5% | +106.9% | +2.12% |
| SPY 2010-2026, r20 > 0 | 69% | +25.1% | +66.6% | +1.93% |
| 20-stock touches, no filter | — | +491% | +261% | +1.07% |
| 20-stock touches, r20 > 0 | 53% of touches | +227% | +153% | +1.19% |

(sums are per-trade returns added up per year, i.e. exposure-aware; return per capital-day is unchanged by the filter in every cell, 0.0000-0.0001 differences.)

Verdict: **fails.** The filter raises the per-trade mean a little in the flat decade and not at all on the stocks, while removing a third to a half of the trades everywhere — so exposure-adjusted return is flat in 2000-2010 and halved in 2010-2026. It does not rescue the bad years: on the touches 2022 gets *worse* with the filter on (hold20 −0.6% → −5.2% per trade, trail −1.2% → −1.4%), because a positive 20-day index return inside a bear market is a rally to sell, not a regime; 2018 improves slightly (−1.0% → −0.3%); 2011 and 2015 worsen. The 200-day-MA variant does help in the flat decade on SPY (hold20 sum +0.5% → +19% / yr, trail +17% → +33%) but costs the same third of the bull-market exposure and is neutral on the stocks (per capital-day 0.0007 → 0.0008). So the bad years are beta the rules cannot see in time with a price-only index signal, and "hold in bull, trail in flat" is not something a 20-day lookback can switch.

State of the research after eight rounds: on hindsight-picked large caps 2011-2026, every rule tested earns less per day of capital than being long; the trailing exit is the only rule with a positive mean in a flat decade and it buys a two-thirds cut in the worst trades; the channel touch adds nothing as an entry; a simple index regime filter does not change any of that. The single remaining question is whether any of this changes on a universe chosen without hindsight.
