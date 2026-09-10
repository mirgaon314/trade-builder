"""Trade-level simulation of the Fibonacci-channel swing rule.

The rule lives in `fib-channel-trader` (https://github.com/mirgaon314/fib-channel-trader):
scan the chart, find the best channel, and if the price sits near a support line
propose a limit buy at that line with a target at the next line and a stop below.
This module turns that one-shot signal into a trade history so it can be scored:

    scan every `scan_every` days on data up to that day
    -> if the gate passes, place an order (buy / target / stop) valid `valid_days`
    -> fill it (at the line, or on the open after a confirmed bounce)
    -> exit at target, stop, or after `max_hold` days
    -> one position at a time, `cost` per side

It needs the `trader` package importable. Set TRADER_PATH to the checkout
(default ~/trader) or install it; `simulate` raises a clear error otherwise.

Research notes rounds 4 and 5 in docs/research-notes.md were produced by this code.
"""
from __future__ import annotations

import contextlib
import os
import sys
import warnings
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

StopFn = Callable[[float, pd.DataFrame], float]
TickFn = Callable[[float], float]


# ----------------------------------------------------------------------------- trader import


def _load_trader():
    path = os.environ.get("TRADER_PATH", str(Path.home() / "trader"))
    if path not in sys.path:
        sys.path.insert(0, path)
    try:
        from trader.channel import ChannelEngine
        from trader.indicators import ichimoku, rsi_with_signal
        import trader.signal.builder as builder
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "tradebuilder.swing needs the `trader` package from fib-channel-trader. "
            "git clone https://github.com/mirgaon314/fib-channel-trader ~/trader "
            "(or set TRADER_PATH to the checkout)"
        ) from e
    return ChannelEngine, ichimoku, rsi_with_signal, builder


def no_tick(p: float) -> float:
    """Tick rounding for markets without a KRX-style tick table (US)."""
    return p


def owen_stop(buy: float, daily: pd.DataFrame, swing_lookback: int = 10, buffer: float = 0.003,
              min_pct: float = 0.03, max_pct: float = 0.05) -> float:
    """Owen's stop: recent swing low (with buffer) if it is 3-5% below entry, else clamp to that band."""
    lo = float(daily["Low"].tail(swing_lookback).min()) * (1 - buffer)
    return min(max(lo, buy * (1 - max_pct)), buy * (1 - min_pct))


@contextlib.contextmanager
def _patched(builder, stop_fn: StopFn | None, tick_fn: TickFn | None):
    """Swap the builder's module-level stop / tick functions for the duration of a run."""
    saved = (builder._stop_price, builder._round_tick)
    if stop_fn is not None:
        builder._stop_price = stop_fn
    if tick_fn is not None:
        builder._round_tick = tick_fn
    try:
        yield
    finally:
        builder._stop_price, builder._round_tick = saved


# ----------------------------------------------------------------------------- gates


def gate_june(sig) -> bool:
    """The rule as shipped in June: state == ready (cloud ok, RSI < 70, reward:risk >= 2)."""
    return sig.state == "ready"


def gate_june_wait(sig) -> bool:
    return sig.state in ("ready", "wait")


def gate_owen(sig) -> bool:
    """Owen's gate: not below the cloud, RSI ok, lower 80% of the channel, reward:risk >= 1."""
    return (
        sig.confirm.get("cloud") != "below"
        and sig.confirm.get("rsi_ok", True)
        and sig.position < 0.8
        and sig.rr >= 1.0
    )


def gate_any(sig) -> bool:
    return True


GATES = {"june": gate_june, "june+wait": gate_june_wait, "owen": gate_owen, "any": gate_any}


# ----------------------------------------------------------------------------- pure pieces (testable without trader)


