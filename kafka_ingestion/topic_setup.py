from __future__ import annotations

from kafka import KafkaAdminClient
from kafka.admin import NewTopic

from config.settings import KAFKA_BROKER, KAFKA_TOPIC


def ensure_topic(topic_name: str = KAFKA_TOPIC, bootstrap_servers: str = KAFKA_BROKER, partitions: int = 1, replication_factor: int = 1):
    admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id="smart-building-energy")
    topics = admin.list_topics()
    if topic_name in topics:
        return True
    admin.create_topics([NewTopic(name=topic_name, num_partitions=partitions, replication_factor=replication_factor)])
    return True
