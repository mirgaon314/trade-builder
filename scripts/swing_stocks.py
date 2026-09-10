"""The channel swing rule on single stocks, three entry/stop variants (research notes round 5).

    python scripts/swing_stocks.py                      # 10 US + 10 KRX, all three variants
    python scripts/swing_stocks.py --us AAPL META --kr 005930 --variants owen-bounce

Variants:
    june         limit buy at the line, builder's stop (2-7%), gate = ready or wait (2:1 reward:risk)
    owen-limit   limit buy at the line, Owen's stop (3-5%), Owen's gate
    owen-bounce  same, but buy the open after a day that touched the line and closed above it
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from tradebuilder.data import fetch
from tradebuilder.swing import fetch_krx, no_tick, owen_stop, simulate

US = ["AAPL", "MSFT", "NVDA", "AMD", "TSLA", "AMZN", "META", "INTC", "BA", "XOM"]
KR = {"005930": "삼성전자", "000660": "SK하이닉스", "005380": "현대차", "079550": "한화에어로", "012450": "한화오션",
      "035420": "NAVER", "051910": "LG화학", "068270": "셀트리온", "105560": "KB금융", "000270": "기아"}

VARIANTS = {
    "june": dict(gate="june+wait", entry="limit", stop_fn=None),
    "owen-limit": dict(gate="owen", entry="limit", stop_fn=owen_stop),
    "owen-bounce": dict(gate="owen", entry="bounce", stop_fn=owen_stop),
}


def fmt(cagr, sharpe, maxdd, trades=None, win=None) -> str:
    s = f"{cagr:+.0%} / {sharpe:.2f} / {maxdd:.0%}" if np.isfinite(cagr) else f"n/a / {sharpe:.2f} / {maxdd:.0%}"
    return s + (f" ({int(trades)}t, {win:.0%})" if trades is not None else "")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--us", nargs="*", default=US)
    p.add_argument("--kr", nargs="*", default=list(KR))
    p.add_argument("--variants", nargs="+", choices=list(VARIANTS), default=list(VARIANTS))
    p.add_argument("--us-start", default="2010-01-01")
    p.add_argument("--kr-start", default="2015-01-01")
    p.add_argument("--out", default="", help="CSV of per-stock/variant stats")
    p.add_argument("--trades-out", default="", help="CSV of every trade (for the touch dataset)")
    a = p.parse_args()

    rows, all_trades = [], []
    items = [("US", t, t) for t in a.us] + [("KRX", c, KR.get(c, c)) for c in a.kr]
    for market, code, name in items:
        df = fetch(code, a.us_start) if market == "US" else fetch_krx(code, a.kr_start)
        tick = no_tick if market == "US" else None
        for v in a.variants:
            t0 = time.time()
            s, tr = simulate(df, tick_fn=tick, **VARIANTS[v])
            rows.append({"market": market, "code": code, "name": name, "variant": v, **{k: x for k, x in s.items() if k != "exits"}})
            tr = tr.assign(market=market, code=code, name=name, variant=v)
            all_trades.append(tr)
            print(f"{market} {name:8s} {v:11s} trades {s['trades']:3d} win {s['win']:.0%} W/L {s['avg_win']:+.1%}/{s['avg_loss']:+.1%}"
                  f" | CAGR {s['cagr']:+.1%} Sh {s['sharpe']:.2f} DD {s['maxdd']:.0%} exp {s['exposure']:.0%}"
                  f" | hold {s['hold_cagr']:+.1%} Sh {s['hold_sharpe']:.2f} DD {s['hold_maxdd']:.0%} ({time.time() - t0:.0f}s)", flush=True)

    tab = pd.DataFrame(rows)
    head = "| | hold CAGR / Sharpe / maxDD | " + " | ".join(a.variants) + " |"
    md = [head, "|" + "---|" * (len(a.variants) + 2)]
    for (m, c, n), g in tab.groupby(["market", "code", "name"], sort=False):
        h = g.iloc[0]
        cells = [fmt(h.hold_cagr, h.hold_sharpe, h.hold_maxdd)]
        for v in a.variants:
            x = g[g.variant == v]
            cells.append(fmt(x.cagr.iloc[0], x.sharpe.iloc[0], x.maxdd.iloc[0], x.trades.iloc[0], x.win.iloc[0]) if len(x) else "—")
        md.append(f"| {n} | " + " | ".join(cells) + " |")
    mean = [fmt(tab.hold_cagr.mean(), tab.hold_sharpe.mean(), tab.hold_maxdd.mean())]
    for v in a.variants:
        x = tab[tab.variant == v]
        mean.append(fmt(np.nanmean(x.cagr), x.sharpe.mean(), x.maxdd.mean()))
    md.append("| **mean** | " + " | ".join(mean) + " |")
    print("\n" + "\n".join(md))
    for v in a.variants:
        x = tab[tab.variant == v]
        print(f"{v:11s} mean win {x.win.mean():.0%} | mean trades {x.trades.mean():.0f} | Sharpe > hold: {(x.sharpe > x.hold_sharpe).sum()}/{len(x)}")

    if a.out:
        tab.to_csv(a.out, index=False)
    if a.trades_out:
        pd.concat(all_trades, ignore_index=True).to_csv(a.trades_out, index=False)


if __name__ == "__main__":
    main()
