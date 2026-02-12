import requests
import pandas as pd


def fetch_esco_rates(zip_code: str = "10001") -> pd.DataFrame:
    """
    Fetch ESCO supply rates from NY DPS Power to Choose.
    Returns a DataFrame with provider, plan name, rate, term, etc.
    """

    url = f"https://documents.dps.ny.gov/PTC/search?zip={zip_code}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    if "offers" not in data:
        raise ValueError("Unexpected API format — 'offers' not found.")

    offers = data["offers"]

    rows = []
    for offer in offers:
        rows.append({
            "provider": offer.get("company", ""),
            "plan_name": offer.get("plan", ""),
            "rate": float(offer.get("rate", 0)),
            "term_months": offer.get("term", ""),
            "green_pct": offer.get("renewable", ""),
            "fees": offer.get("fees", ""),
            "rate_type": "flat"  # ESCO plans are almost always flat supply rates
        })

    return pd.DataFrame(rows)