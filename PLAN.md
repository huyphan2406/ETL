# EXTENDED PLAN: 100% Production-Ready Data Engineering Project

## Overview
Complete implementation plan to transform the Data Engineering project from current state to enterprise-grade production-ready system.

**Total Phases**: 16  
**Estimated Duration**: 12-13 weeks  
**Target Completion**: 100% Production-Ready

---

## PHASE 1: Fix Critical Bugs (Week 1, Days 1-2)

### 1.1 Fix SQL Injection Vulnerability
- **File**: `src/ETL/trigger_kafka.py` (line 21)
- **Issue**: SQL injection in query with `last_timestamp`
- **Solution**: Use parameterized queries: `cursor.execute(query, (last_timestamp,))`
- **Priority**: CRITICAL - Security

### 1.2 Fix Import Error
- **Status**: ✅ COMPLETED - Redis removed from project
- **Note**: Redis functionality has been removed as it was not being used

### 1.3 Fix Tuple Assignment Bug
- **File**: `config/spark_config.py` (line 18)
- **Issue**: `self.app_name = app_name,` creates tuple instead of string
- **Solution**: Remove comma: `self.app_name = app_name`
- **Priority**: CRITICAL - Breaks functionality

### 1.4 Fix Wrong Collection Name
- **File**: `database/schema.py` (line 43)
- **Issue**: `db.Users12345.create_index` wrong collection name
- **Solution**: Change to `db.Users.create_index("user_id", unique=True)`
- **Priority**: CRITICAL - Breaks functionality

### 1.5 Remove Hardcoded Paths
- **Files**: `database/schema.py`, `src/spark/spark_main.py`
- **Issue**: Hardcoded Windows paths
- **Solution**: Use `Path(__file__).parent.parent` for relative paths
- **Priority**: HIGH - Portability

---

## PHASE 2: Code Quality Improvements (Week 1, Days 3-5)

### 2.1 Implement Logging System
- **New File**: `src/utils/logger.py`
- **Features**:
  - Configure logging với file và console handlers
  - Log rotation (RotatingFileHandler)
  - Different log levels per environment
  - Structured logging format
- **Replace**: All `print()` statements with `logger.info/warning/error`
- **Files to Update**: All Python files
- **Priority**: HIGH

### 2.2 Standardize Error Handling
- **New File**: `src/utils/exceptions.py`
- **Custom Exceptions**:
  - `DatabaseConnectionError`
  - `DataValidationError`
  - `CDCProcessingError`
  - `SparkJobError`
- **Update**: All try-except blocks to use custom exceptions
- **Priority**: HIGH

### 2.3 Fix Code Duplication
- **File**: `src/spark/spark_write_data.py`
- **Issue**: Multiple calls to `get_spark_config()`
- **Solution**: Cache config in `__init__` method
- **Priority**: MEDIUM

### 2.4 Add Constants Module
- **New File**: `src/utils/constants.py`
- **Content**:
  - Magic strings ("spark_write", "Users", etc.)
  - Enums for modes, states
  - Default values
- **Priority**: MEDIUM

### 2.5 Improve Type Hints
- **Files**: All Python files
- **Action**: Add complete type hints for all functions and methods
- **Tool**: Use mypy for validation
- **Priority**: MEDIUM

---

## PHASE 3: Migrate to Log-Based CDC (Week 2)

### 3.1 Research và Setup CDC Tool
- **Decision**: Debezium (recommended)
- **Alternatives**: Maxwell, MySQL binlog reader
- **Documentation**: Create comparison document
- **Priority**: HIGH

### 3.2 Setup Debezium Infrastructure
- **Tasks**:
  - Install Kafka Connect
  - Download Debezium MySQL connector
  - Configure MySQL binlog (`log_bin`, `binlog_format=ROW`)
  - Create Debezium connector configuration JSON
- **Files**:
  - `debezium/mysql-connector.json` (new)
  - `scripts/setup-debezium.sh` (new)
- **Priority**: HIGH

### 3.3 Create New CDC Consumer
- **New File**: `src/ETL/cdc_consumer.py`
- **Features**:
  - Consume from Debezium Kafka topics
  - Parse Debezium change event format
  - Transform data (before/after states)
  - Handle CREATE/UPDATE/DELETE operations
  - Error handling và retry logic
