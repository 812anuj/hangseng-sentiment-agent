# HangSeng Sentiment Price Prediction Agent
     A Python-based sentiment analysis and next-day stock price prediction project that combines social media discussions, financial news, historical stock prices, and machine learning.

## Project Overview

This project explores whether sentiment from social media and financial news can help predict the next trading day's stock price movement.

It covers two exchanges:
    - Hong Kong Stock Exchange (HK)
    - South Korean Stock Exchange (KR)

The pipeline collects market discussions and financial news, analyses sentiment, combines sentiment with historical stock data, trains machine learning models, and generates visual reports.

## Key Features
    - Social media data collection using Apify.
    - Financial news collection using Exa.
    - Sentiment analysis using FinBERT.
    - Historical stock price collection using Yahoo Finance.
    - Data cleaning and normalization.
    - Sentiment-based feature engineering.
    - Next-day price prediction using machine learning.
    - Chronological out-of-sample model evaluation.
    - Support and resistance level calculation.
    - Exchange-wise visual reports.

## Supported Assets

### Hong Kong

    | Ticker  | Company |
    | ------- | ------- |
    | 0005.HK | HSBC    |
    | 0700.HK | Tencent |
    | 1299.HK | AIA     |
    | 3690.HK | Meituan |
    | 9988.HK | Alibaba |

### South Korea

    | Ticker    | Company             |
    | --------- | ------------------- |
    | 000660.KS | SK Hynix            |
    | 005380.KS | Hyundai Motor       |
    | 005930.KS | Samsung Electronics |
    | 035420.KS | NAVER               |
    | 035720.KS | Kakao               |

## Data Sources

    | Source        | Purpose                                 |
    | ------------- | --------------------------------------- |
    | LIHKG         | Hong Kong market-level discussions      |
    | Naver Finance | South Korean stock-specific discussions |
    | Exa           | Financial news collection               |
    | Yahoo Finance | Historical stock prices                 |
    | Apify         | Social media data collection            |

Note: LIHKG sentiment represents overall Hong Kong market discussion and is not ticker-specific. Naver posts are ticker-specific.

## Technology Stack

    - Python
    - Pandas and NumPy
    - Scikit-learn
    - Hugging Face Transformers
    - FinBERT
    - PyTorch
    - Apify
    - Exa
    - yfinance
    - Matplotlib

## Project Workflow

    1. Collect social media posts and financial news.
    2. Normalize and validate collected data.
    3. Analyse sentiment and sentiment confidence.
    4. Collect and process historical stock prices.
    5. Build a dataset combining price and sentiment features.
    6. Train and evaluate machine learning models using chronological data splitting.
    7. Generate next-day predictions.
    8. Create exchange-wise sentiment reports and charts.

## Installation

Clone the repository:

    ```bash
    git clone https://github.com/812anuj/hangseng-sentiment-agent.git
    cd hangseng-sentiment-agent
    ```

    Create a virtual environment:

    ```bash
    python -m venv venv
    ```

Activate it on Windows:

    ```powershell
    venv\Scripts\activate
    ```

    Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Environment Configuration

Create a `.env` file in the project root using `.env.example` as a template.

    Add your own API credentials:

    ```env
    APIFY_API_TOKEN=your_apify_token
    EXA_API_KEY=your_exa_api_key
    ```

## Running the Pipeline

Run the relevant ingestion, normalization, sentiment analysis, and price processing modules in the order required by the project.
Running the Pipeline

Activate your virtual environment before running the project:

.\venv\Scripts\Activate.ps1

1. Data Ingestion

    Run the following modules to collect data from the supported sources:

    # LIHKG social posts
    python -m app.ingestion.social_scraper

    # LIHKG thread details
    python -m app.ingestion.scrape_lihkg_threads

    # Naver Finance posts
    python -m app.ingestion.naver_scraper

    # News articles using Exa
    python -m app.ingestion.news_scraper

    # Historical stock prices
    python -m app.ingestion.stock_prices

2. Data Normalization

    python -m app.ingestion.normalize_lihkg
    python -m app.ingestion.normalize_naver

3. Sentiment Analysis

    # LIHKG sentiment analysis
        python -m app.sentiment.lihkg_analyzer

    # Naver sentiment analysis
        python -m app.sentiment.naver_analyzer

4. Sentiment Aggregation

    python -m app.sentiment.lihkg_aggregator
    python -m app.sentiment.naver_aggregator
    python -m app.sentiment.news_aggregator

5. Data Validation

    python -m app.ingestion.validate_stock_data

    Additional inspection and validation scripts are available in app/ingestion/.

6. Build the model dataset:

    ```bash
    python -m app.processing.build_dataset
    ```

    Train and generate predictions:

    ```bash
    python -m app.modeling.train_model
    ```

    Generate visual reports:

    ```bash
    python -m app.reporting.generate_report
    ```

## Model Evaluation

    The project compares:

    - A baseline Linear Regression model using previous-day return.
    - A Ridge Regression model using sentiment and price-related features.

    The evaluation uses chronological out-of-sample testing to avoid randomly mixing future and past observations.

    Current preliminary evaluation:

    | Metric             | Baseline | Sentiment Model |
    | ------------------ | -------: | --------------: |
    | MAE                |    2.20% |           2.33% |
    | RMSE               |    2.96% |           2.98% |
    | Direction Accuracy |   58.33% |          58.33% |

    The historical dataset contains only 28 rows with sentiment observations and known next-day targets. Therefore, these metrics are preliminary and do not establish that sentiment improves prediction performance.

## Generated Reports

    The project generates:

    - `reports/hong_kong_sentiment.png`
    - `reports/south_korea_sentiment.png`
    - `reports/sentiment_summary.csv`

    Predictions are saved to:

    - `data/processed/next_day_predictions.csv`

    Reports include sentiment direction, mentions, predicted prices, and historical support/resistance levels.

## Limitations
    - Historical sentiment coverage is limited.
    - LIHKG sentiment is market-level rather than ticker-specific.
    - Naver sentiment observations are not sufficiently available across historical training dates.
    - Model evaluation uses a small out-of-sample dataset.
    - Predictions are experimental and should not be treated as financial advice.

## Disclaimer

This project is developed for educational and research purposes. It is not intended to provide financial advice or guarantee future stock market performance.
