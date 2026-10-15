from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from config.settings import get_local_data_dir


class LocalStorage:
    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir) if base_dir else get_local_data_dir()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def ensure_dir(self, *parts: str) -> Path:
        path = self.base_dir.joinpath(*parts)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_csv(self, df: pd.DataFrame, relative_path: str) -> Path:
        path = self.base_dir.joinpath(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return path

    def save_parquet(self, df: pd.DataFrame, relative_path: str) -> Path:
        path = self.base_dir.joinpath(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, index=False)
        return path

    def save_json(self, payload: dict, relative_path: str) -> Path:
        path = self.base_dir.joinpath(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        return path

    def read_csv(self, relative_path: str) -> pd.DataFrame:
        path = self.base_dir.joinpath(relative_path)
        if not path.exists():
            return pd.DataFrame()
        return pd.read_csv(path)
