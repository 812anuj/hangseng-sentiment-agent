
import json
from collections import defaultdict
from pathlib import Path


# Input and output files
INPUT_FILE = Path("data/processed/news_sentiment.json")
OUTPUT_FILE = Path("data/processed/news_sentiment_summary.json")


def aggregate_news_sentiment():

    # 1. Read the sentiment analysis results
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        articles = json.load(file)

    # 2. Group articles by stock ticker
    grouped_articles = defaultdict(list)

    for article in articles:
        ticker = article.get("ticker")

        if ticker:
            grouped_articles[ticker].append(article)

    # 3. Create a summary for every ticker
    summaries = []

    for ticker, ticker_articles in grouped_articles.items():

        # Keep only successfully analysed articles
        analysed = [
            article
            for article in ticker_articles
            if article.get("status") == "analyzed"
            and article.get("sentiment_score") is not None
        ]

        # Count articles that were not analysed
        skipped_count = len(ticker_articles) - len(analysed)

        # Count positive, negative and neutral articles
        sentiment_counts = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }

        scores = []

        for article in analysed:

            sentiment = article.get("sentiment")

            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1

            scores.append(float(article["sentiment_score"]))

        # Calculate average sentiment score
        if scores:
            average_score = sum(scores) / len(scores)
        else:
            average_score = None

        # Get company and exchange information
        first_article = ticker_articles[0]

        summary = {
            "ticker": ticker,
            "company": first_article.get("company"),
            "exchange": first_article.get("exchange"),
            "total_articles": len(ticker_articles),
            "analysed_articles": len(analysed),
            "skipped_articles": skipped_count,
            "positive_count": sentiment_counts["positive"],
            "negative_count": sentiment_counts["negative"],
            "neutral_count": sentiment_counts["neutral"],
            "average_sentiment_score": (
                round(average_score, 4)
                if average_score is not None
                else None
            )
        }

        summaries.append(summary)

    # 4. Sort summaries by ticker
    summaries.sort(key=lambda item: item["ticker"])

    # 5. Save the final summary
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(summaries, file, indent=4, ensure_ascii=False)

    # 6. Display the report
    print("\n========== NEWS SENTIMENT SUMMARY ==========")

    for summary in summaries:
        print(
            f"\n{summary['ticker']} | {summary['company']}"
        )
        print("Total articles:", summary["total_articles"])
        print("Analysed:", summary["analysed_articles"])
        print("Skipped:", summary["skipped_articles"])
        print("Positive:", summary["positive_count"])
        print("Negative:", summary["negative_count"])
        print("Neutral:", summary["neutral_count"])
        print(
            "Average sentiment score:",
            summary["average_sentiment_score"]
        )

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    aggregate_news_sentiment()
