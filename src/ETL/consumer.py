import json
from typing import Dict, Any, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError


def create_consumer(
    topic: str = "huydepzai",
    group_id: str = "de-consumer-group",
    bootstrap_servers: list = None,
    auto_offset_reset: str = "earliest",
    enable_auto_commit: bool = True
) -> KafkaConsumer:
    if bootstrap_servers is None:
        bootstrap_servers = ["localhost:9092"]
    
    try:
        consumer = KafkaConsumer(
            topic,
            group_id=group_id,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=enable_auto_commit,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")) if x else None,
            key_deserializer=lambda x: x.decode("utf-8") if x else None
        )
        print(f"Kafka consumer created for topic: {topic}, group: {group_id}")
        return consumer
    except Exception as e:
        print(f"Failed to create Kafka consumer: {e}")
        raise


def process_message(message: Any, topic_partition: Any) -> Optional[Dict[str, Any]]:
    try:
        message_data = {
            "topic": topic_partition.topic,
            "partition": topic_partition.partition,
            "offset": message.offset,
            "key": message.key,
            "value": message.value,
            "timestamp": message.timestamp
        }
        return message_data
    except Exception as e:
        print(f"Error processing message: {e}")
        return None


def consume_messages(consumer: KafkaConsumer, timeout_ms: int = 500):
    print("Starting to consume messages from Kafka")
    
    try:
        while True:
            try:
                msg_pack = consumer.poll(timeout_ms=timeout_ms)
                
                if not msg_pack:
                    continue
                
                for topic_partition, messages in msg_pack.items():
                    for message in messages:
                        message_data = process_message(message, topic_partition)
                        if message_data:
                            print(
                                f"Message received - Topic: {message_data['topic']}, "
                                f"Partition: {message_data['partition']}, "
                                f"Offset: {message_data['offset']}, "
                                f"Key: {message_data['key']}"
                            )
                            if message_data['value']:
                                print(f"Message value: {message_data['value']}")
                            
            except KafkaError as e:
                print(f"Kafka error while consuming: {e}")
                raise
            except Exception as e:
                print(f"Unexpected error while consuming: {e}")
                continue
                
    except KeyboardInterrupt:
        print("Consumer interrupted by user")
    except Exception as e:
        print(f"Fatal error in consumer: {e}")
        raise
    finally:
        consumer.close()
        print("Kafka consumer closed")


def main():
    try:
        consumer = create_consumer()
        consume_messages(consumer)
    except Exception as e:
        print(f"Failed to start consumer: {e}")
        raise


if __name__ == "__main__":
    main()
