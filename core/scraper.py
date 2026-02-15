import json
import subprocess
import pandas as pd

def _run_node_scraper():
    result = subprocess.run(
        ["node", "node_scraper/ct_scraper.js"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)

def fetch_ct_offers_df() -> pd.DataFrame:
    offers = _run_node_scraper()
    return pd.DataFrame(offers)