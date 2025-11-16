from typing import Optional, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config.database_config import get_database_config
from database.schema import create_mongodb_schema
from src.utils.logger import get_logger
from src.utils.exceptions import DatabaseConnectionError


class MongoDBConnect:
    def __init__(self, mongo_uri: str, db_name: str):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client: Optional[Any] = None
        self.db: Optional[Any] = None
        self.logger = get_logger("MongoDBConnect")

    def connect(self) -> Any:
        """Connect to MongoDB database."""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.client.server_info()  # test connection
            self.db = self.client[self.db_name]
            self.logger.info(f"Connected to MongoDB database: {self.db_name}")
            return self.db
        except ConnectionFailure as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise DatabaseConnectionError(f"Failed to connect to MongoDB: {e}") from e

    def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.logger.info("MongoDB connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def main():
    config_MongoDB = get_database_config()
    with MongoDBConnect(config_MongoDB["mongodb"].uri, config_MongoDB["mongodb"].db_name) as mongo:
        db = mongo.connect()
        create_mongodb_schema(db)

    #validate data

if __name__ == "__main__":
    main()

