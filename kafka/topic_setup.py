from __future__ import annotations

import importlib.util
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


_kafka = _load_kafka_python()
KafkaAdminClient = _kafka.KafkaAdminClient
NewTopic = _kafka.admin.NewTopic


def ensure_topic(topic_name: str = KAFKA_TOPIC, bootstrap_servers: str = KAFKA_BROKER, partitions: int = 1, replication_factor: int = 1):
    admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id="smart-building-energy")
    topics = admin.list_topics()
    if topic_name in topics:
        return True
    admin.create_topics([NewTopic(name=topic_name, num_partitions=partitions, replication_factor=replication_factor)])
    return True
