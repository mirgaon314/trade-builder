"""Technical indicators and the feature frame the model learns weights for.

All functions take a close-price Series and return a Series aligned to it.
Nothing here looks into the future: every value at date t uses data <= t.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def sma(close: pd.Series, n: int) -> pd.Series:
    return close.rolling(n).mean()


def ema(close: pd.Series, n: int) -> pd.Series:
    return close.ewm(span=n, adjust=False).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    """Wilder's RSI in [0, 100]."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / n, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100.0 - 100.0 / (1.0 + rs)
    return out.fillna(100.0).where(avg_loss != 0, 100.0)


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Returns (macd_line, signal_line, histogram)."""
    line = ema(close, fast) - ema(close, slow)
    sig = ema(line, signal)
    return line, sig, line - sig


# ---- feature frame ----------------------------------------------------------

DEFAULT_FEATURES = ["ret_1", "ret_5", "ret_20", "sma_gap_10_50", "rsi_14", "macd_hist", "vol_20"]


def feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Indicator features per day, scaled to be roughly unit-free.

    Columns:
        ret_1, ret_5, ret_20  : trailing simple returns
        sma_gap_10_50         : sma10 / sma50 - 1  (trend)
        rsi_14                : (RSI - 50) / 50, in [-1, 1]
        macd_hist             : MACD histogram / close  (momentum)
        vol_20                : 20-day std of daily returns
        y                     : target, 1 if next day's close is higher else 0
    Rows with any NaN (warm-up) are dropped. The last row has no target and is
    dropped too; use `latest_features` for a live signal.
    """
    close = df["close"]
    f = pd.DataFrame(index=df.index)
    f["ret_1"] = close.pct_change(1)
    f["ret_5"] = close.pct_change(5)
    f["ret_20"] = close.pct_change(20)
    f["sma_gap_10_50"] = sma(close, 10) / sma(close, 50) - 1.0
    f["rsi_14"] = (rsi(close, 14) - 50.0) / 50.0
    _, _, hist = macd(close)
    f["macd_hist"] = hist / close
    f["vol_20"] = close.pct_change().rolling(20).std()
    f["y"] = (close.shift(-1) > close).astype(int)
    f.loc[f.index[-1], "y"] = np.nan  # unknown for the last day
    return f.dropna()


def latest_features(df: pd.DataFrame) -> pd.Series:
    """Feature row for the most recent day (no target)."""
    close = df["close"]
    _, _, hist = macd(close)
    row = {
        "ret_1": close.pct_change(1).iloc[-1],
        "ret_5": close.pct_change(5).iloc[-1],
        "ret_20": close.pct_change(20).iloc[-1],
        "sma_gap_10_50": (sma(close, 10) / sma(close, 50) - 1.0).iloc[-1],
        "rsi_14": ((rsi(close, 14) - 50.0) / 50.0).iloc[-1],
        "macd_hist": (hist / close).iloc[-1],
        "vol_20": close.pct_change().rolling(20).std().iloc[-1],
    }
    return pd.Series(row, name=df.index[-1])
