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
scripts/run_backtest.py   end-to-end CLI
scripts/compare_assets.py same walk-forward across several tickers
tests/                    7 tests: indicator sanity, no-look-ahead, cost accounting, fold shapes, explanation sums to log-odds
```

Design notes: [DESIGN.md](DESIGN.md).

Owen (Gaon) Park · [LinkedIn](https://www.linkedin.com/in/owen-park-489202325)
