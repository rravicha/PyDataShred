# DataMesh Architecture & Implementation Guide

## Overview

The DataMesh layer for PyDataShred enables **self-serve, discoverable data products** with **federated governance**. It abstracts over the existing Client→Domain→App→Resource hierarchy and adds:

- **Data Product abstraction**: Discoverable, self-contained datasets with clear ownership
- **Contracts**: Versioned schemas, quality rules, SLAs, compliance policies
- **Governance**: Pluggable, policy-as-code enforcement at ingestion/transformation/publication
- **Discovery Portal**: API-first self-serve catalog for data consumers
- **Runtime Enforcement**: Validation at every phase of the pipeline

---

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────┐
│         Discovery Portal (REST API)                 │
│   ├─ Register Products                              │
│   ├─ Search/Discover                                │
│   ├─ View Contracts & SLAs                          │
│   └─ Compliance Audit Trail                         │
└─────────────────────────────────────────────────────┘
                       ▲
                       │
┌─────────────────────────────────────────────────────┐
│    DataMesh Orchestration Layer                     │
│   ├─ DataProductPipeline (ingestion→transform→pub) │
│   ├─ ContractValidator (schema + quality)          │
│   └─ GovernanceEngine (policy enforcement)         │
└─────────────────────────────────────────────────────┘
                       ▲
                       │
┌─────────────────────────────────────────────────────┐
│    Existing PyDataShred (Enhanced)                  │
│   ├─ Client → Domain → App → Resources             │
│   ├─ PySpark / Pandas Processing                   │
│   ├─ Multi-cloud Targets (S3, Snowflake, etc)      │
│   └─ Metadata Framework                            │
└─────────────────────────────────────────────────────┘
```

### Data Product Model

```python
DataProduct
├── product_id: str
├── product_name: str
├── description: str
├── owner_email: str
├── owner_team: Optional[str]
├── domain: Domain (from PyDataShred)
├── app: App (from PyDataShred)
├── input_resources: List[Resources]
├── output_resources: List[Resources]
├── contract: DataProductContract
│   ├── schema: Schema
│   │   ├── version: str (semantic, timestamp, or hash)
│   │   ├── fields: List[SchemaField]
│   │   │   ├── name: str
│   │   │   ├── data_type: DataType
│   │   │   ├── nullable: bool
│   │   │   ├── description: str
│   │   │   └── constraints: Dict (min, max, pattern, enum)
│   │   └── deprecated: bool
│   ├── quality_rules: List[DataQualityRule]
│   │   ├── rule_id: str
│   │   ├── rule_type: str (null_check, uniqueness, range, pattern, custom)
│   │   ├── applies_to: List[str] (field names)
│   │   └── threshold: float (0.0-1.0)
│   ├── sla: SLA
│   │   ├── freshness_hours: int
│   │   ├── availability_percent: float
│   │   ├── max_latency_seconds: Optional[int]
│   │   └── recovery_time_objective_minutes: Optional[int]
│   ├── compliance_level: ComplianceLevel (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED)
│   ├── retention_days: int
│   └── pii_fields: List[str]
├── tags: List[str]
├── documentation_url: Optional[str]
├── sample_query: Optional[str]
├── created_at: datetime
├── updated_at: datetime
└── deprecated: bool
```

---

## Core Components

### 1. Models (`models.py`)

Defines the data structures for products, contracts, schemas, and quality rules.

**Key Classes:**
- `DataProduct`: Self-serve, discoverable dataset
- `DataProductContract`: Enforceable specification
- `Schema`: Versioned, typed field definitions
- `DataQualityRule`: Enforceable quality requirements
- `SLA`: Service level commitments

**Example:**
```python
product = DataProduct(
    product_id="customer-master",
    product_name="Customer Master Data",
    owner_email="data-team@company.com",
    domain=domain,
    app=app,
    contract=contract
)
```

### 2. Contract Validation (`contract_validation.py`)

Validates data against schema and quality rules.

**Key Classes:**
- `SchemaValidator`: Type and constraint checking
- `QualityRuleEngine`: Null checks, uniqueness, range, pattern, custom
- `ContractValidator`: Full contract validation (schema + quality)

**Example:**
```python
validator = SchemaValidator(schema)
is_valid, errors = validator.validate_record({"id": 1, "name": "Alice"})

