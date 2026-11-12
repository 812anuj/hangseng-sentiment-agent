
import json
from pathlib import Path
from collections import Counter

from langdetect import detect
from transformers import pipeline

def detect_language(text):
    # Check for Korean characters (Hangul)
    if any(
        '\uac00' <= char <= '\ud7a3'
        or '\u1100' <= char <= '\u11ff'
        or '\u3130' <= char <= '\u318f'
        for char in text
    ):
        return "ko"

    # Check for Japanese characters
    if any(
        '\u3040' <= char <= '\u30ff'
        for char in text
    ):
        return "ja"

    # Check for Chinese characters
    if any(
        '\u4e00' <= char <= '\u9fff'
        for char in text
    ):
        return "zh-tw"

    # Use langdetect for other languages
    return detect(text)

# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

INPUT_FILE = Path("data/processed/exa_news_cleaned.json")
OUTPUT_FILE = Path("data/processed/news_sentiment.json")


# --------------------------------------------------
# 2. MODEL CONFIGURATION
# --------------------------------------------------

MODEL_NAME = "Kenpache/finbert-multilingual-v2"

# Languages supported by our current model
SUPPORTED_LANGUAGES = {"en", "zh-cn", "zh-tw"}


# --------------------------------------------------
# 3. LOAD NEWS ARTICLES
# --------------------------------------------------

with INPUT_FILE.open("r", encoding="utf-8") as file:
    articles = json.load(file)

print("Total news articles:", len(articles))


# --------------------------------------------------
# 4. LOAD SENTIMENT MODEL
# --------------------------------------------------

print("\nLoading financial sentiment model...")

classifier = pipeline(
    "text-classification",
    model=MODEL_NAME,
    device=-1
)

print("Model loaded successfully!")


# --------------------------------------------------
# 5. DETECT LANGUAGES AND PREPARE ARTICLES
# --------------------------------------------------

results = []
articles_to_analyze = []
texts_to_analyze = []

for article in articles:

    # Combine headline and article content
    text = (
        article.get("title", "") + "\n" +
        article.get("text", "")
    ).strip()

    # Detect language
    try:
        language = detect_language(text)
    except Exception:
        language = "unknown"

    # Prepare common output information
    result = {
        "news_id": article["news_id"],
        "ticker": article["ticker"],
        "company": article["company"],
        "exchange": article["exchange"],
        "title": article["title"],
        "published_date_utc": article["published_date_utc"],
        "language": language,
    }

    # Skip unsupported languages
    if language not in SUPPORTED_LANGUAGES:

        result.update({
            "status": "skipped_unsupported_language",
            "sentiment": None,
            "positive_score": None,
            "neutral_score": None,
            "negative_score": None,
            "sentiment_score": None,
        })

        results.append(result)
        continue

    # Save supported articles for batch prediction
    articles_to_analyze.append(result)
    texts_to_analyze.append(text)


# --------------------------------------------------
# 6. PREDICT SENTIMENT
# --------------------------------------------------

print("\nAnalysing supported articles...")

if texts_to_analyze:

    predictions = classifier(
        texts_to_analyze,
        top_k=None,
        truncation=True,
        max_length=512,
        batch_size=4
    )

    for article, prediction in zip(
        articles_to_analyze,
        predictions
    ):

        # Convert model output into a dictionary
        scores = {
            item["label"].lower(): item["score"]
            for item in prediction
        }

        positive = scores["positive"]
        neutral = scores["neutral"]
        negative = scores["negative"]

        # Calculate numerical sentiment
        sentiment_score = positive - negative

        # Find strongest sentiment
        sentiment = max(
            scores,
            key=scores.get
        )

        article.update({
            "status": "analyzed",
            "sentiment": sentiment,
            "positive_score": round(positive, 4),
            "neutral_score": round(neutral, 4),
            "negative_score": round(negative, 4),
            "sentiment_score": round(sentiment_score, 4),
        })

        results.append(article)


# --------------------------------------------------
# 7. SAVE RESULTS
# --------------------------------------------------

# Keep original news order
results.sort(key=lambda item: item["news_id"])

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    json.dump(
        results,
        file,
        indent=4,
        ensure_ascii=False
    )


# --------------------------------------------------
# 8. PRINT SUMMARY
# --------------------------------------------------

status_counts = Counter(
    article["status"] for article in results
)

ticker_counts = Counter(
    article["ticker"]
    for article in results
    if article["status"] == "analyzed"
)

print("\n========== NEWS SENTIMENT REPORT ==========")

print("Total articles:", len(results))
print("Successfully analysed:", status_counts["analyzed"])
print(
    "Skipped unsupported language:",
    status_counts["skipped_unsupported_language"]
)

print("\nAnalysed articles per ticker:")

for ticker, count in sorted(ticker_counts.items()):
    print(ticker, ":", count)

print("\nSaved to:", OUTPUT_FILE)

print("============================================")
