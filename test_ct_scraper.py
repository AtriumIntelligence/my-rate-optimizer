from core.ct_scraper import fetch_ct_offers_df

def main():
    print("Fetching CT offers…")
    df = fetch_ct_offers_df(2000)
    print(df)

if __name__ == "__main__":
    main()