
import yfinance as yf
import pandas as pd

from pathlib import Path
from app.config.assets import ASSETS


DATA_FOLDER = Path("data/raw/stock_prices")


def fetch_stock_prices():

    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    for exchange, stocks in ASSETS.items():

        print(f"\n========== {exchange} ==========")

        for ticker, company in stocks.items():

            try:
                print(f"\nFetching {company} ({ticker})")

                stock = yf.Ticker(ticker)

                df = stock.history(
                    period="1y",
                    interval="1d",
                    auto_adjust=True
                )

                if df.empty:
                    print("No data available!")
                    continue

                df = df.reset_index()

                df = df.rename(
                    columns={df.columns[0]: "timestamp"}
                )

                df["ticker"] = ticker
                df["company"] = company
                df["exchange"] = exchange

                file_path = DATA_FOLDER / f"{ticker}.csv"

                df.to_csv(file_path, index=False)

                latest_price = df["Close"].iloc[-1]

                print(f"Latest close: {latest_price:.2f}")
                print(f"Records collected: {len(df)}")
                print(f"Latest date: {df['timestamp'].iloc[-1]}")
                print(f"Saved to: {file_path}")

            except Exception as error:
                print(f"Error fetching {ticker}: {error}")


if __name__ == "__main__":
    fetch_stock_prices()
