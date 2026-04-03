from __future__ import annotations
from dataclasses import dataclass
from typing import List
import pandas as pd

MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@dataclass
class UsagePoint:
    month: str  # "Jan", "Feb", ...
    kwh: float


def build_seasonal_profile(history: List[UsagePoint]) -> pd.Series:
    """
    Takes 1–12 months of usage and returns a 12‑month seasonal profile (index = month name).
    If fewer than 12 months are provided, missing months are filled with the average.
    """
    if not history:
        raise ValueError("At least one UsagePoint is required")

    df = pd.DataFrame([{"month": u.month, "kwh": u.kwh} for u in history])
    df["month"] = pd.Categorical(df["month"], categories=MONTH_ORDER, ordered=True)
    df = df.sort_values("month")

    if df["month"].nunique() == 12:
        profile = df.set_index("month")["kwh"]
        return profile

    avg_kwh = df["kwh"].mean()
    full = pd.Series(index=MONTH_ORDER, dtype=float)

    for _, row in df.iterrows():
        full[row["month"]] = row["kwh"]

    full = full.fillna(avg_kwh)
    return full


def project_usage_over_term(
    history: List[UsagePoint],
    contract_months: int,
    start_month: str,
) -> pd.Series:
    """
    Returns a Series of length `contract_months` with projected kWh per month.
    Uses the seasonal profile built from history and rolls it forward from start_month.
    """
    profile = build_seasonal_profile(history)

    if start_month not in MONTH_ORDER:
        raise ValueError(f"start_month must be one of {MONTH_ORDER}")

    start_idx = MONTH_ORDER.index(start_month)
    months_sequence = []
    for i in range(contract_months):
        idx = (start_idx + i) % 12
        months_sequence.append(MONTH_ORDER[idx])

    projected = pd.Series(
        [profile[m] for m in months_sequence],
        index=months_sequence,
        name="kwh",
    )
    return projected