- **Priority**: HIGH

### 3.4 Update Consumer Logic
- **File**: `src/ETL/consumer.py`
- **Updates**:
  - Proper deserialization for Debezium format
  - Consumer group management
  - Offset management
  - Batch processing
  - Error recovery
- **Priority**: HIGH

### 3.5 Migration Strategy
- **Approach**:
  1. Run both trigger-based and log-based CDC in parallel
  2. Compare outputs for validation
  3. Switch traffic to log-based
  4. Deprecate trigger-based after stability
- **File**: `docs/CDC_MIGRATION_STRATEGY.md` (new)
- **Priority**: HIGH

### 3.6 Remove Trigger Dependencies
- **Files**: `sql/trigger.sql`, `src/ETL/trigger_kafka.py`
- **Action**: Mark as deprecated, remove after migration complete
- **Priority**: LOW (after migration)

---

## PHASE 4: Database & Infrastructure Improvements (Week 3, Days 1-3)

### 4.1 Implement Redis Support
- **Status**: ❌ CANCELLED - Redis removed from project
- **Reason**: Redis was not being used in the ETL pipeline
- **Priority**: N/A

### 4.2 Add Connection Pooling
- **Files**: `database/*_connect.py`
- **Implementation**:
  - MySQL: Use `mysql.connector.pooling`
  - MongoDB: Reuse connections
- **New File**: `database/connection_pool.py` (new)
- **Priority**: HIGH

### 4.3 Improve Data Validation
- **New File**: `src/utils/data_validator.py`
- **Features**:
  - Schema validation
  - Null checks
  - Data type validation
  - Business rule validation
  - Custom validators
- **Priority**: HIGH

### 4.4 Fix Temporary Column Logic
- **File**: `src/spark/spark_write_data.py`
- **Issue**: `spark_temp` column may already exist
- **Solution**: Check column existence before ALTER TABLE
- **Priority**: MEDIUM

---

## PHASE 5: Testing & Quality Assurance (Week 3, Days 4-5 + Week 4, Days 1-2)

### 5.1 Setup Testing Framework
- **New Directory**: `tests/`
- **Structure**:
  - `tests/unit/`
  - `tests/integration/`
  - `tests/fixtures/`
  - `tests/conftest.py`
- **Dependencies**: pytest, pytest-cov, pytest-mock
- **Configuration**: `pytest.ini`, `.coveragerc`
- **Priority**: HIGH

### 5.2 Unit Tests
- **Directory**: `tests/unit/`
- **Coverage**:
  - Database connection classes
  - Config validation
  - Data transformation logic
  - Validation functions
  - Utility functions
- **Target**: 80%+ coverage
- **Priority**: HIGH

### 5.3 Integration Tests
- **Directory**: `tests/integration/`
- **Coverage**:
  - End-to-end ETL pipeline
  - CDC flow (both trigger and log-based)
  - Spark write operations
  - Kafka producer/consumer
  - Database operations
- **Priority**: HIGH

### 5.4 Data Quality Tests
- **Directory**: `tests/data_quality/`
- **Tests**:
  - Schema validation
  - Data completeness
  - Data accuracy
  - Consistency checks
- **Priority**: MEDIUM

---

## PHASE 6: Documentation & Production Readiness (Week 4, Days 3-5)

### 6.1 Create README
- **File**: `README.md` (new)
- **Sections**:
  - Project overview
  - Architecture diagram
  - Prerequisites
  - Installation instructions
  - Configuration guide
  - Usage examples
  - Contributing guidelines
- **Priority**: HIGH

### 6.2 API Documentation
- **Tool**: Sphinx or mkdocs
- **Files**: Docstrings in all code files
- **Generate**: `docs/api/` (new)
- **Priority**: MEDIUM

### 6.3 CDC Migration Guide
- **File**: `docs/CDC_MIGRATION.md` (new)
- **Content**:
  - Comparison trigger vs log-based
  - Step-by-step migration guide
  - Rollback procedures
  - Troubleshooting
- **Priority**: HIGH

### 6.4 Environment Configuration
- **File**: `.env.example` (new)
- **Content**: Template with all required variables
- **Priority**: HIGH

---

## PHASE 7: Monitoring & Observability (Week 5, Days 1-3)