engine = QualityRuleEngine(contract)
result = engine.evaluate_rules(df)  # Works with PySpark & Pandas
```

### 3. Governance (`governance.py`)

Pluggable, policy-based governance enforcement.

**Key Classes:**
- `GovernancePolicy`: Base class for all policies
- `GovernanceEngine`: Policy registration and evaluation
- Built-in policies:
  - `PIIDetectionPolicy`: Detect and protect PII
  - `SchemaDriftPolicy`: Prevent breaking schema changes
  - `NullThresholdPolicy`: Enforce null value limits
  - `DataRetentionPolicy`: Retention limits by compliance level

**Enforcement Points:**
- `INGESTION`: Source data checks
- `TRANSFORMATION`: Quality and governance warnings
- `PUBLICATION`: Mandatory compliance checks

**Example:**
```python
engine = GovernanceEngine()

context = PolicyContext(
    product=product,
    contract=contract,
    enforcement_point=EnforcementPoint.PUBLICATION
)

result = engine.evaluate(context)
# result.passed: bool
# result.violations: List[str]
# result.requires_approval: bool
```

### 4. Discovery Portal API (`discovery_routes.py`, `api_models.py`)

REST API for self-serve data discovery.

**Key Endpoints:**
- `POST /api/v1/datamesh/products/register`: Register new product
- `POST /api/v1/datamesh/products/{id}/contracts`: Publish contract
- `POST /api/v1/datamesh/products/search`: Search products
- `GET /api/v1/datamesh/products/{id}`: Get product details
- `POST /api/v1/datamesh/products/{id}/validate`: Validate product
- `GET /api/v1/datamesh/governance/policies`: List policies
- `GET /api/v1/datamesh/governance/audit-trail`: Compliance history

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/datamesh/products/register \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "customer-master",
    "product_name": "Customer Master",
    "description": "Customer single source of truth",
    "owner_email": "data-team@company.com",
    "domain_id": 1,
    "app_id": 101,
    "tags": ["customer", "high-priority"]
  }'
```

### 5. Pipeline Integration (`pipeline_integration.py`)

Wraps existing PyDataShred pipelines with DataMesh enforcement.

**Key Classes:**
- `DataProductPipeline`: Phases (ingestion, transformation, publication)
- `DataMeshIntegrationHelper`: Wrap existing Domain/App pipelines
- `DataMeshExecutionContext`: Execution state and hooks

**Example:**
```python
pipeline = DataProductPipeline(product, contract, governance_engine)

# Phase 1: Ingestion
ingestion = pipeline.ingestion_phase(df_source, "S3")
if not ingestion["passed"]:
    print(f"Ingestion failed: {ingestion['governance']['violations']}")

# Phase 2: Transformation
transform = pipeline.transformation_phase(df, transform_fn=my_logic)

# Phase 3: Publication
publish = pipeline.publication_phase(df_output, "Snowflake")
if publish["passed"]:
    print(f"Published {publish['metadata']['record_count']} records")
```

---

## Usage Patterns

### Pattern 1: Create & Register a Data Product

```python
from datashredpy.datamesh import (
    DataProduct, DataProductContract, Schema, SchemaField,
    DataType, DataQualityRule, SLA, ComplianceLevel
)

# Define schema
fields = [
    SchemaField(name="id", data_type=DataType.STRING, nullable=False),
    SchemaField(name="email", data_type=DataType.STRING, nullable=False,
                constraints={"pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}),
    SchemaField(name="age", data_type=DataType.INTEGER, nullable=True,
                constraints={"min": 0, "max": 150})
]

schema = Schema(version="1.0.0", fields=fields)

# Define quality rules
rules = [
    DataQualityRule(
        rule_id="unique-id",
        name="IDs are unique",
        rule_type="uniqueness",
        applies_to=["id"],
        threshold=1.0
    ),
    DataQualityRule(
        rule_id="null-check",
        name="No nulls in required fields",
        rule_type="null_check",
        applies_to=["id", "email"],
        threshold=1.0
    )
]

# Define SLA
sla = SLA(
    freshness_hours=24,
    availability_percent=99.5,
    max_latency_seconds=3600
)

# Create contract
contract = DataProductContract(
    contract_id="customer-v1.0.0",
    product_id="customer-master",
    schema=schema,
    quality_rules=rules,
    sla=sla,
    compliance_level=ComplianceLevel.CONFIDENTIAL,
    retention_days=365,
    pii_fields=["email"]
)

# Create product
product = DataProduct(
    product_id="customer-master",
    product_name="Customer Master",
    description="Customer single source of truth",
    owner_email="data-team@company.com",
    domain=domain,
    app=app,
    contract=contract,
    tags=["customer", "high-priority"]
)
```

