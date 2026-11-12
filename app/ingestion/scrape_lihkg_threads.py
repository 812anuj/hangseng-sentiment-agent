
import json
from pathlib import Path

from apify_client import ApifyClient

from app.config.settings import settings


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

ACTOR_ID = "claude_code_reviewer~lihkg-scraper-en"

INPUT_PATH = Path("data/raw/lihkg_posts.json")

OUTPUT_PATH = Path("data/raw/lihkg_thread_details.json")

# Threads selected from our search results
SELECTED_THREAD_IDS = [
    "4178282",
    "4177116",
    "4178872",
    "4176716"
]


# --------------------------------------------------
# 2. Connect to Apify
# --------------------------------------------------

if not settings.APIFY_API_TOKEN:
    raise ValueError("APIFY_API_TOKEN is missing from .env")

client = ApifyClient(settings.APIFY_API_TOKEN)


# --------------------------------------------------
# 3. Scrape complete threads
# --------------------------------------------------

def scrape_thread_details():

    run_input = {
        "mode": "thread",
        "threadIds": SELECTED_THREAD_IDS,
        "threadUrls": [],
        "maxItems": 200,
        "aiLabels": False,
        "proxyConfiguration": {
            "useApifyProxy": True
        }
    }

    print("Starting LIHKG thread scraper...")

    run = client.actor(ACTOR_ID).call(
        run_input=run_input
    )

    print("Actor finished!")
    print("Run ID:", run.id)
    print("Dataset ID:", run.default_dataset_id)

    dataset = client.dataset(run.default_dataset_id)

    records = list(dataset.iterate_items())

    print("Total records downloaded:", len(records))

    return records


# --------------------------------------------------
# 4. Save complete thread data
# --------------------------------------------------

def save_thread_details(records):

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

    print("Thread details saved:", OUTPUT_PATH)
    print("Records saved:", len(records))


# --------------------------------------------------
# 5. Main execution
# --------------------------------------------------

if __name__ == "__main__":

    records = scrape_thread_details()

    if records:

        print("\nFirst downloaded record:")
        print(records[0])

    else:

        print("No thread details returned.")

    save_thread_details(records)
