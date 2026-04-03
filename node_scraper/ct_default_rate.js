const { chromium } = require("playwright");

async function fetchDefaultBusinessRate() {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    await page.goto(
        "https://www.eversource.com/content/ct/business/account-billing/rates-tariffs/electric-supplier-options/standard-service-rates",
        { waitUntil: "domcontentloaded" }
    );

    await page.waitForTimeout(2000);

    const rateText = await page.evaluate(() => {
        const rows = Array.from(document.querySelectorAll("table tr"));
        for (const row of rows) {
            if (row.innerText.toLowerCase().includes("business")) {
                const cells = row.innerText.split("\n");
                const candidate = cells.find(c => c.includes("¢"));
                if (candidate) return candidate;
            }
        }
        return null;
    });

    let rate = null;
    if (rateText) {
        const m = rateText.match(/([\d.]+)/);
        if (m) rate = parseFloat(m[1]);
    }

    console.log(JSON.stringify({ rate_cents_per_kwh: rate }));
    await browser.close();
}

fetchDefaultBusinessRate();