"""Can a model pick the touches worth taking? Walk-forward by year on data/touches.csv.

    python scripts/touch_model.py --data data/touches.csv

For each test year Y: fit on every touch whose outcome was known 60 days before Y began, score the touches
in Y, and compare "take the touches the model likes" against the fixed rules (all touches, Owen's gate,
bounce-confirmed). Pooled across all stocks. Reports out-of-sample AUC, win rate, mean return per trade,
and the learned weights.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

NUMERIC = ["wick", "close_vs_line", "low_vs_line", "gap", "vol_ratio", "ret_5", "ret_20", "rsi_14", "atr_pct", "range_pct",
           "target_pct", "stop_pct", "rr", "position", "ch_score", "ch_rev_rate", "log_touches", "days_to_touch"]
FLAGS = ["bounced", "rsi_ok", "cloud_above", "cloud_in", "is_krx"]


def prepare(ev: pd.DataFrame) -> pd.DataFrame:
    ev = ev.copy()
    ev["touch"] = pd.to_datetime(ev["touch"])
    ev["log_touches"] = np.log1p(ev["ch_touches"])
    ev["cloud_above"] = (ev.cloud == "above").astype(int)
    ev["cloud_in"] = (ev.cloud == "in").astype(int)
    ev["is_krx"] = (ev.market == "KRX").astype(int)
    ev["bounced"] = ev["bounced"].astype(int)
    ev["rsi_ok"] = ev["rsi_ok"].astype(int)
    ev["owen_gate"] = ((ev.cloud != "below") & (ev.rsi_ok == 1) & (ev.position < 0.8) & (ev.rr >= 1.0)).astype(int)
    ev = ev.dropna(subset=NUMERIC + ["ret"])
    ev = ev[ev.why != "open"]  # label not resolved yet
    return ev.sort_values("touch").reset_index(drop=True)


def models():
    return {
        "logit": lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=2000)),
        "gbm": lambda: HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=150, min_samples_leaf=40, l2_regularization=1.0),
    }


def walk_forward(ev: pd.DataFrame, cols: list[str], make, min_train_years: int = 3, embargo_days: int = 60) -> pd.DataFrame:
    years = sorted(ev.touch.dt.year.unique())
    out = []
    for y in years[min_train_years:]:
        cutoff = pd.Timestamp(f"{y}-01-01") - pd.Timedelta(days=embargo_days)
        tr = ev[ev.touch < cutoff]
        te = ev[ev.touch.dt.year == y]
        if len(tr) < 200 or len(te) < 20:
            continue
        m = make().fit(tr[cols].values, tr.win.values)
        p = m.predict_proba(te[cols].values)[:, 1]
        out.append(te.assign(p=p, base_rate=tr.win.mean()))
    return pd.concat(out, ignore_index=True)


def walk_forward_reg(ev: pd.DataFrame, cols: list[str], make, min_train_years: int = 3, embargo_days: int = 60) -> pd.Series:
    """Same folds, but predict the trade return directly; returns the OOS prediction aligned to ev's index."""
    years = sorted(ev.touch.dt.year.unique())
    pred = pd.Series(np.nan, index=ev.index)
    for y in years[min_train_years:]:
        cutoff = pd.Timestamp(f"{y}-01-01") - pd.Timedelta(days=embargo_days)
        tr = ev[ev.touch < cutoff]
        te = ev[ev.touch.dt.year == y]
        if len(tr) < 200 or len(te) < 20:
            continue
        m = make().fit(tr[cols].values, tr.ret.values)
        pred.loc[te.index] = m.predict(te[cols].values)
    return pred


