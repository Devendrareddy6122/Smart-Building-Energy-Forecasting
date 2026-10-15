import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_NAME = "smart-building-energy-forecasting"

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "smart-meter-readings")
HDFS_URL = os.getenv("HDFS_URL", "hdfs://localhost:9000")
LOCAL_STORAGE_PATH = Path(os.getenv("LOCAL_STORAGE_PATH", BASE_DIR / "data" / "processed"))
DATASET_URL = os.getenv(
    "DATASET_URL",
    "https://archive.ics.uci.edu/static/public/235/individual+household+electric+power+consumption.zip",
)


def get_local_data_dir() -> Path:
    return LOCAL_STORAGE_PATH
