# DataMesh Quick Reference

## Installation & Setup

```bash
# Add to your FastAPI app
from datashredpy.datamesh.discovery_routes import router
app.include_router(router)

# Now access at: http://localhost:8000/api/v1/datamesh/
```

## Core Concepts

| Concept | Purpose |
|---------|---------|
| **DataProduct** | Self-serve, discoverable dataset with metadata |
| **Contract** | Specification (schema, quality, SLA, compliance) |
| **Schema** | Typed, versioned field definitions |
| **Quality Rule** | Enforceable data quality requirement |
| **Governance Policy** | Pluggable enforcement rule |
| **SLA** | Service level commitment |

## 5-Minute Quick Start

```python
from datashredpy.datamesh import (
    DataProduct, DataProductContract, Schema, SchemaField,
    DataType, DataQualityRule, SLA, ComplianceLevel,
    DataProductPipeline
)
from datashredpy.api.models import Domain, App, Resources

# 1. Define schema
fields = [
    SchemaField(name="id", data_type=DataType.STRING, nullable=False),
    SchemaField(name="email", data_type=DataType.STRING, nullable=False),
]
schema = Schema(version="1.0.0", fields=fields)

# 2. Define quality rules
rules = [
    DataQualityRule(
        rule_id="unique-id",
        name="IDs are unique",
        rule_type="uniqueness",
        applies_to=["id"],
        threshold=1.0
    )
]

# 3. Define contract
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

# 4. Create data product
domain = Domain(domain_id=1, domain_name="Analytics")
app = App(app_id=101, app_name="Ingestion", resources=Resources(source=None, target=None))

product = DataProduct(
    product_id="my-product",
    product_name="My Data Product",
    description="Description here",
    owner_email="owner@company.com",
    domain=domain,
    app=app,
    contract=contract
)

# 5. Execute pipeline with governance
pipeline = DataProductPipeline(product, contract)
ingestion = pipeline.ingestion_phase(df_source, "S3")
transform = pipeline.transformation_phase(df)
publish = pipeline.publication_phase(df_output, "Snowflake")

print(f"✓ Published!" if publish["passed"] else "✗ Failed")
```

## API Endpoints

### Register Product
```bash
POST /api/v1/datamesh/products/register
{
  "product_id": "customer-master",
  "product_name": "Customer Master",
  "owner_email": "data-team@company.com",
  "domain_id": 1,
  "app_id": 101,
  "tags": ["customer"]
}
```

### Publish Contract
```bash
POST /api/v1/datamesh/products/{product_id}/contracts
{
  "contract_id": "customer-v1.0.0",
  "schema_version": "1.0.0",
  "schema_definition": {...},
  "quality_rules": [...],
  "compliance_level": "confidential",
  "pii_fields": ["email"]
}
```

### Search Products
```bash
POST /api/v1/datamesh/products/search
{
  "query": "customer",
  "tags": ["customer"],
  "skip": 0,
  "limit": 20
}
```

### Validate Product
```bash
POST /api/v1/datamesh/products/{product_id}/validate
# Returns schema + quality + governance validation result
```

### List Policies
```bash
GET /api/v1/datamesh/governance/policies
# Returns all active governance policies
```

### Get Audit Trail
```bash
GET /api/v1/datamesh/governance/audit-trail?product_id=xyz&limit=100
# Returns compliance history
```

## Governance Policies

| Policy | Scope | Decision |
|--------|-------|----------|
| **PII Detection** | INGESTION, PUBLICATION | ALLOW / DENY |
| **Schema Drift** | INGESTION, TRANSFORMATION | ALLOW / WARN |
| **Null Threshold** | PUBLICATION | ALLOW / WARN |
| **Data Retention** | PUBLICATION | ALLOW / REQUIRE_APPROVAL |

## Data Types

```python
DataType.STRING       # Text
DataType.INTEGER      # Whole numbers
DataType.FLOAT        # Decimals
DataType.BOOLEAN      # True/False
DataType.TIMESTAMP    # Date+time
DataType.DATE         # Date only
DataType.BINARY       # Bytes
DataType.ARRAY        # Lists
DataType.STRUCT       # Objects
DataType.DECIMAL      # High precision
```

## Quality Rule Types

```python
DataQualityRule(
    rule_type="null_check",      # No nulls
    # OR
    rule_type="uniqueness",      # Unique values
    # OR
    rule_type="range",           # Min/max bounds
    # OR
    rule_type="pattern",         # Regex match
    # OR
    rule_type="custom",          # Custom logic
    
    threshold=0.95,              # % that must pass
    applies_to=["field_name"]    # Which fields
)
```

