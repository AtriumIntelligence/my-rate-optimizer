from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import pandas as pd


@dataclass
class PlanCostInputs:
    rate_cents_per_kwh: float
    fixed_monthly_fee: float = 0.0  # $/month
    demand_kw: Optional[float] = None
    demand_rate_per_kw: Optional[float] = None  # $/kW-month
    on_peak_share: Optional[float] = None  # 0–1
    on_peak_adder_cents: Optional[float] = None  # extra ¢/kWh on on-peak


def compute_plan_cost(
    monthly_kwh: pd.Series,
    inputs: PlanCostInputs,
) -> float:
    """
    Compute total contract cost in dollars for a plan.
    monthly_kwh: Series of kWh per month (length = contract months)
    """
    months = len(monthly_kwh)

    base_rate = inputs.rate_cents_per_kwh / 100.0  # $/kWh
    energy_cost = (monthly_kwh * base_rate).sum()

    tou_cost = 0.0
    if inputs.on_peak_share is not None and inputs.on_peak_adder_cents is not None:
        adder = inputs.on_peak_adder_cents / 100.0
        tou_kwh = monthly_kwh * inputs.on_peak_share
        tou_cost = (tou_kwh * adder).sum()

    fixed_cost = inputs.fixed_monthly_fee * months

    demand_cost = 0.0
    if inputs.demand_kw is not None and inputs.demand_rate_per_kw is not None:
        demand_cost = inputs.demand_kw * inputs.demand_rate_per_kw * months

    total = energy_cost + tou_cost + fixed_cost + demand_cost
    return float(total)