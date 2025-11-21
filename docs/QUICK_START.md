# Quick Start Guide

## 5-Minute Setup

This guide will help you run the project in 5 minutes.

### Prerequisites

- ✅ Python 3.8+ installed
- ✅ MySQL running
- ✅ MongoDB running
- ✅ Kafka running

### Step 1: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment (1 minute)

Create `.env` file:

```env
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=new_data
MYSQL_JAR_PATH=lib/mysql-connector-j-9.2.0.jar

# MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=new_data
MONGO_PACKAGE_PATH=lib/mongo-spark-connector_2.13-10.5.0.jar
```

### Step 3: Setup Databases (1 minute)

```bash
# MySQL
python database/mysql_connect.py

# MongoDB
python database/mongodb_connect.py
```

### Step 4: Run ETL Pipeline (2 minutes)

```bash
python src/spark/spark_main.py
```

Output:
```
Connected to MySQL database: new_data
Connected to MongoDB database: new_data
Validation successful
STOP SPARK SESSON
```

Done! Data from `data/sample_data.json` is now in MongoDB.

## Verify Data

### Check MongoDB

```bash
mongosh

use new_data
db.Users.find().limit(5)
db.Users.countDocuments()
```

### Check MySQL

```bash
mysql -u root -p

USE new_data;
SELECT * FROM Users LIMIT 5;
SELECT COUNT(*) FROM Users;
```

## What's Next?

1. **Explore the data**: Query MongoDB for insights
2. **Run consumer**: `python src/ETL/consumer.py`
3. **Implement Phase 3**: Add log-based CDC (see PLAN.md)
4. **Add tests**: Setup pytest framework (Phase 5)

## Troubleshooting

### "Module not found" error
```bash
# Make sure you're in the project root
cd /path/to/DE
pip install -r requirements.txt
```

### "Database connection failed"
- Check if MySQL/MongoDB services are running
- Verify credentials in `.env` file
- Test connection: `mysql -u root -p` or `mongosh`

### "Java not found" (Spark)
- Install Java 11+: https://adoptium.net/
- Verify: `java -version`

### "Kafka connection failed"
- Start Kafka: `bin/kafka-server-start.sh config/server.properties`
- Verify: `bin/kafka-topics.sh --list --bootstrap-server localhost:9092`

