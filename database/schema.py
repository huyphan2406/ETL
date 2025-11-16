from pathlib import Path
from typing import Any
from mysql.connector import Error
from src.utils.logger import get_logger
from src.utils.exceptions import DatabaseOperationError
from src.utils.constants import DEFAULT_TABLE_NAME, DEFAULT_COLLECTION_NAME


logger = get_logger("Schema")


def create_mysql_schema(connection: Any, cursor: Any, database: str) -> None:
    """Create MySQL schema from SQL file."""
    schema_path = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"
    cursor.execute(f"DROP DATABASE IF EXISTS {database}")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    logger.info(f"Created database {database} in MySQL")
    try:
        cursor.execute(f"USE {database}")
        with open(schema_path, "r", encoding="utf-8") as file:
            sql_script = file.read()
            sql_commands = [cmd.strip() for cmd in sql_script.split(";") if cmd.strip()]
            for cmd in sql_commands:
                cursor.execute(cmd)
                logger.debug("Executed MySQL command")
        connection.commit()
        logger.info("Created MySQL schema successfully")
    except Error as e:
        connection.rollback()
        logger.error(f"Failed to create MySQL schema: {e}")
        raise DatabaseOperationError(f"Failed to create MySQL schema: {e}") from e


def create_mongodb_schema(db: Any) -> None:
    """Create MongoDB schema with validation."""
    if DEFAULT_COLLECTION_NAME in db.list_collection_names():
        db[DEFAULT_COLLECTION_NAME].drop()
        logger.info(f"Dropped existing collection: {DEFAULT_COLLECTION_NAME}")

    db.create_collection(
        DEFAULT_COLLECTION_NAME,
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user_id", "login"],
                "properties": {
                    "user_id": {"bsonType": "string"},
                    "login": {"bsonType": "string"},
                    "gravatar_ID": {"bsonType": "string"},
                    "avatar_url": {"bsonType": "string"},
                    "url": {"bsonType": "string"},
                },
            }
        }
    )
    db[DEFAULT_COLLECTION_NAME].create_index("user_id", unique=True)
    logger.info(f"Created MongoDB schema for collection: {DEFAULT_COLLECTION_NAME}")


def create_redis_schema(client: Any) -> None:
    """Create Redis schema with sample data."""
    try:
        client.flushdb()  # drop database
        logger.info("Flushed Redis database")

        client.set("user:1:login", "GoogleCodeExporter")
        client.set("user:1:gravatar_id", "")
        client.set("user:1:avatar_url", "https://avatars.githubusercontent.com/u/9614759?")
        client.set("user:1:url", "https://api.github.com/users/GoogleCodeExporter")

        client.sadd("user_id", "user:1")

        logger.info("Added sample data to Redis successfully")
    except Exception as e:
        logger.error(f"Failed to add data to Redis: {e}")
        raise DatabaseOperationError(f"Failed to add data to Redis: {e}") from e


def validate() -> None:
    """Placeholder for validation function."""
    pass