import asyncio
import csv
import sys
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# ✅ Fix: Force UTF-8 Encoding (For Windows Terminal & GitHub Actions)
sys.stdout.reconfigure(encoding='utf-8')

# 🌐 Target Website
URL = "https://www.booking.com/"
BROWSER_WS = "wss://brd-customer-hl_acc3d670-zone-scraping_browser1:etvasmpykg8v@brd.superproxy.io:9222"

# 📌 Function to calculate check-in/check-out dates
def add_days(date, days):
    return (date + timedelta(days=days)).strftime("%Y-%m-%d")

# 🌍 Main scraping function
async def run(url):
    print("🔄 Connecting to remote browser...")
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(BROWSER_WS)
            print("✅ Connected! Navigating to Booking.com...")

            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            print("✅ Page loaded! Checking for popups...")
            await close_popup(page)

            print("✅ Interacting with search form...")
            await interact(page)

            print("✅ Extracting hotel data...")
            data = await parse(page)

            print(f"📊 Data parsed successfully! Found {len(data)} hotels.")
            
            # Save Data
            save_to_csv(data)

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()
            print("📌 Browser closed.")

# ❌ Function to close popups (if any)
async def close_popup(page):
    try:
        close_btn = await page.wait_for_selector('[aria-label="Dismiss sign-in info."]', timeout=25000)
        if close_btn:
            print("⚠️ Popup detected! Closing...")
            await close_btn.click()
            print("✅ Popup closed!")
    except:
        print("🔹 No popup detected.")

# 🔎 Function to fill search form
async def interact(page):
    search_text = "Mumbai"
    check_in = add_days(datetime.now(), 1)
    check_out = add_days(datetime.now(), 2)

    await asyncio.sleep(2)  # Small delay to ensure elements are visible
    print("⌛ Waiting for search input field...")
    search_input = await page.wait_for_selector('[data-testid="destination-container"] input', timeout=60000)

    print("✅ Search form found! Entering details...")
    await search_input.fill(search_text)

    print("📅 Selecting check-in/check-out dates...")
    await page.click('[data-testid="searchbox-dates-container"] button')
    await page.wait_for_selector('[data-testid="searchbox-datepicker-calendar"]')
    await page.click(f'[data-date="{check_in}"]')
    await page.click(f'[data-date="{check_out}"]')

    print("✅ Form filled! Clicking search button...")
    await asyncio.sleep(2)  # Prevent fast interactions
    await page.click('button[type="submit"]')

    print("⌛ Waiting for search results...")
    await page.wait_for_selector('[data-testid="property-card"]', timeout=60000)
    print("✅ Search results loaded!")

# 🏨 Function to parse hotel results
async def parse(page):
    return await page.eval_on_selector_all(
        '[data-testid="property-card"]',
        """els => els.map(el => {
            const name = el.querySelector('[data-testid="title"]')?.innerText.trim() || 'N/A';
            const price = el.querySelector('[data-testid="price-and-discounted-price"]')?.innerText.replace(/[^0-9]/g, '') || 'N/A';
            const review_score = el.querySelector('[data-testid="review-score"]')?.innerText || '';
            const [score_str, , , reviews_str = ''] = review_score.split('\\n');
            const score = parseFloat(score_str) || score_str;
            const reviews = parseInt(reviews_str.replace(/\\D/g, '')) || reviews_str;
            return { name, price, score, reviews };
        })"""
    )

# 📂 Function to save results to CSV
def save_to_csv(data):
    filename = "booking_results.csv"
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "price", "score", "reviews"])
        writer.writeheader()
        writer.writerows(data)

    print(f"📁 Data saved successfully to {filename}")

# 🚀 Run the scraper
if __name__ == "__main__":
    asyncio.run(run(URL))
