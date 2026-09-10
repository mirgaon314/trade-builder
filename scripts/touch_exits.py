"""Release the target cap: re-label every touch in data/touches.csv under exits that let winners run.

    python scripts/touch_exits.py --data data/touches.csv

Exit rules compared on the same touches (buy the next open, initial stop as before):
    target      sell at the next channel line, stop, or 40 days           (rounds 5-6)
    trail2atr   no target; stop trails the highest high by 2 ATR, 120 days
    trail3atr   no target; 3 ATR
    trail8pct   no target; 8% below the highest high
    target+run  hold through the target; once hit, trailing stop >= target - 1 ATR, 2 ATR trail, 120 days
Selections: all touches, bounce-confirmed, Owen's gate + bounce.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from tradebuilder.data import fetch
from tradebuilder.swing import atr_series, fetch_krx, label_forward, label_trailing

RULES = {
    "target": lambda d, i, e, a: label_forward(d, i, e.target, e.stop, 40, 0.0005),
    "trail2atr": lambda d, i, e, a: label_trailing(d, i, e.stop, atr=a, atr_mult=2.0),
    "trail3atr": lambda d, i, e, a: label_trailing(d, i, e.stop, atr=a, atr_mult=3.0),
    "trail8pct": lambda d, i, e, a: label_trailing(d, i, e.stop, atr=a, trail_pct=0.08),
    "target+run": lambda d, i, e, a: label_trailing(d, i, e.stop, atr=a, atr_mult=2.0, target=e.target),
}


def relabel(ev: pd.DataFrame, us_start="2010-01-01", kr_start="2015-01-01") -> pd.DataFrame:
    out = []
    for (market, code), g in ev.groupby(["market", "code"], sort=False):
        t0 = time.time()
        df = fetch(code, us_start) if market == "US" else fetch_krx(code, kr_start)
        daily = df.rename(columns=str.capitalize)
        atr = atr_series(daily)
        pos = pd.Series(np.arange(len(daily)), index=daily.index)
        g = g.copy()
        idx = pos.reindex(pd.to_datetime(g.touch)).values
        for name, fn in RULES.items():
            labs = [fn(daily, int(i), e, atr) if np.isfinite(i) else {"ret": np.nan, "why": "", "days": np.nan, "peak": np.nan}
                    for i, e in zip(idx, g.itertuples())]
            g[f"{name}_ret"] = [l["ret"] for l in labs]
            g[f"{name}_why"] = [l["why"] for l in labs]
            g[f"{name}_days"] = [l["days"] for l in labs]
        out.append(g)
        print(f"{market} {g.name.iloc[0]:8s} {len(g):4d} touches relabeled ({time.time() - t0:.0f}s)", flush=True)
    return pd.concat(out, ignore_index=True)


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--data", default="data/touches.csv")
    args = a.parse_args()
    ev = pd.read_csv(args.data)
    ev = relabel(ev)
    ev = ev.dropna(subset=[f"{r}_ret" for r in RULES])
    ev["touch"] = pd.to_datetime(ev.touch)
    ev["gate"] = (ev.cloud != "below") & ev.rsi_ok & (ev.position < 0.8) & (ev.rr >= 1.0)
    ev.to_csv(Path(args.data).with_name("touches_exits.csv"), index=False)
    years = ev.touch.dt.year.nunique()
    sels = {"all touches": np.ones(len(ev), bool), "bounce-confirmed": ev.bounced.values, "gate + bounce": (ev.gate & ev.bounced).values}
    print(f"\n{len(ev)} touches, {ev.touch.dt.year.min()}-{ev.touch.dt.year.max()}\n")
    rows = []
    for sname, m in sels.items():
        for rname in RULES:
            s = ev[m]
            r, why, days = s[f"{rname}_ret"], s[f"{rname}_why"], s[f"{rname}_days"]
            rows.append({"selection": sname, "exit": rname, "n/yr": len(s) / years, "win": (r > 0).mean(), "avg win": r[r > 0].mean(), "avg loss": r[r <= 0].mean(),
                         "mean ret": r.mean(), "sum ret/yr": r.sum() / years, "hold days": days.mean(), "yrs > 0": (s.groupby(s.touch.dt.year)[f"{rname}_ret"].sum() > 0).sum(),
                         "capital-days/yr": (days.clip(lower=1)).sum() / years})
    tab = pd.DataFrame(rows)
    tab["ret per capital-day"] = tab["sum ret/yr"] / tab["capital-days/yr"] * 252   # crude: return per unit of capital tied up, annualized
    print(tab.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    # year by year for bounce-confirmed: target vs the best trailing
    s = ev[ev.bounced]
    by = s.groupby(s.touch.dt.year)[[f"{r}_ret" for r in RULES]].sum()
    print("\nbounce-confirmed, sum of trade returns per year:")
    print(by.to_string(float_format=lambda x: f"{x:+.2f}"))
    print("\nbounce-confirmed, how trades end:")
    for rname in RULES:
        print(f"  {rname:11s}", s[f"{rname}_why"].value_counts(normalize=True).round(2).to_dict())


if __name__ == "__main__":
    main()
