# PyDataShred DataMesh Module

## Overview

A production-ready **DataMesh layer** for PyDataShred that enables:

✅ **Self-serve data products** - Discoverable datasets with clear ownership  
✅ **Versioned contracts** - Schema, quality rules, SLAs, compliance policies  
✅ **Federated governance** - Pluggable, policy-as-code enforcement  
✅ **Discovery portal** - REST API for data consumers  
✅ **Runtime validation** - Contract enforcement at ingestion, transformation, publication  
✅ **Audit trail** - Full compliance history  
✅ **No breaking changes** - Seamless integration with existing PyDataShred  

---

## Quick Start (5 Minutes)

### 1. Define a Data Product

```python
from datashredpy.datamesh import (
    DataProduct, DataProductContract, Schema, SchemaField,
    DataType, DataQualityRule, SLA, ComplianceLevel
)
from datashredpy.api.models import Domain, App, Resources

# Create schema
fields = [
    SchemaField(name="id", data_type=DataType.STRING, nullable=False),
    SchemaField(name="email", data_type=DataType.STRING, nullable=False),
]
schema = Schema(version="1.0.0", fields=fields)

# Create quality rules
rules = [
    DataQualityRule(
        rule_id="unique-id",
        rule_type="uniqueness",
        applies_to=["id"],
        threshold=1.0
    )
]

# Create contract
contract = DataProductContract(
    contract_id="product-v1.0.0",
    product_id="my-product",
    schema=schema,
    quality_rules=rules,
    sla=SLA(freshness_hours=24, availability_percent=99.5),
    compliance_level=ComplianceLevel.CONFIDENTIAL,
    retention_days=365,
    pii_fields=["email"]
)

# Create product
domain = Domain(domain_id=1, domain_name="Analytics")
app = App(app_id=101, app_name="Ingestion", resources=Resources(source=None, target=None))

product = DataProduct(
    product_id="my-product",
    product_name="My Data Product",
    owner_email="owner@company.com",
    domain=domain,
    app=app,
    contract=contract
)
```

### 2. Execute with Governance

```python
from datashredpy.datamesh import DataProductPipeline

pipeline = DataProductPipeline(product, contract)

# Phase 1: Ingest from source
ingestion = pipeline.ingestion_phase(df_source, "S3")
assert ingestion["passed"], f"Failed: {ingestion['governance']['violations']}"

# Phase 2: Transform with business logic
transform = pipeline.transformation_phase(df, transform_fn=my_logic)

# Phase 3: Publish to target
publish = pipeline.publication_phase(transform["output_df"], "Snowflake")
print(f"✓ Published {publish['metadata']['record_count']} records")
```

### 3. Discover via Portal

```bash
# Register product
curl -X POST http://localhost:8000/api/v1/datamesh/products/register \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "my-product",
    "product_name": "My Data Product",
    "owner_email": "owner@company.com",
    "domain_id": 1,
    "app_id": 101,
    "tags": ["analytics"]
  }'

# Search products
curl -X POST http://localhost:8000/api/v1/datamesh/products/search \
  -H "Content-Type: application/json" \
  -d '{"query": "my-product", "limit": 20}'

# Check governance audit trail
curl http://localhost:8000/api/v1/datamesh/governance/audit-trail
```

---

## What's Included

### 8 Core Python Modules

| Module | Purpose | Lines |
|--------|---------|-------|
| **models.py** | DataProduct, Contract, Schema, Quality, SLA | 450 |
| **contract_validation.py** | Schema & quality validation engines | 450 |
| **governance.py** | Policies, enforcement, audit | 550 |
| **api_models.py** | Pydantic request/response models | 300 |
| **discovery_routes.py** | FastAPI discovery portal | 550 |
| **pipeline_integration.py** | 3-phase pipeline wrapper | 500 |
| **examples.py** | 6 complete runnable examples | 400 |
| **__init__.py** | Public API exports | 50 |
| **DATAMESH.md** | Complete implementation guide | 450 |

**Total: ~4,100 lines** of production code + documentation

### 6 Documentation Files (in root)

| File | Purpose |
|------|---------|
| **DATAMESH_QUICK_REFERENCE.md** | Quick start + API reference |
| **DATAMESH_ARCHITECTURE_DIAGRAMS.md** | 9 detailed ASCII diagrams |
| **DATAMESH_IMPLEMENTATION_SUMMARY.md** | Feature overview |
| **DATAMESH_IMPLEMENTATION_CHECKLIST.md** | Progress tracking |
| **DATAMESH_DOCUMENTATION_INDEX.md** | Navigation guide |
| **DATAMESH.md** (in module) | Full architecture guide |

---

## Core Concepts

### DataProduct
Self-serve, discoverable dataset with ownership and metadata.

