
This module contains the Social Media Scraper for the Lead Sniper system.


import os
from playwright.sync_api import sync_playwright
import google.generativeai as genai

# Configure AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# Integration functions
def send_to_manus_core(data):
    print(f"Sending to Manus Core: {data}")

def send_to_vision_cortex(data):
    print(f"Sending to Vision Cortex: {data}")

def send_to_vertex_ai(data):
    print(f"Sending to Vertex AI: {data}")

# AI Analysis
def analyze_listing(listing_details):
    prompt = f"Is the following property listing a distressed property? Analyze the title and description and return 'Yes' or 'No'.\n\n{listing_details}"
    response = model.generate_content(prompt)
    return response.text.strip()

# Scrapers
def scrape_facebook_marketplace():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.facebook.com/marketplace/")
        page.locator('input[aria-label="Search Marketplace"]').fill('distressed properties')
        page.locator('button[aria-label="Search"]').click()
        page.wait_for_load_state('networkidle')
        listings = page.locator("//a[@href^='/marketplace/item/']").all()
        for listing in listings:
            title = listing.locator("//span[contains(@style, 'text-transform: none;')]").inner_text()
            price = listing.locator("//div[contains(@style, 'font-weight: 700;')]").inner_text()
            link = listing.get_attribute('href')
            analysis = analyze_listing(f'Title: {title}')
            if analysis == 'Yes':
                data = {'title': title, 'price': price, 'link': link, 'source': 'Facebook Marketplace'}
                send_to_manus_core(data)
                send_to_vision_cortex(data)
                send_to_vertex_ai(data)
        browser.close()

def scrape_craigslist():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.craigslist.org/about/sites")
        page.locator('a:has-text("new york")').first.click()
        page.locator('#query').fill('distressed properties')
        page.get_by_role('button', name='search').click()
        page.wait_for_load_state('networkidle')
        listings = page.locator("//li[@class='cl-search-result']").all()
        for listing in listings:
            title = listing.locator("//a[@class='posting-title']").inner_text()
            price = listing.locator("//span[@class='priceinfo']").inner_text()
            link = listing.locator("//a[@class='posting-title']").get_attribute("href")
            analysis = analyze_listing(f'Title: {title}')
            if analysis == 'Yes':
                data = {'title': title, 'price': price, 'link': link, 'source': 'Craigslist'}
                send_to_manus_core(data)
                send_to_vision_cortex(data)
                send_to_vertex_ai(data)
        browser.close()

if __name__ == '__main__':
    print("Starting Social Media Scraper...")
    scrape_facebook_marketplace()
    scrape_craigslist()
    print("Social Media Scraper finished.")
