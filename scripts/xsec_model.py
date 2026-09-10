"""This repo's own daily indicator model as a cross-sectional ranking signal.

    python scripts/xsec_model.py                 # pre-registered: base features, target = next day up (as in model.py)
    python scripts/xsec_model.py --target m21    # sanity variant: target = next 21 trading days up

Every month-end, score every point-in-time S&P 500 member with P(up) from a logistic regression on the
repo's indicator features (walk-forward: fit on all stock-days before the test year with a 60-day
embargo, every 5th day, pooled across stocks), rank cross-sectionally, long top decile / short bottom
decile, one month. Same harness as scripts/xsec.py, so the result is comparable with 12-1 momentum.
"""
from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from tradebuilder.data import fetch
from tradebuilder.indicators import FEATURE_SETS, feature_frame
from universe import download
from xsec import load_prices, long_short, member_mask, report


def daily_panel(tickers: list[str]) -> dict[str, pd.DataFrame]:
    cache = Path("data/sp500_daily.pkl")
    if cache.exists():
        return pickle.load(open(cache, "rb"))
    print(f"downloading daily bars for {len(tickers)} tickers...", flush=True)
    bars = download(tickers, "1999-01-01")
    pickle.dump(bars, open(cache, "wb"))
    return bars


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--features", choices=list(FEATURE_SETS), default="base")
    a.add_argument("--target", choices=["d1", "m21"], default="d1")
    a.add_argument("--start", default="2004-01-01", help="first test year (3 years of training before it)")
    args = a.parse_args()
    cols = FEATURE_SETS[args.features]

    px, tab = load_prices("1999-01-01")
    mask = member_mask(px, tab)
    bars = daily_panel(list(px.columns))
    print(f"{len(bars)} tickers with daily bars", flush=True)

    frames = []
    for t, df in bars.items():
        F = feature_frame(df)
        if args.target == "m21":
            F["y"] = (df["close"].shift(-21).reindex(F.index) > df["close"].reindex(F.index)).astype(float)
            F = F.iloc[:-21]
        F = F[cols + ["y"]].astype("float32")
        F["ticker"] = t
        frames.append(F)
    P = pd.concat(frames)
    P.index.name = "date"
    P = P.reset_index()
    P["is_me"] = P.date.isin(px.index)  # month-end rows (px is resampled to month-end)
    # month-end rows: the exact last trading day may differ from the ME label; map each date to its month
    P["month"] = P.date.dt.to_period("M")
    last_day = P.groupby(["ticker", "month"]).date.transform("max")
    P["is_me"] = P.date == last_day
    print(f"panel {len(P):,} stock-days, {P.is_me.sum():,} month-end rows", flush=True)

    years = range(pd.Timestamp(args.start).year, px.index[-1].year + 1)
    sig_rows = []
    for y in years:
        cutoff = pd.Timestamp(f"{y}-01-01") - pd.Timedelta(days=60)
        tr = P[(P.date < cutoff) & (P.date.dt.dayofyear % 5 == 0)]
        te = P[(P.date.dt.year == y) & P.is_me]
        if len(tr) < 5000 or len(te) == 0:
            continue
        m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000)).fit(tr[cols].values, tr.y.values)
        p = m.predict_proba(te[cols].values)[:, 1]
        sig_rows.append(pd.DataFrame({"month": te.month.values, "ticker": te.ticker.values, "p": p}))
        print(f"{y}: trained on {len(tr):,} rows, scored {len(te):,} month-end rows, in-sample acc {m.score(tr[cols].values, tr.y.values):.3f}", flush=True)
    S = pd.concat(sig_rows)
    sig = S.pivot(index="month", columns="ticker", values="p")
    sig.index = sig.index.to_timestamp("M")
    sig = sig.reindex(px.index)

    spy = fetch("SPY", "1999-01-01")["close"].resample("ME").last().pct_change().shift(-1)
    d = long_short(px, mask, sig, args.start)
    d.to_csv(f"data/xsec_model_{args.features}_{args.target}.csv")
    report(d, spy, f"indicator model ({args.features}, target {args.target})")


if __name__ == "__main__":
    main()