### Pattern 2: Enforce Contract During Pipeline Execution

```python
from datashredpy.datamesh import DataProductPipeline

# Initialize pipeline
pipeline = DataProductPipeline(product, contract)

# Phase 1: Ingest from source
ingestion_result = pipeline.ingestion_phase(df_source, "S3")
assert ingestion_result["passed"], "Ingestion failed governance checks"

# Phase 2: Transform with business logic
transform_result = pipeline.transformation_phase(
    df_source,
    transform_fn=lambda df: df.filter(df.age >= 18)
)

# Phase 3: Publish to target
publish_result = pipeline.publication_phase(
    transform_result["output_df"],
    "Snowflake"
)

if publish_result["passed"]:
    print(f"Success! Published to {publish_result['target']}")
    print(f"Metadata: {publish_result['metadata']}")
```

### Pattern 3: Wrap Existing Pipeline

```python
from datashredpy.datamesh import DataMeshIntegrationHelper

# Existing PyDataShred objects
domain = Domain(domain_id=1, domain_name="Customer Analytics")
app = App(app_id=101, app_name="Customer Ingestion", resources=...)

# Product definition
product_def = {
    "product_id": "customer-master",
    "product_name": "Customer Master",
    "description": "...",
    "owner_email": "...",
    "contract": {...}
}

# Wrap existing pipeline
pipeline = DataMeshIntegrationHelper.wrap_existing_pipeline(
    domain,
    app,
    product_def
)

# Execute with governance
ingestion = pipeline.ingestion_phase(df_source)
transform = pipeline.transformation_phase(df)
publish = pipeline.publication_phase(df_output)
```

### Pattern 4: Register via Discovery Portal

```python
import requests

# Register product
resp = requests.post(
    "http://localhost:8000/api/v1/datamesh/products/register",
    json={
        "product_id": "customer-master",
        "product_name": "Customer Master",
        "description": "Customer data",
        "owner_email": "data-team@company.com",
        "domain_id": 1,
        "app_id": 101,
        "tags": ["customer"]
    }
)
assert resp.status_code == 200

# Publish contract
resp = requests.post(
    "http://localhost:8000/api/v1/datamesh/products/customer-master/contracts",
    json={
        "contract_id": "customer-v1.0.0",
        "product_id": "customer-master",
        "schema_version": "1.0.0",
        "schema_definition": {...},
        "quality_rules": [...],
        "compliance_level": "confidential",
        "pii_fields": ["email"]
    }
)
assert resp.status_code == 200

# Search products
resp = requests.post(
    "http://localhost:8000/api/v1/datamesh/products/search",
    json={"query": "customer", "tags": ["customer"]}
)
products = resp.json()["products"]
```

---

## Governance Policies

### Built-in Policies

#### 1. PIIDetectionPolicy

Detects Personally Identifiable Information and ensures protection.

**Rules:**
- Identifies PII fields by name patterns (email, phone, ssn, etc.)
- Verifies all detected PII is marked in contract
- Enforces CONFIDENTIAL or RESTRICTED for data with PII

**Enforcement:** INGESTION, PUBLICATION

#### 2. SchemaDriftPolicy

Prevents uncontrolled schema changes that break contracts.

**Rules:**
- Validates all fields are properly typed
- Detects breaking changes during upgrades
- Prevents type mismatches

**Enforcement:** INGESTION, TRANSFORMATION

#### 3. NullThresholdPolicy

Enforces maximum null value thresholds.

**Rules:**
- Required fields: < 1% nulls
- Optional fields: < 10% nulls

**Enforcement:** PUBLICATION

#### 4. DataRetentionPolicy

Enforces retention limits by compliance level.

**Rules:**
- PUBLIC: max 30 days
- INTERNAL: max 90 days
- CONFIDENTIAL: max 1 year
- RESTRICTED: requires approval

**Enforcement:** PUBLICATION

### Custom Policies

Create custom policies by extending `GovernancePolicy`:

