# trade-builder

Pick a few technical indicators, let a small model learn **how much each one should count**, then find out whether that edge survives an honest test. No UI, no community, no paper-trading account: this is the core that any of those would sit on.

Three pieces:

1. **Weighted indicator model** (`tradebuilder/model.py`): standardized indicator features → logistic regression → P(next day up). The learned weights are the explanation: for any day you can print "vol_20 pulled toward flat, rsi_14 pulled toward long", summing exactly to the model's log-odds.
2. **Backtest** (`tradebuilder/backtest.py`): long/flat, transaction costs per side, no look-ahead (a position decided on day *t*'s close earns *t*→*t+1*). Reports total return, CAGR, Sharpe, max drawdown, win rate, exposure.
3. **Walk-forward validation** (`tradebuilder/validation.py`): fit on 750 days, trade the next 250 with frozen weights, slide, repeat. Only the stitched out-of-sample curve is reported, and `overfit_warning` says so in plain words when in-sample beats out-of-sample by too much.

Two baselines ship alongside so the model has something to beat: an RSI 30/70 if/then rule and buy & hold.

## Result on SPY (2010-2026, daily, 5 bps per side)

```
weighted (logistic)   OOS  total +312.7% | CAGR +11.6% | Sharpe 0.76 | maxDD -33.7% | win 68% of 133 trades | exposure 90%
RSI 30/70 rule        OOS  total +101.3% | CAGR  +5.6% | Sharpe 0.51 | maxDD -28.3% | win 100% of 12 trades | exposure 18%
buy & hold            OOS  total +456.2% | CAGR +14.2% | Sharpe 0.87 | maxDD -33.7% | exposure 100%
```

The weighted model beats the hand-written rule and **loses to buy & hold**. That is the honest answer for a daily long/flat strategy on an index that went up for sixteen years: the model is right 68% of the time it enters, but sitting out 10% of days costs more than it saves. Out-of-sample Sharpe is positive in 10 of 13 yearly folds and negative in 3 (2015, 2018, 2022 — all drawdown years), so the edge is real but small and not stable enough to pay for itself after costs.

Per-fold table, learned weights, and the explained latest signal are all printed by:

```bash
pip install -r requirements.txt
python scripts/run_backtest.py --ticker SPY --start 2010-01-01
python scripts/run_backtest.py --ticker QQQ --features ichimoku
python scripts/run_backtest.py --csv data/my_bars.csv --train 500 --test 125 --cost-bps 10
python -m pytest tests -q
```

## Does it depend on the asset?

`scripts/compare_assets.py` runs the identical walk-forward on five ETFs (2010-2026, 5 bps per side):

| asset | yrs | model Sharpe | RSI Sharpe | hold Sharpe | model CAGR | hold CAGR | model maxDD | hold maxDD | exposure | OOS folds >0 |
|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 16.5 | 0.76 | 0.51 | 0.87 | +11.6% | +14.2% | -33.7% | -33.7% | 90% | 10/13 |
| QQQ | 16.5 | 0.90 | 0.74 | 0.95 | +16.7% | +19.4% | -28.6% | -35.1% | 89% | 11/13 |
| TLT | 16.5 | 0.20 | -0.08 | 0.12 | +1.6% | +0.6% | -27.2% | -48.4% | 64% | 8/13 |
| GLD | 16.5 | 0.37 | 0.29 | 0.61 | +3.8% | +8.8% | -29.7% | -35.7% | 60% | 7/13 |
| IWM | 16.5 | 0.47 | 0.36 | 0.54 | +6.8% | +9.8% | -30.9% | -41.1% | 70% | 10/13 |

Pattern: the weighted model beats the RSI rule everywhere, loses to buy & hold on everything that trended up (SPY, QQQ, IWM, GLD), and **beats buy & hold on TLT**, the one asset that went sideways and then fell, with about half the drawdown (-27% vs -48%). Same on QQQ: less return than holding, but a shallower worst loss (-29% vs -35%). That is what a long/flat model trained on next-day direction turns out to be: not an alpha engine, a drawdown limiter that charges a fee in bull markets. Whether that fee is worth paying is a question about the investor, not the model.

## Ichimoku as the feature set

A friend's suggestion: instead of the seven generic indicators, feed the model **Ichimoku Kinko Hyo** — conversion/base line gap, signed distance from the cloud, cloud thickness, lagging span. Four features, same walk-forward (`--features ichimoku`):

| asset | yrs | model Sharpe | RSI Sharpe | hold Sharpe | model CAGR | hold CAGR | model maxDD | hold maxDD | exposure | OOS folds >0 |
|---|---|---|---|---|---|---|---|---|---|---|
| SPY | 16.3 | 0.84 | 0.46 | 0.85 | +13.5% | +13.9% | -31.0% | -33.7% | 94% | 11/13 |
| QQQ | 16.3 | 1.01 | 0.76 | 0.95 | +19.9% | +19.4% | -28.6% | -35.1% | 90% | 13/13 |
| TLT | 16.3 | 0.22 | -0.11 | 0.08 | +1.8% | +0.1% | -30.3% | -48.4% | 63% | 8/13 |
| GLD | 16.3 | 0.62 | 0.31 | 0.64 | +8.0% | +9.4% | -32.7% | -29.6% | 69% | 10/13 |
| IWM | 16.3 | 0.60 | 0.30 | 0.53 | +10.0% | +9.6% | -32.6% | -41.1% | 79% | 8/13 |

This is the first configuration that **matches buy & hold on risk-adjusted return while cutting drawdown**: 5-asset portfolio Sharpe 1.05 vs 0.96 for hold, worst loss -17% vs -25%. It beats hold outright on QQQ, TLT and IWM.

Caveats, because this is exactly where people fool themselves:
- It depends on the training window. With 750 training days the portfolio Sharpe is 1.05; with 500 or 1000 it is 0.92-0.94, a tie with hold (0.93-0.94). Drawdown reduction holds in all three.
- Fold by fold it beats hold about half the time (36 of 65 asset-years). The edge is small and comes from avoiding the bad years, not from winning the good ones.
- Adding the Ichimoku features *on top of* the base seven made things worse (mean Sharpe 0.48 vs 0.54): more inputs, same 750 days, more overfitting. Fewer, structurally different features won.
- The textbook Ichimoku rule (long when price is above the cloud and tenkan > kijun) scores 0.36 on its own. The value is in letting the model weight the four signals, not in the rule.

## The channel swing rule as trades (`tradebuilder/swing.py`)

The daily long/flat model is one way to trade; the other one in this account is the Fibonacci-channel swing rule from [`fib-channel-trader`](https://github.com/mirgaon314/fib-channel-trader): buy at a channel support line, target the next line, stop below. `simulate_swing` turns that one-shot signal into a full trade history (scan every 5 days, order valid 5 days, exit at target / stop / 40 days, one position at a time, 5 bps per side) so it can be scored the same way. Entry can be a limit at the line or the open after a confirmed bounce; the stop rule and the entry gate are pluggable. It needs the `trader` package (`TRADER_PATH`, default `~/trader`).

```bash
python scripts/swing_stocks.py --us AAPL META --kr 005930 --variants owen-bounce
python scripts/swing_stocks.py --out stats.csv --trades-out trades.csv   # 10 US + 10 KRX, three variants (~25 min)
```

Findings so far are in `docs/research-notes.md` rounds 4-5: on 20 single stocks the rule keeps drawdowns at roughly half of holding and the bounce-confirmed entry lifts the win rate from 31% to 45%, but no variant beats holding on a risk-adjusted basis. Its ceiling is set by exposure (~16% of days in the market) and a fixed target, not by the entry. Round 6 asks whether a model can pick *which* touches to take: on 3,789 touches it separates bounces a little (out-of-sample AUC 0.69 every year) but, once scored on expected return rather than hit rate, it is a coin flip against the one-line rule "did it close back above the line". Round 7 changes the exit instead and the book goes from Sharpe 0.43 to 0.88 — but an adversarial review the same day shows why: the gain is holding time, not the exit. Entering every 5th day with no channel does as well or better, and buying any touch and holding 20 days with no rules at all beats every rule on return per day of capital. On these 20 stocks the channel touch adds nothing and the stop is a net cost. Rounds 8-9 close the remaining questions: an index regime filter fails, and on a hindsight-free S&P 500 sample (2001-2025) the drift halves but the ordering holds — no rules > stop only > trailing stop, per day of capital. The trailing exit is the one rule that comes out ahead when the index drift is zero (2000-2010 ETFs), buying a large cut in the worst trades. Rounds 10-11 move to the setup quants use — dollar-neutral decile long-short on the point-in-time S&P 500, validated against Kenneth French's momentum factor (0.91 correlation) — and find that neither 12-1 momentum nor this repo's indicator model carries cross-sectional information since 2001. Full record: `docs/research-notes.md`.

## What it does *not* do (yet)

- shorting, position sizing, multiple assets
- trendline learning, community library, trading-personality profiling, tutorials — these are in the original product idea (`docs/idea-doc.pdf`) and would layer on top of this core
- the previous Next.js scaffold was dropped; a UI is worth building only once the core produces something worth showing

## Layout

```
tradebuilder/
  data.py         load_csv / fetch(ticker) → OHLCV frame
  indicators.py   sma, ema, rsi, macd, feature_frame(df), latest_features(df)
  model.py        WeightedIndicatorModel (+ explain), RsiRuleModel, AlwaysLong
  backtest.py     run_backtest(close, positions, cost_bps) → BacktestResult
  validation.py   walk_forward(...), overfit_warning(...)
  swing.py        simulate(df, gate, entry, stop_fn) → trade-level stats of the channel swing rule (needs `trader`)
scripts/run_backtest.py   end-to-end CLI
scripts/compare_assets.py same walk-forward across several tickers
scripts/swing_stocks.py   channel swing rule on 10 US + 10 KRX stocks, three entry/stop variants
scripts/touch_dataset.py  every support-line touch on those stocks with touch-day features + outcome → data/touches.csv (generated, not committed)
scripts/touch_model.py    walk-forward model that picks which touches to take, scored against the hand rules
scripts/touch_exits.py    re-labels every touch under trailing-stop exits (no fixed target)
scripts/touch_book.py     one book across the 20 stocks: N slots, 1/N sizing, daily mark to market, vs equal-weight hold
scripts/regime_filter.py  one index regime filter (20-day return > 0) on ETFs 2000-2026 and on the touches — it fails
scripts/universe.py       hindsight-free S&P 500 sample per year (2001-2025), placebo entries, three exits — holding still wins per capital-day
scripts/xsec.py           cross-sectional long-short on the point-in-time S&P 500 (monthly deciles, dollar-neutral); 12-1 momentum matches French's UMD at 0.91 correlation and earns nothing since 2001
scripts/xsec_model.py     the weighted indicator model as a cross-sectional ranking signal, walk-forward 2004-2026 — no information (long-short t = -0.3)
tests/                    14 tests: indicator sanity, no-look-ahead, cost accounting, fold shapes, explanation sums to log-odds, swing exit/bounce/stop/trailing logic, touch features and labels
```

Design notes: [DESIGN.md](DESIGN.md).

Owen (Gaon) Park · [LinkedIn](https://www.linkedin.com/in/owen-park-489202325)
