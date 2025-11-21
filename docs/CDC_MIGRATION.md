# CDC Migration Guide: Trigger-Based to Log-Based CDC

This guide explains how to migrate from trigger-based CDC to log-based CDC using Debezium.

## Table of Contents

1. [Overview](#overview)
2. [Current State (Trigger-Based CDC)](#current-state-trigger-based-cdc)
3. [Target State (Log-Based CDC)](#target-state-log-based-cdc)
4. [Migration Steps](#migration-steps)
5. [Comparison](#comparison)
6. [Rollback Procedures](#rollback-procedures)
7. [Troubleshooting](#troubleshooting)

## Overview

### What is CDC?

Change Data Capture (CDC) is a technique to identify and capture changes made to data in a database, then deliver those changes in real-time to downstream processes.

### Why Migrate?

**Trigger-Based CDC (Current)**:
- ✅ Simple implementation
- ❌ Performance overhead on database
- ❌ Requires schema changes (log tables)
- ❌ Can miss changes if triggers fail
- ❌ Polling-based (not real-time)

**Log-Based CDC (Target)**:
- ✅ Minimal performance impact
- ✅ No schema changes required
- ✅ Real-time change capture
- ✅ Captures all changes (including direct SQL)
- ✅ Better scalability

## Current State (Trigger-Based CDC)

### Architecture

```
MySQL Users Table
    │
    ├─ BEFORE INSERT Trigger → Users_log_before
    ├─ AFTER INSERT Trigger  → Users_log_after
    ├─ BEFORE UPDATE Trigger → Users_log_before
    ├─ AFTER UPDATE Trigger  → Users_log_after
    ├─ BEFORE DELETE Trigger → Users_log_before
    └─ AFTER DELETE Trigger  → Users_log_after
    │
    ▼
Python Script (trigger_kafka.py)
    │
    ├─ Polls log tables
    ├─ Reads changes
    └─ Sends to Kafka
    │
    ▼
Kafka Topic (datdepzai)
```

### Components

1. **MySQL Triggers**: `sql/trigger.sql`
   - Creates log tables (`Users_log_before`, `Users_log_after`)
   - Triggers capture before/after states

2. **Python Producer**: `src/ETL/trigger_kafka.py` (removed)
   - Polls log tables periodically
   - Sends changes to Kafka

3. **Kafka Consumer**: `src/ETL/consumer.py`
   - Consumes change events

### Limitations

- **Performance**: Triggers add overhead to every INSERT/UPDATE/DELETE
- **Reliability**: If trigger fails, change is lost
- **Latency**: Polling introduces delay
- **Schema Changes**: Requires log tables
- **Direct SQL**: Changes made via direct SQL may not be captured

## Target State (Log-Based CDC)

### Architecture

```
MySQL Binlog
    │
    ▼
Debezium MySQL Connector
    │
    ├─ Reads binlog
    ├─ Parses change events
    └─ Publishes to Kafka
    │
    ▼
Kafka Topic (datdepzai)
    │
    ▼
CDC Consumer (src/ETL/cdc_consumer.py)
    │
    ├─ Deserializes Debezium format
    ├─ Transforms events
    └─ Syncs to MongoDB
```

### Components

1. **Debezium MySQL Connector**
   - Kafka Connect connector
   - Reads MySQL binlog
   - Publishes structured change events

2. **Kafka Connect**
   - Manages connectors
   - Handles offset management
   - Provides REST API

3. **CDC Consumer** (to be created)
   - Consumes Debezium events
   - Transforms to application format
   - Syncs to MongoDB

## Migration Steps

### Phase 1: Preparation

#### 1.1 Enable MySQL Binlog

```sql
-- Check current binlog status
SHOW VARIABLES LIKE 'log_bin';

-- Enable binlog (if not enabled)
-- Add to my.cnf or my.ini:
[mysqld]
log-bin=mysql-bin
binlog_format=ROW
binlog_row_image=FULL
server-id=1
expire_logs_days=7
```

#### 1.2 Create Debezium User

```sql
CREATE USER 'debezium'@'%' IDENTIFIED BY 'debezium_password';
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%';
FLUSH PRIVILEGES;
```

#### 1.3 Install Dependencies

```bash
# Download Debezium MySQL Connector
wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-mysql/2.5.0.Final/debezium-connector-mysql-2.5.0.Final-plugin.tar.gz
tar -xzf debezium-connector-mysql-2.5.0.Final-plugin.tar.gz
# Place in Kafka Connect plugins directory
```

### Phase 2: Setup Kafka Connect

#### 2.1 Configure Kafka Connect

```properties
# config/connect-standalone.properties
bootstrap.servers=localhost:9092
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
key.converter.schemas.enable=true
value.converter.schemas.enable=true
offset.storage.file.filename=/tmp/connect.offsets
offset.flush.interval.ms=10000
plugin.path=/path/to/debezium-connector-mysql
```

#### 2.2 Start Kafka Connect

```bash
bin/connect-standalone.sh config/connect-standalone.properties
```

### Phase 3: Deploy Debezium Connector

#### 3.1 Create Connector Configuration

```json
{
  "name": "mysql-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "tasks.max": "1",
    "database.hostname": "localhost",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "debezium_password",
    "database.server.id": "184054",
    "database.server.name": "mysql-server",
    "database.include.list": "new_data",
    "table.include.list": "new_data.Users",
    "database.history.kafka.bootstrap.servers": "localhost:9092",
    "database.history.kafka.topic": "schema-changes.new_data",
    "include.schema.changes": "true",
    "transforms": "unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones": "false",
    "transforms.unwrap.delete.handling.mode": "rewrite",
    "transforms.unwrap.add.fields": "op,source.ts_ms"
  }
}
```

#### 3.2 Register Connector

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @connector-config.json
```

### Phase 4: Create CDC Consumer

#### 4.1 Create `src/ETL/cdc_consumer.py`

```python
from kafka import KafkaConsumer
import json
from database.mongodb_connect import MongoDBConnect
from config.database_config import get_database_config

def process_debezium_event(event):
    """Process Debezium change event"""
    op = event.get('op')  # c=create, u=update, d=delete
    before = event.get('before', {})
    after = event.get('after', {})
    
    if op == 'c':  # Create
        return after
    elif op == 'u':  # Update
        return after
    elif op == 'd':  # Delete
        return {'user_id': before.get('user_id'), 'deleted': True}
    return None

def main():
    config = get_database_config()
    consumer = KafkaConsumer(
        'mysql-server.new_data.Users',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    with MongoDBConnect(config['mongodb'].uri, config['mongodb'].db_name) as mongo:
        for message in consumer:
            event = message.value
            processed = process_debezium_event(event)
            if processed:
                # Sync to MongoDB
                mongo.db.Users.update_one(
                    {'user_id': processed['user_id']},
                    {'$set': processed},
                    upsert=True
                )
                print(f"Synced event: {event.get('op')} - {processed.get('user_id')}")

if __name__ == "__main__":
    main()
```

### Phase 5: Testing

#### 5.1 Test Change Capture

```sql
-- Insert test record
INSERT INTO Users (user_id, login, gravatar_ID, avatar_url, url)
VALUES (999999, 'test_user', 'test_id', 'http://test.com', 'http://test.com');

-- Update test record
UPDATE Users SET login = 'updated_user' WHERE user_id = 999999;

-- Delete test record
DELETE FROM Users WHERE user_id = 999999;
```

#### 5.2 Verify Events in Kafka

```bash
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic mysql-server.new_data.Users \
  --from-beginning
```

### Phase 6: Cutover

#### 6.1 Stop Trigger-Based CDC

```bash
# Stop trigger_kafka.py process
# Disable triggers (optional, for clean migration)
```

#### 6.2 Start Log-Based CDC

```bash
# Start CDC consumer
python src/ETL/cdc_consumer.py
```

#### 6.3 Monitor

- Check Kafka topic lag
- Verify MongoDB sync
- Monitor Debezium connector status

## Comparison

| Aspect | Trigger-Based | Log-Based (Debezium) |
|--------|---------------|----------------------|
| **Performance** | High overhead | Minimal overhead |
| **Latency** | Polling delay (seconds) | Real-time (milliseconds) |
| **Reliability** | Can miss changes | Captures all changes |
| **Schema Changes** | Requires log tables | No schema changes |
| **Direct SQL** | May not capture | Always captures |
| **Setup Complexity** | Simple | Moderate |
| **Maintenance** | Manual polling script | Managed by Kafka Connect |
| **Scalability** | Limited | High |

## Rollback Procedures

### If Migration Fails

1. **Stop Debezium Connector**
   ```bash
   curl -X DELETE http://localhost:8083/connectors/mysql-connector
   ```

2. **Re-enable Triggers** (if disabled)
   ```sql
   -- Re-enable triggers in MySQL
   ```

3. **Restart Trigger-Based CDC**
   ```bash
   python src/ETL/trigger_kafka.py
   ```

4. **Verify Data Consistency**
   - Compare MongoDB with MySQL
   - Check for missing changes

## Troubleshooting

### Issue: Connector Not Starting

**Symptoms**: Connector shows FAILED status

**Solutions**:
- Check MySQL binlog is enabled
- Verify Debezium user permissions
- Check Kafka Connect logs
- Verify connector configuration

### Issue: No Events in Kafka

**Symptoms**: Connector running but no messages

**Solutions**:
- Check MySQL binlog position
- Verify table.include.list configuration
- Check database.include.list
- Verify topic exists

### Issue: Events Not Processing

**Symptoms**: Events in Kafka but consumer not processing

**Solutions**:
- Check consumer group offset
- Verify deserialization
- Check MongoDB connection
- Review consumer logs

### Issue: Data Inconsistency

**Symptoms**: MongoDB out of sync with MySQL

**Solutions**:
- Run initial snapshot
- Check for failed events
- Verify upsert logic
- Compare record counts

## Best Practices

1. **Initial Snapshot**: Run full snapshot before enabling CDC
2. **Monitoring**: Set up alerts for connector failures
3. **Backup**: Keep binlog backups for recovery
4. **Testing**: Test in staging before production
5. **Documentation**: Document connector configuration
6. **Version Control**: Store connector configs in Git

## Additional Resources

- [Debezium Documentation](https://debezium.io/documentation/)
- [MySQL Binlog Configuration](https://dev.mysql.com/doc/refman/8.0/en/binary-log.html)
- [Kafka Connect Guide](https://kafka.apache.org/documentation/#connect)
- [Project PLAN.md](../PLAN.md) - Phase 3 details

