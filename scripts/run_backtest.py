"""Walk-forward backtest of the weighted-indicator model vs. two baselines.

    python scripts/run_backtest.py --ticker SPY --start 2010-01-01
    python scripts/run_backtest.py --csv data/spy.csv --train 750 --test 250
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from tradebuilder import (AlwaysLong, RsiRuleModel, WeightedIndicatorModel, feature_frame, overfit_warning, walk_forward)
from tradebuilder.data import fetch, load_csv
from tradebuilder.indicators import latest_features


def main() -> None:
    p = argparse.ArgumentParser()
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--ticker")
    src.add_argument("--csv")
    p.add_argument("--start", default="2010-01-01")
    p.add_argument("--train", type=int, default=750)
    p.add_argument("--test", type=int, default=250)
    p.add_argument("--cost-bps", type=float, default=5.0)
    p.add_argument("--C", type=float, default=1.0, help="inverse regularization strength")
    a = p.parse_args()

    df = fetch(a.ticker, a.start) if a.ticker else load_csv(a.csv)
    F = feature_frame(df)
    close = df["close"]
    print(f"{a.ticker or a.csv}: {len(df)} bars {df.index[0].date()} .. {df.index[-1].date()}, {len(F)} feature rows")
    print(f"walk-forward: train {a.train} / test {a.test} days, cost {a.cost_bps} bps per side\n")

    pd.set_option("display.width", 120)
    results = {}
    for name, factory in [
        ("weighted (logistic)", lambda: WeightedIndicatorModel(C=a.C)),
        ("RSI 30/70 rule", RsiRuleModel),
        ("buy & hold", AlwaysLong),
    ]:
        wf = walk_forward(F, close, factory, train=a.train, test=a.test, cost_bps=a.cost_bps)
        results[name] = wf
        print(f"== {name}\n   OOS  {wf.out_of_sample}")

    wf = results["weighted (logistic)"]
    print("\nweighted model, per fold:")
    print(wf.table().to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    warn = overfit_warning(wf)
    print(f"\nWARNING: {warn}" if warn else "\nno overfitting warning triggered")

    last = wf.folds[-1].weights
    print("\nlast fold weights (standardized features):")
    print(last.sort_values(key=abs, ascending=False).to_string(float_format=lambda x: f"{x:+.3f}"))

    model = WeightedIndicatorModel(C=a.C).fit(F.iloc[-a.train:])
    row = latest_features(df)
    ex = model.explain(row)
    print(f"\nlatest signal ({row.name.date()}): P(up) = {ex.attrs['p_up']:.3f} -> {'LONG' if ex.attrs['p_up'] > 0.5 else 'FLAT'}")
    print(ex.to_string(float_format=lambda x: f"{x:+.3f}"))


if __name__ == "__main__":
    main()
