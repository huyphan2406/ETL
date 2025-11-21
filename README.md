# Data Engineering Project

A Data Engineering project featuring ETL pipeline with Apache Spark and Change Data Capture (CDC) capabilities using MySQL, MongoDB, and Kafka.

## Overview

This project implements a complete data engineering pipeline that:
- Processes JSON data files using Apache Spark
- Captures database changes in real-time using CDC
- Synchronizes data across multiple databases
- Streams change events through Kafka

## Architecture

```
┌─────────────────┐
│   JSON File     │ (Source Data)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Spark ETL      │ (Transform & Load)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MongoDB       │ (Data Warehouse)
└─────────────────┘

┌─────────────────┐
│   MySQL         │ (Operational DB)
└────────┬────────┘
         │ Changes
         ▼
┌─────────────────┐
│    Kafka        │ (Message Queue)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Consumer      │ (Process Events)
└─────────────────┘
```

## Features

- **Batch ETL Pipeline**: Process large JSON files with Apache Spark
- **Change Data Capture**: Track and stream database changes (Phase 3: Log-based CDC with Debezium)
- **Multi-Database Support**: MySQL (CDC source) and MongoDB (ETL destination) integration
- **Data Validation**: Automatic validation and reconciliation of written data
- **Kafka Integration**: Message queue for event streaming
- **Production-Ready Architecture**: Scalable, maintainable codebase

## Technology Stack

- **Processing**: Apache Spark (PySpark)
- **Databases**: MySQL, MongoDB
- **Message Queue**: Apache Kafka
- **Language**: Python 3.12
- **Dependency Management**: pip, conda

## Prerequisites

### Software Requirements

- Python 3.8 or higher
- Java 11 or higher (for Spark and Kafka)
- MySQL 5.7+ or 8.0+
- MongoDB 4.0+
- Apache Kafka 2.8+
- Apache Spark 3.5+

### Python Dependencies

See `requirements.txt` for a complete list. Main dependencies:
- pyspark
- mysql-connector-python
- pymongo
- kafka-python
- python-dotenv

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd DE
```

### 2. Create Virtual Environment

```bash
# Using conda
conda env create -f environment.yml
conda activate base

# Or using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials (see Configuration section below).

### 5. Setup Databases

#### MySQL Setup

```bash
# Start MySQL service
# Windows: Services -> MySQL80 -> Start
# Linux: sudo systemctl start mysql

# Create database and schema
python database/mysql_connect.py
```

#### MongoDB Setup

```bash
# Start MongoDB service
# Windows: Services -> MongoDB -> Start
# Linux: sudo systemctl start mongod

# Create database and schema
python database/mongodb_connect.py
```

### 6. Setup Kafka

```bash
# Start Zookeeper (if needed)
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka broker
bin/kafka-server-start.sh config/server.properties

# Create topics (optional - auto-created by default)
bin/kafka-topics.sh --create --topic datdepzai --bootstrap-server localhost:9092
bin/kafka-topics.sh --create --topic huydepzai --bootstrap-server localhost:9092
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=new_data
MYSQL_JAR_PATH=lib/mysql-connector-j-9.2.0.jar

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=new_data
MONGO_PACKAGE_PATH=lib/mongo-spark-connector_2.13-10.5.0.jar
```

See `docs/ENV_TEMPLATE.md` for a complete template and setup instructions.

## Usage

### 1. Batch ETL Pipeline

Process JSON files and load data into MongoDB:

```bash
python src/spark/spark_main.py
```

This will:
- Read JSON file from `data/sample_data.json`
- Transform data using Spark
- Validate and write to MongoDB
- Clean up temporary fields

### 2. CDC Pipeline (Change Data Capture)

**Current Status**: Trigger-based CDC has been removed. Phase 3 will implement log-based CDC using Debezium.

**Future Implementation**:
- Debezium MySQL connector for binlog-based CDC
- Real-time change event streaming to Kafka
- Automatic synchronization to MongoDB

