# Architecture Documentation

## System Overview

This Data Engineering project implements a Lambda Architecture pattern with:
- Batch processing layer (Spark ETL)
- Streaming layer (CDC pipeline)  
- Serving layer (MongoDB data warehouse)

## Components

### 1. Data Sources

#### JSON Files
- Location: `data/sample_data.json`
- Format: GitHub Events JSON
- Schema: Nested structure with `actor` and `repo` objects
- Size: ~28,600 records

### 2. Processing Layer

#### Apache Spark
- Mode: Local[*] (all available cores)
- Memory: 4GB executor, 2GB driver
- Connectors:
  - MySQL JDBC driver
  - MongoDB Spark Connector

#### Spark Jobs
- `spark_main.py`: Main ETL pipeline
  - Read JSON with schema validation
  - Transform nested structures
  - Write to MongoDB
  - Validate data completeness

### 3. Storage Layer

#### MySQL (Operational Database)
- Purpose: CDC source (Phase 3)
- Database: `new_data`
- Table: `Users`
- Schema:
  ```sql
  CREATE TABLE Users(
      user_id BIGINT,
      login VARCHAR(255) NOT NULL,
      gravatar_ID VARCHAR(255),
      avatar_url VARCHAR(255),
      url VARCHAR(255)
  );
  ```

#### MongoDB (Analytical Database)
- Purpose: ETL destination, data warehouse
- Database: `new_data`
- Collection: `Users`
- Schema Validation:
  ```json
  {
    "bsonType": "object",
    "required": ["user_id", "login"],
    "properties": {
      "user_id": {"bsonType": "string"},
      "login": {"bsonType": "string"},
      "gravatar_ID": {"bsonType": "string"},
      "avatar_url": {"bsonType": "string"},
      "url": {"bsonType": "string"}
    }
  }
  ```

### 4. Message Queue

#### Apache Kafka
- Bootstrap Servers: `localhost:9092`
- Topics:
  - `datdepzai`: CDC events (future)
  - `huydepzai`: Consumer topic

### 5. Application Layer

#### Configuration Management
- `config/database_config.py`: Database connections from .env
- `config/spark_config.py`: Spark session configuration

#### Database Connections
- `database/mysql_connect.py`: MySQL connection with context manager
- `database/mongodb_connect.py`: MongoDB connection with context manager

#### ETL Jobs
- `src/spark/spark_main.py`: Main ETL pipeline
- `src/spark/spark_write_data.py`: Write and validation logic

#### Streaming
- `src/ETL/consumer.py`: Kafka message consumer

## Data Flow

### Batch ETL Pipeline

```
1. Source: data/sample_data.json
   ↓
2. Spark Read
   - Apply schema: StructType with actor and repo
   - Parse JSON
   ↓
3. Transform
   - Extract: actor.id → user_id
   - Extract: actor.login → login
   - Extract: actor.gravatar_id → gravatar_id
   - Extract: actor.avatar_url → avatar_url
   - Extract: actor.url → url
   - Add: spark_temp = "spark_write" (for validation)
   ↓
4. Write
   - Target: MongoDB Users collection
   - Mode: append
   ↓
5. Validate
   - Read back from MongoDB
   - Compare with source DataFrame
   - Add missing records if any
   - Remove spark_temp field
```

### CDC Pipeline (Phase 3 - Future)

```
1. MySQL Users table
   ↓ (binlog events)
2. Debezium Connector
   - Captures INSERT/UPDATE/DELETE
   - Converts to Kafka messages
   ↓
3. Kafka Topic
   - Topic: mysql-server.new_data.Users
   - Format: Debezium change event
   ↓
4. CDC Consumer
   - Parse Debezium messages
   - Transform data
   - Sync to MongoDB
```

## Design Decisions

### Why MySQL + MongoDB?

**MySQL (OLTP)**:
- Operational database
- ACID transactions
- Structured data
- CDC source

**MongoDB (OLAP)**:
- Analytical database
- Flexible schema
- Fast aggregations
- Horizontal scaling

### Why Spark?

- Distributed processing for large files
- Rich transformation APIs
- Multiple data source support
- In-memory processing

### Why Kafka?

- Decoupling producers and consumers
- Reliable message delivery
- Scalability
- Event streaming

## Performance Considerations

### Spark Optimization
- Executor Memory: 4GB
- Driver Memory: 2GB
- Cores: 2 per executor
- Partitioning: Automatic

### Data Validation
- Temporary column tracking (`spark_temp`)
- DataFrame comparison (`exceptAll`)
- Automatic reconciliation

## Security

### Current Implementation
- Environment-based configuration
- No hardcoded credentials
- Connection pooling (planned in Phase 4)

### Planned Improvements (Phase 10)
- SSL/TLS for all connections
- Secrets management (Vault/AWS Secrets Manager)
- Authentication and authorization
- Security scanning

## Scalability

### Current
- Local Spark mode
- Single MySQL instance
- Single MongoDB instance

### Future (Phase 8+)
- Spark cluster mode
- MySQL replication
- MongoDB sharding
- Kubernetes deployment

## Monitoring (Phase 7+)

Planned monitoring features:
- Prometheus metrics
- Grafana dashboards
- Alerting rules
- Health checks

## Testing (Phase 5+)

Planned testing framework:
- Unit tests (pytest)
- Integration tests
- Data quality tests
- Load testing

## Known Limitations

1. No CDC implementation yet (Phase 3)
2. No logging system (uses print statements)
3. No tests
4. No monitoring
5. Single-node deployment only

## Next Steps

See `PLAN.md` for the complete roadmap. Priority items:

1. **Phase 3**: Implement log-based CDC with Debezium
2. **Phase 4**: Add connection pooling and data validation
3. **Phase 5**: Setup testing framework
4. **Phase 6**: Complete documentation
5. **Phase 7**: Add monitoring and observability

## References

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Debezium Documentation](https://debezium.io/documentation/) (for Phase 3)
