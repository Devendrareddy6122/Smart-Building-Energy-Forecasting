from __future__ import annotations

import json
import logging
import time
from typing import Iterable

from kafka import KafkaProducer

from config.settings import KAFKA_BROKER, KAFKA_TOPIC

logger = logging.getLogger(__name__)


class SmartMeterProducer:
    def __init__(self, bootstrap_servers: str | None = None, topic: str | None = None):
        self.bootstrap_servers = bootstrap_servers or KAFKA_BROKER
        self.topic = topic or KAFKA_TOPIC
        self.producer = None

    def connect(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                api_version=(0, 10, 2),
            )
            logger.info("Kafka producer connected to %s", self.bootstrap_servers)
            return True
        except Exception as exc:  # pragma: no cover
            logger.warning("Kafka producer failed to connect: %s", exc)
            return False

    def publish_records(self, records: Iterable[dict], delay_seconds: float = 0.0) -> int:
        if self.producer is None:
            self.connect()
        if self.producer is None:
            raise ConnectionError("Kafka producer is not connected.")

        count = 0
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("Each record must be a dictionary.")
            self.producer.send(self.topic, value=record)
            count += 1
            if delay_seconds > 0:
                time.sleep(delay_seconds)
        self.producer.flush()
        return count

    def publish_from_dataframe(self, df, delay_seconds: float = 0.0, building_id: str = "B001") -> int:
        records = []
        for _, row in df.iterrows():
            payload = {
                "building_id": building_id,
                "timestamp": row["timestamp"],
                "active_power": float(row["active_power_kw"]),
            }
            records.append(payload)
        return self.publish_records(records, delay_seconds=delay_seconds)