```python
DataProduct(
    product_id="customer-master",
    product_name="Customer Master Data",
    owner_email="data-team@company.com",
    domain=domain,
    app=app,
    contract=contract,
    tags=["customer", "confidential"]
)
```

### Contract
Enforceable specification with schema, quality, SLA, compliance.

```python
DataProductContract(
    contract_id="customer-v1.0.0",
    schema=Schema(...),
    quality_rules=[...],
    sla=SLA(...),
    compliance_level=ComplianceLevel.CONFIDENTIAL,
    pii_fields=["email"]
)
```

### Schema
Versioned, typed field definitions with constraints.

```python
Schema(
    version="1.0.0",
    fields=[
        SchemaField(name="id", data_type=DataType.STRING, nullable=False),
        SchemaField(name="age", data_type=DataType.INTEGER, nullable=True,
                   constraints={"min": 0, "max": 150})
    ]
)
```

### Quality Rules
Enforceable data quality requirements with 5 types.

```python
DataQualityRule(
    rule_type="uniqueness",      # null_check, range, pattern, custom
    applies_to=["id"],
    threshold=1.0                 # 100% must pass
)
```

### Governance Policies
Pluggable enforcement rules (4 built-in + custom).

```python
# Built-in:
PIIDetectionPolicy()              # PII protection
SchemaDriftPolicy()               # Breaking change prevention
NullThresholdPolicy()             # Null value limits
DataRetentionPolicy()             # Retention by compliance level

# Custom:
class MyPolicy(GovernancePolicy):
    def evaluate(self, context): ...
```

### Pipeline Phases

1. **INGESTION** - Governance + schema validation
2. **TRANSFORMATION** - Quality warnings + business logic
3. **PUBLICATION** - Full enforcement + audit trail

---

## Governance Policies

### PIIDetectionPolicy
Detects and protects Personally Identifiable Information.

**Detects**: email, phone, ssn, credit_card, password, etc.  
**Enforces**: CONFIDENTIAL or RESTRICTED compliance for PII  
**Decision**: ALLOW / DENY  

### SchemaDriftPolicy
Prevents breaking schema changes.

**Prevents**: Type changes, field removals  
**Allows**: New optional fields, nullable changes  
**Decision**: ALLOW / WARN  

### NullThresholdPolicy
Enforces null value limits.

**Rules**: 
- Required fields: < 1% nulls
- Optional fields: < 10% nulls

**Decision**: ALLOW / WARN  

### DataRetentionPolicy
Enforces retention limits by compliance level.

**Rules**:
- PUBLIC: max 30 days
- INTERNAL: max 90 days
- CONFIDENTIAL: max 1 year
- RESTRICTED: manual approval

**Decision**: ALLOW / REQUIRE_APPROVAL / DENY  

---

## API Endpoints

### Products
- `POST /api/v1/datamesh/products/register` - Register product
- `GET /api/v1/datamesh/products/{id}` - Get product details
- `POST /api/v1/datamesh/products/search` - Search products

### Contracts
- `POST /api/v1/datamesh/products/{id}/contracts` - Publish contract
- `GET /api/v1/datamesh/products/{id}/contracts/{contract_id}` - Get contract

### Validation
- `POST /api/v1/datamesh/products/{id}/validate` - Validate product
- `POST /api/v1/datamesh/products/{id}/schema-compatibility` - Check version compatibility

### Governance
- `GET /api/v1/datamesh/governance/policies` - List policies
- `GET /api/v1/datamesh/governance/audit-trail` - Compliance history

### Operations
- `GET /api/v1/datamesh/health` - Health check
- `GET /api/v1/datamesh/stats` - Statistics

---

## Integration with FastAPI

```python
from fastapi import FastAPI
from datashredpy.datamesh.discovery_routes import router

app = FastAPI()
app.include_router(router)

# Endpoints now available at: /api/v1/datamesh/*
# Swagger UI at: /docs
```

---

## Examples

See `examples.py` for 6 complete runnable examples:

1. Create a DataProduct with contract
2. Schema validation (single record + batch)
3. Schema compatibility checking
4. Governance policy evaluation
5. Pipeline integration with 3 phases
6. Discovery portal API usage

**Run all examples:**
```bash
python datashredpy/datamesh/examples.py
```

---

## Documentation Map

```
Quick Start
├── README.md (this file)
├── DATAMESH_QUICK_REFERENCE.md ⭐ START HERE
├── examples.py (run for working code)
└── DATAMESH_ARCHITECTURE_DIAGRAMS.md (understand design)

Detailed Info
├── datashredpy/datamesh/DATAMESH.md (full guide)
├── DATAMESH_IMPLEMENTATION_SUMMARY.md (overview)
└── DATAMESH_IMPLEMENTATION_CHECKLIST.md (tracking)

Source Code
├── models.py
├── contract_validation.py
├── governance.py
├── api_models.py
├── discovery_routes.py
├── pipeline_integration.py
└── __init__.py
```

