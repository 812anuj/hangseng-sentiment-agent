import json
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "processed"


def load_json(filename):
    """Load a JSON file."""

    file_path = DATA_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_predictions():
    """Load next-day stock predictions."""

    file_path = DATA_DIR / "next_day_predictions.csv"

    return pd.read_csv(file_path)


def load_sentiment_data():
    """Load sentiment results from all sources."""

    lihkg = load_json("lihkg_sentiment.json")
    naver = load_json("naver_sentiment.json")
    news = load_json("news_sentiment.json")

    return lihkg, naver, news

def get_sentiment_summary(predictions, lihkg, naver, news):
    """Create a sentiment summary for each stock."""

    rows = []

    for _, stock in predictions.iterrows():

        ticker = stock["ticker"]
        exchange = stock["exchange"]

        # Get news for this particular stock
        stock_news = [
            item for item in news
            if item.get("ticker") == ticker
            and item.get("status") == "analyzed"
        ]

        news_scores = [
            item["sentiment_score"]
            for item in stock_news
            if item.get("sentiment_score") is not None
        ]

        # Get Naver posts for this Korean stock
        stock_naver = [
            item for item in naver
            if str(item.get("ticker")) == ticker.replace(".KS", "")
        ]

        naver_scores = [
            item["sentiment_score"]
            for item in stock_naver
            if item.get("sentiment_score") is not None
        ]

        # LIHKG posts are Hong Kong market-level,
        # not specific to individual stocks.
        lihkg_scores = [
            item["sentiment_score"]
            for item in lihkg
            if item.get("status") == "analyzed"
            and item.get("sentiment_score") is not None
        ] if exchange == "Hong Kong" else []

        scores = []

        scores.extend(news_scores)
        scores.extend(naver_scores)
        scores.extend(lihkg_scores)

        average = sum(scores) / len(scores) if scores else 0

        if average > 0.05:
            direction = "Positive"
        elif average < -0.05:
            direction = "Negative"
        else:
            direction = "Neutral"

        rows.append({
            "ticker": ticker,
            "company": stock["company"],
            "exchange": exchange,
            "current_price": stock["Close"],
            "predicted_price": stock["predicted_next_close"],
            "news_mentions": len(stock_news),
            "naver_mentions": len(stock_naver),
            "lihkg_market_mentions": len(lihkg_scores),
            "average_sentiment": round(average, 4),
            "sentiment_direction": direction
        })

    return pd.DataFrame(rows)

def generate_charts(summary):
    """Generate sentiment charts for each exchange."""

    report_dir = BASE_DIR / "reports"
    report_dir.mkdir(exist_ok=True)

    # Save the complete summary as CSV
    summary.to_csv(
        report_dir / "sentiment_summary.csv",
        index=False
    )

    # Generate one chart for each exchange
    for exchange in ["Hong Kong", "South Korea"]:

        exchange_data = summary[
            summary["exchange"] == exchange
        ]

        plt.figure(figsize=(10, 5))

        plt.bar(
            exchange_data["ticker"],
            exchange_data["average_sentiment"]
        )

        plt.axhline(y=0, linewidth=1)

        plt.title(f"{exchange} - Stock Sentiment")
        plt.xlabel("Stock Ticker")
        plt.ylabel("Average Sentiment Score")

        plt.xticks(rotation=30)
        plt.tight_layout()

        filename = exchange.lower().replace(" ", "_")
        chart_path = report_dir / f"{filename}_sentiment.png"

        plt.savefig(chart_path)
        plt.close()

        print(f"Chart saved: {chart_path}")

def add_support_resistance(summary):
    """Calculate support and resistance from the last 20 sessions."""

    price_dir = BASE_DIR / "data" / "raw" / "stock_prices"

    support_values = []
    resistance_values = []

    for _, stock in summary.iterrows():

        ticker = stock["ticker"]

        file_path = price_dir / f"{ticker}.csv"

        prices = pd.read_csv(file_path)

        # Use the latest 20 trading sessions
        recent_prices = prices.tail(20)

        support = recent_prices["Low"].min()
        resistance = recent_prices["High"].max()

        support_values.append(round(support, 2))
        resistance_values.append(round(resistance, 2))

    summary["support"] = support_values
    summary["resistance"] = resistance_values

    return summary

if __name__ == "__main__":

    predictions = load_predictions()
    lihkg, naver, news = load_sentiment_data()

    print("Prediction records:", len(predictions))
    print("LIHKG records:", len(lihkg))
    print("Naver records:", len(naver))
    print("News records:", len(news))

    print("\nData loaded successfully!")
    summary = get_sentiment_summary(
        predictions, lihkg, naver, news
    )
    summary = add_support_resistance(summary)

    print("\n========== SENTIMENT SUMMARY ==========")
    print(summary.to_string(index=False))
        
    generate_charts(summary)
    print("\nVISUAL REPORT GENERATED SUCCESSFULLY!")