## Compliance Levels

| Level | Max Retention | Requires PII? |
|-------|---------------|---------------|
| PUBLIC | 30 days | No |
| INTERNAL | 90 days | No |
| CONFIDENTIAL | 365 days | Can contain PII |
| RESTRICTED | Custom | Needs approval |

## Phase Enforcement

### INGESTION Phase
✓ Governance policies (INGESTION scope)
✓ Schema validation on sample
✗ Quality check (not yet)

### TRANSFORMATION Phase
✓ Quality rule checks (warning only)
✓ Governance warnings
✗ Enforcement (not yet)

### PUBLICATION Phase
✓ Full schema validation
✓ Quality rule enforcement
✓ Governance policy enforcement
✓ SLA verification
✓ Audit trail recording

## Common Patterns

### Pattern: Wrap Existing Pipeline
```python
from datashredpy.datamesh import DataMeshIntegrationHelper

pipeline = DataMeshIntegrationHelper.wrap_existing_pipeline(
    domain=my_domain,
    app=my_app,
    product_definition={
        "product_id": "...",
        "contract": {...}
    }
)
```

### Pattern: Custom Policy
```python
from datashredpy.datamesh.governance import GovernancePolicy, PolicyEvaluation, PolicyDecision

class MyPolicy(GovernancePolicy):
    def __init__(self):
        super().__init__(
            policy_id="my-policy",
            policy_name="My Policy",
            severity="error"
        )
    
    def evaluate(self, context):
        violations = []
        if # some check:
            violations.append("Violation")
        
        return PolicyEvaluation(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            decision=PolicyDecision.DENY if violations else PolicyDecision.ALLOW,
            is_enforced=True,
            message="...",
            violations=violations
        )

# Register
engine.register_policy(MyPolicy())
```

### Pattern: Schema Versioning
```python
# v1.0.0 → v1.1.0 (backward compatible)
schema_v1_1 = Schema(
    version="1.1.0",
    fields=[
        # All v1.0.0 fields here
        # Plus new optional fields
        SchemaField(name="new_field", nullable=True)
    ]
)

# Check compatibility
compatible, issues = schema_v1_1.is_compatible_with(schema_v1)
assert compatible, f"Incompatible: {issues}"
```

### Pattern: Validate Data
```python
from datashredpy.datamesh import ContractValidator

validator = ContractValidator(contract)

# Single record
is_valid, errors = validator.schema_validator.validate_record(record)

# Batch
batch_result = validator.schema_validator.validate_batch(records)
# → {"valid_records": X, "invalid_records": Y, "error_summary": {...}}

# Quality rules
quality = validator.quality_engine.evaluate_rules(df)
# → {"passed": bool, "rules_passed": X, "rules_failed": Y, "details": {...}}

# Full validation
report = validator.validate_data(df)
# → {"schema_validation": {...}, "quality_validation": {...}, "overall_passed": bool}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "PII policy violation" | Mark PII fields in `contract.pii_fields`, set compliance to CONFIDENTIAL |
| "Schema drift detected" | Review field changes, ensure types match |
| "Null threshold exceeded" | Increase threshold or fix data quality |
| "Requires approval" | RESTRICTED retention needs manual approval |

## Configuration

Environment variables (optional):

```bash
# Governance mode
export DATAMESH_ENFORCEMENT_MODE=strict  # or warn, disabled

# Metadata storage
export DATAMESH_METADATA_STORE=file      # or db, s3
export DATAMESH_METADATA_PATH=/metadata
```

## Files Created

```
datashredpy/datamesh/
├── __init__.py                  (Public API exports)
├── models.py                    (DataProduct, Contract, etc.)
├── contract_validation.py       (Schema & quality validation)
├── governance.py                (Policies & enforcement)
├── api_models.py                (Pydantic models)
├── discovery_routes.py          (FastAPI routes)
├── pipeline_integration.py      (Pipeline wrapper)
├── examples.py                  (Usage examples)
└── DATAMESH.md                  (Full documentation)
```

## Learn More

- **Architecture**: See `DATAMESH.md` for detailed design
- **Examples**: Run `examples.py` for 6 complete examples
- **API**: Swagger at `/api/v1/datamesh/` (auto-generated)
- **Tests**: See `tests/test_datamesh.py` (coming soon)

## Support

For issues or questions:
1. Check `examples.py` for usage patterns
2. Review `DATAMESH.md` for architecture decisions
3. Examine policy code in `governance.py` for customization