def exit_check(o: float, h: float, l: float, c: float, entry: float, target: float, stop: float,
               held: int, max_hold: int) -> tuple[float, str] | None:
    """Exit price and reason for one bar of an open long, or None to keep holding.

    Order of checks: gap through the stop at the open, stop touched, target touched, time.
    A target hit fills at max(open, target) so an up-gap is not given away.
    """
    if o <= stop:
        return o, "stop-gap"
    if l <= stop:
        return stop, "stop"
    if h >= target:
        return max(o, target), "target"
    if held >= max_hold:
        return c, "time"
    return None


def touched(l: float, c: float, line: float) -> tuple[bool, bool]:
    """(price reached the line today, and it closed back above it)."""
    return l <= line, l <= line and c > line


def _weekly(daily: pd.DataFrame) -> pd.DataFrame:
    return daily.resample("W-FRI").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}).dropna()


_ENGINE = None


def _signal_at(tr, daily: pd.DataFrame, weekly_all: pd.DataFrame, i: int):
    """The builder's signal using only bars up to index i. Returns (Signal | None, ScoredChannel | None)."""
    global _ENGINE
    ChannelEngine, ichimoku, rsi_with_signal, builder = tr
    if _ENGINE is None:
        _ENGINE = ChannelEngine()
    d = daily.iloc[: i + 1]
    w = weekly_all[weekly_all.index <= daily.index[i]]
    adp = _ENGINE.analyze_adaptive(w, d)
    best = adp.result.best
    if best is None:
        return None, None
    view = _ENGINE._window(d, adp.window_days)
    try:
        return builder.build_signal(best, view, ichimoku(view), rsi_with_signal(view)), best
    except Exception:
        return None, None


# ----------------------------------------------------------------------------- simulation


def simulate(
    df: pd.DataFrame,
    *,
    gate: str | Callable = "june",
    entry: str = "limit",
    stop_fn: StopFn | None = None,
    tick_fn: TickFn | None = None,
    scan_every: int = 5,
    valid_days: int = 5,
    max_hold: int = 40,
    cost: float = 0.0005,
    start: int = 300,
) -> tuple[dict, pd.DataFrame]:
    """Run the swing rule over `df` (lowercase ohlcv, daily) and return (stats, trades).

    entry = "limit"  : fill at the line the day price reaches it
    entry = "bounce" : wait for a day that reaches the line and closes above it, buy the next open;
                       the stop is lifted to at least 5% below that fill
    stop_fn / tick_fn override the builder's stop price and tick rounding (None = builder default).
    """
    warnings.filterwarnings("ignore")
    tr = _load_trader()
    builder = tr[3]
    ok_fn = GATES[gate] if isinstance(gate, str) else gate
    if entry not in ("limit", "bounce"):
        raise ValueError("entry must be 'limit' or 'bounce'")

    daily = df.rename(columns=str.capitalize)
    weekly_all = _weekly(daily)
    O, H, L, C = (daily[c].values for c in ("Open", "High", "Low", "Close"))
    idx = daily.index
    equity = np.ones(len(idx))
    pos = None      # (entry_px, target, stop, entry_i, order_i)
    order = None    # (buy, target, stop, placed_i)
    trades: list[dict] = []
    eq = 1.0
    scans = signals = 0

    with _patched(builder, stop_fn, tick_fn):
        for i in range(start, len(idx)):
            t = idx[i]
            if pos is not None:
                entry_px, tgt, stp, ei, oi = pos
                hit = exit_check(O[i], H[i], L[i], C[i], entry_px, tgt, stp, i - ei, max_hold)
                if hit is None:
                    equity[i] = eq * (C[i] / entry_px)
                    continue
                exit_px, why = hit
                r = exit_px / entry_px - 1 - cost
                eq *= 1 + r
                trades.append({"order": idx[oi], "entry": idx[ei], "exit": t, "entry_px": entry_px, "exit_px": exit_px,
                               "target": tgt, "stop": stp, "ret": r, "why": why, "days": i - ei})
                pos = None

            if order is not None:
                buy, tgt, stp, oi = order
                reached, bounced = touched(L[i], C[i], buy)
                if i - oi > valid_days:
                    order = None
                elif entry == "limit" and reached:
                    fill = min(O[i], buy)
                    eq *= 1 - cost
                    pos = (fill, tgt, stp, i, oi)
                    order = None
                    equity[i] = eq * (C[i] / fill)
                    continue
                elif entry == "bounce" and bounced and i + 1 < len(idx):
                    fill = O[i + 1]
                    eq *= 1 - cost
                    pos = (fill, tgt, max(stp, fill * 0.95), i + 1, oi)
                    order = None
                    equity[i] = eq
                    continue
            equity[i] = eq

            if pos is None and order is None and (i - start) % scan_every == 0:
                scans += 1
                sig, _ = _signal_at(tr, daily, weekly_all, i)
                if sig is not None and ok_fn(sig) and sig.target > sig.buy > sig.stop:
                    signals += 1
                    order = (sig.buy, sig.target, sig.stop, i)

    return _stats(equity, daily, trades, start, scans, signals), pd.DataFrame(trades)


