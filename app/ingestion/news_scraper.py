
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

from exa_py import Exa

from app.config.settings import settings


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

OUTPUT_PATH = Path("data/raw/exa_news.json")

RESULTS_PER_COMPANY = 5

DAYS_BACK = 10

# Our 10 selected companies
ASSETS = [
    {
        "ticker": "0700.HK",
        "company": "Tencent",
        "exchange": "Hong Kong"
    },
    {
        "ticker": "9988.HK",
        "company": "Alibaba",
        "exchange": "Hong Kong"
    },
    {
        "ticker": "3690.HK",
        "company": "Meituan",
        "exchange": "Hong Kong"
    },
    {
        "ticker": "0005.HK",
        "company": "HSBC",
        "exchange": "Hong Kong"
    },
    {
        "ticker": "1299.HK",
        "company": "AIA Group",
        "exchange": "Hong Kong"
    },
    {
        "ticker": "005930.KS",
        "company": "Samsung Electronics",
        "exchange": "South Korea"
    },
    {
        "ticker": "000660.KS",
        "company": "SK Hynix",
        "exchange": "South Korea"
    },
    {
        "ticker": "035420.KS",
        "company": "NAVER",
        "exchange": "South Korea"
    },
    {
        "ticker": "035720.KS",
        "company": "Kakao",
        "exchange": "South Korea"
    },
    {
        "ticker": "005380.KS",
        "company": "Hyundai Motor",
        "exchange": "South Korea"
    }
]


# --------------------------------------------------
# 2. Connect to Exa
# --------------------------------------------------

if not settings.EXA_API_KEY:
    raise ValueError("EXA_API_KEY is missing from .env")

exa = Exa(api_key=settings.EXA_API_KEY)


# --------------------------------------------------
# 3. Search news for one company
# --------------------------------------------------

def search_company_news(asset):

    company = asset["company"]
    ticker = asset["ticker"]

    query = (
        f"{company} {ticker} stock price "
        f"financial business news"
    )

    # Calculate the date 10 days ago
    start_date = (
        datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)
    ).date().isoformat()

    print(f"\nSearching news for {company} ({ticker})...")

    try:

        response = exa.search(
            query,
            type="auto",
            category="news",
            num_results=RESULTS_PER_COMPANY,
            start_published_date=start_date,
            contents={
                "text": {
                    "max_characters": 2500
                }
            }
        )

        news_records = []

        for article in response.results:

            news = {

                "ticker": ticker,
                "company": company,
                "exchange": asset["exchange"],

                "source": "Exa",

                "title": article.title,
                "url": article.url,
                "author": article.author,

                "published_date": article.published_date,

                "text": article.text or "",

                "retrieved_at_utc": datetime.now(
                    timezone.utc
                ).isoformat()
            }

            news_records.append(news)

        print("Articles found:", len(news_records))

        return news_records

    except Exception as error:

        print(f"News search failed for {company}: {error}")

        return []


# --------------------------------------------------
# 4. Search news for all companies
# --------------------------------------------------

def scrape_all_news():

    all_news = []

    for asset in ASSETS:

        company_news = search_company_news(asset)

        all_news.extend(company_news)

    return all_news


# --------------------------------------------------
# 5. Remove duplicate articles
# --------------------------------------------------

def remove_duplicates(news_records):

    unique_news = []

    seen_urls = set()

    for article in news_records:

        url = article.get("url")

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        unique_news.append(article)

    return unique_news


# --------------------------------------------------
# 6. Save news data
# --------------------------------------------------

def save_news_data(news_records):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            news_records,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\nNews data saved:", OUTPUT_PATH)
    print("Total unique articles:", len(news_records))


# --------------------------------------------------
# 7. Main execution
# --------------------------------------------------

if __name__ == "__main__":

    print("Starting Exa news scraper...")

    all_news = scrape_all_news()

    unique_news = remove_duplicates(all_news)

    save_news_data(unique_news)

    print("\n========== NEWS SUMMARY ==========")

    print("Companies searched:", len(ASSETS))
    print("Articles collected:", len(unique_news))

    for asset in ASSETS:

        count = sum(
            1 for article in unique_news
            if article["ticker"] == asset["ticker"]
        )

        print(
            f"{asset['company']} ({asset['ticker']}): {count} articles"
        )
