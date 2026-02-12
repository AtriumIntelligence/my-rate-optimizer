import pandas as pd
import re

# ---------------------------------------------------------
# Basic Filters & Cost Calculations
# ---------------------------------------------------------

def filter_electric_residential(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to electric residential plans only."""
    return df[
        (df["COMMODITY"].str.upper() == "ELECTRIC") &
        (df["SERVICE_CLASS"].str.upper() == "RESIDENTIAL")
    ]


def compute_monthly_cost(df: pd.DataFrame, usage_kwh: float) -> pd.DataFrame:
    """Compute monthly cost based on rate and usage."""
    df = df.copy()
    df["monthly_cost"] = df["RATE"].astype(float) * usage_kwh
    return df


# ---------------------------------------------------------
# Cancellation Fee Parsing (Robust)
# ---------------------------------------------------------

def parse_cancellation_fee(value):
    """
    Convert cancellation fee strings into numeric values.
    Handles cases like:
    - "0"
    - "None"
    - "No fee"
    - "$10/month for the remaining term"
    - "Early termination fee applies"
    - "See terms"
    """
    if value is None:
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).lower().strip()

    # Common "no fee" patterns
    no_fee_terms = ["", "none", "no", "no fee", "n/a", "na", "0", "$0"]
    if text in no_fee_terms:
        return 0.0

    # Extract any number from the string
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    if numbers:
        return float(numbers[0])

    # If no number found, treat as zero (unknown)
    return 0.0


# ---------------------------------------------------------
# Value-Added Services Parsing
# ---------------------------------------------------------

def parse_value_added(value):
    """
    Convert value-added service flags into numeric values.
    Many ESCOs use:
    - "1" for yes
    - "0" for no
    - or descriptive text
    """
    if value is None:
        return 0

    text = str(value).lower().strip()

    if text in ["1", "yes", "true", "included"]:
        return 1

    return 0


# ---------------------------------------------------------
# Scoring Engine (Best Value Plans)
# ---------------------------------------------------------

def score_plans(
    df: pd.DataFrame,
    usage: float,
    prefer_fixed=False,
    prefer_green=False,
    avoid_cancellation_fees=False,
    avoid_value_added=False
):
    """
    Score plans based on:
    - Monthly cost
    - Cancellation fees
    - Green energy %
    - Fixed vs variable preference
    - Value-added services
    """

    df = compute_monthly_cost(df, usage).copy()

    # Parse cancellation fees
    df["CANCELLATION_FEE_PARSED"] = df["CANCELLATION_FEE"].apply(parse_cancellation_fee)

    # Parse value-added services
    df["VALUE_ADDED_PARSED"] = df["VALUE_ADDED"].apply(parse_value_added)

    # Base score = negative monthly cost (lower cost = higher score)
    df["score"] = -df["monthly_cost"]

    # Cancellation fee penalty
    if avoid_cancellation_fees:
        df["score"] -= df["CANCELLATION_FEE_PARSED"] * 0.1

    # Green energy preference
    if prefer_green:
        df["score"] += df["PERCENTAGE_GREEN"].astype(float) * 5

    # Fixed vs variable preference
    if prefer_fixed:
        df["score"] += df["OFFER_TYPE"].apply(lambda x: 10 if str(x).lower() == "fixed" else -10)

    # Value-added services preference
    if avoid_value_added:
        df["score"] -= df["VALUE_ADDED_PARSED"] * 10

    return df.sort_values("score", ascending=False)


# ---------------------------------------------------------
# Cheapest Plan (Simple)
# ---------------------------------------------------------

def get_cheapest_plan(df: pd.DataFrame):
    """Return the single cheapest plan by rate."""
    return df.sort_values("RATE").iloc[0]