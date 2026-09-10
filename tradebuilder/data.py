"""Price data: a CSV on disk, or a ticker via yfinance (optional dependency).

Everything downstream expects a DataFrame indexed by date with lowercase
columns: open, high, low, close, volume.
"""
from __future__ import annotations

import pandas as pd

COLUMNS = ["open", "high", "low", "close", "volume"]


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase columns, flatten yfinance MultiIndex, keep OHLCV, sort by date."""
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = [c[0] for c in df.columns]
    df = df.rename(columns={c: str(c).lower() for c in df.columns})
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"missing columns {missing}; have {list(df.columns)}")
    out = df[COLUMNS].astype(float).sort_index()
    out.index = pd.to_datetime(out.index)
    out.index.name = "date"
    return out.dropna()


def load_csv(path: str) -> pd.DataFrame:
    """CSV with a date column (first column) and OHLCV columns in any case."""
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return normalize(df)


def fetch(ticker: str, start: str = "2010-01-01", end: str | None = None) -> pd.DataFrame:
    """Daily bars from Yahoo via yfinance, adjusted for splits/dividends."""
    try:
        import yfinance as yf
    except ImportError as e:  # pragma: no cover
        raise ImportError("pip install yfinance  (or use load_csv)") from e
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if df is None or len(df) == 0:
        raise ValueError(f"no data returned for {ticker}")
    return normalize(df)
