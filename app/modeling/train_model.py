
import pandas as pd
import numpy as np

from pathlib import Path

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Dataset location
DATASET_PATH = BASE_DIR / "data" / "processed" / "model_dataset.csv"


def load_dataset():
    """Load and prepare the stock sentiment dataset."""

    print("Loading dataset...")

    df = pd.read_csv(DATASET_PATH)

    print(f"Total rows loaded: {len(df)}")

    # Convert date columns into datetime format
    df["date"] = pd.to_datetime(df["date"])
    df["target_next_date"] = pd.to_datetime(df["target_next_date"])

    # Remove rows where the next-day target is unavailable
    df = df.dropna(subset=["target_next_return"])

    print(f"Rows with known next-day targets: {len(df)}")

    return df


def prepare_features(df):
    """Prepare input features and target for machine learning."""

    feature_columns = [
        "previous_day_return",
        "naver_sentiment",
        "naver_count",
        "lihkg_sentiment",
        "lihkg_count",
        "news_sentiment",
        "news_count",
    ]

    # Keep only the required columns
    X = df[feature_columns].copy()

    # Replace missing sentiment values with zero
    X = X.fillna(0)

    # Actual next-day return that the model must predict
    y = df["target_next_return"]

    return X, y



def chronological_split(df, test_ratio=0.3):
    """Split sentiment-bearing data chronologically."""

    # Keep rows with at least one sentiment source
    sentiment_df = df[
        (df["naver_count"] > 0) |
        (df["lihkg_count"] > 0) |
        (df["news_count"] > 0)
    ].copy()

    # Get unique dates in chronological order
    unique_dates = sorted(sentiment_df["date"].unique())

    # Keep earlier dates for training and later dates for testing
    split_index = int(len(unique_dates) * (1 - test_ratio))

    train_dates = unique_dates[:split_index]
    test_dates = unique_dates[split_index:]

    train_df = sentiment_df[
        sentiment_df["date"].isin(train_dates)
    ].copy()

    test_df = sentiment_df[
        sentiment_df["date"].isin(test_dates)
    ].copy()

    print("\n========== SENTIMENT DATA SPLIT ==========")
    print(f"Total sentiment rows: {len(sentiment_df)}")
    print(f"Training rows: {len(train_df)}")
    print(f"Testing rows: {len(test_df)}")
    print(f"Training dates: {train_df['date'].min().date()} to {train_df['date'].max().date()}")
    print(f"Testing dates: {test_df['date'].min().date()} to {test_df['date'].max().date()}")

    return train_df, test_df



def train_baseline_model(train_df, test_df):
    """Train a price-only baseline model."""

    print("\n========== BASELINE MODEL ==========")

    # Use only previous day's return
    X_train = train_df[["previous_day_return"]]
    y_train = train_df["target_next_return"]

    X_test = test_df[["previous_day_return"]]
    y_test = test_df["target_next_return"]

    # Create and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predict next-day returns
    predictions = model.predict(X_test)

    # Evaluate predictions
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    # Check whether the predicted direction matches the actual direction
    direction_accuracy = np.mean(
        np.sign(predictions) == np.sign(y_test)
    ) * 100

    print(f"MAE: {mae:.6f}")
    print(f"RMSE: {rmse:.6f}")
    print(f"Direction Accuracy: {direction_accuracy:.2f}%")

    return model, predictions


def train_sentiment_model(train_df, test_df):
    """Train a model using price and sentiment features."""

    print("\n========== SENTIMENT MODEL ==========")

    # Prepare training features
    X_train, y_train = prepare_features(train_df)

    # Prepare testing features
    X_test, y_test = prepare_features(test_df)

    # Create and train the model
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)

    # Predict next-day returns
    predictions = model.predict(X_test)

    # Evaluate predictions
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    direction_accuracy = np.mean(
        np.sign(predictions) == np.sign(y_test)
    ) * 100

    print(f"MAE: {mae:.6f}")
    print(f"RMSE: {rmse:.6f}")
    print(f"Direction Accuracy: {direction_accuracy:.2f}%")

    return model, predictions


def prepare_features_for_prediction(df):
    feature_columns = [
        "previous_day_return",
        "naver_sentiment",
        "naver_count",
        "lihkg_sentiment",
        "lihkg_count",
        "news_sentiment",
        "news_count",
    ]

    X = df[feature_columns].copy()
    X = X.fillna(0)

    return X, None



def prepare_features_for_prediction(df):
    """Prepare features when actual next-day targets are unavailable."""

    feature_columns = [
        "previous_day_return",
        "naver_sentiment",
        "naver_count",
        "lihkg_sentiment",
        "lihkg_count",
        "news_sentiment",
        "news_count",
    ]

    X = df[feature_columns].copy()
    X = X.fillna(0)

    return X


def generate_predictions(df, model):
    """Predict the next trading day's closing price."""

    print("\n========== NEXT-DAY PREDICTIONS ==========")

    # Get the latest row for each stock
    latest_rows = (
        df.sort_values("date")
        .groupby("ticker")
        .tail(1)
        .copy()
    )

    X = prepare_features_for_prediction(latest_rows)

    # Predict next-day returns
    latest_rows["predicted_next_return"] = model.predict(X)

    # Calculate estimated next-day closing prices
    latest_rows["predicted_next_close"] = (
        latest_rows["Close"] *
        (1 + latest_rows["predicted_next_return"])
    )

    for _, row in latest_rows.iterrows():
        direction = (
            "UP" if row["predicted_next_return"] > 0
            else "DOWN" if row["predicted_next_return"] < 0
            else "NEUTRAL"
        )

        print(
            f"{row['ticker']} | "
            f"Current: {row['Close']:.2f} | "
            f"Predicted: {row['predicted_next_close']:.2f} | "
            f"Direction: {direction}"
        )

    # Save predictions
    output_path = BASE_DIR / "data" / "processed" / "next_day_predictions.csv"

    latest_rows.to_csv(output_path, index=False)

    print(f"\nPredictions saved to: {output_path}")

    return latest_rows



if __name__ == "__main__":

    # Load complete dataset
    df = load_dataset()

    # Keep a separate copy of rows with known targets
    labeled_df = df.dropna(subset=["target_next_return"]).copy()

    # Split historical sentiment data
    train_df, test_df = chronological_split(labeled_df)

    if train_df.empty or test_df.empty:
        raise ValueError("Not enough data for training and testing.")

    # Evaluate baseline model
    train_baseline_model(train_df, test_df)

    # Evaluate sentiment model
    train_sentiment_model(train_df, test_df)

    # Train final sentiment model using all available labeled data
    X_all, y_all = prepare_features(labeled_df)

    final_model = Ridge(alpha=1.0)
    final_model.fit(X_all, y_all)

    # Predict using the latest available rows
    predictions = generate_predictions(df, final_model)

    print("\n========== PIPELINE COMPLETED ==========")
