
import json
from pathlib import Path

from apify_client import ApifyClient

from app.config.settings import settings


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

ACTOR_ID = "claude_code_reviewer~lihkg-scraper-en"

OUTPUT_PATH = Path("data/raw/lihkg_posts.json")

SEARCH_KEYWORDS = ["港股"]

MAX_ITEMS = 10


# --------------------------------------------------
# 2. Connect to Apify
# --------------------------------------------------

if not settings.APIFY_API_TOKEN:
    raise ValueError("APIFY_API_TOKEN is missing from .env")

client = ApifyClient(settings.APIFY_API_TOKEN)


# --------------------------------------------------
# 3. Scrape LIHKG
# --------------------------------------------------

def scrape_lihkg():

    run_input = {
        "mode": "search",
        "catIds": [],
        "keywords": SEARCH_KEYWORDS,
        "maxItems": MAX_ITEMS,
        "order": "desc_create_time",
        "dateFrom": "10d",
        "aiLabels": False,
        "onlyNew": False,
        "bulkInput": "",
        "threadIds": [],
        "threadUrls": [],
        "proxyConfiguration": {
            "useApifyProxy": True
        }
    }

    print("Starting LIHKG scraper...")

    run = client.actor(ACTOR_ID).call(
        run_input=run_input
    )

    print("Actor finished!")
    print("Run ID:", run.id)
    print("Dataset ID:", run.default_dataset_id)

    # Download results
    dataset = client.dataset(run.default_dataset_id)

    records = list(dataset.iterate_items())

    print("Total records downloaded:", len(records))

    return records


# --------------------------------------------------
# 4. Save raw data
# --------------------------------------------------

def save_raw_data(records):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("Raw data saved:", OUTPUT_PATH)
    print("Records saved:", len(records))


# --------------------------------------------------
# 5. Main execution
# --------------------------------------------------

if __name__ == "__main__":

    records = scrape_lihkg()

    if records:

        print("\nFirst scraped record:")
        print(records[0])

    else:

        print("No records returned by LIHKG.")

    save_raw_data(records)





# Verify that our API token works
# user = client.user().get()
# print("Connected to Apify successfully!")
# print("Apify username:", user.username)




