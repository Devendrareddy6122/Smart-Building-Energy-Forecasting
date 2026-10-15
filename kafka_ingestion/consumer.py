from __future__ import annotations

import json
import logging

from kafka import KafkaConsumer

from config.settings import KAFKA_BROKER, KAFKA_TOPIC

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