def summarize(name: str, d: pd.DataFrame, mask) -> dict:
    s = d[mask]
    return {"rule": name, "n": len(s), "win": s.win.mean(), "mean_ret": s.ret.mean(), "sum_ret_per_year": s.ret.sum() / d.touch.dt.year.nunique(),
            "per_year": len(s) / d.touch.dt.year.nunique()}


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--data", default="data/touches.csv")
    args = a.parse_args()
    ev = prepare(pd.read_csv(args.data))
    cols = NUMERIC + FLAGS
    print(f"{len(ev)} touches, {ev.touch.dt.year.min()}-{ev.touch.dt.year.max()}, base win {ev.win.mean():.1%}, mean ret {ev.ret.mean():+.2%}\n")

    rows = []
    for mname, make in models().items():
        d = walk_forward(ev, cols, make)
        auc = roc_auc_score(d.win, d.p)
        auc_bounce = roc_auc_score(d.win, d.bounced)
        yrs = d.touch.dt.year
        per_year_auc = [roc_auc_score(g.win, g.p) if g.win.nunique() > 1 else np.nan for _, g in d.groupby(yrs)]
        print(f"== {mname}: OOS {d.touch.dt.year.min()}-{d.touch.dt.year.max()}, n={len(d)}, AUC {auc:.3f} (bounce flag alone {auc_bounce:.3f}); "
              f"years with AUC>0.5: {sum(x > 0.5 for x in per_year_auc)}/{len(per_year_auc)}")
        top = d.groupby(yrs).p.transform(lambda s: s >= s.quantile(0.7))       # top 30% within each year
        half = d.groupby(yrs).p.transform(lambda s: s >= s.quantile(0.5))
        # the classifier optimizes P(win); what we want is E[ret] = p*target - (1-p)*|stop|
        d["exp_ret"] = d.p * d.target_pct + (1 - d.p) * d.stop_pct
        top_er = d.groupby(yrs).exp_ret.transform(lambda s: s >= s.quantile(0.7))
        # and a regressor on the return itself, same folds
        reg_make = (lambda: make_pipeline(StandardScaler(), Ridge(alpha=10.0))) if mname == "logit" else \
                   (lambda: HistGradientBoostingRegressor(max_depth=3, learning_rate=0.05, max_iter=150, min_samples_leaf=40, l2_regularization=1.0))
        d["r_hat"] = walk_forward_reg(ev, cols, reg_make).reindex(d.index if d.index.equals(ev.index) else ev.index).loc[ev.index[ev.touch.dt.year >= d.touch.dt.year.min()]].values
        top_r = d.groupby(yrs).r_hat.transform(lambda s: s >= s.quantile(0.7))
        table = pd.DataFrame([
            summarize("all touches", d, np.ones(len(d), bool)),
            summarize("owen gate", d, d.owen_gate == 1),
            summarize("bounce-confirmed", d, d.bounced == 1),
            summarize("gate + bounce", d, (d.owen_gate == 1) & (d.bounced == 1)),
            summarize(f"{mname} p > base rate", d, d.p > d.base_rate),
            summarize(f"{mname} p > 0.5", d, d.p > 0.5),
            summarize(f"{mname} top half / yr", d, half),
            summarize(f"{mname} top 30% / yr", d, top),
            summarize(f"{mname} top 30% & bounced", d, top & (d.bounced == 1)),
            summarize(f"{mname} E[ret] top 30% / yr", d, top_er),
            summarize(f"{mname} E[ret] > 0", d, d.exp_ret > 0),
            summarize(f"{mname} regressor top 30% / yr", d, top_r),
            summarize(f"{mname} regressor r_hat > 0", d, d.r_hat > 0),
        ])
        print(table.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
        # by year: does the model's top-30% beat bounce every year?
        by = d.groupby(yrs).apply(lambda g: pd.Series({"n": len(g), "all": g.win.mean(), "bounce": g[g.bounced == 1].win.mean(),
                                                       "model_top30": g[g.p >= g.p.quantile(0.7)].win.mean(),
                                                       "model_top30_ret": g[g.p >= g.p.quantile(0.7)].ret.mean(),
                                                       "bounce_ret": g[g.bounced == 1].ret.mean()}))
        print(by.to_string(float_format=lambda x: f"{x:.3f}"))
        print()
        if mname == "logit":
            m = make().fit(ev[cols].values, ev.win.values)
            w = pd.Series(m[-1].coef_[0], index=cols).sort_values(key=np.abs, ascending=False)
            print("logit weights on standardized inputs (fit on everything, for reading only):")
            print(w.round(3).to_string()); print()
        rows.append(table.assign(model=mname))
    pd.concat(rows).to_csv(Path(args.data).with_name("touch_model_results.csv"), index=False)


if __name__ == "__main__":
    main()
