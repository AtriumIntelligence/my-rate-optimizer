from scraper.esco_scraper import fetch_esco_rates

print("Fetching ESCO rates for ZIP 10001...")
df = fetch_esco_rates("10001")

print(df.head())
print(f"\nTotal plans found: {len(df)}")