---

## Usage Patterns

### Pattern 1: Create Data Product
See `models.py` and Example 1 in `examples.py`

### Pattern 2: Validate Data
See `contract_validation.py` and Example 2 in `examples.py`

### Pattern 3: Check Schema Compatibility
See Example 3 in `examples.py`

### Pattern 4: Evaluate Governance
See `governance.py` and Example 4 in `examples.py`

### Pattern 5: Integrate Pipeline
See `pipeline_integration.py` and Example 5 in `examples.py`

### Pattern 6: Create Custom Policy
See "Custom Policies" in `DATAMESH.md`

---

## Key Features

✅ **Schema Validation**
- Type checking
- Constraint enforcement (min, max, pattern, enum)
- Single record and batch validation

✅ **Quality Rules**
- 5 rule types: null_check, uniqueness, range, pattern, custom
- Framework-agnostic (PySpark & Pandas)
- Configurable thresholds per rule

✅ **Governance Enforcement**
- 4 built-in policies + pluggable custom policies
- 3 enforcement points: ingestion, transformation, publication
- Policy decisions: allow, warn, deny, require_approval

✅ **Schema Versioning**
- Semantic versioning (v1.0.0)
- Timestamp versioning (20231213)
- Hash-based versioning
- Backward compatibility checking

✅ **Discovery Portal**
- RESTful API
- Full-text search
- Tag-based filtering
- Compliance reporting
- Audit trail

✅ **Pipeline Integration**
- 3-phase execution
- Phase-specific governance
- Execution hooks
- Metadata generation

✅ **Backward Compatibility**
- No changes to existing Domain/App/Resource models
- DataMesh is purely additive
- Existing pipelines continue to work

---

## Requirements

**Python**: 3.10+  
**Dependencies** (already in PyDataShred):
- fastapi
- pydantic
- dataclasses (Python 3.7+)
- typing (Python 3.5+)

**Optional**:
- pyspark (for Spark DataFrames)
- pandas (for Pandas DataFrames)

---

## Configuration

Environment variables (optional):

```bash
# Governance mode
export DATAMESH_ENFORCEMENT_MODE=strict  # strict, warn, disabled

# Metadata storage
export DATAMESH_METADATA_STORE=file      # file, db, s3
export DATAMESH_METADATA_PATH=/metadata
```

---

## Testing

**Syntax validation:**
```bash
python -m py_compile datashredpy/datamesh/*.py
```

**Import validation:**
```bash
python -c "from datashredpy.datamesh import DataProduct; print('✓ OK')"
```

**Run examples:**
```bash
python datashredpy/datamesh/examples.py
```

---

## Performance

- **Schema validation**: O(n) where n = number of records
- **Quality rules**: O(n) per rule
- **Policy evaluation**: O(p) where p = number of policies (typically 4-10)
- **No overhead** on existing pipelines when DataMesh not used

---

## Troubleshooting

**Import error?** Make sure you're in the PyDataShred directory:
```bash
cd /workspaces/PyDataShred
python -c "from datashredpy.datamesh import DataProduct"
```

**API endpoint not found?** Make sure you included the router:
```python
from datashredpy.datamesh.discovery_routes import router
app.include_router(router)
```

**Governance check fails?** Review violation messages for remediation:
```python
result = engine.evaluate(context)
if not result["passed"]:
    for violation in result["violations"]:
        print(f"Fix: {violation}")
```

---

## Next Steps

1. **Read** `DATAMESH_QUICK_REFERENCE.md` (5 min)
2. **Run** `python datashredpy/datamesh/examples.py` (15 min)
3. **Create** your first DataProduct (30 min)
4. **Integrate** with your pipeline (1 hour)
5. **Deploy** to production

---

## Support

- **Quick questions**: See `DATAMESH_QUICK_REFERENCE.md`
- **Architecture questions**: See `DATAMESH_ARCHITECTURE_DIAGRAMS.md`
- **Implementation guide**: See `DATAMESH.md`
- **Working examples**: Run `examples.py`
- **Source code**: Review the `.py` files (well-documented)

---

## Contributing

To extend DataMesh:

1. **Custom Policy**: Extend `GovernancePolicy` class (see `governance.py`)
2. **Custom Validator**: Extend `SchemaValidator` class (see `contract_validation.py`)
3. **Additional Endpoint**: Add route to `discovery_routes.py`

All code is production-ready and extensively documented.

---

**Ready to start?** Open `DATAMESH_QUICK_REFERENCE.md` ⭐

