const { chromium } = require("playwright");
const fs = require("fs");

async function debugCT() {
    const browser = await chromium.launch({
        headless: false,   // MUST be false
        slowMo: 150,       // Human-like interaction
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

    // Scroll to modal buttons
    await page.evaluate(() => window.scrollBy(0, 400));

    // Click Eversource Business using real mouse events
    await page.locator("text=Eversource Business").click({ force: true });

    await page.waitForTimeout(2000);

    // Click Search & Compare Rates
    await page.locator("text=Search & Compare Rates").click({ force: true });

    // Wait for AJAX-loaded offer cards
    await page.waitForSelector(".list-item--ect-card", { timeout: 20000 });

    // Extract offer section
    const offerHTML = await page.evaluate(() => {
        const container =
            document.querySelector(".rate-board-results") ||
            document.querySelector(".view-content") ||
            document.body;

        return container.innerHTML;
    });

    fs.writeFileSync("ct_debug_section.html", offerHTML);

    console.log("WROTE ct_debug_section.html — send me this file.");
}

debugCT();