```python
from datashredpy.datamesh.governance import GovernancePolicy, PolicyEvaluation, PolicyDecision

class CustomPolicy(GovernancePolicy):
    def __init__(self):
        super().__init__(
            policy_id="my-custom-policy",
            policy_name="My Custom Policy",
            description="...",
            severity="error"
        )
    
    def evaluate(self, context):
        # Your logic here
        violations = []
        
        if # some condition:
            violations.append("Policy violation")
        
        decision = PolicyDecision.DENY if violations else PolicyDecision.ALLOW
        
        return PolicyEvaluation(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            decision=decision,
            is_enforced=True,
            message="...",
            violations=violations
        )

# Register with engine
engine.register_policy(CustomPolicy())
```

---

## Schema Versioning & Compatibility

### Versioning Strategies

1. **Semantic**: v1.0.0, v1.1.0, v2.0.0
2. **Timestamp**: 20231213_120000
3. **Hash**: content-based content hash

### Backward Compatibility Rules

New schema is compatible with old if:
- All required fields (nullable=False) in old schema exist in new
- Types match exactly (no automatic coercion)
- New fields are always nullable
- Old nullable fields can become required

```python
validator = ContractValidator(new_contract)
compatible, issues = validator.check_backward_compatibility(old_contract)

if not compatible:
    print(f"Incompatible: {issues}")
```

---

## Quality Rules

### Built-in Rule Types

| Type | Purpose | Example |
|------|---------|---------|
| `null_check` | Verify non-null fields | Field `id` must be 100% non-null |
| `uniqueness` | Enforce unique values | Field `email` must be unique |
| `range` | Numeric bounds | Age must be 0-150 |
| `pattern` | Regex matching | Email must match pattern |
| `custom` | SQL/Python expression | Custom logic |

### Quality Rule Evaluation

Rules are evaluated at publication and report:
- **status**: PASSED, FAILED, ERROR
- **pass_rate**: Percentage of records passing (0.0-1.0)
- **threshold**: Required pass rate (configurable per rule)

---

## Compliance & Governance Audit Trail

Track all governance evaluations:

```python
# Get audit trail
trail = engine.get_audit_trail(product_id="customer-master", limit=100)

# Example entry
{
    "timestamp": "2024-12-13T10:00:00",
    "product_id": "customer-master",
    "overall_decision": "allow",
    "evaluations": [...],
    "violations": [...]
}
```

---

## Best Practices

### 1. Define Clear Contracts Early

- Be explicit about schema, quality, and compliance requirements
- Document all PII fields
- Set realistic SLAs

### 2. Embrace Semantic Versioning

```
v1.0.0  → Initial schema
v1.1.0  → Added optional field (backward compatible)
v2.0.0  → Breaking change (consumer action required)
```

### 3. Progressive Enforcement

- Start policies as **warnings** (WARN)
- Monitor violations
- Enforce when stable (DENY)

### 4. Domain Ownership

- Each data product has a single owner/team
- Owners responsible for SLA compliance
- Clear escalation paths

### 5. Consumer-Driven Contracts

- Involve downstream teams in contract definition
- Include sample queries for common use cases
- Provide clear documentation

---

## Integration with Existing PyDataShred

**No Breaking Changes:**
- Existing Domain/App/Resource models are unchanged
- DataProduct wraps these models
- Governance is optional (can be disabled)
- Discovery portal is independent

**Backward Compatibility:**
```python
# Old way (still works)
domain = Domain(...)
app = App(...)
# Execute pipeline directly

# New way (with governance)
product = DataProduct(domain=domain, app=app, ...)
pipeline = DataProductPipeline(product, contract)
# Execute with enforcement
```

---

## Configuration

Environment variables (optional):

```bash
# Governance settings
DATAMESH_ENFORCEMENT_MODE=strict|warn|disabled  # Default: strict
DATAMESH_REQUIRE_APPROVAL=true|false            # Default: false

# Storage (metadata, contracts, policies)
DATAMESH_METADATA_STORE=file|db|s3             # Default: file
DATAMESH_METADATA_PATH=/path/to/metadata        # Default: ./metadata
```

---

## See Also

- [Examples](examples.py): Comprehensive usage examples
- [API Routes](discovery_routes.py): Discovery portal REST API
- [Models](models.py): Data structures
- [Governance](governance.py): Policy framework
- [Validation](contract_validation.py): Schema & quality checking
