from playwright.sync_api import sync_playwright
import pandas as pd

def fetch_ct_offers_df(monthly_usage=2000):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        page = browser.new_page()

        # 1. Load homepage (forces Cloudflare + session init)
        page.goto("https://www.energizect.com", wait_until="domcontentloaded")
        page.wait_for_timeout(1500)

        # 2. Navigate to Rate Board
        page.click("text=Rate Board")
        page.wait_for_timeout(1500)

        # 3. Navigate to Compare Rates
        page.click("text=Compare Rates")
        page.wait_for_timeout(2000)

        # 4. Now the REAL form is loaded — select dropdowns
        page.select_option("select[name='utility']", "1206")          # Eversource
        page.select_option("select[name='customerClass']", "1206")    # Business
        page.select_option("select[name='monthlyUsage']", str(monthly_usage))

        # 5. Click Search
        page.click("text=Search & Compare Rates")

        # 6. Wait for offer cards
        page.wait_for_selector(".list-item--ect-card", timeout=20000)

        # 7. Call the API from inside the browser
        api_url = (
            "https://www.energizect.com/ectr_search_api/offers"
            f"?customerClass[]=1206&monthlyUsage={monthly_usage}&planTypeEdc[]=1191"
        )

        data = page.evaluate(
            """async (api_url) => {
                const resp = await fetch(api_url, {
                    method: "GET",
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                });
                return await resp.json();
            }""",
            api_url,
        )

        browser.close()

    offers = data.get("data", [])
    if not offers:
        raise RuntimeError("No offers returned from EnergizeCT API.")

    df = pd.DataFrame(offers)

    df = df.rename(
        columns={
            "supplierName": "supplier",
            "rate": "rate_cents_per_kwh",
            "term": "term_description",
            "renewableEnergy": "recs_pct",
            "monthlyCost": "monthly_cost_at_usage",
            "phone": "phone",
        }
    )

    return df