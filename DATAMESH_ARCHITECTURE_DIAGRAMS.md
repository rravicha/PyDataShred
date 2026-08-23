# DataMesh Architecture Diagrams

## 1. Overall System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    END USERS                                   │
│  (Data Analysts, Data Engineers, Business Teams)               │
└────────────────┬───────────────────────────────__──────────────┘
                 │
┌────────────────▼──────────────────────────────────────────────┐
│           DISCOVERY PORTAL (REST API)                         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Search Products │ View Contracts │ Check SLAs │ Audit... │ │
│  └──────────────────────────────────────────────────────────┘ │
│  Endpoints: /api/v1/datamesh/products/search                  │
│             /api/v1/datamesh/governance/audit-trail           │
└────────────────┬──────────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────────┐
│         DATAMESH ORCHESTRATION LAYER                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ DataProductPipeline (3-phase execution)                │  │
│  │  ├─ INGESTION: Governance + Schema validation          │  │
│  │  ├─ TRANSFORMATION: Quality checks + warnings          │  │
│  │  └─▶ PUBLICATION: Full validation + enforcement        │  │
│  └────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ GovernanceEngine (Policy Enforcement)                    │ │
│  │  ├─ PIIDetectionPolicy                                   │ │
│  │  ├─ SchemaDriftPolicy                                    │ │
│  │  ├─ NullThresholdPolicy                                  │ │
│  │  └─▶ DataRetentionPolicy (+ custom policies)             │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ContractValidator (Schema + Quality)                     │ │
│  │  ├─ SchemaValidator: Type/constraint checking            │ │
│  │  └─▶ QualityRuleEngine: Null/unique/range/pattern        │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────┬─────────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────────┐
│         EXISTING PYDATASHRED LAYER (UNCHANGED)                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Client → Domain → App → Resources                       │ │
│  │                                                          │ │
│  │ ├─ File Ingestion (CSV, JSON, Parquet, etc)            │ │
│  │ ├─ Database Ingestion (MySQL, Snowflake, RDS)          │ │
│  │ ├─ PySpark Processing & Transformations                │ │
│  │ ├─ Pandas Processing                                    │ │
│  │ ├─ SCD (Slowly Changing Dimensions)                    │ │
│  │ └─▶ Multi-cloud Targets (S3, RDS, Snowflake, DDB)       │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Metadata Ingestion Framework                            │ │
│  │  └─▶ Captures lineage, transformations, quality metrics  │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────────┐
│            EXECUTION ENGINES                                  │
│  ├─ PySpark (distributed)                                    │
│  ├─ Pandas (single-machine)                                  │
│  ├─ Apache Airflow (orchestration)                           │
│  ├─ Apache Beam (streaming)                                  │
│  └─▶ AWS Step Functions (serverless)                          │
└────────────────────────────────────────────────────────────────┘
```

## 2. DataProduct Hierarchy

```
Client
  │
  └─▶ Domain (autonomous data domain)
     │   Product Owner: data-team@company.com
     │   Examples: Customer Analytics, Finance, Marketing
     │
     └─▶ App (data ingestion/processing)
        │   Examples: Customer Ingestion, Order Processing
        │
        ├─ DataProduct 1 (wraps App)
        │  ├─ product_id: "customer-master"
        │  ├─ Contract
        │  │  ├─ Schema: customers [id, name, email, signup_date]
        │  │  ├─ Quality: unique IDs, valid emails
        │  │  ├─ SLA: 1h freshness, 99.5% availability
        │  │  └─▶ Compliance: CONFIDENTIAL, 365-day retention
        │  ├─ Owner: data-team@company.com
        │  ├─ Tags: [customer, high-value, confidential]
        │  └─▶ Documentatio
## 3. Contract Structure

```
DataProductContract
├── Schema (versioned, typed)
│   ├── version: "1.0.0"n: https://docs.company.com/customer
        │
        └─▶ DataProduct 2 (another wrapped App)
           └─▶ ...
```