def _curve_stats(curve: pd.Series) -> tuple[float, float, float]:
    r = curve.pct_change().dropna()
    cagr = float((curve.iloc[-1] / curve.iloc[0]) ** (252 / len(curve)) - 1)
    sharpe = float(r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else 0.0
    maxdd = float((curve / curve.cummax() - 1).min())
    return cagr, sharpe, maxdd


def _stats(equity: np.ndarray, daily: pd.DataFrame, trades: list[dict], start: int, scans: int, signals: int) -> dict:
    eqs = pd.Series(equity[start:], index=daily.index[start:])
    tr = pd.DataFrame(trades)
    cagr, sharpe, maxdd = _curve_stats(eqs)
    hold_cagr, hold_sharpe, hold_maxdd = _curve_stats(daily["Close"].iloc[start:])
    n = len(tr)
    return {
        "trades": n,
        "win": float((tr.ret > 0).mean()) if n else 0.0,
        "avg_win": float(tr.ret[tr.ret > 0].mean()) if n and (tr.ret > 0).any() else 0.0,
        "avg_loss": float(tr.ret[tr.ret <= 0].mean()) if n and (tr.ret <= 0).any() else 0.0,
        "cagr": cagr, "sharpe": sharpe, "maxdd": maxdd,
        "exposure": float((eqs.diff() != 0).mean()),
        "scans": scans, "signals": signals,
        "exits": tr.why.value_counts().to_dict() if n else {},
        "hold_cagr": hold_cagr, "hold_sharpe": hold_sharpe, "hold_maxdd": hold_maxdd,
    }


# ----------------------------------------------------------------------------- touch-event dataset


def bar_features(daily: pd.DataFrame, i: int, line: float) -> dict:
    """What the touch day looks like at its close, using bars up to i only. Pure pandas, no `trader`."""
    o, h, l, c = (float(daily[k].iloc[i]) for k in ("Open", "High", "Low", "Close"))
    close = daily["Close"]
    rng = h - l
    vol = daily["Volume"]
    v20 = float(vol.iloc[max(0, i - 20): i].mean()) if i > 0 else np.nan
    tr_ = pd.concat([daily["High"] - daily["Low"], (daily["High"] - close.shift()).abs(), (daily["Low"] - close.shift()).abs()], axis=1).max(axis=1)
    atr14 = float(tr_.iloc[max(0, i - 14): i].mean()) if i > 0 else np.nan
    d = close.diff()
    up = d.clip(lower=0).iloc[max(0, i - 14): i + 1].mean()
    dn = (-d.clip(upper=0)).iloc[max(0, i - 14): i + 1].mean()
    rsi14 = 100.0 if dn == 0 else 100 - 100 / (1 + up / dn)
    return {
        "wick": (c - l) / rng if rng > 0 else 0.5,           # 0 = closed at the low, 1 = closed at the high
        "close_vs_line": c / line - 1,
        "low_vs_line": l / line - 1,                          # how deep it pierced
        "gap": o / float(close.iloc[i - 1]) - 1 if i > 0 else 0.0,
        "vol_ratio": float(vol.iloc[i]) / v20 if v20 and v20 > 0 else np.nan,
        "ret_5": c / float(close.iloc[i - 5]) - 1 if i >= 5 else np.nan,
        "ret_20": c / float(close.iloc[i - 20]) - 1 if i >= 20 else np.nan,
        "rsi_14": rsi14,
        "atr_pct": atr14 / c if atr14 else np.nan,
        "range_pct": rng / c,
    }


def label_forward(daily: pd.DataFrame, i: int, target: float, stop: float, max_hold: int, cost: float) -> dict:
    """Outcome of buying the open of bar i+1 and running the exit rule for up to max_hold bars."""
    O, H, L, C = (daily[c].values for c in ("Open", "High", "Low", "Close"))
    if i + 1 >= len(O):
        return {"fill": np.nan, "ret": np.nan, "why": "", "days": np.nan}
    fill = O[i + 1]
    stop = max(stop, fill * 0.95)
    for j in range(i + 1, min(len(O), i + 1 + max_hold + 1)):
        hit = exit_check(O[j], H[j], L[j], C[j], fill, target, stop, j - (i + 1), max_hold)
        if hit is not None:
            px, why = hit
            return {"fill": fill, "ret": px / fill - 1 - 2 * cost, "why": why, "days": j - (i + 1)}
    return {"fill": fill, "ret": C[-1] / fill - 1 - 2 * cost, "why": "open", "days": len(O) - 1 - (i + 1)}


def atr_series(daily: pd.DataFrame, n: int = 14) -> np.ndarray:
    """Average true range per bar using bars up to and including that bar (simple mean)."""
    close = daily["Close"]
    tr_ = pd.concat([daily["High"] - daily["Low"], (daily["High"] - close.shift()).abs(), (daily["Low"] - close.shift()).abs()], axis=1).max(axis=1)
    return tr_.rolling(n, min_periods=1).mean().values


def label_trailing(daily: pd.DataFrame, i: int, stop: float, *, atr: np.ndarray | None = None, atr_mult: float = 2.0,
                   trail_pct: float | None = None, target: float | None = None, max_hold: int = 120, cost: float = 0.0005) -> dict:
    """Outcome of buying the open of bar i+1 with a stop that only rises: no fixed target unless `target` is given.

    The stop starts at max(stop, 5% below the fill). After each bar it is lifted to the highest high since
    entry minus `atr_mult` ATRs (or minus `trail_pct` of that high). With `target`, the position is held
    through the target and the trailing stop is lifted to at least the target minus one ATR once it is hit,
    so the trade can keep what the fixed rule would have taken and still run.
    """
    O, H, L, C = (daily[c].values for c in ("Open", "High", "Low", "Close"))
    if i + 1 >= len(O):
        return {"fill": np.nan, "ret": np.nan, "why": "", "days": np.nan, "peak": np.nan}
    if atr is None:
        atr = atr_series(daily)
    fill = O[i + 1]
    stp = max(stop, fill * 0.95)
    hi = fill
    hit_target = False
    last = min(len(O) - 1, i + 1 + max_hold)
    for j in range(i + 1, last + 1):
        if O[j] <= stp:
            return {"fill": fill, "ret": O[j] / fill - 1 - 2 * cost, "why": "stop-gap", "days": j - (i + 1), "peak": hi / fill - 1}
        if L[j] <= stp:
            return {"fill": fill, "ret": stp / fill - 1 - 2 * cost, "why": "trail" if stp > fill else "stop", "days": j - (i + 1), "peak": hi / fill - 1}
        hi = max(hi, H[j])
        trail = hi * (1 - trail_pct) if trail_pct is not None else hi - atr_mult * atr[j]
        if target is not None and H[j] >= target:
            hit_target = True
        if hit_target:
            trail = max(trail, target - atr[j])
        stp = max(stp, trail)
    return {"fill": fill, "ret": C[last] / fill - 1 - 2 * cost, "why": "time", "days": last - (i + 1), "peak": hi / fill - 1}


def touch_events(
    df: pd.DataFrame,
    *,
    stop_fn: StopFn | None = owen_stop,
    tick_fn: TickFn | None = None,
    scan_every: int = 5,
    valid_days: int = 5,
    max_hold: int = 40,
    cost: float = 0.0005,
    start: int = 300,
) -> pd.DataFrame:
    """Every touch of a proposed support line, with what was known at that day's close and what happened next.

    Unlike `simulate`, no gate is applied and events may overlap: the point is a dataset for a model that
    decides *which* touches to take. Each row = one order whose line was reached within `valid_days`.
    Columns: order/touch dates, the order (line, target, stop), the builder's own read of the chart at
    order time (state, confidence, cloud, rsi_ok, position, rr, channel score/rev_rate/touches), the
    touch-day bar features, and the label (fill at next open, ret, why, days, win).
    """
    warnings.filterwarnings("ignore")
    tr = _load_trader()
    builder = tr[3]
    daily = df.rename(columns=str.capitalize)
    weekly_all = _weekly(daily)
    L, C = daily["Low"].values, daily["Close"].values
    idx = daily.index
    rows: list[dict] = []
    order = None
    with _patched(builder, stop_fn, tick_fn):
        for i in range(start, len(idx)):
            if order is not None:
                sig, best, oi = order
                if i - oi > valid_days:
                    order = None
                elif L[i] <= sig.buy:
                    reached, bounced = touched(L[i], C[i], sig.buy)
                    row = {
                        "order": idx[oi], "touch": idx[i], "days_to_touch": i - oi,
                        "line": sig.buy, "target": sig.target, "stop": sig.stop,
                        "target_pct": sig.target / sig.buy - 1, "stop_pct": sig.stop / sig.buy - 1, "rr": sig.rr,
                        "state": sig.state, "confidence": sig.confidence,
                        "cloud": sig.confirm.get("cloud", ""), "rsi_ok": bool(sig.confirm.get("rsi_ok", True)),
                        "position": sig.position,
                        "ch_score": float(best.score.score), "ch_rev_rate": float(best.score.rev_rate), "ch_touches": int(best.score.touches),
                        "bounced": bounced,
                        **bar_features(daily, i, sig.buy),
                        **label_forward(daily, i, sig.target, sig.stop, max_hold, cost),
                    }
                    rows.append(row)
                    order = None
            if order is None and (i - start) % scan_every == 0:
                sig, best = _signal_at(tr, daily, weekly_all, i)
                if sig is not None and sig.target > sig.buy > sig.stop:
                    order = (sig, best, i)
    out = pd.DataFrame(rows)
    if len(out):
        out["win"] = (out["ret"] > 0).astype(int)
    return out


# ----------------------------------------------------------------------------- data helper for KRX


def fetch_krx(code: str, start: str = "2015-01-01") -> pd.DataFrame:
    """Daily bars for a KRX code via FinanceDataReader (optional dependency), lowercase ohlcv."""
    try:
        import FinanceDataReader as fdr
    except ImportError as e:  # pragma: no cover
        raise ImportError("pip install finance-datareader  (for KRX data)") from e
    df = fdr.DataReader(code, start)[["Open", "High", "Low", "Close", "Volume"]].astype(float)
    df.columns = [c.lower() for c in df.columns]
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    df = df.dropna()
    # FinanceDataReader returns zero-price rows on halted days (e.g. 삼성전자 around the 2018 split); they are not bars
    return df[(df[["open", "high", "low", "close"]] > 0).all(axis=1)]
