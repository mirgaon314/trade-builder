"""Hindsight-free universe: each year, 40 random members of the S&P 500 *as of that January*, placebo
entries every 5th day, the same three exits (hold 20d / stop-only 20d / trail 8%). Does anything earn
more per day of capital than the universe drift once the 2026 stock picking is gone?

    python scripts/universe.py --per-year 40 --seed 0

Membership: data/sp500_ticker_start_end.csv (from github.com/fja05680/sp500, Clenow's list + Wikipedia
changes). Prices: yfinance, which only has *surviving* tickers — every year's coverage (fraction of
sampled members with price data) is printed, and that gap is the residual survivorship bias.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from regime_filter import three_exits
from tradebuilder.data import normalize
from tradebuilder.swing import atr_series, owen_stop


def members_on(tab: pd.DataFrame, day: pd.Timestamp) -> list[str]:
    ok = (tab.start_date <= day) & (tab.end_date.isna() | (tab.end_date > day))
    return sorted(tab[ok].ticker.unique())


def download(tickers: list[str], start: str) -> dict[str, pd.DataFrame]:
    import yfinance as yf
    out = {}
    ysyms = [t.replace(".", "-") for t in tickers]
    for k in range(0, len(ysyms), 60):
        chunk = ysyms[k: k + 60]
        raw = yf.download(chunk, start=start, auto_adjust=True, progress=False, group_by="ticker", threads=True)
        for t, ys in zip(tickers[k: k + 60], chunk):
            try:
                df = raw[ys].dropna(how="all") if len(chunk) > 1 else raw.dropna(how="all")
                if len(df) < 250:
                    continue
                out[t] = normalize(df)
            except Exception:
                continue
    return out


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--per-year", type=int, default=40)
    a.add_argument("--seed", type=int, default=0)
    a.add_argument("--years", default="2001-2025")
    args = a.parse_args()
    y0, y1 = (int(x) for x in args.years.split("-"))
    tab = pd.read_csv("data/sp500_ticker_start_end.csv", parse_dates=["start_date", "end_date"])
    rng = np.random.default_rng(args.seed)
    sample = {y: list(rng.choice(members_on(tab, pd.Timestamp(f"{y}-01-01")), args.per_year, replace=False)) for y in range(y0, y1 + 1)}
    allt = sorted({t for v in sample.values() for t in v})
    print(f"{len(allt)} unique tickers across {y1 - y0 + 1} years; downloading...", flush=True)
    bars = download(allt, f"{y0 - 1}-01-01")
    print(f"{len(bars)} with price data", flush=True)

    rows, cover = [], []
    for y, ts in sample.items():
        have = [t for t in ts if t in bars and (bars[t].index.year == y).sum() > 200]
        cover.append({"year": y, "sampled": len(ts), "with_data": len(have)})
        for t in have:
            df = bars[t]
            daily = df.rename(columns=str.capitalize)
            atr = atr_series(daily)
            idx = np.where(df.index.year == y)[0]
            for i in idx[::5]:
                if i < 20:
                    continue
                lab = three_exits(df, daily, atr, int(i), owen_stop(float(df["close"].iloc[i]), daily.iloc[: i + 1]))
                if lab:
                    rows.append({"year": y, "ticker": t, **lab})
        print(f"{y}: {len(have)}/{len(ts)} members with data", flush=True)
    d = pd.DataFrame(rows)
    cv = pd.DataFrame(cover).set_index("year")
    d.to_csv("data/universe_trades.csv", index=False)

    def summ(x: pd.DataFrame) -> pd.Series:
        out = {}
        for r in ("hold20", "fix20", "trail8"):
            days = x[f"{r}_days"].clip(lower=1)
            out[f"{r} mean"] = x[r].mean()
            out[f"{r} /capday"] = x[r].sum() / days.sum()
        out["n"] = len(x)
        return pd.Series(out)

    by = d.groupby("year").apply(summ)
    by["coverage"] = cv.with_data / cv.sampled
    print("\nper year (placebo entries every 5th day; /capday = summed return per day of capital):")
    print(by.to_string(float_format=lambda v: f"{v:.4f}"))
    for lab, (s, e) in {"2001-2010": (2001, 2010), "2011-2025": (2011, 2025), "all": (y0, y1)}.items():
        x = d[(d.year >= s) & (d.year <= e)]
        m = summ(x)
        print(f"\n{lab}: n={int(m['n'])}  hold20 {m['hold20 mean']:+.2%} ({m['hold20 /capday']:.4%}/day)  "
              f"fix20 {m['fix20 mean']:+.2%} ({m['fix20 /capday']:.4%}/day)  trail8 {m['trail8 mean']:+.2%} ({m['trail8 /capday']:.4%}/day)  "
              f"| years trail8 > hold20 per capday: {(by.loc[s:e, 'trail8 /capday'] > by.loc[s:e, 'hold20 /capday']).sum()}/{len(by.loc[s:e])}  "
              f"| p5 hold {x.hold20.quantile(.05):+.1%} trail {x.trail8.quantile(.05):+.1%}")
    print(f"\nmean coverage {by.coverage.mean():.0%} (min {by.coverage.min():.0%} in {by.coverage.idxmin()})")


if __name__ == "__main__":
    main()
