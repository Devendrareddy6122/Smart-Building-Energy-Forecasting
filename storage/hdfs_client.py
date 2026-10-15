from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class HDFSClient:
    def __init__(self, url: str | None = None, fallback_root: str | Path | None = None):
        self.url = url or "hdfs://localhost:9000"
        self.fallback_root = Path(fallback_root) if fallback_root else Path("./data")
        self.hdfs = None

    def connect(self):
        try:
            from hdfs import InsecureClient

            self.hdfs = InsecureClient(self.url, user="hdfs")
            logger.info("Connected to HDFS at %s", self.url)
            return True
        except Exception as exc:  # pragma: no cover - depends on external service
            logger.warning("HDFS unavailable at %s: %s", self.url, exc)
            self.hdfs = None
            return False

    def write_csv(self, df: pd.DataFrame, remote_path: str) -> str:
        if self.hdfs is not None:
            local_path = self.fallback_root / "tmp_hdfs.csv"
            df.to_csv(local_path, index=False)
            self.hdfs.upload(remote_path, str(local_path), overwrite=True)
            return remote_path
        local_path = self.fallback_root / remote_path.lstrip("/")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(local_path, index=False)
        return str(local_path)

    def read_csv(self, remote_path: str) -> pd.DataFrame:
        if self.hdfs is not None:
            try:
                return pd.read_csv(remote_path)
            except Exception as exc:  # pragma: no cover
                logger.warning("Unable to read HDFS path %s: %s", remote_path, exc)
                return pd.DataFrame()
        local_path = self.fallback_root / remote_path.lstrip("/")
        if local_path.exists():
            return pd.read_csv(local_path)
        return pd.DataFrame()
