import csv
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL for scraping
BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"

# Star rating mapping dictionary
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

def scrape_books(max_pages=3):
    """
    Scrapes book details (Title, Price, Rating, Stock) across multiple pages.
    """
    books_data = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    print(f"[*] Starting extraction for {max_pages} pages...")

    for page in range(1, max_pages + 1):
        url = BASE_URL.format(page)
        print(f"[-] Fetching: Page {page} -> {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Check for HTTP errors (4xx, 5xx)
        except requests.exceptions.RequestException as err:
            print(f"[!] Error fetching page {page}: {err}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article", class_="product_pod")

        for book in articles:
            # 1. Extract Title
            title_tag = book.h3.find("a")
            title = title_tag["title"] if title_tag else "Unknown Title"

            # 2. Extract Price
            price_tag = book.find("p", class_="price_color")
            price = price_tag.get_text(strip=True).replace("Â", "") if price_tag else "N/A"

            # 3. Extract Rating
            star_tag = book.find("p", class_="star-rating")
            rating_class = star_tag["class"][1] if star_tag and len(star_tag["class"]) > 1 else "Zero"
            rating = RATING_MAP.get(rating_class, 0)

            # 4. Extract Stock Status
            stock_tag = book.find("p", class_="instock availability")
            availability = stock_tag.get_text(strip=True) if stock_tag else "Unknown"

            books_data.append({
                "Title": title,
                "Price": price,
                "Rating (Out of 5)": rating,
                "Availability": availability
            })

        time.sleep(1)  # Respectful crawling delay

    print(f"[+] Total records scraped: {len(books_data)}")
    return books_data


def export_to_csv(data, filename="scraped_books_dataset.csv"):
    """
    Saves the extracted records into a CSV dataset.
    """
    if not data:
        print("[!] No data found to save.")
        return

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"[✓] Dataset successfully saved to '{filename}'")


if __name__ == "__main__":
    extracted_records = scrape_books(max_pages=3)
    export_to_csv(extracted_records)