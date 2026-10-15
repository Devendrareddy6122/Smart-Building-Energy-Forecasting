from __future__ import annotations

import pandas as pd

from preprocessing.clean_data import preprocess_power_data
from storage.local_storage import LocalStorage


def main() -> None:
    storage = LocalStorage("./data")
    raw_path = storage.base_dir / "raw" / "household_power_consumption.txt"
    if not raw_path.exists():
        raise FileNotFoundError(f"Dataset not found at {raw_path}. Run the dataset download script first.")

    df = pd.read_csv(raw_path, sep=";", low_memory=False)
    prepared = preprocess_power_data(df)
    storage.save_csv(prepared, "processed/hourly_consumption.csv")
    print(f"Saved {len(prepared)} hourly records to {storage.base_dir / 'processed' / 'hourly_consumption.csv'}")


if __name__ == "__main__":
    main()