│   ├── Fields
│   │   ├── id: STRING (required)
│   │   ├── email: STRING (required, pattern: email_regex)
│   │   ├── age: INTEGER (optional, range: 0-150)
│   │   ├── signup_date: TIMESTAMP (required)
│   │   └── preferences: STRUCT (optional)
│   └── Compatibility: Can upgrade to 1.1.0 (new optional field)
│
├── Quality Rules
│   ├── null_check: id is 100% non-null
│   ├── uniqueness: email values are unique
│   ├── range: age between 0-150
│   ├── pattern: email matches ^[\w.-]+@[\w.-]+\.\w+$
│   └── custom: revenue > 0 for premium customers
│
├── SLA (Service Levels)
│   ├── freshness_hours: 24
│   ├── availability_percent: 99.5
│   ├── max_latency_seconds: 3600
│   └── rto_minutes: 30
│
└── Compliance & Governance
    ├── compliance_level: CONFIDENTIAL
    ├── retention_days: 365
    ├── pii_fields: [email, phone]
    └── tags: [customer, pii, high-value]
```

## 4. Pipeline Execution Flow with Governance

```
User initiates pipeline
         │
         ▼
┌─────────────────────────────────────┐
│    INGESTION PHASE                  │
│  Source: S3, Database, API          │
├─────────────────────────────────────┤
│ ✓ Check Governance Policies         │
│   ├─▶ PIIDetectionPolicy (INGESTION) │
│   ├─▶ SchemaDriftPolicy              │
│   └─▶ Result: ALLOW / WARN / DENY    │
│                                     │
│ ✓ Validate Schema                   │
│   ├─▶ Type checking                  │
│   ├─▶ Constraint validation          │
│   └─▶ Error summary                  │
│                                     │
│ ✓ Count Records                     │
│   └─▶ Log source metrics             │
└─────────────────────────────────────┘
         │
         ├─ PASS? ──NO──▶ FAIL (log violations, exit)
         │
         ▼ YES
┌─────────────────────────────────────┐
│    TRANSFORMATION PHASE             │
│  Business Logic: Filtering, Joins   │
├─────────────────────────────────────┤
│ ✓ Apply Transform Function          │
│   ├─ User-defined logic             │
│   └─▶ Output DataFrame               │
│                                     │
│ ✓ Quality Rule Checks               │
│   ├─ Null checks (warning)          │
│   ├─ Pass rates per rule            │
│   └─▶ Non-blocking (WARN)            │
│                                     │
│ ✓ Governance Warnings               │
│   ├─ Policy checks (non-enforcing)  │
│   └─▶ Alert if issues but allow      │
└─────────────────────────────────────┘
         │
         ▼ (Always proceed to publication)
┌─────────────────────────────────────┐
│    PUBLICATION PHASE                │
│  Target: Snowflake, S3, RDS         │
├─────────────────────────────────────┤
│ ✓ Full Schema Validation            │
│   ├─ ALL records checked            │
│   ├─ Type/constraint enforcement    │
│   └─▶ FAIL if invalid                │
│                                     │
│ ✓ Quality Rule Enforcement          │
│   ├─ ENFORCED (not just warnings)   │
│   ├─ Each rule must pass threshold  │
│   └─▶ FAIL if any rule fails         │
│                                     │
│ ✓ Governance Enforcement            │
│   ├─ PIIDetectionPolicy (ENFORCE)   │
│   ├─ DataRetentionPolicy (ENFORCE)  │
│   └─▶ FAIL or REQUIRE_APPROVAL       │
│                                     │
│ ✓ SLA Verification                  │
│   ├─ Freshness check                │
│   ├─ Latency check                  │
│   └─▶ Log compliance status          │
│                                     │
│ ✓ Generate Metadata                 │
│   ├─ Record count                   │
│   ├─ Execution timestamp            │
│   ├─ Schema version used            │
│   └─▶ Quality scores                 │
│                                     │
│ ✓ Publish to Target                 │
│   ├─ Write DataFrame                │
│   └─▶ Update catalog                 │
│                                     │
│ ✓ Audit Trail                       │
│   ├─ Record all policy decisions    │
│   ├─ Timestamp & user               │
│   └─▶ Compliance history             │
└─────────────────────────────────────┘
         │
         ├─ PASS? ──YES──▶ SUCCESS! ✓
         │
         └─▶ PASS? ──NO──▶ FAIL (log violations, exit)
              │
              └─▶ REQUIRE_APPROVAL? ──YES──▶ QUEUE for review
                 │
                 └─▶ DENY? ──YES──▶ FAIL (exit)
