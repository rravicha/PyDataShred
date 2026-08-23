# PyDataShred - DataMesh Architecture & Governance Deep Dive

This document provides a deep architectural guide to PyDataShred's **DataMesh** layer, explaining:
1. Federated Domain Ownership vs Centralized Monoliths
2. Data Product Contracts as Enforceable Code
3. Policy-as-Code Implementation & Governance Engine Internals
4. Schema Evolution, Drift Detection, and Backward Compatibility Algorithms
5. 3-Phase Lifecycle Orchestration

---

## 1. Domain Ownership vs Centralized Monoliths

Traditional data architectures route all data through a central data engineering team, creating bottlenecks:

```
Traditional Monolith:
Sources ──▶ Central Data Team (Bottleneck) ──▶ Monolithic Lake ──▶ Consumers

DataMesh Architecture (PyDataShred):
[ Domain A: Retail ]   ──▶ [ Data Product A (Contract + SLA) ] ──┐
[ Domain B: Airline ]  ──▶ [ Data Product B (Contract + SLA) ] ──┼─▶ Self-Serve Discovery Portal
[ Domain C: Finance ]  ──▶ [ Data Product C (Contract + SLA) ] ──┘   (Federated Governance)
```

In PyDataShred, each business domain defines and manages its own **Data Products**, while global federated policies (PII, retention, schema stability) are automatically enforced by the platform.

---

## 2. Data Product Contract Anatomy

A `DataProductContract` is a machine-readable, enforceable specification defining:

```
DataProductContract
├── Schema (Versioned: Semantic / Timestamp / Hash)
│   ├── SchemaField (Name, Type, Nullable, Constraints: min, max, pattern, enum)
│   └── Backward Compatibility Checker
├── DataQualityRules (null_check, uniqueness, range, pattern, custom SQL/Python)
├── SLA (Freshness, Availability %, Max Latency, RTO)
├── ComplianceLevel (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED)
├── Data Retention (Statutory maximum days)
└── PII Fields (Explicit classification)
```

---

## 3. Policy-as-Code & The Governance Engine

The `GovernanceEngine` uses an extensible visitor/evaluator pattern:

```python
class GovernancePolicy(ABC):
    @abstractmethod
    def evaluate(self, context: PolicyContext) -> PolicyEvaluation:
        pass
```

### Policy Evaluation Lifecycle

1. **Ingestion Phase**:
   - `PIIDetectionPolicy`: Verifies that any columns containing email, phone, SSN, or card patterns are registered in `contract.pii_fields`.
   - `SchemaDriftPolicy`: Verifies schema field definitions and data types.
2. **Transformation Phase**:
   - Quality rules and policies evaluate with non-blocking warnings (`WARN`), allowing intermediate data cleaning.
3. **Publication Phase**:
   - Mandatory evaluation of all policies.
   - `NullThresholdPolicy`: Strictly enforces null limits.
   - `DataRetentionPolicy`: Confirms retention period does not exceed compliance bounds.
   - If any policy yields `DENY`, the publication phase aborts and records the failure in the audit log.

---

## 4. Schema Versioning & Backward Compatibility Algorithm

PyDataShred applies strict schema compatibility rules:

```
For each field in NEW Schema:
  - If field is NOT in OLD schema AND is NOT nullable: INCOMPATIBLE (Breaks legacy readers)
  - If field IS in OLD schema:
      - Types must match exactly
      - Required field CAN become Nullable (Safe upgrade)

For each field in OLD Schema:
  - If field is NOT in NEW schema AND is NOT nullable: INCOMPATIBLE (Removed required field)
  - If field is NOT in NEW schema AND IS nullable: COMPATIBLE (Safe removal)
```

### Semantic Versioning Rules:
- `v1.0.0` &rarr; `v1.1.0`: Added optional nullable fields (Compatible).
- `v1.0.0` &rarr; `v2.0.0`: Type changes or required field additions/removals (Breaking change).

---

## 5. Summary & Best Practices

1. **Explicit Contracts**: Always define field constraints (`min`, `max`, `pattern`) and declare all PII fields in `contract.pii_fields`.
2. **Progressive Enforcement**: Start new custom policies in `severity="warn"` mode, inspect logs in the Discovery Portal, then upgrade to `severity="error"`.
3. **Automated Audits**: Use `GovernanceEngine.get_audit_trail()` for automated SOC2/GDPR compliance reporting.
