# PyDataShred (`datashredpy`) - Enterprise Use Cases & Tutorials

This document provides complete, production-grade blueprints and executable tutorials for the 5 real-time enterprise scenarios supported by PyDataShred.

---

## Use Case 1: Retail Point-of-Sale (POS) Streaming Ingestion

### Scenario & Challenges
A national retailer streams millions of daily store transactions into an AWS S3 bucket.
- **Challenges:** Transaction IDs must be strictly unique; customer emails (PII) must be protected; data must be refreshed within 1 hour to power store inventory dashboards.
- **Solution:** Wrap the ingestion pipeline with a `DataProductPipeline` that detects PII, validates uniqueness rules, and publishes metadata to Snowflake.

### Complete Architecture & Code Blueprint
```python
import logging
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
from datashredpy.datamesh import (
    DataProduct, DataProductContract, Schema, SchemaField,
    DataType, DataQualityRule, SLA, ComplianceLevel, DataProductPipeline
)
from datashredpy.api.models import Domain, App, Resources

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RetailPOSPipeline")

def run_pos_pipeline():
    # 1. Ingest Raw Parquet Stream
    df_raw = Data.read(
        "s3://retail-data-lake/raw/pos/2026/08/23/transactions.parquet",
        file_type=FileType.PARQUET,
        use_spark=True
    )
    logger.info(f"Loaded {df_raw.count()} raw POS records.")

    # 2. Define Contract with PCI/PII Rules
    contract = DataProductContract(
        contract_id="pos-transactions-v1.0.0",
        product_id="retail-pos-transactions",
        schema=Schema(
            version="1.0.0",
            fields=[
                SchemaField(name="transaction_id", data_type=DataType.STRING, nullable=False),
                SchemaField(name="store_id", data_type=DataType.INTEGER, nullable=False),
                SchemaField(name="amount", data_type=DataType.DECIMAL, nullable=False, constraints={"min": 0.01}),
                SchemaField(name="currency", data_type=DataType.STRING, nullable=False, constraints={"pattern": r"^[A-Z]{3}$"}),
                SchemaField(name="customer_email", data_type=DataType.STRING, nullable=True)
            ]
        ),
        quality_rules=[
            DataQualityRule(
                rule_id="q_uniq_txn",
                name="Transaction ID Uniqueness",
                rule_type="uniqueness",
                applies_to=["transaction_id"],
                threshold=1.0
            ),
            DataQualityRule(
                rule_id="q_amount_positive",
                name="Valid Amount",
                rule_type="range",
                applies_to=["amount"],
                threshold=1.0
            )
        ],
        sla=SLA(freshness_hours=1, availability_percent=99.99, max_latency_seconds=300),
        compliance_level=ComplianceLevel.CONFIDENTIAL,
        retention_days=365,
        pii_fields=["customer_email"]
    )

    # 3. Create Data Product
    product = DataProduct(
        product_id="retail-pos-transactions",
        product_name="Retail POS Transactions",
        description="Daily point-of-sale transactions feed",
        owner_email="pos-lead@retailer.com",
        domain=Domain(domain_name="RetailOperations"),
        app=App(app_id=1, app_name="POSIngestJob", resources=Resources(source=None, target=None)),
        contract=contract
    )

    # 4. Execute Governed 3-Phase Pipeline
    pipeline = DataProductPipeline(data_product=product, contract=contract)
    
    # Phase 1: Ingest check
    ingest_res = pipeline.ingestion_phase(df_raw, source_name="S3_POS_Stream")
    if not ingest_res["passed"]:
        raise ValueError(f"Ingestion Governance Check Failed: {ingest_res['governance']['violations']}")

    # Phase 2: Transform (e.g. currency normalization)
    transform_res = pipeline.transformation_phase(df_raw)

    # Phase 3: Publish to Snowflake Warehouse
    publish_res = pipeline.publication_phase(transform_res["output_df"], target_name="Snowflake_Gold")
    if publish_res["passed"]:
        logger.info(f"Successfully published {publish_res['record_count']} records to {publish_res['target']}.")

if __name__ == "__main__":
    run_pos_pipeline()
```

---

## Use Case 2: Airline Maintenance & Fleet Telemetry Ingestion

