"""One book across all 20 stocks: take every selected touch (if a slot is free), size 1/N per position,
mark to market daily, and compare the equity curve with holding the same stocks equal-weight.

    python scripts/touch_book.py --data data/touches_exits.csv --slots 8

Uses the per-touch labels written by scripts/touch_exits.py (fill = next open, exit price/day per exit rule).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from tradebuilder.data import fetch
from tradebuilder.swing import fetch_krx

COST = 0.0005


def curve_stats(curve: pd.Series) -> dict:
    r = curve.pct_change().dropna()
    return {"cagr": (curve.iloc[-1] / curve.iloc[0]) ** (252 / len(curve)) - 1, "sharpe": r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0.0,
            "maxdd": (curve / curve.cummax() - 1).min()}


def book(ev: pd.DataFrame, bars: dict, rule: str, slots: int, select) -> tuple[pd.Series, dict]:
    """Daily book returns. Each trade: enter at next open after the touch, hold `days` bars, exit at the labelled return."""
    cal = sorted(set().union(*[set(b.index) for b in bars.values()]))
    cal = pd.DatetimeIndex(cal)
    pos_ret = pd.Series(0.0, index=cal)      # sum of position returns per day (each position weighted 1/slots)
    n_open = pd.Series(0, index=cal)
    open_until: dict[tuple, pd.Timestamp] = {}
    taken = skipped = 0
    ev = ev[select].sort_values("touch")
    for e in ev.itertuples():
        b = bars[(e.market, e.code)]
        t = pd.Timestamp(e.touch)
        i = b.index.get_loc(t)
        if i + 1 >= len(b):
            continue
        days = int(getattr(e, f"{rule}_days"))
        ret = float(getattr(e, f"{rule}_ret"))
        entry_day = b.index[i + 1]
        exit_i = min(len(b) - 1, i + 1 + days)
        exit_day = b.index[exit_i]
        # free slots at entry
        open_until = {k: v for k, v in open_until.items() if v >= entry_day}
        if len(open_until) >= slots or (e.market, e.code) in {k[0] for k in open_until}:
            skipped += 1
            continue
        open_until[((e.market, e.code), entry_day)] = exit_day
        taken += 1
        # daily path: open->close on entry day, close->close in between, and the last day closes the trade at the labelled return
        o, c = b["open"].values, b["close"].values
        path = [c[i + 1] / o[i + 1] - 1]
        for j in range(i + 2, exit_i + 1):
            path.append(c[j] / c[j - 1] - 1)
        # scale the path so the compounded result equals the labelled trade return (exit at stop/trail price, costs)
        got = np.prod([1 + x for x in path]) - 1
        if len(path) and abs(1 + got) > 1e-9:
            path[-1] = (1 + ret) / np.prod([1 + x for x in path[:-1]]) - 1
        else:
            path = [ret]
        dates = b.index[i + 1: i + 1 + len(path)]
        pos_ret.loc[dates] += np.array(path) / slots
        n_open.loc[dates] += 1
    curve = (1 + pos_ret).cumprod()
    st = curve_stats(curve)
    st.update({"trades": taken, "skipped_full": skipped, "avg_open": n_open.mean(), "exposure": (n_open > 0).mean(), "max_open": n_open.max()})
    return curve, st


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--data", default="data/touches_exits.csv")
    a.add_argument("--slots", type=int, nargs="+", default=[8])
    a.add_argument("--rules", nargs="+", default=["target", "trail3atr", "trail8pct"])
    args = a.parse_args()
    ev = pd.read_csv(args.data, parse_dates=["touch"])
    bars = {}
    for (m, c), g in ev.groupby(["market", "code"], sort=False):
        bars[(m, c)] = fetch(c, "2010-01-01") if m == "US" else fetch_krx(c, "2015-01-01")
    # equal-weight hold of the same stocks (each stock enters the book the day its data starts)
    closes = pd.concat({k: b["close"] for k, b in bars.items()}, axis=1)
    rets = closes.pct_change()
    hold = (1 + rets.mean(axis=1).fillna(0)).cumprod()
    hold = hold[hold.index >= ev.touch.min()]
    hs = curve_stats(hold / hold.iloc[0])
    print(f"equal-weight hold of the 20 stocks, {hold.index[0].date()}..{hold.index[-1].date()}: CAGR {hs['cagr']:+.1%} Sharpe {hs['sharpe']:.2f} maxDD {hs['maxdd']:.0%}\n")
    sels = {"all": np.ones(len(ev), bool), "bounce": ev.bounced.values, "gate+bounce": (ev.gate & ev.bounced).values}
    rows = []
    for slots in args.slots:
        for sname, sel in sels.items():
            for rule in args.rules:
                curve, st = book(ev, bars, rule, slots, sel)
                curve = curve[curve.index >= hold.index[0]]
                st.update(curve_stats(curve / curve.iloc[0]))
                rows.append({"slots": slots, "select": sname, "exit": rule, **st})
                print(f"slots {slots:2d} {sname:12s} {rule:10s} CAGR {st['cagr']:+.1%} Sharpe {st['sharpe']:.2f} maxDD {st['maxdd']:.0%} | trades {st['trades']} skipped {st['skipped_full']} avg open {st['avg_open']:.1f} exposure {st['exposure']:.0%}", flush=True)
    pd.DataFrame(rows).to_csv(Path(args.data).with_name("touch_book_results.csv"), index=False)


if __name__ == "__main__":
    main()
