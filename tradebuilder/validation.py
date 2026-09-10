"""Walk-forward validation: the guardrail against fooling yourself.

Fit on a window of past data, trade the next window with those weights,
slide forward, repeat. Stitch the out-of-sample windows together and that is
the only backtest number worth quoting.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pandas as pd

from .backtest import BacktestResult, run_backtest


@dataclass
class Fold:
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    in_sample: BacktestResult
    out_of_sample: BacktestResult
    weights: pd.Series | None


@dataclass
class WalkForwardResult:
    folds: list[Fold]
    out_of_sample: BacktestResult   # all test windows stitched together
    positions: pd.Series

    def table(self) -> pd.DataFrame:
        rows = []
        for f in self.folds:
            rows.append({
                "test_start": f.test_start.date(), "test_end": f.test_end.date(),
                "IS_sharpe": f.in_sample.metrics["sharpe"], "OOS_sharpe": f.out_of_sample.metrics["sharpe"],
                "OOS_return": f.out_of_sample.metrics["total_return"], "OOS_maxDD": f.out_of_sample.metrics["max_drawdown"],
            })
        return pd.DataFrame(rows)


def walk_forward(
    F: pd.DataFrame,
    close: pd.Series,
    model_factory: Callable[[], object],
    train: int = 750,
    test: int = 250,
    step: int | None = None,
    cost_bps: float = 5.0,
) -> WalkForwardResult:
    """Anchored-window walk-forward.

    Args:
        F: feature frame (must contain 'y' and the model's features)
        close: close prices covering F.index
        model_factory: returns a fresh, unfit model with fit()/positions()
        train, test: window lengths in rows (trading days)
        step: how far to slide each fold; default = test (no overlap)
    """
    step = step or test
    if len(F) < train + test:
        raise ValueError(f"need at least {train + test} rows, have {len(F)}")
    folds: list[Fold] = []
    oos_positions: list[pd.Series] = []
    start = 0
    while start + train + test <= len(F):
        F_tr = F.iloc[start : start + train]
        F_te = F.iloc[start + train : start + train + test]
        model = model_factory().fit(F_tr)
        pos_tr = model.positions(F_tr)
        pos_te = model.positions(F_te)
        folds.append(Fold(
            F_tr.index[0], F_tr.index[-1], F_te.index[0], F_te.index[-1],
            run_backtest(close, pos_tr, cost_bps), run_backtest(close, pos_te, cost_bps),
            getattr(model, "weights", None),
        ))
        oos_positions.append(pos_te)
        start += step
    positions = pd.concat(oos_positions)
    positions = positions[~positions.index.duplicated(keep="last")]
    return WalkForwardResult(folds=folds, out_of_sample=run_backtest(close, positions, cost_bps), positions=positions)


def overfit_warning(result: WalkForwardResult, gap: float = 1.0) -> str | None:
    """Plain-language warning when in-sample looks much better than out-of-sample."""
    is_s = pd.Series([f.in_sample.metrics["sharpe"] for f in result.folds])
    oos_s = pd.Series([f.out_of_sample.metrics["sharpe"] for f in result.folds])
    msgs = []
    if is_s.mean() - oos_s.mean() > gap:
        msgs.append(f"in-sample Sharpe {is_s.mean():.2f} vs out-of-sample {oos_s.mean():.2f}: the model fits the past better than it predicts the future (overfitting).")
    if (oos_s <= 0).mean() >= 0.5:
        msgs.append(f"{int((oos_s <= 0).sum())} of {len(oos_s)} test windows have Sharpe <= 0: the edge is not stable across time.")
    return " ".join(msgs) if msgs else None