### 7.1 Add Metrics
- **File**: `src/utils/metrics.py` (new)
- **Metrics**:
  - Records processed
  - Processing latency
  - Error rates
  - Database connection health
- **Integration**: Prometheus
- **Priority**: HIGH

### 7.2 Health Checks
- **File**: `src/utils/health.py` (new)
- **Checks**:
  - Database connectivity
  - Kafka broker status
  - CDC connector status
  - Spark cluster health
- **Priority**: HIGH

### 7.3 Alerting Setup
- **Integration**: Prometheus + Alertmanager
- **File**: `monitoring/alerts.yml` (new)
- **Alerts**: Failed jobs, high latency, connection failures
- **Priority**: MEDIUM

---

## PHASE 8: Docker & Containerization (Week 5, Days 4-5 + Week 6, Days 1-2)

### 8.1 Dockerfile cho Application
- **File**: `Dockerfile` (new)
- **Features**:
  - Multi-stage build
  - Python 3.12 base
  - Non-root user
  - Health checks
- **Priority**: HIGH

### 8.2 Docker Compose Setup
- **File**: `docker-compose.yml` (new)
- **Services**: MySQL, MongoDB, Redis, Kafka, Zookeeper, Kafka Connect, Spark, App, Prometheus, Grafana
- **Priority**: HIGH

### 8.3 Environment-Specific Configs
- **Files**: 
  - `docker-compose.dev.yml` (new)
  - `docker-compose.prod.yml` (new)
  - `.dockerignore` (new)
- **Priority**: MEDIUM

### 8.4 Health Checks
- **File**: `src/utils/health.py` (extend)
- **Features**: HTTP health check endpoint
- **Priority**: HIGH

---

## PHASE 9: CI/CD Pipeline (Week 6, Days 3-5)

### 9.1 GitHub Actions Setup
- **File**: `.github/workflows/ci.yml` (new)
- **Jobs**:
  - Lint code (flake8, black, mypy)
  - Run unit tests
  - Run integration tests
  - Build Docker images
  - Security scanning
  - Code coverage
- **Priority**: HIGH

### 9.2 Deployment Pipeline
- **File**: `.github/workflows/deploy.yml` (new)
- **Stages**: Build, test, push, deploy staging, smoke tests, deploy prod
- **Priority**: HIGH

### 9.3 Pre-commit Hooks
- **File**: `.pre-commit-config.yaml` (new)
- **Hooks**: Black, Flake8, MyPy, Bandit
- **Priority**: MEDIUM

---

## PHASE 10: Security Hardening (Week 7)

### 10.1 Secrets Management
- **File**: `src/utils/secrets.py` (new)
- **Integration**: AWS Secrets Manager / HashiCorp Vault
- **Features**: Secret rotation, encrypted storage
- **Priority**: HIGH

### 10.2 SSL/TLS Configuration
- **File**: `config/ssl_config.py` (new)
- **Updates**: SSL for all database connections, Kafka SSL
- **Priority**: HIGH

### 10.3 Authentication & Authorization
- **Directory**: `src/auth/` (new)
- **Features**: API keys, RBAC, audit logging
- **Priority**: MEDIUM

### 10.4 Security Scanning
- **Files**: 
  - `security/requirements-audit.txt` (new)
  - `.snyk` (new)
- **Tools**: Bandit, Safety, Snyk
- **Priority**: HIGH

---

## PHASE 11: Performance Optimization (Week 8)

### 11.1 Spark Optimization
- **File**: `config/spark_optimization.py` (new)
- **Optimizations**: Dynamic partition pruning, broadcast joins, caching, partitioning
- **Priority**: MEDIUM

### 11.2 Database Query Optimization
- **Directory**: `sql/optimization/` (new)
- **Content**: Index scripts, query analysis
- **Priority**: MEDIUM

### 11.3 Kafka Consumer Tuning
- **File**: `src/ETL/consumer_config.py` (new)
- **Settings**: Batch size, parallelism, offset management
- **Priority**: MEDIUM

### 11.4 Caching Strategy
- **File**: `src/utils/cache.py` (new)
- **Features**: Redis caching, invalidation, TTL
- **Priority**: MEDIUM

---

## PHASE 12: Disaster Recovery & Backup (Week 9)

### 12.1 Backup Scripts
- **Directory**: `scripts/backup/` (new)
- **Scripts**: MySQL, MongoDB, Redis, Kafka offsets
- **Priority**: HIGH

