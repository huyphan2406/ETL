from typing import Optional, Any
import redis
from redis.exceptions import ConnectionError as RedisConnectionError
from config.database_config import get_database_config
from database.schema import create_redis_schema
from src.utils.logger import get_logger
from src.utils.exceptions import DatabaseConnectionError


class RedisConnect:
    def __init__(self, host: str, port: int, user: str, password: str, db: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = int(db)
        self.config = {"host": host, "port": port, "username": user, "password": password, "db": db}
        self.client: Optional[Any] = None
        self.logger = get_logger("RedisConnect")

    def connect(self) -> Any:
        """Connect to Redis database."""
        try:
            self.client = redis.Redis(**self.config, decode_responses=True)
            self.client.ping()  # test connection
            self.logger.info(f"Connected to Redis database: {self.db}")
            return self.client
        except RedisConnectionError as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise DatabaseConnectionError(f"Failed to connect to Redis: {e}") from e

    def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            self.client.close()
            self.logger.info("Redis connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def main():
    config_Redis = get_database_config()
    with RedisConnect(config_Redis["redis"].host, config_Redis["redis"].port, config_Redis["redis"].user, config_Redis["redis"].password, config_Redis["redis"].database) as redis:
        create_redis_schema(redis.connect())

    # validate data

if __name__ == "__main__":
    main()