"""Build the touch-event dataset: every time price reaches a proposed channel support line, what the day
looked like at its close, and what buying the next open would have done (target / stop / 40 days).

    python scripts/touch_dataset.py --out data/touches.csv
    python scripts/touch_dataset.py --us AAPL META --kr 005930 --out touches_small.csv

Same 10 US + 10 KRX stocks as scripts/swing_stocks.py. No entry gate: the gate's inputs are columns,
so a model can learn them. Baselines printed at the end: all touches, Owen's gate, bounce-confirmed.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from tradebuilder.data import fetch
from tradebuilder.swing import fetch_krx, no_tick, owen_stop, touch_events

from swing_stocks import KR, US  # noqa: E402  (same universe)


def owen_gate_mask(ev: pd.DataFrame) -> pd.Series:
    return (ev.cloud != "below") & ev.rsi_ok & (ev.position < 0.8) & (ev.rr >= 1.0)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--us", nargs="*", default=US)
    p.add_argument("--kr", nargs="*", default=list(KR))
    p.add_argument("--us-start", default="2010-01-01")
    p.add_argument("--kr-start", default="2015-01-01")
    p.add_argument("--out", required=True)
    a = p.parse_args()

    parts = []
    items = [("US", t, t) for t in a.us] + [("KRX", c, KR.get(c, c)) for c in a.kr]
    for market, code, name in items:
        t0 = time.time()
        df = fetch(code, a.us_start) if market == "US" else fetch_krx(code, a.kr_start)
        ev = touch_events(df, stop_fn=owen_stop, tick_fn=no_tick if market == "US" else None)
        ev.insert(0, "name", name); ev.insert(0, "code", code); ev.insert(0, "market", market)
        parts.append(ev)
        print(f"{market} {name:8s} touches {len(ev):4d} win {ev.win.mean():.0%} | bounced {ev.bounced.sum():4d} win {ev[ev.bounced].win.mean():.0%}"
              f" | owen-gate {owen_gate_mask(ev).sum():4d} win {ev[owen_gate_mask(ev)].win.mean():.0%} ({time.time() - t0:.0f}s)", flush=True)

    ev = pd.concat(parts, ignore_index=True)
    ev.to_csv(a.out, index=False)
    g = owen_gate_mask(ev)
    print(f"\n{len(ev)} touch events -> {a.out}")
    print(f"all touches      n {len(ev):5d} win {ev.win.mean():.1%} mean ret {ev.ret.mean():+.2%}")
    print(f"owen gate        n {g.sum():5d} win {ev[g].win.mean():.1%} mean ret {ev[g].ret.mean():+.2%}")
    print(f"bounce-confirmed n {ev.bounced.sum():5d} win {ev[ev.bounced].win.mean():.1%} mean ret {ev[ev.bounced].ret.mean():+.2%}")
    print(f"gate + bounce    n {(g & ev.bounced).sum():5d} win {ev[g & ev.bounced].win.mean():.1%} mean ret {ev[g & ev.bounced].ret.mean():+.2%}")


if __name__ == "__main__":
    main()