### 12.2 Backup Automation
- **File**: `scripts/backup/backup_scheduler.py` (new)
- **Features**: Scheduled backups, retention, verification, cloud storage
- **Priority**: HIGH

### 12.3 Disaster Recovery Plan
- **File**: `docs/DISASTER_RECOVERY.md` (new)
- **Content**: Recovery procedures, RTO/RPO, failover
- **Priority**: MEDIUM

### 12.4 Point-in-Time Recovery
- **Directory**: `scripts/recovery/` (new)
- **Features**: PITR scripts, oplog replay, consistency checks
- **Priority**: MEDIUM

---

## PHASE 13: Advanced Monitoring & Alerting (Week 10)

### 13.1 Distributed Tracing
- **File**: `src/utils/tracing.py` (new)
- **Integration**: OpenTelemetry / Jaeger
- **Features**: Request tracing, performance analysis
- **Priority**: MEDIUM

### 13.2 Advanced Metrics
- **File**: `src/utils/metrics.py` (extend)
- **Metrics**: Business, infrastructure, custom, cost tracking
- **Priority**: MEDIUM

### 13.3 Alerting Rules
- **File**: `monitoring/alerts.yml` (extend)
- **Alerts**: Error rates, latency, resources, data quality, downtime
- **Priority**: MEDIUM

### 13.4 Dashboards
- **Directory**: `monitoring/grafana/dashboards/` (new)
- **Dashboards**: System overview, ETL health, database, Kafka, Spark
- **Priority**: MEDIUM

---

## PHASE 14: Load Testing & Performance Testing (Week 11)

### 14.1 Load Testing Framework
- **Directory**: `tests/load/` (new)
- **Tools**: Locust, k6, or custom scripts
- **Tests**: High volume ingestion, concurrent consumers, database load, Spark stress
- **Priority**: LOW

### 14.2 Performance Benchmarks
- **File**: `tests/performance/benchmarks.py` (new)
- **Metrics**: Throughput, latency (p50/p95/p99), resource utilization
- **Priority**: LOW

### 14.3 Capacity Planning
- **File**: `docs/CAPACITY_PLANNING.md` (new)
- **Content**: Resource requirements, scaling strategies, cost estimates
- **Priority**: LOW

---

## PHASE 15: Production Environment Setup (Week 12)

### 15.1 Production Configuration
- **Directory**: `config/production/` (new)
- **Content**: Environment-specific configs, resource limits, security policies
- **Priority**: HIGH

### 15.2 Graceful Shutdown
- **File**: `src/utils/shutdown.py` (new)
- **Features**: Signal handlers, in-flight completion, resource cleanup
- **Priority**: HIGH

### 15.3 Resource Management
- **Directory**: `kubernetes/` (new, if using K8s)
- **Content**: Resource quotas, limit ranges, HPA
- **Priority**: MEDIUM

### 15.4 Multi-Environment Support
- **File**: `config/environments.py` (new)
- **Features**: Environment detection, config switching, feature flags
- **Priority**: HIGH

---

## PHASE 16: Documentation & Runbooks (Week 13)

### 16.1 API Documentation
- **File**: `docs/API.md` (new)
- **Tool**: OpenAPI/Swagger
- **Content**: API endpoints, schemas, examples
- **Priority**: MEDIUM

### 16.2 Runbooks
- **Directory**: `docs/runbooks/` (new)
- **Content**: Common issues, troubleshooting, maintenance, emergency procedures
- **Priority**: MEDIUM

### 16.3 Architecture Documentation
- **File**: `docs/ARCHITECTURE.md` (new)
- **Content**: System architecture, data flow, component interactions, tech stack
- **Priority**: HIGH

### 16.4 Onboarding Guide
- **File**: `docs/ONBOARDING.md` (new)
- **Content**: Dev setup, local environment, contribution guidelines, code review
- **Priority**: MEDIUM
















# PHASE 3: CDC Migration Guide - Hướng Dẫn Chi Tiết Từng Bước

