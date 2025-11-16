"""
Kafka consumer for processing CDC messages.
Consumes messages from Kafka topics and processes them.
"""
import json
from typing import Dict, Any, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError as KafkaLibError
from src.utils.logger import get_logger
from src.utils.exceptions import KafkaError
from src.utils.constants import KAFKA_TOPIC_CONSUMER, DEFAULT_CONSUMER_GROUP, DEFAULT_POLL_TIMEOUT_MS


logger = get_logger("KafkaConsumer")


def create_consumer(
    topic: str = KAFKA_TOPIC_CONSUMER,
    group_id: str = DEFAULT_CONSUMER_GROUP,
    bootstrap_servers: list = None,
    auto_offset_reset: str = "earliest",
    enable_auto_commit: bool = True
) -> KafkaConsumer:
    """
    Create and configure Kafka consumer.
    
    Args:
        topic: Kafka topic to consume from
        group_id: Consumer group ID
        bootstrap_servers: List of Kafka broker addresses
        auto_offset_reset: Offset reset policy
        enable_auto_commit: Enable automatic offset committing
        
    Returns:
        Configured KafkaConsumer instance
    """
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
        logger.info(f"Kafka consumer created for topic: {topic}, group: {group_id}")
        return consumer
    except Exception as e:
        logger.error(f"Failed to create Kafka consumer: {e}")
        raise KafkaError(f"Failed to create Kafka consumer: {e}") from e


def process_message(message: Any, topic_partition: Any) -> Optional[Dict[str, Any]]:
    """
    Process a single Kafka message.
    
    Args:
        message: Kafka message object
        topic_partition: Topic partition object
        
    Returns:
        Parsed message data or None if error
    """
    try:
        message_data = {
            "topic": topic_partition.topic,
            "partition": topic_partition.partition,
            "offset": message.offset,
            "key": message.key,
            "value": message.value,
            "timestamp": message.timestamp
        }
        logger.debug(f"Processed message from {topic_partition.topic}:{topic_partition.partition} at offset {message.offset}")
        return message_data
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return None


def consume_messages(consumer: KafkaConsumer, timeout_ms: int = DEFAULT_POLL_TIMEOUT_MS) -> None:
    """
    Consume and process messages from Kafka.
    
    Args:
        consumer: KafkaConsumer instance
        timeout_ms: Poll timeout in milliseconds
    """
    logger.info("Starting to consume messages from Kafka")
    
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
                            logger.info(
                                f"Message received - Topic: {message_data['topic']}, "
                                f"Partition: {message_data['partition']}, "
                                f"Offset: {message_data['offset']}, "
                                f"Key: {message_data['key']}"
                            )
                            # Process message value here
                            if message_data['value']:
                                logger.debug(f"Message value: {message_data['value']}")
                            
            except KafkaLibError as e:
                logger.error(f"Kafka error while consuming: {e}")
                raise KafkaError(f"Kafka error: {e}") from e
            except Exception as e:
                logger.error(f"Unexpected error while consuming: {e}")
                # Continue processing other messages
                continue
                
    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error in consumer: {e}")
        raise
    finally:
        consumer.close()
        logger.info("Kafka consumer closed")


def main() -> None:
    """Main function to run Kafka consumer."""
    try:
        consumer = create_consumer()
        consume_messages(consumer)
    except Exception as e:
        logger.error(f"Failed to start consumer: {e}")
        raise


if __name__ == "__main__":
    main()
