import requests
import pandas as pd

BASE_URL = "https://documents.dps.ny.gov/PTC/api/Service"

def fetch_offers(zip_code: str) -> pd.DataFrame:
    url = f"{BASE_URL}/GetActiveOffersByZip/{zip_code}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return pd.DataFrame(r.json())