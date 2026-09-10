"""Cross-sectional long-short on the point-in-time S&P 500: rank every member each month-end by one signal,
long the top decile, short the bottom decile, equal weight, hold one month. Beta is removed by construction.

    python scripts/xsec.py --signal mom12_1          # classic 12-1 momentum (pre-registered first run)
    python scripts/xsec.py --signal rev1              # 1-month reversal (sanity: should be the mirror)

Membership: data/sp500_ticker_start_end.csv. Prices: yfinance (survivors only — delisted losers are missing,
which *hurts* the short leg, so the bias runs against the strategy). Costs: 10 bps per side on turnover.
Reports annual return, vol, Sharpe, max drawdown, t-stat, and alpha/beta against SPY for the long-short
book, the long leg alone, and the equal-weight universe.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from tradebuilder.data import fetch
from universe import download

COST = 0.0010


def load_prices(start: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    tab = pd.read_csv("data/sp500_ticker_start_end.csv", parse_dates=["start_date", "end_date"])
    cache = Path("data/sp500_monthly_close.csv")
    if cache.exists():
        px = pd.read_csv(cache, index_col=0, parse_dates=True)
    else:
        tickers = sorted(tab.ticker.unique())
        print(f"downloading {len(tickers)} tickers...", flush=True)
        bars = download(tickers, start)
        px = pd.concat({t: b["close"] for t, b in bars.items()}, axis=1).resample("ME").last()
        px.to_csv(cache)
        print(f"{px.shape[1]} tickers with data, cached to {cache}", flush=True)
    return px, tab


def member_mask(px: pd.DataFrame, tab: pd.DataFrame) -> pd.DataFrame:
    m = pd.DataFrame(False, index=px.index, columns=px.columns)
    for r in tab.itertuples():
        if r.ticker not in m.columns:
            continue
        end = r.end_date if pd.notna(r.end_date) else pd.Timestamp("2100-01-01")
        m.loc[(m.index >= r.start_date) & (m.index < end), r.ticker] = True
    return m


def signals(px: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "mom12_1": px.shift(1) / px.shift(12) - 1,        # return from 12 months ago to 1 month ago
        "rev1": -(px / px.shift(1) - 1),                  # last month's return, flipped
        "mom6_1": px.shift(1) / px.shift(6) - 1,
    }


def stats(r: pd.Series, spy: pd.Series | None = None) -> dict:
    r = r.dropna()
    ann, vol = r.mean() * 12, r.std() * np.sqrt(12)
    eq = (1 + r).cumprod()
    out = {"ann": ann, "vol": vol, "sharpe": ann / vol if vol > 0 else 0, "maxdd": (eq / eq.cummax() - 1).min(),
           "t": r.mean() / r.std() * np.sqrt(len(r)) if r.std() > 0 else 0, "months": len(r), "months>0": (r > 0).mean()}
    if spy is not None:
        s = spy.reindex(r.index).dropna(); rr = r.reindex(s.index)
        b = np.cov(rr, s)[0, 1] / s.var()
        out["beta"] = b; out["alpha_ann"] = (rr - b * s).mean() * 12
    return out


def long_short(px: pd.DataFrame, mask: pd.DataFrame, sig: pd.DataFrame, start: str, decile: float = 0.1) -> pd.DataFrame:
    """Monthly decile long-short on `sig` (month-end x ticker): returns a frame with long / short / ls / univ columns."""
    fwd = px.shift(-1) / px - 1
    rows, prev_long, prev_short = [], set(), set()
    for t in px.index:
        if t < pd.Timestamp(start) or t >= px.index[-1] or t not in sig.index:
            continue
        s = sig.loc[t].reindex(px.columns)
        ok = mask.loc[t] & s.notna() & fwd.loc[t].notna()
        s = s[ok]
        if len(s) < 100:
            continue
        k = max(10, int(len(s) * decile))
        long, short = set(s.nlargest(k).index), set(s.nsmallest(k).index)
        turn = (len(long - prev_long) + len(short - prev_short)) / (2 * k)
        rl, rs, ru = fwd.loc[t][list(long)].mean(), fwd.loc[t][list(short)].mean(), fwd.loc[t][ok].mean()
        rows.append({"date": t, "n": len(s), "long": rl - COST * turn, "short": rs, "ls": (rl - rs) / 2 - COST * turn, "univ": ru, "turnover": turn})
        prev_long, prev_short = long, short
    return pd.DataFrame(rows).set_index("date")


def report(d: pd.DataFrame, spy: pd.Series, label: str, decile: float = 0.1) -> None:
    print(f"signal {label}: {len(d)} months {d.index[0].date()}..{d.index[-1].date()}, universe {d.n.mean():.0f} names/month, decile {d.n.mean() * decile:.0f}, turnover {d.turnover.mean():.0%}/month\n")
    tab_ = pd.DataFrame({
        "long-short (half each, dollar-neutral)": stats(d.ls, spy),
        "long decile only": stats(d.long, spy),
        "equal-weight universe": stats(d.univ, spy),
        "SPY": stats(spy.reindex(d.index).dropna()),
    }).T
    print(tab_.to_string(float_format=lambda x: f"{x:.3f}"))
    yr = d.groupby(d.index.year)[["ls", "long", "univ"]].apply(lambda g: (1 + g).prod() - 1)
    yr["months>0"] = d.groupby(d.index.year).ls.apply(lambda g: (g > 0).mean())
    print("\nby year:")
    print(yr.to_string(float_format=lambda x: f"{x:+.1%}"))
    for lab, (s, e) in {"2001-2008": (2001, 2008), "2009-2016": (2009, 2016), "2017-2025": (2017, 2025)}.items():
        x = d[(d.index.year >= s) & (d.index.year <= e)]
        if len(x) < 12:
            continue
        st = stats(x.ls, spy)
        print(f"{lab}: long-short ann {st['ann']:+.1%} Sharpe {st['sharpe']:.2f} maxDD {st['maxdd']:.0%} t {st['t']:.1f} beta {st['beta']:.2f} alpha {st['alpha_ann']:+.1%}")


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--signal", default="mom12_1", choices=["mom12_1", "rev1", "mom6_1"])
    a.add_argument("--decile", type=float, default=0.1)
    a.add_argument("--start", default="2001-01-01")
    args = a.parse_args()
    px, tab = load_prices("1999-01-01")
    mask = member_mask(px, tab)
    sig = signals(px)[args.signal]
    spy = fetch("SPY", "1999-01-01")["close"].resample("ME").last().pct_change().shift(-1)
    d = long_short(px, mask, sig, args.start, args.decile)
    d.to_csv(f"data/xsec_{args.signal}.csv")
    report(d, spy, args.signal, args.decile)


if __name__ == "__main__":
    main()
