import re
import json
from pathlib import Path


from transformers import pipeline




INPUT_FILE = Path("data/processed/lihkg_cleaned.json")
OUTPUT_FILE = Path("data/processed/lihkg_sentiment.json")

MODEL_NAME = "Kenpache/finbert-multilingual-v2"

SUPPORTED_LANGUAGES = {"en", "zh-cn", "zh-tw"}

# Replies shorter than 3 characters are skipped
MIN_TEXT_LENGTH = 3


def build_analysis_text(record):
    """
    Original threads: analyse title + text.
    Replies: analyse only their own text.
    """

    text = (record.get("text") or "").strip()

    if record.get("record_type") == "thread":
        title = (record.get("title") or "").strip()
        return f"{title}. {text}".strip()

    return text


def detect_lihkg_language(text):
    """
    Estimate language using the text and known LIHKG source context.
    LIHKG discussions in this dataset are predominantly Cantonese/
    Traditional Chinese.
    """

    # Remove URLs so website addresses don't affect language detection
    text = re.sub(r"https?://\S+", "", text)

    # Count Chinese characters
    chinese_count = sum(
        1 for char in text
        if "\u4e00" <= char <= "\u9fff"
    )

    # Count English alphabet characters
    english_count = sum(
        1 for char in text
        if ("a" <= char.lower() <= "z")
    )

    if chinese_count >= 3 and chinese_count >= english_count:
        return "zh-tw"

    if english_count >= 3 and english_count > chinese_count:
        return "en"

    return None


def analyse_lihkg_posts():

    # 1. Load cleaned LIHKG records
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    print("Total LIHKG records:", len(records))

    # 2. Load the financial sentiment model
    print("\nLoading financial sentiment model...")

    classifier = pipeline(
        "text-classification",
        model=MODEL_NAME,
        device=-1
    )

    print("Model loaded successfully!")

    results = []
    texts_to_analyse = []
    records_to_analyse = []

    # 3. Prepare records and detect languages
    for record in records:

        analysis_text = build_analysis_text(record)

        result = record.copy()
        result["analysis_text"] = analysis_text

        if len(analysis_text.strip()) < MIN_TEXT_LENGTH:
            result["language"] = None
            result["status"] = "skipped_short_text"
            result["sentiment"] = None
            result["sentiment_score"] = None
            result["positive_probability"] = None
            result["negative_probability"] = None
            result["neutral_probability"] = None

            results.append(result)
            continue

        language = detect_lihkg_language(analysis_text)

        result["language"] = language
        result["language_detection_method"] = "source_context_heuristic"

        if language not in SUPPORTED_LANGUAGES:
            result["status"] = "skipped_unsupported_language"
            result["sentiment"] = None
            result["sentiment_score"] = None
            result["positive_probability"] = None
            result["negative_probability"] = None
            result["neutral_probability"] = None

            results.append(result)
            continue

        texts_to_analyse.append(analysis_text)
        records_to_analyse.append(result)

    # 4. Analyse supported records in batches
    print("\nAnalysing supported LIHKG posts...")

    if texts_to_analyse:

        predictions = classifier(
            texts_to_analyse,
            top_k=None,
            truncation=True,
            max_length=512,
            batch_size=4
        )

        for record, prediction in zip(records_to_analyse, predictions):

            scores = {
                item["label"].lower(): float(item["score"])
                for item in prediction
            }

            positive = scores.get("positive", 0.0)
            negative = scores.get("negative", 0.0)
            neutral = scores.get("neutral", 0.0)

            sentiment_score = positive - negative

            sentiment = max(scores, key=scores.get)

            record["status"] = "analyzed"
            record["sentiment"] = sentiment
            record["sentiment_score"] = round(
                sentiment_score, 4
            )
            record["positive_probability"] = round(positive, 4)
            record["negative_probability"] = round(negative, 4)
            record["neutral_probability"] = round(neutral, 4)

            results.append(record)

    # 5. Save all results
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    # 6. Display summary
    analysed = [
        item for item in results
        if item.get("status") == "analyzed"
    ]

    skipped_short = sum(
        1 for item in results
        if item.get("status") == "skipped_short_text"
    )

    skipped_language = sum(
        1 for item in results
        if item.get("status") == "skipped_unsupported_language"
    )

    print("\n========== LIHKG SENTIMENT REPORT ==========")
    print("Total records:", len(results))
    print("Successfully analysed:", len(analysed))
    print("Skipped short text:", skipped_short)
    print("Skipped unsupported language:", skipped_language)

    print("\nSentiment counts:")

    for sentiment in ["positive", "negative", "neutral"]:
        count = sum(
            1 for item in analysed
            if item.get("sentiment") == sentiment
        )
        print(f"{sentiment.capitalize()}: {count}")

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    analyse_lihkg_posts()

