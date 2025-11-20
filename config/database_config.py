import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Optional

# cấu hình của toàn bộ database
class DatabaseConfig:
    def validate(self) -> None:
        for key, value in self.__dict__.items():
            if value is None:
                raise ValueError(f"MISSING CONFIG FOR {key}")

@dataclass
class MongoDBConfig(DatabaseConfig):
    uri : str
    db_name : str
    jar_path : Optional[str] = None
    collection : str = "Users"

@dataclass
class MySQLConfig(DatabaseConfig):
    host : str
    user : str
    password : str
    database : str
    port : int
    jar_path: Optional[str] = None
    table : str = "Users"

def get_database_config() -> Dict[str,DatabaseConfig]:

    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    config = {
        "mongodb" :  MongoDBConfig(
            uri = os.getenv("MONGO_URI"),
            db_name = os.getenv("MONGO_DB_NAME"),
            jar_path = os.getenv("MONGO_PACKAGE_PATH")
        ),
        "mysql" : MySQLConfig (
            host = os.getenv("MYSQL_HOST"),
            port = int(os.getenv("MYSQL_PORT")),
            user = os.getenv("MYSQL_USER"),
            password = os.getenv("MYSQL_PASSWORD"),
            database = os.getenv("MYSQL_DATABASE"),
            jar_path = os.getenv("MYSQL_JAR_PATH")
        )
    }

    for db, setting in config.items():
        setting.validate()

    return config