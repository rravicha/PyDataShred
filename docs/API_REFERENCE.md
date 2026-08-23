# PyDataShred (`datashredpy`) - Complete API Reference

This document provides a comprehensive technical reference for all public classes, methods, enums, models, and functions in the `datashredpy` package.

---

## 1. Module: `datashredpy.helper.data`

### Class `Data`
Unified reader class supporting multiple file formats, data lakes, warehouses, and APIs.

#### Method `Data.read(...)`
```python
@classmethod
def read(
    cls,
    rel_path: str,
    api_type: Optional[ApiType] = None,
    file_type: Optional[FileType] = None,
    db_type: Optional[DbType] = None,
    use_pandas: Optional[bool] = False,
    use_spark: Optional[bool] = True,
    snowpark_options: Optional[dict] = False,
    **options
) -> Union[pd.DataFrame, pyspark.sql.DataFrame, List[Dict]]
```
- **`rel_path`** (`str`): File path, S3 URI, Snowflake table name, or REST API endpoint.
- **`file_type`** (`FileType`, optional): File format enum (`CSV`, `JSON`, `PARQUET`, `DELTA`, `EXCEL`, `XML`, `TSV`, `SNOWFLAKE`).
- **`api_type`** (`ApiType`, optional): `ApiType.DEFAULT_API` for REST endpoint ingestion.
- **`use_pandas`** (`bool`, default `False`): When `True`, processes data into a Pandas DataFrame.
- **`use_spark`** (`bool`, default `True`): When `True`, processes data into a PySpark DataFrame.
- **`snowpark_options`** (`dict`, optional): Configuration dictionary for Snowflake connection.
- **`**options`**: Additional kwargs forwarded directly to underlying Pandas/Spark readers (e.g. `sep`, `header`, `inferSchema`, `encoding`).

---

## 2. Module: `datashredpy.helper.transform`

### Class `ETL`
Slowly Changing Dimension (SCD Type 2) automation engine.

#### Constructor
```python
ETL(
    source_df: pyspark.sql.DataFrame,
    target_df: pyspark.sql.DataFrame,
    key_columns: Union[str, List[str]]
)
```
- **`source_df`**: Incoming delta PySpark DataFrame.
- **`target_df`**: Existing dimension PySpark DataFrame.
- **`key_columns`**: Single primary key column name or list of composite business key column names.

#### Method `apply_scd2()`
```python
def apply_scd2(self) -> pyspark.sql.DataFrame
```
- **Returns**: A unified PySpark DataFrame with audit columns (`start_date`, `end_date`, `etl_flag`) where:
  - New records are inserted with `etl_flag = "current"`, `end_date = NULL`.
  - Modified records have the previous row marked `etl_flag = "expired"` with `end_date = current_timestamp()`.
  - Unchanged records are preserved.

---

## 3. Module: `datashredpy.utilities.init_spark`

### Class `SparkSessionOption`
Thread-safe Singleton and Factory for PySpark session management.

#### Method `get_spark_instance(...)`
```python
@classmethod
def get_spark_instance(
    cls,
    app_name: str = "PyDataShred",
    master: str = "local[*]",
    config_options: Optional[Dict[str, str]] = None,
    snow_spark: bool = False
) -> pyspark.sql.SparkSession
```
- **`app_name`**: Spark application identifier.
- **`master`**: Master URL (e.g., `"local[*]"`, `"yarn"`).
- **`config_options`**: Dict of Spark configuration properties.
- **`snow_spark`**: If `True`, injects the official Snowflake Spark Connector package.

#### Method `get_spark_session(...)`
```python
@staticmethod
def get_spark_session(
    app_name: str = "PyDataShred",
    master: str = "local[*]",
    config_options: Optional[Dict[str, str]] = None
) -> pyspark.sql.SparkSession
```
Creates a new standalone `SparkSession` (non-singleton).

---

## 4. Module: `datashredpy.helper.enums`

### Enums
- **`FileType`**: `CSV`, `TXT`, `TSV`, `JSON`, `PARQUET`, `DELTA`, `EXCEL`, `XML`, `HTML`, `PDF`, `SNOWFLAKE`.
- **`ApiType`**: `DEFAULT_API`.
- **`ConfigOptions.Spark`**: `SPARK_EXECUTOR_MEMORY`, `SPARK_EXECUTOR_CORES`, `SPARK_DRIVER_MEMORY`.

---

## 5. Module: `datashredpy.datamesh.models`

