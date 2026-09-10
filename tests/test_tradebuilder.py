import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tradebuilder import AlwaysLong, WeightedIndicatorModel, feature_frame, rsi, run_backtest, sma, walk_forward


def _prices(n=1200, seed=0, drift=0.0003):
    rng = np.random.default_rng(seed)
    r = rng.normal(drift, 0.01, n)
    close = 100 * np.cumprod(1 + r)
    idx = pd.bdate_range("2015-01-01", periods=n)
    return pd.DataFrame({"open": close, "high": close * 1.01, "low": close * 0.99, "close": close, "volume": 1e6}, index=idx)


def test_sma_and_rsi_ranges():
    df = _prices(300)
    assert np.isclose(sma(df["close"], 5).iloc[-1], df["close"].iloc[-5:].mean())
    r = rsi(df["close"]).dropna()
    assert r.between(0, 100).all()


def test_feature_frame_has_no_lookahead_and_target():
    df = _prices(300)
    F = feature_frame(df)
    assert "y" in F.columns and set(F["y"].unique()) <= {0, 1}
    # last feature row is the day before the last close (target needs t+1)
    assert F.index[-1] == df.index[-2]


def test_buy_and_hold_matches_price_path():
    df = _prices(300)
    pos = pd.Series(1, index=df.index)
    res = run_backtest(df["close"], pos, cost_bps=0.0)
    expected = df["close"].iloc[-1] / df["close"].iloc[0] - 1
    assert np.isclose(res.metrics["total_return"], expected, rtol=1e-9)
    assert res.metrics["n_trades"] == 1


def test_flat_earns_nothing_and_costs_apply_on_changes():
    df = _prices(100)
    flat = pd.Series(0, index=df.index)
    assert run_backtest(df["close"], flat).metrics["total_return"] == 0.0
    pos = pd.Series([1, 0] * 50, index=df.index)
    res = run_backtest(df["close"], pos, cost_bps=100.0)
    assert res.metrics["n_trades"] == 50
    assert res.metrics["total_return"] < 0.0  # 1% per flip on a driftless-ish path


def test_positions_use_only_past_data():
    """Shifting a position series earlier must change the result (proves the t -> t+1 convention)."""
    df = _prices(200, seed=3)
    pos = (df["close"].pct_change() > 0).astype(int)
    a = run_backtest(df["close"], pos, 0.0).metrics["total_return"]
    b = run_backtest(df["close"], pos.shift(-1).fillna(0).astype(int), 0.0).metrics["total_return"]
    assert not np.isclose(a, b)


def test_walk_forward_shapes():
    df = _prices(1200)
    F = feature_frame(df)
    wf = walk_forward(F, df["close"], WeightedIndicatorModel, train=500, test=200)
    assert len(wf.folds) == (len(F) - 500) // 200
    assert wf.positions.index.is_monotonic_increasing
    assert set(wf.positions.unique()) <= {0, 1}
    assert wf.folds[0].weights is not None and len(wf.folds[0].weights) == 7


def test_explain_sums_to_log_odds():
    df = _prices(600)
    F = feature_frame(df)
    m = WeightedIndicatorModel().fit(F)
    row = F.iloc[-1]
    ex = m.explain(row)
    assert np.isclose(ex.attrs["intercept"] + ex["contribution"].sum(), ex.attrs["log_odds"])
    assert np.isclose(ex.attrs["p_up"], m.proba(F.iloc[[-1]]).iloc[0], atol=1e-9)
