# Design notes

## Why weights instead of rules

An if/then strategy ("RSI < 30 → buy") is one point in a space of strategies. Giving each indicator a weight and fitting the weights turns that into a search over the space, and logistic regression keeps the search small enough that the answer stays readable. The weights **are** the model, so explanation is free.

## Why the target is next-day direction

Predicting the sign of tomorrow's return is the smallest question that still produces a tradeable signal. Regression on the return magnitude is noisier and invites overfitting. Position is long/flat, so a wrong "up" call costs one day of exposure, not leverage.

## Why walk-forward, not one train/test split

Markets change regime. A single split hides whether the weights fitted in 2012 still work in 2022. Walk-forward answers that per year, and the stitched out-of-sample equity curve is what a live trader would actually have seen. `overfit_warning` compares mean in-sample vs. out-of-sample Sharpe and counts losing folds.

## No look-ahead, enforced

- `feature_frame` builds every feature from data up to and including day *t*.
- `run_backtest` applies the day-*t* position to the *t → t+1* return (`pct_change().shift(-1)`).
- `tests/test_positions_use_only_past_data` fails if this alignment changes.

## Costs

`cost_bps` is charged on every position change, including the first entry. 5 bps per side is a reasonable retail assumption for a liquid ETF; the model's edge shrinks quickly as this rises, which is itself a useful thing to see.

## Extending

- new indicator: add a column in `feature_frame` and `latest_features`, list it in `DEFAULT_FEATURES`
- new model: implement `fit(F)` and `positions(F)`; optional `weights` for the fold table
- new asset: any OHLCV CSV via `load_csv`
