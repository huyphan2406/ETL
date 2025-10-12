import json
import time
from kafka import KafkaProducer
from database.mysql_connect import MySQLConnect
from config.database_config import get_database_config
from mysql.connector.errors import OperationalError, InterfaceError

def get_data_trigger(mysql_client, last_timestamp):
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
            query += f" WHERE changed_at > STR_TO_DATE('{last_timestamp}', '%Y-%m-%d %H:%i:%s.%f')"

        cursor.execute(query)
        rows = cursor.fetchall()
        connection.commit()

        schema = ["user_id", "login", "gravatar_id", "avatar_url", "url", "state", "log_timestamp"]
        data = [dict(zip(schema, row)) for row in rows]

        new_timestamp = max(
            (row["log_timestamp"] for row in data),
            default=last_timestamp
        )

        return data, new_timestamp

    except Exception as e:
        print(f"❌ Error in get_data_trigger: {e}")
        return [], last_timestamp


def main():
    config = get_database_config()
    last_timestamp = None

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

                while True:
                    data, new_timestamp = get_data_trigger(mysql_client, last_timestamp)
                    last_timestamp = new_timestamp  # cập nhật timestamp mới

                    for record in data:
                        try:
                            time.sleep(1)
                            producer.send(topic="datdepzai", value=record).get(timeout=5)
                            print("✅ Sent:", record)
                        except Exception as e:
                            print("❌ Kafka send error:", e)

                    producer.flush()
                    time.sleep(3)  # tránh query quá dài

        except (OperationalError, InterfaceError) as conn_err:
            print(f"🔌 MySQL connection error: {conn_err}. Retrying in 3s...")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}. Restarting in 3s...")
            time.sleep(3)


if __name__ == "__main__":
    main()
