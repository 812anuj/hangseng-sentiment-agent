
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter


# 1. File locations
input_file = Path("data/raw/exa_news.json")
output_file = Path("data/processed/exa_news_cleaned.json")


# 2. Load raw articles
with input_file.open("r", encoding="utf-8") as file:
    articles = json.load(file)


cleaned_articles = []


# 3. Process every article
for article in articles:

    # Clean article text
    text = article.get("text") or ""

    # Replace multiple spaces and newlines with one space
    text = re.sub(r"\s+", " ", text).strip()

    # Clean title
    title = (article.get("title") or "").strip()

    # Convert publication date into UTC
    published_date = article.get("published_date")

    published = datetime.fromisoformat(
        published_date.replace("Z", "+00:00")
    )

    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)

    published = published.astimezone(timezone.utc)

    # Create standardized article
    cleaned_article = {
        "news_id": len(cleaned_articles) + 1,
        "ticker": article.get("ticker"),
        "company": article.get("company"),
        "exchange": article.get("exchange"),
        "source": article.get("source"),
        "title": title,
        "url": article.get("url"),
        "author": article.get("author"),
        "published_date_utc": published.isoformat(),
        "text": text,
        "text_length": len(text),
    }

    cleaned_articles.append(cleaned_article)


# 4. Create output folder if necessary
output_file.parent.mkdir(parents=True, exist_ok=True)


# 5. Save cleaned articles
with output_file.open("w", encoding="utf-8") as file:
    json.dump(cleaned_articles, file, indent=4, ensure_ascii=False)


# 6. Print summary
ticker_counts = Counter(
    article["ticker"] for article in cleaned_articles
)

print("\n========== NEWS NORMALIZATION ==========")
print("Raw articles:", len(articles))
print("Cleaned articles:", len(cleaned_articles))
print("Removed articles:", len(articles) - len(cleaned_articles))

print("\nArticles per ticker:")

for ticker, count in sorted(ticker_counts.items()):
    print(ticker, ":", count)

print("\nSaved to:", output_file)
print("========================================")
