from __future__ import annotations

import importlib.util
import json
import logging
import sysconfig
from pathlib import Path

from config.settings import KAFKA_BROKER, KAFKA_TOPIC


def _load_kafka_python():
    project_root = Path(__file__).resolve().parent.parent
    candidate_path = None
    for entry in __import__("sys").path:
        if not entry:
            continue
        base = Path(entry)
        candidate = base / "kafka" / "__init__.py"
        if candidate.exists() and base != project_root:
            candidate_path = candidate
            break
    if candidate_path is None:
        raise ImportError("The kafka-python package is not installed.")

    package_dir = candidate_path.parent
    spec = importlib.util.spec_from_file_location("kafka", candidate_path, submodule_search_locations=[str(package_dir)])
    module = importlib.util.module_from_spec(spec)
    old_kafka = __import__("sys").modules.get("kafka")
    __import__("sys").modules["kafka"] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if old_kafka is not None:
            __import__("sys").modules["kafka"] = old_kafka
        else:
            __import__("sys").modules.pop("kafka", None)
    return module


KafkaConsumer = _load_kafka_python().KafkaConsumer

logger = logging.getLogger(__name__)


class SmartMeterConsumer:
    def __init__(self, bootstrap_servers: str | None = None, topic: str | None = None):
        self.bootstrap_servers = bootstrap_servers or KAFKA_BROKER
        self.topic = topic or KAFKA_TOPIC
        self.consumer = None

    def connect(self):
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )
            logger.info("Kafka consumer connected to %s", self.bootstrap_servers)
            return True
        except Exception as exc:  # pragma: no cover
            logger.warning("Kafka consumer failed to connect: %s", exc)
            return False

    def read_messages(self, max_messages: int = 10):
        if self.consumer is None:
            self.connect()
        if self.consumer is None:
            raise ConnectionError("Kafka consumer is not connected.")

        messages = []
        for message in self.consumer:
            messages.append(message.value)
            if len(messages) >= max_messages:
                break
        return messages

    @staticmethod
    def validate_message(message: dict) -> bool:
        if not isinstance(message, dict):
            return False
        required = {"building_id", "timestamp", "active_power"}
        if not required.issubset(message.keys()):
            return False
        return True
