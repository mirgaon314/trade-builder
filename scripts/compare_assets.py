"""Same walk-forward, several assets: does the weighted model's edge depend on what it trades?

    python scripts/compare_assets.py --tickers SPY QQQ TLT GLD IWM --start 2010-01-01
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from tradebuilder import FEATURE_SETS, AlwaysLong, RsiRuleModel, WeightedIndicatorModel, feature_frame, walk_forward
from tradebuilder.data import fetch


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--tickers", nargs="+", default=["SPY", "QQQ", "TLT", "GLD", "IWM"])
    p.add_argument("--start", default="2010-01-01")
    p.add_argument("--train", type=int, default=750)
    p.add_argument("--test", type=int, default=250)
    p.add_argument("--cost-bps", type=float, default=5.0)
    p.add_argument("--features", choices=list(FEATURE_SETS), default="base", help="which indicator set the model learns weights for")
    p.add_argument("--out", default="")
    a = p.parse_args()

    rows = []
    for t in a.tickers:
        df = fetch(t, a.start)
        F = feature_frame(df)
        close = df["close"]
        r = {"asset": t, "years": round(len(F) / 252, 1)}
        for name, factory in [("model", lambda: WeightedIndicatorModel(features=FEATURE_SETS[a.features])), ("rsi", RsiRuleModel), ("hold", AlwaysLong)]:
            wf = walk_forward(F, close, factory, train=a.train, test=a.test, cost_bps=a.cost_bps)
            m = wf.out_of_sample.metrics
            r[f"{name}_sharpe"] = m["sharpe"]; r[f"{name}_cagr"] = m["cagr"]; r[f"{name}_maxdd"] = m["max_drawdown"]
            if name == "model":
                oos = [f.out_of_sample.metrics["sharpe"] for f in wf.folds]
                r["model_folds_pos"] = f"{sum(s > 0 for s in oos)}/{len(oos)}"
                r["model_exposure"] = m["exposure"]
        rows.append(r)
        print(f"{t}: model Sharpe {r['model_sharpe']:.2f} | rsi {r['rsi_sharpe']:.2f} | hold {r['hold_sharpe']:.2f}", flush=True)

    tab = pd.DataFrame(rows)
    cols = ["asset", "years", "model_sharpe", "rsi_sharpe", "hold_sharpe", "model_cagr", "hold_cagr", "model_maxdd", "hold_maxdd", "model_exposure", "model_folds_pos"]
    print("\n" + tab[cols].to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    if a.out:
        md = ["| asset | yrs | model Sharpe | RSI Sharpe | hold Sharpe | model CAGR | hold CAGR | model maxDD | hold maxDD | exposure | OOS folds >0 |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            md.append(f"| {r['asset']} | {r['years']} | {r['model_sharpe']:.2f} | {r['rsi_sharpe']:.2f} | {r['hold_sharpe']:.2f} | {r['model_cagr']:+.1%} | {r['hold_cagr']:+.1%} | {r['model_maxdd']:.1%} | {r['hold_maxdd']:.1%} | {r['model_exposure']:.0%} | {r['model_folds_pos']} |")
        Path(a.out).write_text("\n".join(md) + "\n")
        print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
