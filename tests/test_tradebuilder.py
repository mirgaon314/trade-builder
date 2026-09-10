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
    assert wf.folds[0].weights is not None and len(wf.folds[0].weights) == 7  # default set stays 7; ichimoku is opt-in


def test_explain_sums_to_log_odds():
    df = _prices(600)
    F = feature_frame(df)
    m = WeightedIndicatorModel().fit(F)
    row = F.iloc[-1]
    ex = m.explain(row)
    assert np.isclose(ex.attrs["intercept"] + ex["contribution"].sum(), ex.attrs["log_odds"])
    assert np.isclose(ex.attrs["p_up"], m.proba(F.iloc[[-1]]).iloc[0], atol=1e-9)


# ---------------------------------------------------------------- swing simulator (pure pieces run without `trader`)

from tradebuilder.swing import exit_check, owen_stop, touched


def test_exit_check_order_of_precedence():
    # gap below the stop at the open beats everything
    assert exit_check(o=90, h=120, l=85, c=100, entry=100, target=110, stop=95, held=1, max_hold=40) == (90, "stop-gap")
    # stop touched intraday fills at the stop
    assert exit_check(o=100, h=105, l=94, c=100, entry=100, target=110, stop=95, held=1, max_hold=40) == (95, "stop")
    # target touched fills at max(open, target): an up-gap is kept
    assert exit_check(o=112, h=115, l=111, c=113, entry=100, target=110, stop=95, held=1, max_hold=40) == (112, "target")
    # time exit at the close
    assert exit_check(o=100, h=101, l=99, c=100.5, entry=100, target=110, stop=95, held=40, max_hold=40) == (100.5, "time")
    assert exit_check(o=100, h=101, l=99, c=100.5, entry=100, target=110, stop=95, held=5, max_hold=40) is None


def test_touched_and_bounce():
    assert touched(l=99, c=101, line=100) == (True, True)    # reached and closed back above
    assert touched(l=99, c=99.5, line=100) == (True, False)  # reached, closed below
    assert touched(l=101, c=102, line=100) == (False, False)


def test_owen_stop_clamps_to_3_5_pct_band():
    idx = pd.bdate_range("2020-01-01", periods=20)
    daily = pd.DataFrame({"Low": 100.0}, index=idx)
    assert np.isclose(owen_stop(100.0, daily), 97.0)          # low too close -> 3% below
    daily["Low"] = 80.0
    assert np.isclose(owen_stop(100.0, daily), 95.0)          # low too far -> 5% below
    daily["Low"] = 96.0
    assert np.isclose(owen_stop(100.0, daily), 96.0 * 0.997)  # inside the band -> the low minus buffer


def test_simulate_smoke_if_trader_available():
    """End to end on synthetic bars when the fib-channel-trader checkout is present; skipped otherwise."""
    pytest = __import__("pytest")
    from tradebuilder.swing import simulate
    try:
        stats, trades = simulate(_prices(600, seed=3), gate="any", entry="bounce", stop_fn=owen_stop, start=300)
    except ImportError as e:
        pytest.skip(str(e))
    assert set(stats) >= {"trades", "win", "cagr", "sharpe", "maxdd", "exposure", "hold_cagr"}
    assert np.isfinite(stats["cagr"]) and np.isfinite(stats["sharpe"])
    if len(trades):
        assert (trades.entry_px > 0).all() and trades.ret.notna().all()
        assert (trades.target > trades.stop).all()


from tradebuilder.swing import bar_features, label_forward


def _bars(rows):
    idx = pd.bdate_range("2021-01-01", periods=len(rows))
    return pd.DataFrame(rows, columns=["Open", "High", "Low", "Close", "Volume"], index=idx, dtype=float)


def test_bar_features_read_the_touch_day():
    daily = _bars([[100, 101, 99, 100, 1000]] * 30 + [[99, 104, 94, 102, 3000]])  # last bar: pierced to 94, closed at 102
    f = bar_features(daily, 30, line=95.0)
    assert np.isclose(f["wick"], (102 - 94) / (104 - 94))
    assert np.isclose(f["low_vs_line"], 94 / 95 - 1) and np.isclose(f["close_vs_line"], 102 / 95 - 1)
    assert np.isclose(f["vol_ratio"], 3.0) and np.isclose(f["gap"], -0.01)
    assert 0 <= f["rsi_14"] <= 100 and f["atr_pct"] > 0


def test_label_forward_target_then_stop():
    base = [[100, 101, 99, 100, 1]] * 5
    # touch at i=4; next open 100; day 6 hits 110 target
    daily = _bars(base + [[100, 100.5, 99.5, 100, 1], [101, 111, 100, 110, 1]])
    lab = label_forward(daily, 4, target=110.0, stop=96.0, max_hold=40, cost=0.0)
    assert lab["why"] == "target" and np.isclose(lab["ret"], 0.10) and lab["days"] == 1
    # stop is lifted to at least 5% below the fill
    daily = _bars(base + [[100, 100.5, 99.5, 100, 1], [100, 100.5, 94.0, 95, 1]])
    lab = label_forward(daily, 4, target=110.0, stop=90.0, max_hold=40, cost=0.0)
    assert lab["why"] == "stop" and np.isclose(lab["ret"], -0.05)
    # no next bar -> no label
    assert np.isnan(label_forward(daily, len(daily) - 1, 110.0, 90.0, 40, 0.0)["ret"])


from tradebuilder.swing import label_trailing


def test_label_trailing_lets_winners_run_and_exits_on_pullback():
    base = [[100, 101, 99, 100, 1]] * 5
    up = [[100 + k, 101 + k, 99 + k, 100 + k, 1] for k in range(1, 21)]      # grinds up 20 points
    down = [[119, 119, 100, 101, 1]]                                         # then a sharp pullback
    daily = _bars(base + [[100, 100.5, 99.5, 100, 1]] + up + down)
    lab = label_trailing(daily, 4, stop=90.0, trail_pct=0.05, max_hold=120, cost=0.0)
    # highest high 121 -> trailing stop 114.95; pullback day opens 119 (above), low 100 hits the stop
    assert lab["why"] == "trail" and np.isclose(lab["ret"], 121 * 0.95 / 100 - 1) and lab["peak"] > 0.2
    # with a fixed target of 110 the old rule would have sold at 110; trailing kept ~15%
    from tradebuilder.swing import label_forward
    assert label_forward(daily, 4, 110.0, 90.0, 120, 0.0)["ret"] < lab["ret"]
    # a losing trade still stops out at the initial stop
    dn = _bars(base + [[100, 100.5, 99.5, 100, 1], [100, 100, 93, 94, 1]])
    lab = label_trailing(dn, 4, stop=96.0, trail_pct=0.05, cost=0.0)
    assert lab["why"] == "stop" and np.isclose(lab["ret"], -0.04)
