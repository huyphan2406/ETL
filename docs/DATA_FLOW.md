# Data Flow Documentation

## Overview

This document describes how data flows through the system from source to destination.

## Current Implementation

### Batch ETL Pipeline

#### Step 1: Data Source
- **File**: `data/sample_data.json`
- **Format**: JSON (GitHub Events)
- **Size**: ~28,600 records
- **Structure**:
  ```json
  {
    "actor": {
      "id": 123,
      "login": "username",
      "gravatar_id": "",
      "url": "https://...",
      "avatar_url": "https://..."
    },
    "repo": {
      "id": 456,
      "name": "repo/name",
      "url": "https://..."
    }
  }
  ```

#### Step 2: Spark Read & Parse
- **File**: `src/spark/spark_main.py`
- **Process**:
  1. Create Spark session
  2. Define schema (StructType)
  3. Read JSON with schema validation
  4. Create DataFrame

#### Step 3: Transform
- **Operation**: Flatten nested structure
- **Transformation**:
  ```python
  actor.id → user_id (cast to string)
  actor.login → login
  actor.gravatar_id → gravatar_id
  actor.avatar_url → avatar_url
  actor.url → url
  + spark_temp = "spark_write" (temporary tracking field)
  ```

#### Step 4: Write to MongoDB
- **File**: `src/spark/spark_write_data.py`
- **Method**: `write_all_db()`
- **Destination**: MongoDB `new_data.Users` collection
- **Mode**: append
- **Connector**: MongoDB Spark Connector

#### Step 5: Validation
- **Method**: `validate_all_db()`
- **Process**:
  1. Read back from MongoDB
  2. Select same fields as written DataFrame
  3. Compare using `exceptAll()`
  4. If missing records found:
     - Write missing records
     - Log count
  5. Remove `spark_temp` field from MongoDB

#### Step 6: Cleanup
- Stop Spark session
- Close connections

### Data Transformation Example

**Input (JSON)**:
```json
{
  "actor": {
    "id": 4293484,
    "login": "cdondrup",
    "gravatar_id": "",
    "url": "https://api.github.com/users/cdondrup",
    "avatar_url": "https://avatars.githubusercontent.com/u/4293484?"
  }
}
```

**Output (MongoDB Document)**:
```json
{
  "_id": ObjectId("..."),
  "user_id": "4293484",
  "login": "cdondrup",
  "gravatar_id": "",
  "avatar_url": "https://avatars.githubusercontent.com/u/4293484?",
  "url": "https://api.github.com/users/cdondrup"
}
```

## Future Implementation (Phase 3)

### Log-Based CDC Pipeline

#### Step 1: MySQL Changes
- Application performs INSERT/UPDATE/DELETE on `Users` table
- MySQL writes to binlog (ROW format)

#### Step 2: Debezium Capture
- Debezium connector monitors MySQL binlog
- Captures all change events
- Transforms to standardized format

#### Step 3: Kafka Streaming
- Change events published to Kafka topic
- Topic format: `mysql-server.new_data.Users`
- Message format: Debezium envelope

#### Step 4: CDC Consumer Processing
- Consumer reads from Kafka
- Parses Debezium messages
- Extracts operation type (CREATE/UPDATE/DELETE)
- Extracts before/after states

#### Step 5: MongoDB Synchronization
- **CREATE**: `insertOne()` to MongoDB
- **UPDATE**: `updateOne()` or `replaceOne()`
- **DELETE**: `deleteOne()` from MongoDB

### Debezium Message Format

```json
{
  "before": {
    "user_id": 123,
    "login": "old_name",
    ...
  },
  "after": {
    "user_id": 123,
    "login": "new_name",
    ...
  },
  "source": {
    "version": "2.5.0",
    "connector": "mysql",
    "name": "mysql-server",
    "ts_ms": 1234567890,
    "db": "new_data",
    "table": "Users"
  },
  "op": "u",  // c=create, u=update, d=delete, r=read
  "ts_ms": 1234567890
}
```

## Data Consistency

### Validation Strategy

1. **Write Tracking**: Add temporary `spark_temp` field
2. **Read Back**: Query with filter `WHERE spark_temp = 'spark_write'`
3. **Compare**: Use `exceptAll()` to find differences
4. **Reconcile**: Write missing records
5. **Cleanup**: Remove temporary field

### Idempotency

- MongoDB uses `user_id` as unique index
- Duplicate writes will fail or update existing
- Ensures data consistency

## Performance Characteristics

### Batch ETL
- **Throughput**: ~1000-5000 records/second
- **Latency**: Minutes (depending on file size)
- **Use case**: Historical data, large batches

### CDC (Phase 3)
- **Throughput**: ~500-2000 events/second
- **Latency**: < 1 second
- **Use case**: Real-time sync, streaming

## Error Handling

### Current
- Try-catch blocks
- Print statements
- Basic exception propagation

### Planned (Phase 2)
- Custom exceptions
- Structured logging
- Retry logic
- Dead letter queues

## Data Quality

### Current
- Schema validation (Spark)
- Required fields check (MongoDB)
- Duplicate prevention (unique index)
- Completeness check (validation)

### Planned (Phase 4)
- Data type validation
- Business rule validation
- Null checks
- Range checks
- Custom validators

## Scalability Considerations

### Current Bottlenecks
- Single Spark driver
- Single database instances
- No connection pooling
- Local file system

### Scaling Path
1. **Phase 8**: Docker & Containerization
2. **Phase 11**: Performance Optimization
3. **Phase 15**: Production Setup
   - Spark cluster mode
   - Database replication
   - Load balancing

## Monitoring Points

### Planned Metrics (Phase 7)
- Records processed per minute
- Processing latency (p50, p95, p99)
- Error rates
- Database connection health
- Kafka lag
- Data quality metrics

## Security Considerations

### Current
- Environment variables for credentials
- No SSL/TLS
- No encryption at rest

### Planned (Phase 10)
- SSL for all connections
- Secrets management
- Audit logging
- Access control