```

## 5. Governance Policy Evaluation

```
┌─────────────────────────────────────┐
│  GovernanceEngine.evaluate()         │
│  (Evaluates ALL applicable policies) │
└─────────────────────────────────────┘
         │
         ├─▶ PIIDetectionPolicy
         │   ├─ Detect: email, phone, ssn fields
         │   ├─ Verify: marked in contract.pii_fields
         │   ├─ Check: compliance_level is CONFIDENTIAL+
         │   └─▶ Result: ALLOW / DENY
         │
         ├─▶ SchemaDriftPolicy
         │   ├─ Validate: all fields typed
         │   ├─ Check: no breaking changes
         │   └─▶ Result: ALLOW / WARN
         │
         ├─▶ NullThresholdPolicy
         │   ├─ Required fields: <1% nulls
         │   ├─ Optional fields: <10% nulls
         │   └─▶ Result: ALLOW / WARN
         │
         ├─▶ DataRetentionPolicy
         │   ├─ PUBLIC: max 30 days
         │   ├─ INTERNAL: max 90 days
         │   ├─ CONFIDENTIAL: max 365 days
         │   ├─ RESTRICTED: requires approval
         │   └─▶ Result: ALLOW / REQUIRE_APPROVAL / DENY
         │
         └─▶ Custom Policies (user-defined)
             └─▶ Result: ALLOW / WARN / DENY / REQUIRE_APPROVAL
                 │
                 ▼
        ┌─────────────────────────────┐
        │ Aggregate Results            │
        │ overall_decision = worst()   │
        └─────────────────────────────┘
                 │
                 ├─ ALLOW: ✓ Proceed
                 ├─ WARN: ⚠ Log but proceed
                 ├─ DENY: ✗ Block operation
                 └─▶ REQUIRE_APPROVAL: ⏳ Queue for review
```

## 6. Schema Versioning & Compatibility

```
Base Schema (v1.0.0)
├── id: STRING (required)
├── name: STRING (required)
└── email: STRING (optional)

    │
    ├─ Upgrade to v1.1.0 (backward compatible ✓)
    │   └── Add: phone: STRING (optional) ← New field is nullable
    │
    ├─ Upgrade to v1.2.0 (NOT compatible ✗)
    │   └── Change: id: INTEGER ← Type changed, breaks consumers
    │
    ├─ Upgrade to v1.3.0 (backward compatible ✓)
    │   └── Change: name nullable ← Required → optional is safe
    │
    └─▶ Upgrade to v2.0.0 (breaking change)
        └── Remove: email ← Required field removed, breaks consumers


Compatibility Check Algorithm:
────────────────────────────
For each field in NEW schema:
  1. If NOT in old schema AND NOT nullable: INCOMPATIBLE ✗
  2. If in old schema:
     a. Type must match exactly: INCOMPATIBLE if different ✗
     b. Can become nullable: COMPATIBLE ✓
     c. Can stay nullable: COMPATIBLE ✓

For each field in OLD schema:
  1. If NOT in new schema AND NOT nullable: INCOMPATIBLE ✗
  2. If NOT in new schema AND nullable: COMPATIBLE ✓
