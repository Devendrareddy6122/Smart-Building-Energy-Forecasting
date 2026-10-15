from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

from config.settings import DATASET_URL


def download_dataset(target_dir: str | Path = "./data/raw") -> Path:
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    dataset_path = target / "household_power_consumption.zip"
    response = requests.get(DATASET_URL, timeout=60)
    response.raise_for_status()
    dataset_path.write_bytes(response.content)
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        archive.extractall(target)
    return dataset_path


if __name__ == "__main__":
    result = download_dataset()
    print(f"Downloaded dataset to {result.parent}")
