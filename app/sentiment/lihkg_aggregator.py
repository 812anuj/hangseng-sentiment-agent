
import json
from pathlib import Path
from collections import Counter

INPUT_FILE = Path("data/processed/lihkg_sentiment.json")
OUTPUT_FILE = Path("data/processed/lihkg_sentiment_summary.json")


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    analysed = [
        record for record in records
        if record["status"] == "analyzed"
    ]

    skipped = len(records) - len(analysed)

    sentiment_counts = Counter(
        record["sentiment"] for record in analysed
    )

    scores = [
        record["sentiment_score"]
        for record in analysed
        if record["sentiment_score"] is not None
    ]

    average_score = (
        sum(scores) / len(scores) if scores else 0
    )

    summary = {
        "source": "LIHKG",
        "exchange": "Hong Kong",
        "asset_scope": "market",
        "total_records": len(records),
        "analysed_records": len(analysed),
        "skipped_records": skipped,
        "positive": sentiment_counts["positive"],
        "negative": sentiment_counts["negative"],
        "neutral": sentiment_counts["neutral"],
        "average_sentiment_score": round(average_score, 4),
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=4)

    print("\n========== LIHKG SENTIMENT SUMMARY ==========")
    for key, value in summary.items():
        print(f"{key}: {value}")

    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
