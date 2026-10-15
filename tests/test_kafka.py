from kafka_ingestion.consumer import SmartMeterConsumer


def test_kafka_message_validation():
    valid = {"building_id": "B001", "timestamp": "2026-10-14T10:00:00", "active_power": 245.6}
    invalid = {"building_id": "B001", "timestamp": "2026-10-14T10:00:00"}

    assert SmartMeterConsumer.validate_message(valid) is True
    assert SmartMeterConsumer.validate_message(invalid) is False
