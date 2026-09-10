"""Long/flat daily backtest with transaction costs and the usual report numbers.

Convention (no look-ahead): the position decided on day t, using data through
day t's close, earns the return from t's close to t+1's close.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

TRADING_DAYS = 252


@dataclass
class BacktestResult:
    equity: pd.Series
    returns: pd.Series
    positions: pd.Series
    metrics: dict = field(default_factory=dict)

    def __str__(self) -> str:
        m = self.metrics
        return (
            f"total {m['total_return']:+.1%} | CAGR {m['cagr']:+.1%} | Sharpe {m['sharpe']:.2f} | "
            f"maxDD {m['max_drawdown']:.1%} | win {m['win_rate']:.0%} of {m['n_trades']} trades | "
            f"exposure {m['exposure']:.0%}"
        )


def _trade_pnls(returns: pd.Series, positions: pd.Series) -> list[float]:
    """Compound P&L of each contiguous long stretch."""
    pnls, cur, in_trade = [], 1.0, False
    for pos, r in zip(positions.values, returns.values):
        if pos == 1:
            cur *= 1.0 + r
            in_trade = True
        elif in_trade:
            pnls.append(cur - 1.0)
            cur, in_trade = 1.0, False
    if in_trade:
        pnls.append(cur - 1.0)
    return pnls


def run_backtest(close: pd.Series, positions: pd.Series, cost_bps: float = 5.0) -> BacktestResult:
    """Simulate long/flat positions on a close series.

    Args:
        close: close prices indexed by date
        positions: 0/1 per date, decided at that date's close
        cost_bps: one-way cost per position change, in basis points of equity
    """
    close = close.loc[positions.index]
    fwd = close.pct_change().shift(-1)            # return from t close to t+1 close
    pos = positions.astype(float)
    gross = pos * fwd
    turnover = pos.diff().abs().fillna(pos.abs())  # entering on day 1 counts
    cost = turnover * cost_bps / 1e4
    net = (gross - cost).dropna()
    equity = (1.0 + net).cumprod()

    years = max(len(net), 1) / TRADING_DAYS
    total = float(equity.iloc[-1] - 1.0) if len(equity) else 0.0
    cagr = float((1.0 + total) ** (1.0 / years) - 1.0) if years > 0 and total > -1 else -1.0
    sharpe = float(net.mean() / net.std() * np.sqrt(TRADING_DAYS)) if net.std() > 0 else 0.0
    dd = equity / equity.cummax() - 1.0
    pnls = _trade_pnls(net, pos.loc[net.index])
    metrics = {
        "total_return": total,
        "cagr": cagr,
        "sharpe": sharpe,
        "max_drawdown": float(dd.min()) if len(dd) else 0.0,
        "win_rate": float(np.mean([p > 0 for p in pnls])) if pnls else 0.0,
        "n_trades": len(pnls),
        "exposure": float(pos.loc[net.index].mean()) if len(net) else 0.0,
        "days": int(len(net)),
    }
    return BacktestResult(equity=equity, returns=net, positions=pos.loc[net.index], metrics=metrics)
