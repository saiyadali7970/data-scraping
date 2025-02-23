import asyncio
import csv
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

URL = "https://www.booking.com/"
BROWSER_WS = "wss://brd-customer-hl_acc3d670-zone-scraping_browser1:etvasmpykg8v@brd.superproxy.io:9222"

# Function to calculate check-in/check-out dates
def add_days(date, days):
    return (date + timedelta(days=days)).strftime("%Y-%m-%d")

# Main function
async def run(url):
    print("Connecting to browser...")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(BROWSER_WS)
        print("Connected! Navigating to site...")
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        print("Navigated! Waiting for popup...")
        await close_popup(page)
        await interact(page)
        
        print("Parsing data...")
        data = await parse(page)
        print(f"Data parsed: {data}")

        # Save data to CSV
        save_to_csv(data)

        await browser.close()

# Function to close popups (if any)
async def close_popup(page):
    try:
        close_btn = await page.wait_for_selector('[aria-label="Dismiss sign-in info."]', timeout=25000)
        if close_btn:
            print("Popup appeared! Closing...")
            await close_btn.click()
            print("Popup closed!")
    except:
        print("Popup didn't appear.")

# Function to fill search form and submit
async def interact(page):
    search_text = "Mumbai"
    check_in = add_days(datetime.now(), 1)
    check_out = add_days(datetime.now(), 2)
    
    await asyncio.sleep(2)  # Small delay
    print("Waiting for search form...")
    search_input = await page.wait_for_selector('[data-testid="destination-container"] input', timeout=60000)
    print("Search form appeared! Filling it...")

    await search_input.fill(search_text)
    await page.click('[data-testid="searchbox-dates-container"] button')
    await page.wait_for_selector('[data-testid="searchbox-datepicker-calendar"]')
    await page.click(f'[data-date="{check_in}"]')
    await page.click(f'[data-date="{check_out}"]')

    print("Form filled! Waiting before clicking submit...")
    await asyncio.sleep(2)  # Small delay before clicking

    print("Clicking submit button...")
    await page.click('button[type="submit"]')

    # **Wait for search results instead of just waiting for load_state**
    print("Waiting for search results to load...")
    await page.wait_for_selector('[data-testid="property-card"]', timeout=60000)
    print("Results loaded!")

# Function to parse search results
async def parse(page):
    return await page.eval_on_selector_all(
        '[data-testid="property-card"]',
        """els => els.map(el => {
            const name = el.querySelector('[data-testid="title"]')?.innerText || 'N/A';
            const price = el.querySelector('[data-testid="price-and-discounted-price"]')?.innerText || 'N/A';
            const review_score = el.querySelector('[data-testid="review-score"]')?.innerText || '';
            const [score_str, , , reviews_str = ''] = review_score.split('\\n');
            const score = parseFloat(score_str) || score_str;
            const reviews = parseInt(reviews_str.replace(/\\D/g, '')) || reviews_str;
            return { name, price, score, reviews };
        })"""
    )

# Function to save data to CSV
def save_to_csv(data):
    filename = "booking_results.csv"
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "price", "score", "reviews"])
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Data successfully saved to {filename}")

# Run the script
if __name__ == "__main__":
    asyncio.run(run(URL))
