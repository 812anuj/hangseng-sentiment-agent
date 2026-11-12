
import json
from pathlib import Path
from collections import defaultdict

INPUT_PATH = Path("data/processed/naver_sentiment.json")
OUTPUT_PATH = Path("data/processed/naver_sentiment_summary.json")

def aggregate_sentiment():
    with INPUT_PATH.open("r", encoding="utf-8") as file:
        posts = json.load(file)

    stock_data = defaultdict(list)

    # Group posts belonging to the same stock
    for post in posts:
        stock_data[post["ticker"]].append(post)

    summaries = []

    for ticker, ticker_posts in stock_data.items():
        positive = sum(
            1 for post in ticker_posts
            if post["sentiment"] == "positive"
        )

        negative = sum(
            1 for post in ticker_posts
            if post["sentiment"] == "negative"
        )

        neutral = sum(
            1 for post in ticker_posts
            if post["sentiment"] == "neutral"
        )

        total = len(ticker_posts)

        average_score = sum(
            post["sentiment_score"] for post in ticker_posts
        ) / total

        summary = {
            "ticker": ticker,
            "company": ticker_posts[0]["company"],
            "exchange": "South Korea",
            "source": "Naver Finance",
            "total_posts": total,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "average_sentiment_score": round(average_score, 4),
            "total_likes": sum(post["likes"] for post in ticker_posts),
            "total_views": sum(post["views"] for post in ticker_posts)
        }

        summaries.append(summary)

    # Sort stocks by number of posts, highest first
    summaries.sort(
        key=lambda item: item["total_posts"],
        reverse=True
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(summaries, file, ensure_ascii=False, indent=4)

    print("\n========== NAVER SENTIMENT SUMMARY ==========")

    for summary in summaries:
        print(
            f"{summary['ticker']} | "
            f"{summary['company']} | "
            f"Posts: {summary['total_posts']} | "
            f"Positive: {summary['positive']} | "
            f"Negative: {summary['negative']} | "
            f"Neutral: {summary['neutral']} | "
            f"Average: {summary['average_sentiment_score']}"
        )

    print("\nSaved to:", OUTPUT_PATH)

if __name__ == "__main__":
    aggregate_sentiment()