import requests
import pandas as pd

ZIP = "10001"
URL = f"https://documents.dps.ny.gov/PTC/api/Service/GetActiveOffersByZip/{ZIP}"

print(f"Fetching offers for ZIP {ZIP}...")
resp = requests.get(URL, timeout=10)
resp.raise_for_status()

data = resp.json()
print(f"Total records returned: {len(data)}")

# Convert to DataFrame for easy inspection
df = pd.DataFrame(data)

# Show the first few rows and key columns
print(df.head()[[
    "DISPLAY_NAME",
    "OFFER_TYPE",
    "RATE",
    "SERVICE_ZONE",
    "SERVICE_CLASS",
    "PERCENTAGE_GREEN"
]])

electric_res = df[
    (df["COMMODITY"] == "ELECTRIC") &
    (df["SERVICE_CLASS"] == "Residential")
]

print("Electric residential offers:", len(electric_res))
print(electric_res.sort_values("RATE")[[
    "DISPLAY_NAME", "RATE", "OFFER_TYPE", "SERVICE_ZONE"
]].head(10))

# ---- Additional test: compute monthly cost and rank ----

# Filter to electric residential
electric_res = df[
    (df["COMMODITY"] == "ELECTRIC") &
    (df["SERVICE_CLASS"] == "Residential")
]

# Compute monthly cost for a sample usage (e.g., 600 kWh)
usage_kwh = 600
electric_res = electric_res.copy()
electric_res["monthly_cost"] = electric_res["RATE"] * usage_kwh

# Sort by cheapest
electric_res_sorted = electric_res.sort_values("RATE")

print("\nCheapest 10 plans for 600 kWh:")
print(electric_res_sorted.head(10)[[
    "DISPLAY_NAME",
    "RATE",
    "monthly_cost",
    "OFFER_TYPE",
    "SERVICE_ZONE"
]])