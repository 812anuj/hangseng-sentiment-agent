from pathlib import Path
import pandas as pd

DATA_FOLDER = Path("data/raw/stock_prices")

def validation_stock_data():
    csv_files = list(DATA_FOLDER.glob("*.csv"))
    print(f"Number of CSV files: {len(csv_files)}")

    for file_path in csv_files:
        print("\n" + "=" * 45)
        print(f"checking {file_path.name}")

        df = pd.read_csv(file_path)

        missing_values = df.isnull().sum().sum()
        dublicate_date = df['timestamp'].duplicated().sum()

        print(f'total records: {len(df)}')       
        print(f'missing values: {missing_values}')
        print(f"dublicate date: {dublicate_date}")

        if missing_values == 0 and dublicate_date == 0:
            print("status: Passed")
        else:
            print("status: NEEDS ATENTION")

if __name__ == "__main__":
    validation_stock_data()
            