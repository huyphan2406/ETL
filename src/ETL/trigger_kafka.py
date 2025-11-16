import json
import time
from typing import List, Dict, Any, Optional, Tuple
from kafka import KafkaProducer
from database.mysql_connect import MySQLConnect
from config.database_config import get_database_config
from mysql.connector.errors import OperationalError, InterfaceError
from src.utils.logger import get_logger
from src.utils.exceptions import DatabaseConnectionError, KafkaError, CDCProcessingError
from src.utils.constants import KAFKA_TOPIC_TRIGGER, DEFAULT_SLEEP_INTERVAL, DEFAULT_KAFKA_TIMEOUT

def get_data_trigger(mysql_client: MySQLConnect, last_timestamp: Optional[str]) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Get data from MySQL trigger log table.
    
    Args:
        mysql_client: MySQL connection client
        last_timestamp: Last processed timestamp
        
    Returns:
        Tuple of (data list, new_timestamp)
    """
    logger = get_logger("CDC-Trigger")
    try:
        connection, cursor = mysql_client.connection, mysql_client.cursor
        connection.database = "new_data"

        query = (
            "SELECT user_id, login, gravatar_id, avatar_url, url, state, "
            "CONCAT(DATE_FORMAT(changed_at, '%Y-%m-%d %H:%i:%s.'), "
            "LPAD(MICROSECOND(changed_at) DIV 1000, 3, '0')) AS log_timestamp "
            "FROM Users_log_after"
        )

        if last_timestamp:
            query += " WHERE changed_at > STR_TO_DATE(%s, '%Y-%m-%d %H:%i:%s.%f')"
            cursor.execute(query, (last_timestamp,))
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        connection.commit()

        schema = ["user_id", "login", "gravatar_id", "avatar_url", "url", "state", "log_timestamp"]
        data = [dict(zip(schema, row)) for row in rows]

        new_timestamp = max(
            (row["log_timestamp"] for row in data),
            default=last_timestamp
        )

        logger.info(f"Retrieved {len(data)} records from trigger log")
        return data, new_timestamp

    except Exception as e:
        logger.error(f"Error in get_data_trigger: {e}")
        raise CDCProcessingError(f"Failed to get trigger data: {e}") from e


def main() -> None:
    """Main function for CDC trigger-based producer."""
    logger = get_logger("CDC-Trigger-Main")
    config = get_database_config()
    last_timestamp: Optional[str] = None

    while True:
        try:
            with MySQLConnect(
                host=config["mysql"].host,
                port=config["mysql"].port,
                user=config["mysql"].user,
                password=config["mysql"].password,
                database=config["mysql"].database,
            ) as mysql_client:

                producer = KafkaProducer(
                    bootstrap_servers='localhost:9092',
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                logger.info("Kafka producer initialized")

                while True:
                    try:
                        data, new_timestamp = get_data_trigger(mysql_client, last_timestamp)
                        last_timestamp = new_timestamp

                        for record in data:
                            try:
                                time.sleep(1)
                                producer.send(topic=KAFKA_TOPIC_TRIGGER, value=record).get(timeout=DEFAULT_KAFKA_TIMEOUT)
                                logger.debug(f"Sent record to Kafka: {record.get('user_id', 'unknown')}")
                            except Exception as e:
                                logger.error(f"Kafka send error: {e}")
                                raise KafkaError(f"Failed to send message to Kafka: {e}") from e

                        producer.flush()
                        if data:
                            logger.info(f"Successfully sent {len(data)} records to Kafka")
                        time.sleep(DEFAULT_SLEEP_INTERVAL)
                    except CDCProcessingError as e:
                        logger.error(f"CDC processing error: {e}")
                        time.sleep(DEFAULT_SLEEP_INTERVAL)

        except (OperationalError, InterfaceError) as conn_err:
            logger.error(f"MySQL connection error: {conn_err}. Retrying in {DEFAULT_SLEEP_INTERVAL}s...")
            time.sleep(DEFAULT_SLEEP_INTERVAL)
        except DatabaseConnectionError as e:
            logger.error(f"Database connection error: {e}. Retrying in {DEFAULT_SLEEP_INTERVAL}s...")
            time.sleep(DEFAULT_SLEEP_INTERVAL)
        except Exception as e:
            logger.error(f"Unexpected error: {e}. Restarting in {DEFAULT_SLEEP_INTERVAL}s...")
            time.sleep(DEFAULT_SLEEP_INTERVAL)


if __name__ == "__main__":
    main()
