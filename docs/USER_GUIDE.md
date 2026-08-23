# PyDataShred (`datashredpy`) - Complete User Guide

> **Version:** 2.0.0  
> **Author:** Raghavendran Ravichandran  
> **License:** Apache-2.0  

---

## Table of Contents
1. [Introduction & Core Philosophy](#1-introduction--core-philosophy)
2. [Installation & Dependency Sets](#2-installation--dependency-sets)
3. [Architecture & The Entity Model](#3-architecture--the-entity-model)
4. [Data Ingestion Engine (`Data.read`)](#4-data-ingestion-engine-dataread)
   - [Reading with Pandas (In-Memory)](#reading-with-pandas-in-memory)
   - [Reading with PySpark (Distributed)](#reading-with-pyspark-distributed)
   - [Supported File Formats & Connectors](#supported-file-formats--connectors)
5. [Spark Session Utilities (`SparkSessionOption`)](#5-spark-session-utilities-sparksessionoption)
6. [Slowly Changing Dimensions (SCD Type 2)](#6-slowly-changing-dimensions-scd-type-2)
   - [Audit Column Mechanics](#audit-column-mechanics)
   - [Single vs Composite Business Keys](#single-vs-composite-business-keys)
7. [DataMesh & Data Product Framework](#7-datamesh--data-product-framework)
   - [DataProduct & DataProductContract](#dataproduct--dataproductcontract)
   - [Quality Rule Engine](#quality-rule-engine)
   - [Service Level Agreements (SLAs)](#service-level-agreements-slas)
8. [Federated Governance (Policy-as-Code)](#8-federated-governance-policy-as-code)
   - [Built-in Governance Policies](#built-in-governance-policies)
   - [Custom Policy Implementation](#custom-policy-implementation)
9. [3-Phase Pipeline Orchestration (`DataProductPipeline`)](#9-3-phase-pipeline-orchestration-dataproductpipeline)
10. [Discovery Portal REST API](#10-discovery-portal-rest-api)
11. [Deployment & Multi-Cloud Strategies](#11-deployment--multi-cloud-strategies)
12. [Troubleshooting & FAQ](#12-troubleshooting--faq)

---

## 1. Introduction & Core Philosophy

**PyDataShred** (`datashredpy`) is an enterprise-grade Python platform engineered to unify and streamline:
1. **Multi-Source Data Ingestion**: Abstracting low-level reader logic across CSV, TSV, JSON, Parquet, Delta Lake, Excel, XML, Snowflake Snowpark, and REST APIs.
2. **Automated SCD Type 2 Transformation**: Managing historical dimensional states, timestamp lifecycles, and active/expired flags automatically.
3. **DataMesh Governance**: Elevating raw pipelines into discoverable, governed **Data Products** governed by machine-enforceable contracts and policy-as-code.

---

## 2. Installation & Dependency Sets

PyDataShred is modularized to avoid heavy dependencies when deployed in lightweight serverless containers:

```bash
# Minimal base installation (FastAPI & Pydantic)
pip install pydatashred

# In-Memory Pandas stack (Excel, XML, JSON, CSV)
pip install "pydatashred[pandas]"

# Big Data Distributed stack (PySpark)
pip install "pydatashred[pyspark]"

# AWS Cloud integrations (Boto3, S3, DynamoDB, RDS)
pip install "pydatashred[aws]"

# Complete enterprise suite
pip install "pydatashred[all]"
```

---

## 3. Architecture & The Entity Model

PyDataShred represents enterprise data topologies hierarchically:

```
Client (e.g. Enterprise Client / Airline)
  └── Domain (e.g. Avionics, CustomerAnalytics, Billing)
        └── App (e.g. MechanicLogIngest, TransactionProcessor)
              └── Resources (Source ──▶ Target)
                    ├── AWS S3 / RDS / DynamoDB
                    ├── Snowflake Snowpark
                    └── On-Premises NAS / Local Storage
```

### Creating Entities with `CreateEntity`

```python
from datashredpy.core.delegator import CreateEntity
from datashredpy.helper.models import Domain, App, Resources, Aws, S3, Bucket

domain_data = {
    "domain_id": 101,
    "domain_name": "CustomerAnalytics",
    "app": App(
        app_id=1,
        app_name="CustomerIngest",
        resources=Resources(
            source=Aws(url="s3.amazonaws.com", region="us-east-1", s3=S3(bucket=Bucket("raw-cust", "inbound/", "cust.csv"))),
            target=None
        )
    )
}

entity = CreateEntity(entity_type="domain", entity_data=domain_data)
```

---

## 4. Data Ingestion Engine (`Data.read`)

The `Data` class provides a single, uniform method `Data.read()` to ingest any supported format.

### Method Signature

```python
Data.read(
    rel_path: str,
    api_type: ApiType = None,
    file_type: FileType = None,
    db_type: DbType = None,
    use_pandas: Optional[bool] = False,
    use_spark: Optional[bool] = True,
    snowpark_options: Optional[dict] = False,
    **options
)
```

### Reading with Pandas (In-Memory)

```python
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType

# Ingest CSV into a Pandas DataFrame
df_csv = Data.read("data/customers.csv", file_type=FileType.CSV, use_pandas=True)

# Ingest Excel spreadsheet
df_excel = Data.read("data/quarterly_report.xlsx", file_type=FileType.EXCEL, use_pandas=True)

# Ingest XML file into flat DataFrame
df_xml = Data.read("data/feed.xml", file_type=FileType.XML, use_pandas=True)
```

### Reading with PySpark (Distributed)

```python
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType

# Read Parquet directory
df_parquet = Data.read("data/telemetry.parquet", file_type=FileType.PARQUET, use_spark=True)

# Read Delta Lake ACID table
df_delta = Data.read("/mnt/delta/gold_orders", file_type=FileType.DELTA, use_spark=True)

# Read from Snowflake via Snowpark
df_snow = Data.read(
    "ANALYTICS.CUSTOMERS",
    file_type=FileType.SNOWFLAKE,
    use_spark=True,
    snowpark_options={"account": "org_account", "user": "SERVICE_USER"}
)
```

---

## 5. Spark Session Utilities (`SparkSessionOption`)

`SparkSessionOption` manages thread-safe singleton PySpark instances:

```python
from datashredpy.utilities.init_spark import SparkSessionOption

# Get or create Singleton Spark session
spark = SparkSessionOption.get_spark_instance(
    app_name="DataShred_Production_Job",
    master="local[*]",
    config_options={
        "spark.executor.memory": "4g",
        "spark.sql.shuffle.partitions": "16"
    },
    snow_spark=False  # Set True to load Snowflake Spark connector JARs
)
```

---

## 6. Slowly Changing Dimensions (SCD Type 2)

Slowly Changing Dimensions (Type 2) captures every state update as a distinct row with validity date boundaries and active flags.

### The `ETL.apply_scd2` Workflow

```python
from datashredpy.helper.transform import ETL

# Initialize ETL with source delta and current target dimension
scd_handler = ETL(
    source_df=df_source_spark,
    target_df=df_target_spark,
    key_columns="customer_id"  # Supports list: ["store_id", "product_sku"]
)

# Apply SCD Type 2 logic
df_final = scd_handler.apply_scd2()
```

### Automated Audit Lifecycle
- **New Records**: Inserted with `start_date = current_timestamp()`, `end_date = NULL`, `etl_flag = 'current'`.
- **Changed Records**: 
  - Old row: `end_date` updated to `current_timestamp()`, `etl_flag` updated to `'expired'`.
  - New row: Inserted with `start_date = current_timestamp()`, `end_date = NULL`, `etl_flag = 'current'`.
- **Unchanged Records**: Retained in their existing state.

---

## 7. DataMesh & Data Product Framework

A **Data Product** bundles dataset storage, operational logic, schemas, and governance rules into an autonomous, discoverable asset.

```python
from datashredpy.datamesh import (
    DataProduct, DataProductContract, Schema, SchemaField,
    DataType, DataQualityRule, SLA, ComplianceLevel
)

# 1. Schema Contract
schema = Schema(
    version="1.0.0",
    fields=[
        SchemaField("account_id", DataType.STRING, nullable=False),
        SchemaField("balance", DataType.DECIMAL, nullable=False, constraints={"min": 0}),
        SchemaField("email", DataType.STRING, nullable=False)
    ]
)

# 2. Quality Rules
rules = [
    DataQualityRule(rule_id="q1", name="Unique Account", rule_type="uniqueness", applies_to=["account_id"], threshold=1.0),
    DataQualityRule(rule_id="q2", name="Valid Balance", rule_type="range", applies_to=["balance"], threshold=0.99)
]

# 3. SLA
sla = SLA(freshness_hours=4, availability_percent=99.9, max_latency_seconds=600)

# 4. Enforceable Contract
contract = DataProductContract(
    contract_id="acc-v1.0.0",
    product_id="account-balances",
    schema=schema,
    quality_rules=rules,
    sla=sla,
    compliance_level=ComplianceLevel.CONFIDENTIAL,
    retention_days=365,
    pii_fields=["email"]
)
```

---

## 8. Federated Governance (Policy-as-Code)

The `GovernanceEngine` enforces corporate compliance rules at key lifecycle points:

- **`PIIDetectionPolicy`**: Scans schema field names for email, SSN, phone, and card patterns. Demands declaration in `pii_fields` and rejects `PUBLIC` classification.
- **`SchemaDriftPolicy`**: Prevents breaking schema changes and untyped field additions.
- **`NullThresholdPolicy`**: Enforces maximum allowable null percentages (strict &lt;1% for required fields).
- **`DataRetentionPolicy`**: Enforces compliance caps:
  - `PUBLIC`: Max 30 days
  - `INTERNAL`: Max 90 days
  - `CONFIDENTIAL`: Max 365 days
  - `RESTRICTED`: Mandates Board Approval

---

## 9. 3-Phase Pipeline Orchestration (`DataProductPipeline`)

```python
from datashredpy.datamesh import DataProductPipeline

pipeline = DataProductPipeline(product, contract)

# Phase 1: Ingestion
res_ingest = pipeline.ingestion_phase(df_source, source_name="S3_Inbound")
if not res_ingest["passed"]:
    raise RuntimeError(f"Ingestion governance failed: {res_ingest['governance']['violations']}")

# Phase 2: Transformation
res_transform = pipeline.transformation_phase(df_source, transform_fn=my_business_logic)

# Phase 3: Publication
res_publish = pipeline.publication_phase(res_transform["output_df"], target_name="Snowflake_Prod")
if res_publish["passed"]:
    print(f"Published {res_publish['record_count']} records to {res_publish['target']}")
```

---

## 10. Discovery Portal REST API

PyDataShred includes a built-in FastAPI discovery portal in `datashredpy.datamesh.discovery_routes`:

- `POST /api/v1/datamesh/products/register`: Register data product for self-serve discovery.
- `POST /api/v1/datamesh/products/{id}/contracts`: Publish and validate a new contract version.
- `POST /api/v1/datamesh/products/search`: Search products by tag, domain, owner, and query.
- `POST /api/v1/datamesh/products/{id}/validate`: Execute full runtime validation.
- `POST /api/v1/datamesh/products/{id}/schema-compatibility`: Verify backward compatibility between versions.
- `GET /api/v1/datamesh/governance/policies`: List all active governance policies.
- `GET /api/v1/datamesh/governance/audit-trail`: Fetch regulatory compliance audit records.

---

## 11. Deployment Strategies

### AWS Lambda Deployment
Use the included `pydatashred-lambda-layer.zip` for serverless ETL pipelines triggered by S3 uploads or EventBridge schedules.

### Databricks & PySpark Clusters
Install `pydatashred[all]` via cluster libraries. Leverage `SparkSessionOption.get_spark_instance()` for distributed execution.

---

## 12. Troubleshooting & FAQ

**Q: How do I handle CSV files with non-standard delimiters?**  
A: Pass pandas or spark options directly into `Data.read()`, e.g., `Data.read("file.txt", file_type=FileType.CSV, sep="|", use_pandas=True)`.

**Q: What happens if a quality rule fails during the Transformation phase?**  
A: The transformation phase issues non-blocking warnings (`WARN`), allowing intermediate transformations to finish. Full enforcement occurs in the `publication_phase()`, which blocks publication (`DENY`) if thresholds are not met.