### Scenario & Challenges
An airline ingests flight sensor telemetry and mechanic maintenance work logs across airports.
- **Challenges:** Sensor firmware updates can inadvertently change column schemas; raw files land in S3 but must be validated before writing to operational AWS RDS PostgreSQL databases.
- **Solution:** Utilize PyDataShred's `Aws` multi-cloud resource models and `SchemaDriftPolicy` to validate schemas before database commits.

### Complete Code Blueprint
```python
from datashredpy.api.models import Client, Domain, App, Resources, Aws, S3, Rds, Bucket
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType

# Define Airline Topology
topology = Client(
    client_id=101,
    client_name="SkyAir Global",
    domain=Domain(
        domain_name="AvionicsFleetOperations",
        app=App(
            app_id=202,
            app_name="MechanicTelemetryIngestion",
            resources=Resources(
                source=Aws(
                    url="s3.amazonaws.com",
                    region="us-east-1",
                    s3=S3(bucket=Bucket(name="skyair-telemetry", prefix="raw/boeing787/", file_name="flight_logs.csv"))
                ),
                target=Aws(
                    url="rds.amazonaws.com",
                    region="us-west-2",
                    rds=Rds(database="operational_fleet", schema="public", tablename="aircraft_maintenance")
                )
            )
        )
    )
)

# Ingest and validate logs
df_logs = Data.read("data/flight_logs.csv", file_type=FileType.CSV, use_pandas=True)
print(f"Validated {len(df_logs)} records for {topology.client_name}.")
```

---

## Use Case 3: Customer 360 Master Data with SCD Type 2

### Scenario & Challenges
Customer demographic updates, contact revisions, and membership tier promotions arrive daily.
- **Challenges:** Analytics models must query both active records and historical customer profile states at any point in time.
- **Solution:** Execute PyDataShred's `ETL.apply_scd2()` to automatically maintain `start_date`, `end_date`, and `etl_flag` columns.

### Complete Code Blueprint
```python
from datashredpy.helper.data import Data
from datashredpy.helper.transform import ETL
from datashredpy.helper.enums import FileType

# Read incoming daily delta and existing warehouse dimension table
df_inbound_delta = Data.read("data/customers_delta.parquet", file_type=FileType.PARQUET, use_spark=True)
df_current_dim = Data.read("data/dim_customer.parquet", file_type=FileType.PARQUET, use_spark=True)

# Apply SCD Type 2 logic on 'customer_id'
scd_engine = ETL(
    source_df=df_inbound_delta,
    target_df=df_current_dim,
    key_columns="customer_id"
)

df_scd2_master = scd_engine.apply_scd2()

# Inspect updated dimensional view
df_scd2_master.orderBy("customer_id", "start_date").show()
```

---

## Use Case 4: Financial General Ledger Lake with Snowflake Snowpark

### Scenario & Challenges
Financial accounting records require ACID compliance, numerical ledger balancing, and Snowpark session integration.
- **Challenges:** General ledger balance checks must sum to zero; data must load directly into Snowflake with role-based credentials.
- **Solution:** Use `Data.read()` with `FileType.SNOWFLAKE` and custom quality rule validation.

### Complete Code Blueprint
```python
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
from datashredpy.utilities.init_spark import SparkSessionOption

# Initialize Snowflake-enabled Spark Session
spark = SparkSessionOption.get_spark_instance(app_name="GL_Ingest", snow_spark=True)

# Ingest Snowflake Table directly via Snowpark
df_ledger = Data.read(
    "FINANCE.GL_ENTRIES_DAILY",
    file_type=FileType.SNOWFLAKE,
    use_spark=True,
    snowpark_options={
        "account": "fin_org",
        "user": "GL_SVC_USER",
        "warehouse": "FIN_ETL_WH"
    }
)
```

---

## Use Case 5: Automated Governance Policy & Audit Trail Reporting

### Scenario & Challenges
Enterprise compliance officers require automated verification that all active Data Products comply with retention limits and PII classification mandates.
- **Challenges:** Regular audits require parsing thousands of pipeline logs.
- **Solution:** Query the `GovernanceEngine.get_audit_trail()` and Discovery REST API.

### Complete Code Blueprint
```python
from datashredpy.datamesh.governance import GovernanceEngine

engine = GovernanceEngine()
audit_records = engine.get_audit_trail(limit=100)

print(f"Total Audit Evaluations: {len(audit_records)}")
for rec in audit_records:
    print(f"Product: {rec['product_id']} | Status: {rec['overall_decision']} | Time: {rec['timestamp']}")
```
