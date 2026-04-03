import json
import subprocess


def fetch_eversource_default_business_rate() -> float | None:
    try:
        result = subprocess.run(
            ["node", "node_scraper/ct_default_rate.js"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        return data.get("rate_cents_per_kwh")
    except Exception:
        return None