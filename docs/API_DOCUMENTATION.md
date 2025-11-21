# API Documentation

Complete API reference for the Data Engineering project.

## Table of Contents

1. [Configuration Modules](#configuration-modules)
2. [Database Connection Classes](#database-connection-classes)
3. [Spark Modules](#spark-modules)
4. [ETL Modules](#etl-modules)

---

## Configuration Modules

### `config.database_config`

Database configuration management.

#### Classes

##### `DatabaseConfig`

Base class for database configurations.

**Methods**:
- `validate() -> None`: Validates that all required configuration values are set.

##### `MongoDBConfig(DatabaseConfig)`

MongoDB configuration dataclass.

**Attributes**:
- `uri: str` - MongoDB connection URI
- `db_name: str` - Database name
- `jar_path: Optional[str]` - Path to MongoDB Spark connector JAR
- `collection: str` - Default collection name (default: "Users")

**Example**:
```python
from config.database_config import MongoDBConfig

config = MongoDBConfig(
    uri="mongodb://localhost:27017/",
    db_name="new_data",
    jar_path="lib/mongo-spark-connector_2.13-10.5.0.jar"
)
```

##### `MySQLConfig(DatabaseConfig)`

MySQL configuration dataclass.

**Attributes**:
- `host: str` - MySQL server hostname
- `port: int` - MySQL server port
- `user: str` - MySQL username
- `password: str` - MySQL password
- `database: str` - Database name
- `jar_path: Optional[str]` - Path to MySQL JDBC connector JAR
- `table: str` - Default table name (default: "Users")

**Example**:
```python
from config.database_config import MySQLConfig

config = MySQLConfig(
    host="localhost",
    port=3306,
    user="root",
    password="password",
    database="new_data",
    jar_path="lib/mysql-connector-j-9.2.0.jar"
)
```

#### Functions

##### `get_database_config() -> Dict[str, DatabaseConfig]`

Loads database configurations from environment variables.

**Returns**:
- `Dict[str, DatabaseConfig]`: Dictionary with keys "mongodb" and "mysql"

**Raises**:
- `ValueError`: If any required configuration is missing

**Example**:
```python
from config.database_config import get_database_config

configs = get_database_config()
mysql_config = configs["mysql"]
mongo_config = configs["mongodb"]
```

---

### `config.spark_config`

Spark session configuration management.

#### Classes

##### `SparkConnect`

Manages Spark session creation and configuration.

**Constructor**:
```python
SparkConnect(
    app_name: str,
    master_url: str = "local[*]",
    executor_memory: Optional[str] = "4g",
    executor_cores: Optional[str] = 2,
    driver_memory: Optional[str] = "2g",
    num_executor: Optional[int] = 3,
    jars: Optional[List[str]] = None,
    spark_conf: Optional[Dict[str, str]] = None,
    log_level: str = "WARN"
)
```

**Parameters**:
- `app_name: str` - Spark application name
- `master_url: str` - Spark master URL (default: "local[*]")
- `executor_memory: Optional[str]` - Executor memory (default: "4g")
- `executor_cores: Optional[str]` - Cores per executor (default: 2)
- `driver_memory: Optional[str]` - Driver memory (default: "2g")
- `num_executor: Optional[int]` - Number of executors (default: 3)
- `jars: Optional[List[str]]` - List of JAR file paths
- `spark_conf: Optional[Dict[str, str]]` - Additional Spark configurations
- `log_level: str` - Spark log level (default: "WARN")

**Attributes**:
- `spark: SparkSession` - Spark session instance

**Methods**:
- `stop() -> None`: Stops the Spark session

**Example**:
```python
from config.spark_config import SparkConnect

spark_conn = SparkConnect(
    app_name="my-etl-job",
    master_url="local[*]",
    executor_memory="4g",
    executor_cores=2,
    jars=["lib/mysql-connector-j-9.2.0.jar"]
)
spark = spark_conn.spark
# Use spark session
spark_conn.stop()
```

#### Functions

##### `get_spark_config() -> Dict`

Gets Spark configuration for database writes.

**Returns**:
- `Dict`: Configuration dictionary with keys:
  - `"mysql"`: MySQL JDBC configuration
  - `"mongodb"`: MongoDB connection configuration

**Example**:
```python
from config.spark_config import get_spark_config

spark_config = get_spark_config()
mysql_jdbc_url = spark_config["mysql"]["jdbc_url"]
mongo_uri = spark_config["mongodb"]["uri"]
```

---

## Database Connection Classes

### `database.mysql_connect`

MySQL database connection management.

#### Classes

##### `MySQLConnect`

Context manager for MySQL connections.

**Constructor**:
```python
MySQLConnect(host: str, port: int, user: str, password: str, database: str)
```

**Parameters**:
- `host: str` - MySQL server hostname
- `port: int` - MySQL server port
- `user: str` - MySQL username
- `password: str` - MySQL password
- `database: str` - Database name

**Attributes**:
- `connection: mysql.connector.connection.MySQLConnection` - MySQL connection object
- `cursor: mysql.connector.cursor.MySQLCursor` - MySQL cursor object

**Methods**:
- `connect() -> Tuple[MySQLConnection, MySQLCursor]`: Establishes connection
- `close() -> None`: Closes connection and cursor
- `__enter__() -> MySQLConnect`: Context manager entry
- `__exit__(...) -> None`: Context manager exit

**Example**:
```python
from database.mysql_connect import MySQLConnect

with MySQLConnect("localhost", 3306, "root", "password", "new_data") as mysql:
    cursor = mysql.cursor
    cursor.execute("SELECT * FROM Users LIMIT 10")
    results = cursor.fetchall()
    # Connection automatically closed
```

---

### `database.mongodb_connect`

MongoDB database connection management.

#### Classes

##### `MongoDBConnect`

Context manager for MongoDB connections.

**Constructor**:
```python
MongoDBConnect(mongo_uri: str, db_name: str)
```

**Parameters**:
- `mongo_uri: str` - MongoDB connection URI
- `db_name: str` - Database name

**Attributes**:
- `client: pymongo.MongoClient` - MongoDB client
- `db: pymongo.database.Database` - Database object

**Methods**:
- `connect() -> Database`: Establishes connection and returns database
- `close() -> None`: Closes MongoDB client
- `__enter__() -> MongoDBConnect`: Context manager entry
- `__exit__(...) -> None`: Context manager exit

**Example**:
```python
from database.mongodb_connect import MongoDBConnect

with MongoDBConnect("mongodb://localhost:27017/", "new_data") as mongo:
    db = mongo.db
    users = db.Users.find({"login": "test_user"})
    # Connection automatically closed
```

---

### `database.schema`

Database schema creation utilities.

#### Functions

##### `create_mysql_schema(connection, cursor, database: str) -> None`

Creates MySQL database and schema from SQL file.

**Parameters**:
- `connection`: MySQL connection object
- `cursor`: MySQL cursor object
- `database: str` - Database name

**Raises**:
- `Exception`: If schema creation fails

**Example**:
```python
from database.mysql_connect import MySQLConnect
from database.schema import create_mysql_schema

with MySQLConnect("localhost", 3306, "root", "password", "new_data") as mysql:
    create_mysql_schema(mysql.connection, mysql.cursor, "new_data")
```

##### `create_mongodb_schema(db) -> None`

Creates MongoDB collection with schema validation.

**Parameters**:
- `db`: MongoDB database object

**Example**:
```python
from database.mongodb_connect import MongoDBConnect
from database.schema import create_mongodb_schema

with MongoDBConnect("mongodb://localhost:27017/", "new_data") as mongo:
    create_mongodb_schema(mongo.db)
```

---

## Spark Modules

### `src.spark.spark_main`

Main ETL pipeline entry point.

#### Functions

##### `main() -> None`

Main ETL pipeline function.

**Process**:
1. Initializes Spark session
2. Reads JSON file from `data/sample_data.json`
3. Transforms nested JSON structure
4. Validates and writes to MongoDB
5. Stops Spark session

**Example**:
```bash
python src/spark/spark_main.py
```

---

### `src.spark.spark_write_data`

Spark DataFrame write and validation operations.

#### Classes

##### `SparkWrite`

Handles Spark DataFrame writes to databases.

**Constructor**:
```python
SparkWrite(spark: SparkSession, config: Dict[str, Any])
```

**Parameters**:
- `spark: SparkSession` - Spark session
- `config: Dict[str, Any]` - Database configuration dictionary

**Methods**:

###### `spark_write_mysql(df, table_name, jdbc_url, config, mode="append") -> None`

Writes DataFrame to MySQL table.

**Parameters**:
- `df: DataFrame` - Spark DataFrame to write
- `table_name: str` - Target table name
- `jdbc_url: str` - JDBC connection URL
- `config: Dict[str, Any]` - MySQL configuration
- `mode: str` - Write mode (default: "append")

**Note**: Adds temporary `spark_temp` column for validation tracking.

###### `validate_spark_mysql(df_write: DataFrame) -> None`

Validates MySQL write by comparing with source DataFrame.

**Parameters**:
- `df_write: DataFrame` - Source DataFrame to validate

**Process**:
1. Reads written data from MySQL
2. Compares with source DataFrame
3. Adds missing records if any
4. Removes temporary `spark_temp` column

###### `spark_write_mongodb(df, database, collection, uri, mode="append") -> None`

Writes DataFrame to MongoDB collection.

**Parameters**:
- `df: DataFrame` - Spark DataFrame to write
- `database: str` - MongoDB database name
- `collection: str` - Collection name
- `uri: str` - MongoDB connection URI
- `mode: str` - Write mode (default: "append")

###### `validate_spark_mongodb(df_write: DataFrame) -> None`

Validates MongoDB write by comparing with source DataFrame.

**Parameters**:
- `df_write: DataFrame` - Source DataFrame to validate

**Process**:
1. Reads written data from MongoDB
2. Compares with source DataFrame
3. Adds missing records if any
4. Removes temporary `spark_temp` field

###### `write_all_db(df: DataFrame, mode: str = "append") -> None`

Writes DataFrame to all configured databases.

**Parameters**:
- `df: DataFrame` - Spark DataFrame to write
- `mode: str` - Write mode (default: "append")

**Note**: Currently only writes to MongoDB.

###### `validate_all_db(df: DataFrame) -> None`

Validates writes to all configured databases.

**Parameters**:
- `df: DataFrame` - Spark DataFrame to validate

**Note**: Currently only validates MongoDB.

**Example**:
```python
from pyspark.sql import SparkSession
from config.spark_config import SparkConnect, get_spark_config
from src.spark.spark_write_data import SparkWrite

spark_conn = SparkConnect(app_name="etl-job")
spark = spark_conn.spark
spark_config = get_spark_config()

# Create DataFrame
df = spark.read.json("data/sample_data.json")

# Write and validate
spark_write = SparkWrite(spark, spark_config)
spark_write.write_all_db(df)
spark_write.validate_all_db(df)
```

---

## ETL Modules

### `src.ETL.consumer`

Kafka consumer for processing messages.

#### Functions

##### `create_consumer(topic, group_id, bootstrap_servers, auto_offset_reset, enable_auto_commit) -> KafkaConsumer`

Creates a Kafka consumer instance.

**Parameters**:
- `topic: str` - Kafka topic name (default: "huydepzai")
- `group_id: str` - Consumer group ID (default: "de-consumer-group")
- `bootstrap_servers: list` - Kafka broker addresses (default: ["localhost:9092"])
- `auto_offset_reset: str` - Offset reset policy (default: "earliest")
- `enable_auto_commit: bool` - Enable auto commit (default: True)

**Returns**:
- `KafkaConsumer`: Configured Kafka consumer

**Raises**:
- `Exception`: If consumer creation fails

##### `process_message(message, topic_partition) -> Optional[Dict[str, Any]]`

Processes a Kafka message.

**Parameters**:
- `message`: Kafka message object
- `topic_partition`: Topic partition object

**Returns**:
- `Optional[Dict[str, Any]]`: Processed message data or None on error

##### `consume_messages(consumer, timeout_ms=500) -> None`

Consumes messages from Kafka topic.

**Parameters**:
- `consumer: KafkaConsumer` - Kafka consumer instance
- `timeout_ms: int` - Poll timeout in milliseconds (default: 500)

**Process**:
- Continuously polls for messages
- Processes each message
- Prints message details
- Handles errors gracefully

##### `main() -> None`

Main consumer function.

**Example**:
```bash
python src/ETL/consumer.py
```

---

## Error Handling

### Common Exceptions

#### `ValueError`
Raised when required configuration values are missing.

**Example**:
```python
from config.database_config import get_database_config

try:
    config = get_database_config()
except ValueError as e:
    print(f"Configuration error: {e}")
```

#### `mysql.connector.Error`
Raised for MySQL connection or query errors.

**Example**:
```python
from database.mysql_connect import MySQLConnect
from mysql.connector import Error

try:
    with MySQLConnect("localhost", 3306, "user", "pass", "db") as mysql:
        # Database operations
        pass
except Error as e:
    print(f"MySQL error: {e}")
```

#### `pymongo.errors.ConnectionFailure`
Raised when MongoDB connection fails.

**Example**:
```python
from database.mongodb_connect import MongoDBConnect
from pymongo.errors import ConnectionFailure

try:
    with MongoDBConnect("mongodb://localhost:27017/", "db") as mongo:
        # Database operations
        pass
except ConnectionFailure as e:
    print(f"MongoDB connection error: {e}")
```

---

## Usage Examples

### Complete ETL Pipeline

```python
from pathlib import Path
from config.spark_config import SparkConnect, get_spark_config
from config.database_config import get_database_config
from src.spark.spark_write_data import SparkWrite
from pyspark.sql.functions import col, lit

# Initialize
config = get_database_config()
spark_config = get_spark_config()
spark_conn = SparkConnect(app_name="etl-pipeline")
spark = spark_conn.spark

# Read data
json_path = Path("data/sample_data.json")
df = spark.read.json(str(json_path))

# Transform
df_transformed = df.select(
    col("actor.id").cast("string").alias("user_id"),
    col("actor.login").alias("login"),
    col("actor.gravatar_id").alias("gravatar_id"),
    col("actor.avatar_url").alias("avatar_url"),
    col("actor.url").alias("url")
).withColumn("spark_temp", lit("spark_write"))

# Write and validate
spark_write = SparkWrite(spark, spark_config)
spark_write.validate_all_db(df_transformed)

# Cleanup
spark_conn.stop()
```

### Database Schema Setup

```python
from config.database_config import get_database_config
from database.mysql_connect import MySQLConnect
from database.mongodb_connect import MongoDBConnect
from database.schema import create_mysql_schema, create_mongodb_schema

config = get_database_config()

# Setup MySQL
with MySQLConnect(
    config["mysql"].host,
    config["mysql"].port,
    config["mysql"].user,
    config["mysql"].password,
    config["mysql"].database
) as mysql:
    create_mysql_schema(mysql.connection, mysql.cursor, config["mysql"].database)

# Setup MongoDB
with MongoDBConnect(config["mongodb"].uri, config["mongodb"].db_name) as mongo:
    create_mongodb_schema(mongo.db)
```

---

## Version Information

- **Python**: 3.12+
- **PySpark**: 3.5+
- **MySQL Connector**: 9.2.0
- **MongoDB Spark Connector**: 3.0.1
- **Kafka Python**: Latest

---

For more information, see:
- [README.md](../README.md) - Project overview
- [PLAN.md](../PLAN.md) - Implementation plan
- [CDC_MIGRATION.md](./CDC_MIGRATION.md) - CDC migration guide