```

## 7. Discovery Portal Information Flow

```
User
 │
 ├─▶ Search Endpoint
 │   ├─ POST /api/v1/datamesh/products/search
 │   ├─ Query: {query, tags, domain, owner, compliance_level}
 │   └─▶ Response: [DataProduct with contract summary]
 │
 ├─▶ Product Details
 │   ├─ GET /api/v1/datamesh/products/{product_id}
 │   ├─ Includes: metadata, tags, documentation
 │   └─▶ Includes: Contract (schema, quality, SLA)
 │
 ├─▶ Contract Details
 │   ├─ GET /api/v1/datamesh/products/{id}/contracts/{contract_id}
 │   ├─ Schema: field definitions with constraints
 │   ├─ Quality: rules and thresholds
 │   ├─ SLA: commitments
 │   └─▶ Compliance: levels and retention
 │
 ├─▶ Validate Product
 │   ├─ POST /api/v1/datamesh/products/{id}/validate
 │   ├─ Schema validation result
 │   ├─ Quality validation result
 │   └─▶ Governance validation result
 │
 ├─▶ Check Compatibility
 │   ├─ POST /api/v1/datamesh/products/{id}/schema-compatibility
 │   ├─ Compare: old_contract vs new_contract
 │   ├─ Result: compatible? [YES/NO]
 │   └─▶ Issues: [list of incompatibilities]
 │
 ├─▶ List Policies
 │   ├─ GET /api/v1/datamesh/governance/policies
 │   └─▶ Policies: [name, scope, enforcement_points, status]
 │
 └─▶ Audit Trail
     ├─ GET /api/v1/datamesh/governance/audit-trail
     ├─ Filter: product_id, date_range
     └─▶ Results: [timestamp, product, decision, violations]
```

## 8. Class Hierarchy

```
GovernancePolicy (Abstract)
├── PIIDetectionPolicy
│   └── evaluate(): Detects PII fields, checks compliance
├── SchemaDriftPolicy
│   └── evaluate(): Prevents breaking schema changes
├── NullThresholdPolicy
│   └── evaluate(): Enforces null value limits
├── DataRetentionPolicy
│   └── evaluate(): Enforces retention by compliance level
└── CustomPolicy (User-defined)
    └── evaluate(): Custom logic


DataProduct
├── metadata: [id, name, description, owner, tags]
├── domain: Domain (existing PyDataShred)
├── app: App (existing PyDataShred)
├── resources: [input_resources, output_resources]
└── contract: DataProductContract


DataProductContract
├── schema: Schema
│   ├── version: str
│   ├── fields: [SchemaField]
│   │   ├── name: str
│   │   ├── data_type: DataType
│   │   ├── nullable: bool
│   │   └── constraints: Dict
│   └── is_compatible_with(): Backward compatibility check
├── quality_rules: [DataQualityRule]
├── sla: SLA
├── compliance_level: ComplianceLevel
└── pii_fields: [str]


DataProductPipeline
├── ingestion_phase(df, source): Governance + schema checks
├── transformation_phase(df, fn): Quality warnings + transforms
├── publication_phase(df, target): Full validation + enforcement
└── get_execution_summary(): Lifecycle metrics


GovernanceEngine
├── register_policy(policy): Add custom policy
├── unregister_policy(id): Remove policy
├── evaluate(context): Check all applicable policies
├── get_audit_trail(): Compliance history
└── list_policies(): All registered policies
```

## 9. Deployment Architecture

```
                        ┌─────────────────────┐
                        │   Users/Clients     │
                        └──────────┬──────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌──────────────┐        ┌──────────────────┐        ┌──────────────┐
│   Data       │        │   Analytics      │        │   Business   │
│  Engineers   │        │   Dashboards     │        │   Apps       │
└──────┬───────┘        └────────┬─────────┘        └──────┬───────┘
       │                         │                        │
       └─────────────────────────┼────────────────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │   Discovery Portal API    │
                    │  /api/v1/datamesh/*       │
                    │  (FastAPI + Pydantic)     │
                    └────────────┬──────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
    ┌─────────┐          ┌─────────────┐         ┌──────────┐
    │ Product │          │ Governance  │         │ Contract │
    │ Catalog │          │   Engine    │         │  Store   │
    └─────────┘          └─────────────┘         └──────────┘
         │                       │                      │
         └───────────────────────┼──────────────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │   PyDataShred Pipeline    │
                    │ (PySpark, Pandas, APIs)   │
                    └────────────┬──────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
    ┌─────────┐          ┌──────────────┐          ┌────────┐
    │    S3   │          │  Snowflake   │          │  RDS   │
    │  (Files)│          │  (Data Wh)   │          │ (SQL)  │
    └─────────┘          └──────────────┘          └────────┘
```

---

## Summary

The DataMesh layer creates a **self-serve, discoverable, governed** layer on top of PyDataShred while maintaining **full backward compatibility** and enabling **autonomous data domains** with **federated governance**.

