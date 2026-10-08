import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd


BASE_URL = "https://books.toscrape.com/"
all_books = []


# Scrape all 50 pages
for page in range(1, 51):

    if page == 1:
        page_url = BASE_URL
    else:
        page_url = f"{BASE_URL}catalogue/page-{page}.html"

    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    print(f"Page {page}: {len(books)} books")

    # Extract data from each book
    for book in books:

        title = book.find("h3").find("a")["title"]

        price = book.find(
            "p",
            class_="price_color"
        ).text

        rating = book.find(
            "p",
            class_="star-rating"
        )["class"][1]

        availability = book.find(
            "p",
            class_="availability"
        ).text.strip()

        link = book.find("h3").find("a")["href"]
        full_link = urljoin(page_url, link)

        # Open book detail page to get category
        detail_response = requests.get(full_link)
        detail_soup = BeautifulSoup(
            detail_response.text,
            "html.parser"
        )

        breadcrumb = detail_soup.select(
            "ul.breadcrumb li"
        )

        if len(breadcrumb) > 2:
            category = breadcrumb[2].text.strip()
        else:
            category = "Unknown"

        book_data = {
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability,
            "category": category,
            "url": full_link
        }

        all_books.append(book_data)


# Create DataFrame
df = pd.DataFrame(all_books)

# Clean price
df["price"] = (
    df["price"]
    .str.replace("Â£", "", regex=False)
    .astype(float)
)

# Save dataset
df.to_csv(
    "data/books_dataset.csv",
    index=False,
    encoding="utf-8-sig"
)


# Final verification
print("\nScraping completed successfully!")
print("Total books:", len(df))
print("Dataset shape:", df.shape)