For detailed migration guide, see `docs/CDC_MIGRATION.md`.  
For implementation plan, see `PLAN.md` Phase 3.

### 3. Kafka Consumer

Consume messages from Kafka:

```bash
python src/ETL/consumer.py
```

## Project Structure

```
DE/
├── config/                 # Configuration files
│   ├── database_config.py  # Database configurations
│   └── spark_config.py     # Spark session config
├── database/               # Database connection classes
│   ├── mongodb_connect.py  # MongoDB connection
│   ├── mysql_connect.py    # MySQL connection
│   └── schema.py           # Schema creation scripts
├── data/                   # Data files
│   └── sample_data.json    # Sample JSON data
├── docs/                   # Documentation
│   ├── API_DOCUMENTATION.md # Complete API reference
│   ├── CDC_MIGRATION.md     # CDC migration guide
│   └── ENV_TEMPLATE.md      # Environment variables template
├── lib/                    # JAR files
│   ├── mongo-spark-connector_2.13-10.5.0.jar
│   └── mysql-connector-j-9.2.0.jar
├── sql/                    # SQL scripts
│   ├── schema.sql          # MySQL schema
│   └── trigger.sql         # MySQL triggers (for trigger-based CDC)
├── src/                    # Source code
│   ├── ETL/                # ETL scripts
│   │   └── consumer.py     # Kafka consumer
│   └── spark/              # Spark jobs
│       ├── spark_main.py   # Main ETL pipeline
│       └── spark_write_data.py  # Spark write logic
├── .env                    # Environment variables (create from docs/ENV_TEMPLATE.md)
├── .gitignore              # Git ignore rules
├── PLAN.md                 # Implementation plan
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## Data Flow

### Batch ETL Process

1. **Extract**: Read JSON file from `data/sample_data.json`
2. **Transform**: Flatten nested JSON structure (actor.*)
3. **Load**: Write to MongoDB Users collection
4. **Validate**: Compare written data with source, add missing records

### CDC Process (Phase 3 - Future)

1. MySQL captures changes via binlog
2. Debezium connector streams changes to Kafka
3. CDC consumer processes change events
4. Data synchronized to MongoDB

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[API Documentation](docs/API_DOCUMENTATION.md)**: Complete API reference for all modules
- **[CDC Migration Guide](docs/CDC_MIGRATION.md)**: Step-by-step guide for migrating to log-based CDC
- **[Environment Template](docs/ENV_TEMPLATE.md)**: Environment variables configuration guide

## Development

### Running Tests

```bash
# Run all tests (when implemented in Phase 5)
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### Code Style

```bash
# Format code
black src/ config/ database/

# Lint code
flake8 src/ config/ database/

# Type checking
mypy src/ config/ database/
```

## Roadmap

See `PLAN.md` for the complete 16-phase implementation plan:

- **Phase 1**: Fix Critical Bugs ✅
- **Phase 2**: Code Quality (Simplified version)
- **Phase 3**: Migrate to Log-Based CDC (Debezium)
- **Phase 4**: Database & Infrastructure Improvements
- **Phase 5-16**: Testing, Documentation, Monitoring, Security, etc.

## Troubleshooting

### Common Issues

#### MySQL Connection Error
```
Error: Access denied for user
```
**Solution**: Check MySQL credentials in `.env` file

#### MongoDB Connection Error
```
Error: Connection refused
```
**Solution**: Ensure MongoDB service is running

#### Kafka Connection Error
```
Error: NoBrokersAvailable
```
**Solution**: Start Kafka broker on port 9092

#### Spark Java Heap Space Error
```
Error: Java heap space
```
**Solution**: Increase driver/executor memory in `spark_main.py`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational purposes.

## Contact

For questions or issues, please create an issue in the repository.

## Acknowledgments

- Apache Spark for distributed processing
- Debezium for CDC capabilities
- MongoDB and MySQL communities
