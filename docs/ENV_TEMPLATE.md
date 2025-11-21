# Environment Variables Template

Copy this content to create your `.env` file in the project root.

```env
# ============================================
# Data Engineering Project - Environment Variables
# ============================================
# Copy this content to .env file and fill in your actual values
# DO NOT commit .env file to version control

# ============================================
# MySQL Configuration
# ============================================
# MySQL database connection settings
# Used for: CDC source, operational database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=new_data
MYSQL_JAR_PATH=lib/mysql-connector-j-9.2.0.jar

# ============================================
# MongoDB Configuration
# ============================================
# MongoDB connection settings
# Used for: ETL destination, data warehouse
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=new_data
MONGO_PACKAGE_PATH=lib/mongo-spark-connector_2.13-10.5.0.jar

# ============================================
# Kafka Configuration (Optional)
# ============================================
# Kafka broker settings for CDC streaming
# Used for: Change Data Capture event streaming
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_CDC=datdepzai
KAFKA_TOPIC_CONSUMER=huydepzai
KAFKA_CONSUMER_GROUP=de-consumer-group

# ============================================
# Spark Configuration (Optional)
# ============================================
# Spark cluster settings (if using remote cluster)
# Leave as default for local mode
SPARK_MASTER=local[*]
SPARK_EXECUTOR_MEMORY=4g
SPARK_DRIVER_MEMORY=2g
SPARK_EXECUTOR_CORES=2
```

## Setup Instructions

1. Create a `.env` file in the project root directory
2. Copy the content above into the `.env` file
3. Replace placeholder values with your actual credentials
4. Ensure `.env` is in `.gitignore` (never commit credentials)

## Required Variables

### MySQL (Required)
- `MYSQL_HOST`: MySQL server hostname
- `MYSQL_PORT`: MySQL server port (default: 3306)
- `MYSQL_USER`: MySQL username
- `MYSQL_PASSWORD`: MySQL password
- `MYSQL_DATABASE`: Database name
- `MYSQL_JAR_PATH`: Path to MySQL JDBC connector JAR file

### MongoDB (Required)
- `MONGO_URI`: MongoDB connection URI
- `MONGO_DB_NAME`: MongoDB database name
- `MONGO_PACKAGE_PATH`: Path to MongoDB Spark connector JAR file

### Kafka (Optional - for CDC)
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses
- `KAFKA_TOPIC_CDC`: Topic name for CDC events
- `KAFKA_TOPIC_CONSUMER`: Topic name for consumer
- `KAFKA_CONSUMER_GROUP`: Consumer group ID

### Spark (Optional)
- `SPARK_MASTER`: Spark master URL
- `SPARK_EXECUTOR_MEMORY`: Executor memory allocation
- `SPARK_DRIVER_MEMORY`: Driver memory allocation
- `SPARK_EXECUTOR_CORES`: Number of cores per executor

## Security Notes

- Never commit `.env` file to version control
- Use environment-specific configurations for different environments
- For production, consider using secret management systems (AWS Secrets Manager, HashiCorp Vault, etc.)
- Rotate credentials regularly
- Use least-privilege database users

