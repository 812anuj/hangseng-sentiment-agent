
import json
from pathlib import Path

from apify_client import ApifyClient
from app.config.settings import settings


# Apify actor ID
ACTOR_ID = "hgservices~naver-stock-discussion-scraper"

# Where we will save scraped posts
OUTPUT_PATH = Path("data/raw/naver_posts.json")

# Five South Korean companies
STOCKS = {
    "005930": "Samsung Electronics",
    "000660": "SK Hynix",
    "035420": "NAVER",
    "035720": "Kakao",
    "005380": "Hyundai Motor",
}

# Check whether the Apify token exists
if not settings.APIFY_API_TOKEN:
    raise ValueError("APIFY_API_TOKEN is missing from .env")

client = ApifyClient(settings.APIFY_API_TOKEN)


def scrape_naver_posts():

    all_posts = []

    for stock_code, company_name in STOCKS.items():

        print(f"\nScraping {company_name} ({stock_code})...")

        run_input = {
            "dateFrom": "2026-11-01",
            "maxResults": 20,
            "stocks": [stock_code]
        }

        run = client.actor(ACTOR_ID).call(
            run_input=run_input
        )

        dataset = client.dataset(run.default_dataset_id)

        records = list(dataset.iterate_items())

        print(f"Posts collected: {len(records)}")

        # Add our own stock metadata to every record
        for record in records:

            record["ticker"] = stock_code
            record["company"] = company_name
            record["exchange"] = "South Korea"
            record["source"] = "Naver Finance"

            all_posts.append(record)

    return all_posts


def save_posts(posts):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:

        json.dump(
            posts,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\nTotal posts collected:", len(posts))
    print("Saved to:", OUTPUT_PATH)


if __name__ == "__main__":

    posts = scrape_naver_posts()

    save_posts(posts)

    if posts:
        print("\nFirst scraped post:")

        print(
            json.dumps(
                posts[0],
                ensure_ascii=False,
                indent=4
            )
        )
