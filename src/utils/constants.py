"""
Constants module for the Data Engineering project.
Contains magic strings, default values, and enums.
"""
from enum import Enum


# Database table/collection names
DEFAULT_TABLE_NAME = "Users"
DEFAULT_COLLECTION_NAME = "Users"
DEFAULT_KEY_COLUMN = "id"

# Spark temporary column
SPARK_TEMP_COLUMN = "spark_temp"
SPARK_TEMP_VALUE = "spark_write"

# Kafka topics
KAFKA_TOPIC_TRIGGER = "datdepzai"
KAFKA_TOPIC_CONSUMER = "huydepzai"

# Kafka consumer group
DEFAULT_CONSUMER_GROUP = "de-consumer-group"

# Write modes
class WriteMode(Enum):
    """Spark write modes."""
    APPEND = "append"
    OVERWRITE = "overwrite"
    IGNORE = "ignore"
    ERROR = "errorifexists"


# CDC states
class CDCState(Enum):
    """CDC operation states."""
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


# Log table names
LOG_TABLE_BEFORE = "Users_log_before"
LOG_TABLE_AFTER = "Users_log_after"

# Default values
DEFAULT_SPARK_APP_NAME = "DE-Pipeline"
DEFAULT_SPARK_MASTER = "local[*]"
DEFAULT_EXECUTOR_MEMORY = "4g"
DEFAULT_DRIVER_MEMORY = "2g"
DEFAULT_EXECUTOR_CORES = 2
DEFAULT_NUM_EXECUTORS = 3
DEFAULT_LOG_LEVEL = "WARN"

# Timeouts
DEFAULT_KAFKA_TIMEOUT = 5  # seconds
DEFAULT_POLL_TIMEOUT_MS = 500  # milliseconds
DEFAULT_SLEEP_INTERVAL = 3  # seconds

# Data paths
DATA_DIR = "data"
SQL_DIR = "sql"
LOGS_DIR = "logs"

