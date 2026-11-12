
import json
from pathlib import Path

import pandas as pd


PRICE_FOLDER = Path("data/raw/stock_prices")
OUTPUT_FILE = Path("data/processed/model_dataset.csv")

SOURCES = {
    "Naver": {
        "file": "data/processed/naver_sentiment.json",
        "timestamp": "timestamp_utc",
        "score": "sentiment_score",
    },
    "LIHKG": {
        "file": "data/processed/lihkg_sentiment.json",
        "timestamp": "timestamp_utc",
        "score": "sentiment_score",
    },
    "News": {
        "file": "data/processed/news_sentiment.json",
        "timestamp": "published_date_utc",
        "score": "sentiment_score",
    },
}


def load_sentiment():
    """Load analyzed sentiment records from all sources."""

    events = {source: [] for source in SOURCES}

    for source, config in SOURCES.items():
        with open(config["file"], "r", encoding="utf-8") as file:
            records = json.load(file)

        for record in records:
            # Ignore records that were not successfully analyzed.
            if record.get("status", "analyzed") != "analyzed":
                continue

            score = record.get(config["score"])

            if score is None:
                continue

            ticker = record.get("ticker")

            # Naver tickers need the Yahoo Finance suffix.
            if source == "Naver" and ticker:
                ticker = f"{ticker}.KS"

            events[source].append({
                "ticker": ticker,
                "exchange": record.get("exchange"),
                "timestamp": pd.to_datetime(
                    record[config["timestamp"]], utc=True
                ),
                "score": float(score),
            })

    return events


def build_stock_dataset(price_file, events):
    """Combine one stock's prices with available sentiment."""

    prices = pd.read_csv(price_file)

    ticker = prices["ticker"].iloc[0]
    exchange = prices["exchange"].iloc[0]

    if exchange == "Hong Kong":
        timezone = "Asia/Hong_Kong"
        market_close = "16:00"
    else:
        timezone = "Asia/Seoul"
        market_close = "15:30"

    # Convert price timestamps into local exchange dates.
    prices["timestamp"] = pd.to_datetime(
        prices["timestamp"], utc=True
    )

    prices["date"] = (
        prices["timestamp"]
        .dt.tz_convert(timezone)
        .dt.date
    )

    trading_dates = sorted(prices["date"].unique())

    # Prepare sentiment buckets for each source and trading date.
    sentiment_values = {
        source: {date: [] for date in trading_dates}
        for source in SOURCES
    }

    future_events = {source: 0 for source in SOURCES}

    for source, source_events in events.items():

        for event in source_events:

            # Match ticker-specific sources to the correct stock.
            if source != "LIHKG" and event["ticker"] != ticker:
                continue

            # LIHKG is market-level, so it applies to HK stocks only.
            if source == "LIHKG" and exchange != "Hong Kong":
                continue

            local_timestamp = event["timestamp"].tz_convert(timezone)

            # Assign sentiment to the latest trading date
            # on or before its local publication date.
            local_date = local_timestamp.date()

            previous_sessions = [
                date for date in trading_dates
                if date <= local_date
            ]

            if previous_sessions:
                assigned_date = previous_sessions[-1]
            else:
                assigned_date = trading_dates[0]

            sentiment_values[source][assigned_date].append(
                event["score"]
            )

    # Create daily sentiment features.
    for source in SOURCES:
        prices[f"{source.lower()}_sentiment"] = prices["date"].map(
            lambda date: (
                sum(sentiment_values[source][date])
                / len(sentiment_values[source][date])
                if sentiment_values[source][date]
                else float("nan")
            )
        )

        prices[f"{source.lower()}_count"] = prices["date"].map(
            lambda date: len(sentiment_values[source][date])
        )

    # Price-based features.
    prices["previous_day_return"] = prices["Close"].pct_change()

    # Prediction target: the next available trading session.
    prices["target_next_date"] = prices["date"].shift(-1)
    prices["target_next_close"] = prices["Close"].shift(-1)

    prices["target_next_return"] = (
        prices["target_next_close"] / prices["Close"] - 1
    )

    prices["sentiment_source_count"] = (
        (prices["naver_count"] > 0).astype(int)
        + (prices["lihkg_count"] > 0).astype(int)
        + (prices["news_count"] > 0).astype(int)
    )

    columns = [
        "date",
        "target_next_date",
        "ticker",
        "company",
        "exchange",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "previous_day_return",
        "naver_sentiment",
        "naver_count",
        "lihkg_sentiment",
        "lihkg_count",
        "news_sentiment",
        "news_count",
        "sentiment_source_count",
        "target_next_close",
        "target_next_return",
    ]

    result = prices[columns].copy()

    print(
        f"{ticker}: {len(result)} rows | "
        f"Dates with sentiment: "
        f"{(result['sentiment_source_count'] > 0).sum()}"
    )

    for source, count in future_events.items():
        if count:
            print(f"  {source} events after latest available session: {count}")

    return result


def main():
    print("Loading sentiment data...")
    events = load_sentiment()

    all_datasets = []

    print("\nBuilding datasets...")

    for price_file in sorted(PRICE_FOLDER.glob("*.csv")):
        dataset = build_stock_dataset(price_file, events)
        all_datasets.append(dataset)

    if not all_datasets:
        print("No stock price files found!")
        return

    final_dataset = pd.concat(all_datasets, ignore_index=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    final_dataset.to_csv(OUTPUT_FILE, index=False)

    print("\n========== DATASET SUMMARY ==========")
    print("Total rows:", len(final_dataset))
    print("Total stocks:", final_dataset["ticker"].nunique())
    print(
        "Rows with at least one sentiment source:",
        (final_dataset["sentiment_source_count"] > 0).sum(),
    )
    print(
        "Rows with prediction targets:",
        final_dataset["target_next_close"].notna().sum(),
    )
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
