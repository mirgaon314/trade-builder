"""Models that turn a feature row into a long/flat position.

WeightedIndicatorModel is the point of the project: instead of hand-written
if/then rules, the user picks indicators and a small linear model learns how
much each one should count. The learned weights double as the explanation.

Two baselines are included so the weighted model has something to beat.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from .indicators import DEFAULT_FEATURES


class WeightedIndicatorModel:
    """Standardize features -> logistic regression -> P(next day up)."""

    def __init__(self, features: list[str] | None = None, C: float = 1.0, threshold: float = 0.5):
        self.features = list(features or DEFAULT_FEATURES)
        self.C = C
        self.threshold = threshold
        self.scaler = StandardScaler()
        self.clf = LogisticRegression(C=C, max_iter=1000)

    def fit(self, F: pd.DataFrame) -> "WeightedIndicatorModel":
        X = self.scaler.fit_transform(F[self.features].values)
        self.clf.fit(X, F["y"].astype(int).values)
        return self

    def proba(self, F: pd.DataFrame) -> pd.Series:
        X = self.scaler.transform(F[self.features].values)
        return pd.Series(self.clf.predict_proba(X)[:, 1], index=F.index, name="p_up")

    def positions(self, F: pd.DataFrame) -> pd.Series:
        """1 = long, 0 = flat."""
        return (self.proba(F) > self.threshold).astype(int).rename("position")

    def accuracy(self, F: pd.DataFrame) -> float:
        return float(np.mean(self.positions(F).values == F["y"].astype(int).values))

    @property
    def weights(self) -> pd.Series:
        """Coefficient per feature (on standardized inputs); sign = direction, size = influence."""
        return pd.Series(self.clf.coef_[0], index=self.features, name="weight")

    def explain(self, row: pd.Series) -> pd.DataFrame:
        """Per-feature contribution to the log-odds for one feature row."""
        z = (row[self.features].values - self.scaler.mean_) / self.scaler.scale_
        contrib = self.clf.coef_[0] * z
        out = pd.DataFrame({"value": row[self.features].values, "z": z, "weight": self.clf.coef_[0], "contribution": contrib}, index=self.features)
        out.attrs["intercept"] = float(self.clf.intercept_[0])
        out.attrs["log_odds"] = float(self.clf.intercept_[0] + contrib.sum())
        out.attrs["p_up"] = float(1.0 / (1.0 + np.exp(-out.attrs["log_odds"])))
        return out.sort_values("contribution", key=np.abs, ascending=False)


class RsiRuleModel:
    """Classic if/then baseline: long when RSI < 30 (oversold), flat when RSI > 70, otherwise hold last state."""

    def __init__(self, enter: float = 30.0, exit: float = 70.0):
        self.enter = (enter - 50.0) / 50.0  # feature frame stores scaled RSI
        self.exit = (exit - 50.0) / 50.0
        self.features = ["rsi_14"]

    def fit(self, F: pd.DataFrame) -> "RsiRuleModel":
        return self

    def positions(self, F: pd.DataFrame) -> pd.Series:
        pos, state = [], 0
        for r in F["rsi_14"].values:
            if r < self.enter:
                state = 1
            elif r > self.exit:
                state = 0
            pos.append(state)
        return pd.Series(pos, index=F.index, name="position")


class AlwaysLong:
    """Buy and hold."""

    features: list[str] = []

    def fit(self, F: pd.DataFrame) -> "AlwaysLong":
        return self

    def positions(self, F: pd.DataFrame) -> pd.Series:
        return pd.Series(1, index=F.index, name="position")