### Enums
- **`DataType`**: `STRING`, `INTEGER`, `FLOAT`, `BOOLEAN`, `TIMESTAMP`, `DATE`, `BINARY`, `ARRAY`, `STRUCT`, `DECIMAL`.
- **`VersioningStrategy`**: `SEMANTIC`, `TIMESTAMP`, `HASH`.
- **`ComplianceLevel`**: `PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`.

### Dataclass `SchemaField`
```python
SchemaField(
    name: str,
    data_type: DataType,
    nullable: bool = True,
    description: Optional[str] = None,
    constraints: Optional[Dict[str, Any]] = None  # e.g. {"min": 0, "max": 100, "pattern": "..."}
)
```

### Dataclass `Schema`
```python
Schema(
    version: str,
    fields: List[SchemaField],
    versioning_strategy: VersioningStrategy = VersioningStrategy.SEMANTIC,
    created_at: datetime = datetime.utcnow(),
    deprecated: bool = False
)
```
- **`is_compatible_with(other: Schema) -> Tuple[bool, List[str]]`**: Evaluates backward compatibility.

### Dataclass `DataQualityRule`
```python
DataQualityRule(
    rule_id: str,
    name: str,
    description: Optional[str] = None,
    rule_type: Literal["null_check", "uniqueness", "range", "pattern", "custom"] = "custom",
    applies_to: Optional[List[str]] = None,
    threshold: float = 0.95,
    enabled: bool = True,
    custom_logic: Optional[str] = None
)
```

### Dataclass `SLA`
```python
SLA(
    freshness_hours: int,
    availability_percent: float,
    max_latency_seconds: Optional[int] = None,
    recovery_time_objective_minutes: Optional[int] = None
)
```

### Dataclass `DataProductContract`
```python
DataProductContract(
    contract_id: str,
    product_id: str,
    schema: Schema,
    quality_rules: List[DataQualityRule] = field(default_factory=list),
    sla: Optional[SLA] = None,
    compliance_level: ComplianceLevel = ComplianceLevel.INTERNAL,
    retention_days: int = 90,
    pii_fields: List[str] = field(default_factory=list),
    tags: List[str] = field(default_factory=list)
)
```

### Dataclass `DataProduct`
```python
DataProduct(
    product_id: str,
    product_name: str,
    description: str,
    owner_email: str,
    domain: Domain,
    app: App,
    contract: DataProductContract,
    owner_team: Optional[str] = None,
    input_resources: List[Resources] = field(default_factory=list),
    output_resources: List[Resources] = field(default_factory=list),
    tags: List[str] = field(default_factory=list),
    documentation_url: Optional[str] = None,
    sample_query: Optional[str] = None
)
```

---

## 6. Module: `datashredpy.datamesh.governance`

### Enums
- **`EnforcementPoint`**: `INGESTION`, `TRANSFORMATION`, `PUBLICATION`.
- **`PolicyScope`**: `GLOBAL`, `DOMAIN`, `PRODUCT`.
- **`PolicyDecision`**: `ALLOW`, `DENY`, `WARN`, `REQUIRE_APPROVAL`.

### Class `GovernanceEngine`
- **`register_policy(policy: GovernancePolicy)`**: Registers custom or built-in policy.
- **`evaluate(context: PolicyContext, stop_on_deny: bool = True) -> Dict[str, Any]`**: Evaluates context against all applicable policies.
- **`get_audit_trail(product_id: Optional[str], limit: int = 100) -> List[Dict]`**: Returns history log of policy decisions.

### Built-in Policies
- **`PIIDetectionPolicy`**: Scans schema fields for email/phone/SSN/card patterns.
- **`SchemaDriftPolicy`**: Detects breaking changes and un-typed field mutations.
- **`NullThresholdPolicy`**: Validates null percentage against quality thresholds.
- **`DataRetentionPolicy`**: Enforces statutory retention day caps.

---

## 7. Module: `datashredpy.datamesh.pipeline_integration`

### Class `DataProductPipeline`
- **`ingestion_phase(df_source, source_name: str = "unknown") -> Dict[str, Any]`**: Checks ingestion governance and validates initial record counts.
- **`transformation_phase(df, transform_fn: Optional[Callable] = None) -> Dict[str, Any]`**: Applies business transformation function and evaluates non-blocking quality rules.
- **`publication_phase(df, target_name: str = "unknown") -> Dict[str, Any]`**: Performs mandatory contract validation, quality rule enforcement, and governance audit logging.
- **`get_execution_summary() -> Dict[str, Any]`**: Returns lifecycle metadata for the run.
