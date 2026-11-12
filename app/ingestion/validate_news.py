import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


# 1. Load raw news articles
input_file = Path("data/raw/exa_news.json")

with input_file.open("r", encoding="utf-8") as file:
    articles = json.load(file)


# 2. Prepare validation counters
missing_text = 0
missing_date = 0
short_text = 0
old_articles = 0
duplicate_urls = 0

seen_urls = set()
ticker_counts = Counter()


# 3. Calculate the 10-day cutoff
now = datetime.now(timezone.utc)
cutoff = now - timedelta(days=10)


# 4. Check every article
for article in articles:

    ticker = article.get("ticker", "UNKNOWN")
    text = (article.get("text") or "").strip()
    published_date = article.get("published_date")
    url = article.get("url")

    ticker_counts[ticker] += 1

    if not text:
        missing_text += 1

    if len(text) < 200:
        short_text += 1

    if not published_date:
        missing_date += 1
    else:
        try:
            published = datetime.fromisoformat(
                published_date.replace("Z", "+00:00")
            )

            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)

            if published < cutoff:
                old_articles += 1

        except ValueError:
            missing_date += 1

    if url:
        if url in seen_urls:
            duplicate_urls += 1
        else:
            seen_urls.add(url)


# 5. Print validation report
print("\n========== NEWS VALIDATION REPORT ==========")

print("Total articles:", len(articles))
print("Missing text:", missing_text)
print("Missing dates or invalid dates:", missing_date)
print("Short articles (<200 characters):", short_text)
print("Articles older than 10 days:", old_articles)
print("Duplicate URLs:", duplicate_urls)

print("\nArticles per ticker:")

for ticker, count in sorted(ticker_counts.items()):
    print(ticker, ":", count)

print("\n============================================")