## Mục Lục
1. [Tổng Quan về CDC](#tổng-quan-về-cdc)
2. [Chuẩn Bị](#chuẩn-bị)
3. [Bước 1: Cấu Hình MySQL Binlog](#bước-1-cấu-hình-mysql-binlog)
4. [Bước 2: Cài Đặt Kafka Connect](#bước-2-cài-đặt-kafka-connect)
5. [Bước 3: Download Debezium Connector](#bước-3-download-debezium-connector)
6. [Bước 4: Tạo Debezium Connector Config](#bước-4-tạo-debezium-connector-config)
7. [Bước 5: Khởi Động Kafka Connect](#bước-5-khởi-động-kafka-connect)
8. [Bước 6: Tạo CDC Consumer](#bước-6-tạo-cdc-consumer)
9. [Bước 7: Test và Validation](#bước-7-test-và-validation)
10. [Troubleshooting](#troubleshooting)

---

## Tổng Quan về CDC

### CDC là gì?
**Change Data Capture (CDC)** là kỹ thuật theo dõi và capture các thay đổi trong database.

### So sánh Trigger-based vs Log-based CDC

| Tiêu chí | Trigger-based (Hiện tại) | Log-based (Debezium) |
|----------|-------------------------|----------------------|
| **Cách hoạt động** | MySQL triggers → Log tables → Poll | MySQL binlog → Debezium → Kafka |
| **Performance** | Chậm (polling) | Real-time |
| **Overhead** | Tăng tải database | Không tăng tải |
| **Reliability** | Có thể miss events | Không miss events |
| **Setup** | Đơn giản | Phức tạp hơn |

### Tại sao chọn Debezium?
- ✅ Enterprise-grade, được Red Hat maintain
- ✅ Tích hợp tốt với Kafka ecosystem
- ✅ Hỗ trợ nhiều databases (MySQL, PostgreSQL, MongoDB, etc.)
- ✅ Schema evolution support
- ✅ Transaction support

---

## Chuẩn Bị

### Yêu Cầu Hệ Thống
- ✅ MySQL 5.7+ hoặc 8.0+
- ✅ Kafka đã cài đặt và chạy
- ✅ Zookeeper (nếu dùng Kafka < 2.8)
- ✅ Java 11+ (cho Kafka Connect)
- ✅ Python 3.8+ (cho consumer)

### Kiểm Tra Trạng Tháih
# Kiểm tra MySQL đang chạy
mysql --version

# Kiểm tra Kafka đang chạy
kafka-topics.sh --list --bootstrap-server localhost:9092

# Kiểm tra Java version
java -version---

## Bước 1: Cấu Hình MySQL Binlog

### 1.1 Tìm MySQL Config File

**Windows:**
- Thường ở: `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`
- Hoặc: `C:\Program Files\MySQL\MySQL Server 8.0\my.ini`

**Linux/Mac:**
- Thường ở: `/etc/mysql/my.cnf` hoặc `/etc/my.cnf`

### 1.2 Backup Config Filel
# Windows (PowerShell)
Copy-Item "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini" "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini.backup"
### 1.3 Thêm Binlog Configuration

Mở file `my.ini` (Windows) và thêm vào section `[mysqld]`:

[mysqld]
# Enable binary logging
log_bin = mysql-bin
binlog_format = ROW
binlog_row_image = FULL

# Server ID (unique cho mỗi MySQL server)
server_id = 1

# Binlog retention (optional - giữ logs trong 7 ngày)
expire_logs_days = 7
max_binlog_size = 100M**Giải thích:**
- `log_bin = mysql-bin`: Bật binary logging
- `binlog_format = ROW`: Format ROW để capture đầy đủ thay đổi
- `binlog_row_image = FULL`: Capture cả before và after image
- `server_id = 1`: ID duy nhất cho server

### 1.4 Restart MySQL

**Windows (PowerShell):**l
# Tìm tên service
Get-Service | Where-Object {$_.Name -like "*mysql*"}

# Restart (thay MySQL80 bằng tên service của bạn)
Restart-Service MySQL80### 1.5 Verify Binlog Đã Bật

Kết nối MySQL và chạy:ql
SHOW VARIABLES LIKE 'log_bin';
-- Kết quả: log_bin = ON

SHOW VARIABLES LIKE 'binlog_format';
-- Kết quả: binlog_format = ROW

SHOW BINARY LOGS;
-- Sẽ hiển thị danh sách binlog files### 1.6 Tạo User cho Debezium

-- Tạo user
CREATE USER 'debezium'@'localhost' IDENTIFIED BY 'debezium_password';

-- Cấp quyền
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'localhost';

FLUSH PRIVILEGES;

-- Verify
SHOW GRANTS FOR 'debezium'@'localhost';---

## Bước 2: Cài Đặt Kafka Connect

### 2.1 Download Kafka (nếu chưa có)

Download từ: https://kafka.apache.org/downloads

### 2.2 Cấu Hình Kafka Connect

Tạo file: `config/connect-standalone.properties`

# Kafka Connect Standalone Config
bootstrap.servers=localhost:9092

# Plugin path - nơi đặt Debezium connector
plugin.path=libs

# Key và value converters
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
key.converter.schemas.enable=false
value.converter.schemas.enable=false

# Offset storage
offset.storage.file.filename=/tmp/connect.offsets
offset.flush.interval.ms=10000

# Rest API (optional)
rest.host.name=localhost
rest.port=8083### 2.3 Tạo Thư Mục

# Windows
mkdir libs
mkdir logs---

## Bước 3: Download Debezium Connector

### 3.1 Download Debezium MySQL Connector

**Windows (PowerShell):**
cd libs
mkdir debezium-connector-mysql
cd debezium-connector-mysql

# Download (version 2.5.0)
Invoke-WebRequest -Uri "https://repo1.maven.org/maven2/io/debezium/debezium-connector-mysql/2.5.0.Final/debezium-connector-mysql-2.5.0.Final-plugin.tar.gz" -OutFile "debezium.tar.gz"

# Giải nén (cần 7-Zip hoặc tar)
# Nếu có tar:
tar -xzf debezium.tar.gz**Hoặc download manual:**
1. Vào: https://repo1.maven.org/maven2/io/debezium/debezium-connector-mysql/
2. Chọn version mới nhất (ví dụ: 2.5.0.Final)
3. Download file: `debezium-connector-mysql-2.5.0.Final-plugin.tar.gz`
4. Giải nén vào `libs/debezium-connector-mysql/`

---

## Bước 4: Tạo Debezium Connector Config

### 4.1 Tạo Thư Mục
shell
mkdir debezium### 4.2 Tạo Connector Configuration

Tạo file: `debezium/mysql-connector.json`
on
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
    "database.history.kafka.topic": "schema-changes.mysql-server",
    "include.schema.changes": "true",
    "snapshot.mode": "initial",
    "snapshot.locking.mode": "minimal",
    "transforms": "unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones": "false",
    "transforms.unwrap.delete.handling.mode": "rewrite",
    "transforms.unwrap.add.fields": "op,source.ts_ms"
  }
}**Lưu ý:** Thay các giá trị:
- `database.hostname`: Host MySQL của bạn
- `database.user`: User Debezium (đã tạo ở bước 1.6)
- `database.password`: Password của user
- `database.include.list`: Database name (ví dụ: "new_data")
- `table.include.list`: Table name (ví dụ: "new_data.Users")

---

## Bước 5: Khởi Động Kafka Connect

### 5.1 Start Zookeeper (nếu cần)
rshell
# Trong thư mục Kafka
bin\windows\zookeeper-server-start.bat config\zookeeper.properties### 5.2 Start Kafka Broker
ll
bin\windows\kafka-server-start.bat config\server.properties### 5.3 Start Kafka Connect
ll
bin\windows\connect-standalone.bat config\connect-standalone.properties debezium\mysql-connector.json### 5.4 Verify Connector Đã Chạy

**Kiểm tra logs:**
- Tìm dòng: `Connector mysql-connector started`

**Kiểm tra Kafka topics:**shell
bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092

# Sẽ thấy topics:
# - mysql-server.new_data.Users (change events)
# - schema-changes.mysql-server (schema changes)---

## Bước 6: Tạo CDC Consumer

Tạo file: `src/ETL/cdc_consumer.py`
n
"""
CDC Consumer for Debezium change events.
"""
import json
from typing import Dict, Any, Optional
from kafka import KafkaConsumer
from kafka.errors import KafkaError as KafkaLibError
from src.utils.logger import get_logger
from src.utils.exceptions import KafkaError, CDCProcessingError
from src.utils.constants import DEFAULT_CONSUMER_GROUP, DEFAULT_POLL_TIMEOUT_MS


logger = get_logger("CDCConsumer")


class DebeziumMessage:
    """Wrapper class for Debezium change event."""
    
    def __init__(self, message: Dict[str, Any]):
        self.raw = message
        self.before = message.get("before")
        self.after = message.get("after")
        self.source = message.get("source", {})
        self.op = message.get("op")  # c=create, u=update, d=delete, r=read
        
    @property
    def operation(self) -> str:
        """Get operation type as string."""
        op_map = {
            "c": "CREATE",
            "u": "UPDATE", 
            "d": "DELETE",
            "r": "READ"
        }
        return op_map.get(self.op, "UNKNOWN")
    
    @property
    def table(self) -> str:
        """Get table name."""
        return self.source.get("table", "")
    
    def get_data(self) -> Optional[Dict[str, Any]]:
        """Get the actual data."""
        if self.op == "d":
            return self.before
        return self.after


class CDCConsumer:
    """Consumer for Debezium CDC messages."""
    
    def __init__(
        self,
        topic: str,
        bootstrap_servers: list = None,
        group_id: str = DEFAULT_CONSUMER_GROUP
    ):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers or ["localhost:9092"]
        self.group_id = group_id
        self.consumer: Optional[KafkaConsumer] = None
        self.logger = get_logger("CDCConsumer")
        
    def create_consumer(self) -> KafkaConsumer:
        """Create Kafka consumer."""
        try:
            consumer = KafkaConsumer(
                self.topic,
                group_id=self.group_id,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode("utf-8")) if x else None
            )
            self.logger.info(f"CDC Consumer created for topic: {self.topic}")
            return consumer
        except Exception as e:
            self.logger.error(f"Failed to create CDC consumer: {e}")
            raise KafkaError(f"Failed to create CDC consumer: {e}") from e
    
    def process_change_event(self, message: DebeziumMessage) -> None:
        """Process a Debezium change event."""
        try:
            operation = message.operation
            data = message.get_data()
            
            if not data:
                return
            
            self.logger.info(
                f"{operation} on {message.table}: user_id={data.get('user_id', 'N/A')}"
            )
            
            # TODO: Implement your logic here
            # Ví dụ: Sync to MongoDB, update cache, etc.
                
        except Exception as e:
            self.logger.error(f"Error processing change event: {e}")
            raise CDCProcessingError(f"Failed to process: {e}") from e
    
    def consume(self, timeout_ms: int = DEFAULT_POLL_TIMEOUT_MS) -> None:
        """Start consuming messages."""
        if not self.consumer:
            self.consumer = self.create_consumer()
        
        self.logger.info(f"Starting to consume from topic: {self.topic}")
        
        try:
            while True:
                try:
                    msg_pack = self.consumer.poll(timeout_ms=timeout_ms)
                    
                    if not msg_pack:
                        continue
                    
                    for topic_partition, messages in msg_pack.items():
                        for kafka_message in messages:
                            try:
                                debezium_msg = DebeziumMessage(kafka_message.value)
                                self.process_change_event(debezium_msg)
                            except Exception as e:
                                self.logger.error(f"Error: {e}")
                                continue
                                
                except KafkaLibError as e:
                    self.logger.error(f"Kafka error: {e}")
                    raise KafkaError(f"Kafka error: {e}") from e
                    
        except KeyboardInterrupt:
            self.logger.info("Consumer interrupted")
        finally:
            if self.consumer:
                self.consumer.close()


def main() -> None:
    """Main function."""
    # Topic format: <database.server.name>.<database>.<table>
    topic = "mysql-server.new_data.Users"
    
    try:
        consumer = CDCConsumer(topic=topic)
        consumer.consume()
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        raise


if __name__ == "__main__":
    main()---

## Bước 7: Test và Validation

### 7.1 Test với MySQL

USE new_data;

-- INSERT
INSERT INTO Users (user_id, login, gravatar_ID, avatar_url, url) 
VALUES (999, 'test_user', 'test123', 'https://test.com/avatar', 'https://test.com/user');

-- UPDATE
UPDATE Users SET login = 'test_user_updated' WHERE user_id = 999;

-- DELETE
DELETE FROM Users WHERE user_id = 999;### 7.2 Chạy Consumer
owershell
python src/ETL/cdc_consumer.pyBạn sẽ thấy logs: