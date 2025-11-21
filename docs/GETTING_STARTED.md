# Getting Started Guide

Quick guide to get the Data Engineering project up and running.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.8+ installed
- [ ] Java 11+ installed (for Spark)
- [ ] MySQL 8.0 installed and running
- [ ] MongoDB 4.4+ installed and running
- [ ] 8GB RAM minimum
- [ ] 10GB free disk space

## Step-by-Step Setup

### Step 1: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy template
copy .env.example .env    # Windows
cp .env.example .env      # Linux/Mac

# Edit .env file with your credentials
```

Update these values in `.env`:
```ini
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password

MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=new_data
```

### Step 3: Setup Databases

#### MySQL Setup

```bash
# Connect to MySQL
mysql -u root -p

# Create database
CREATE DATABASE new_data;

# Exit MySQL
exit

# Run schema setup
python database/mysql_connect.py
```

#### MongoDB Setup

```bash
# MongoDB will auto-create database
# Just run the schema setup
python database/mongodb_connect.py
```

### Step 4: Verify Setup

```python
# Test MySQL connection
python -c "from database.mysql_connect import MySQLConnect; from config.database_config import get_database_config; cfg = get_database_config(); print('MySQL OK')"

# Test MongoDB connection  
python -c "from database.mongodb_connect import MongoDBConnect; from config.database_config import get_database_config; cfg = get_database_config(); print('MongoDB OK')"
```

If both print "OK", you're ready!

### Step 5: Run Your First ETL Job

```bash
python src/spark/spark_main.py
```

You should see:
```
Connected to MySQL database: new_data
Connected to MongoDB database: new_data
Reading JSON file: ...
Validation successful
MongoDB connection closed
STOP SPARK SESSON
```

## Common Issues

### Issue: "No module named 'pyspark'"

**Solution**:
```bash
pip install pyspark
```

### Issue: "MySQL connection refused"

**Solutions**:
1. Check MySQL is running: `mysql --version`
2. Verify credentials in `.env`
3. Test connection: `mysql -u root -p`

### Issue: "MongoDB connection refused"

**Solutions**:
1. Start MongoDB:
   ```bash
   # Windows (Services)
   services.msc → MongoDB → Start
   
   # Linux
   sudo systemctl start mongod
   
   # Mac
   brew services start mongodb-community
   ```

### Issue: "FileNotFoundError: sample_data.json"

**Solution**: Ensure you're running from project root directory:
```bash
cd C:\Users\Laptop\PycharmProjects\DE
python src/spark/spark_main.py
```

### Issue: "Java not found"

**Solution**:
1. Install Java 11+: https://www.oracle.com/java/technologies/downloads/
2. Set JAVA_HOME environment variable
3. Verify: `java -version`

## Next Steps

After successful setup:

1. **Explore the code**: Read `src/spark/spark_main.py` to understand the ETL flow
2. **Modify sample data**: Add your own JSON files to `data/`
3. **Phase 3**: Setup CDC with Debezium (see `PLAN.md`)
4. **Read architecture**: Check `docs/ARCHITECTURE.md` for detailed design

## Development Workflow

```bash
# 1. Activate environment
venv\Scripts\activate

# 2. Make changes to code

# 3. Run ETL pipeline
python src/spark/spark_main.py

# 4. Verify in MongoDB
mongosh
use new_data
db.Users.find().limit(5)
```

## Troubleshooting

For more help:
1. Check `README.md` for detailed troubleshooting
2. Review `PLAN.md` for implementation details
3. Open an issue in the repository

---

**Happy Data Engineering!** 🚀

