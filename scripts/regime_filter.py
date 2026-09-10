"""One regime filter: enter only when the index's 20-day return is positive. Nothing else changes.

    python scripts/regime_filter.py

Two panels, same three exits (hold 20 days no stop / stop only 20 days / trail 8%), with and without the filter:
  1. index ETFs SPY QQQ IWM, placebo entries every 5th day, 2000-2010 (flat decade) and 2010-2026 (bull)
  2. the 20-stock touch dataset (data/touches_exits.csv), index = SPY for US, KOSPI for KRX
Reported per rule: trades/yr, mean per trade, summed trade return per year (exposure-aware), 5th percentile,
and return per capital-day. A "200-day MA" variant of the filter is printed once as a sanity check only.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from tradebuilder.data import fetch
from tradebuilder.swing import atr_series, exit_check, fetch_krx, label_trailing, owen_stop

COST = 0.0005


def three_exits(df: pd.DataFrame, daily: pd.DataFrame, atr: np.ndarray, i: int, stop: float) -> dict:
    O, H, L, C = (df[k].values for k in ("open", "high", "low", "close"))
    if i + 21 >= len(O):
        return {}
    fill = O[i + 1]
    stp = max(stop, fill * 0.95)
    hold = C[i + 21] / fill - 1 - 2 * COST
    fix, fix_days = hold, 20
    for j in range(i + 1, i + 22):
        hit = exit_check(O[j], H[j], L[j], C[j], fill, 1e12, stp, j - (i + 1), 20)
        if hit:
            fix, fix_days = hit[0] / fill - 1 - 2 * COST, j - (i + 1)
            break
    tr = label_trailing(daily, i, stp, atr=atr, trail_pct=0.08)
    return {"hold20": hold, "hold20_days": 20, "fix20": fix, "fix20_days": fix_days, "trail8": tr["ret"], "trail8_days": tr["days"]}


def regime(index_close: pd.Series) -> pd.DataFrame:
    return pd.DataFrame({"r20": index_close.pct_change(20), "above200": index_close > index_close.rolling(200).mean()})


def summarize(d: pd.DataFrame, years: float) -> pd.DataFrame:
    rows = []
    for rule in ("hold20", "fix20", "trail8"):
        r, days = d[rule], d[f"{rule}_days"].clip(lower=1)
        rows.append({"rule": rule, "n/yr": len(d) / years, "mean": r.mean(), "sum/yr": r.sum() / years, "p5": r.quantile(0.05),
                     "per_cap_day": r.sum() / days.sum()})
    return pd.DataFrame(rows).set_index("rule")


def panel_etf() -> None:
    spy = fetch("SPY", "1999-01-01")
    print("=== panel 1: index ETFs, placebo entries every 5th day, filter = SPY 20-day return > 0 ===")
    for tk in ["SPY", "QQQ", "IWM"]:
        df = fetch(tk, "1999-01-01")
        daily = df.rename(columns=str.capitalize)
        atr = atr_series(daily)
        reg = regime(spy["close"]).reindex(df.index).ffill()
        pos = pd.Series(np.arange(len(df)), index=df.index)
        for span, (s, e) in {"2000-2010": ("2000-01-01", "2010-01-01"), "2010-2026": ("2010-01-01", "2027-01-01")}.items():
            rows = []
            for t in df.index[(df.index >= s) & (df.index < e)][::5]:
                i = pos[t]
                if i < 200:
                    continue
                lab = three_exits(df, daily, atr, i, owen_stop(float(df["close"].iloc[i]), daily.iloc[: i + 1]))
                if lab:
                    rows.append({"date": t, "on": bool(reg.r20.iloc[i] > 0), "ma": bool(reg.above200.iloc[i]), **lab})
            d = pd.DataFrame(rows)
            yrs = (d.date.max() - d.date.min()).days / 365.25
            base, filt, ma = summarize(d, yrs), summarize(d[d.on], yrs), summarize(d[d.ma], yrs)
            out = pd.concat({"no filter": base, "r20>0": filt, "above 200MA": ma}, axis=1)
            print(f"\n{tk} {span}  (filter on {d.on.mean():.0%} of days; 200MA on {d.ma.mean():.0%})")
            print(out.to_string(float_format=lambda x: f"{x:.4f}"))


def panel_touches() -> None:
    ev = pd.read_csv("data/touches_exits.csv", parse_dates=["touch"])
    spy, ks = fetch("SPY", "2009-01-01")["close"], fetch("^KS11", "2014-01-01")["close"]
    reg = {"US": regime(spy), "KRX": regime(ks)}
    rows = []
    for (m, c), g in ev.groupby(["market", "code"], sort=False):
        df = fetch(c, "2010-01-01") if m == "US" else fetch_krx(c, "2015-01-01")
        daily = df.rename(columns=str.capitalize)
        atr = atr_series(daily)
        pos = pd.Series(np.arange(len(df)), index=df.index)
        rg = reg[m].reindex(df.index).ffill()
        for e in g.itertuples():
            i = pos.get(e.touch)
            if i is None:
                continue
            lab = three_exits(df, daily, atr, int(i), e.stop)
            if lab:
                rows.append({"market": m, "date": e.touch, "on": bool(rg.r20.iloc[i] > 0), "ma": bool(rg.above200.iloc[i]), **lab})
    d = pd.DataFrame(rows)
    print("\n=== panel 2: 20-stock channel touches, filter = own index 20-day return > 0 (SPY / KOSPI) ===")
    for m in ["US", "KRX", "ALL"]:
        x = d if m == "ALL" else d[d.market == m]
        yrs = (x.date.max() - x.date.min()).days / 365.25
        out = pd.concat({"no filter": summarize(x, yrs), "r20>0": summarize(x[x.on], yrs), "above 200MA": summarize(x[x.ma], yrs)}, axis=1)
        print(f"\n{m}  (filter on {x.on.mean():.0%} of touches; 200MA on {x.ma.mean():.0%})")
        print(out.to_string(float_format=lambda x: f"{x:.4f}"))
    # the years the filter is supposed to fix
    yrs_ = d.date.dt.year
    by = d.groupby(yrs_).apply(lambda g: pd.Series({"n": len(g), "on%": g.on.mean(), "trail8 all": g.trail8.mean(), "trail8 on": g[g.on].trail8.mean(),
                                                    "hold20 all": g.hold20.mean(), "hold20 on": g[g.on].hold20.mean()}))
    print("\nby year (touches, ALL):")
    print(by.to_string(float_format=lambda x: f"{x:.3f}"))


if __name__ == "__main__":
    panel_etf()
    panel_touches()
