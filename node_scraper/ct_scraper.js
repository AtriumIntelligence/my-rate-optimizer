const { chromium } = require("playwright");

async function fetchCTOffers() {
    const browser = await chromium.launch({
        headless: false,
        args: [
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process"
        ]
    });

    const context = await browser.newContext({
        userAgent:
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        viewport: { width: 1400, height: 900 }
    });

    const page = await context.newPage();

    await page.goto(
        "https://www.energizect.com/rate-board/compare-energy-supplier-rates",
        { waitUntil: "domcontentloaded" }
    );

    await page.waitForTimeout(3000);

    // Handle modal
    try {
        await page.click("text=Eversource Business", { timeout: 5000 });
        await page.click("text=Search & Compare Rates", { timeout: 5000 });
    } catch {}

    await page.waitForTimeout(5000);

    // ⭐ DOM scraping using real card structure
    const offers = await page.evaluate(() => {
        // Each offer card has this class
        const cards = Array.from(document.querySelectorAll(".rate-board__result"));

        return cards.map(card => {
            const get = (selector) => {
                const el = card.querySelector(selector);
                return el ? el.innerText.trim() : null;
            };

            // Supplier name
            const supplier = get(".supplier-name, .supplier, .supplier__name");

            // Phone
            const phoneMatch = card.innerText.match(/\(\d{3}\)\s*\d{3}-\d{4}/);
            const phone = phoneMatch ? phoneMatch[0] : null;

            // Rate
            const rateMatch = card.innerText.match(/([\d.]+)₵ per kWh/);
            const rate = rateMatch ? parseFloat(rateMatch[1]) : null;

            // Monthly cost
            const monthlyMatch = card.innerText.match(/\$([\d.]+)\s+at/);
            const monthly = monthlyMatch ? parseFloat(monthlyMatch[1]) : null;

            // Term
            const term = get(".plan-term, .term, .plan-description__term");

            // Green %
            const greenMatch = card.innerText.match(/([\d.]+)% RECs/);
            const green = greenMatch ? parseFloat(greenMatch[1]) : null;

            return {
                supplier,
                phone,
                rate_cents_per_kwh: rate,
                monthly_cost: monthly,
                term,
                green_pct: green
            };
        });
    });

    console.log(JSON.stringify(offers, null, 2));
    await browser.close();
}

fetchCTOffers();