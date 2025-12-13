"""
PyDataShred DataMesh Module
===========================
Self-serve, discoverable data products with federated governance.

This module adds a DataMesh layer to PyDataShred, enabling:
- Data Product abstraction (wraps Domain/App)
- Versioned contracts with schema, quality, and SLA
- Federated governance policies (pluggable, policy-as-code)
- Discovery portal for self-serve data consumption
- Runtime contract enforcement
- Governance audit trail

Quick Start:
    from datashredpy.datamesh import DataProduct, DataProductPipeline
    
    # Create product
    product = DataProduct(...)
    
    # Create contract
    contract = DataProductContract(...)
    
    # Wrap pipeline
    pipeline = DataProductPipeline(product, contract)
    
    # Execute with governance
    ingestion_result = pipeline.ingestion_phase(df_source)
    transform_result = pipeline.transformation_phase(df)
    publish_result = pipeline.publication_phase(df_output)

Modules:
    - models.py: Core data structures (DataProduct, Contract, SLA, etc.)
    - contract_validation.py: Schema validation and quality enforcement
    - governance.py: Federated governance policies and enforcement
    - api_models.py: Pydantic models for REST API
    - discovery_routes.py: FastAPI routes for discovery portal
    - pipeline_integration.py: Integration with PyDataShred pipelines
    - examples.py: Comprehensive usage examples

Documentation:
    See DATAMESH.md for architecture, design patterns, and best practices.
"""

from datashredpy.datamesh.models import (
    DataProduct,
    DataProductContract,
    Schema,
    SchemaField,
    DataQualityRule,
    SLA,
    DataType,
    ComplianceLevel,
    VersioningStrategy
)

from datashredpy.datamesh.contract_validation import (
    SchemaValidator,
    QualityRuleEngine,
    ContractValidator
)

from datashredpy.datamesh.governance import (
    GovernanceEngine,
    GovernancePolicy,
    PolicyContext,
    PolicyEvaluation,
    EnforcementPoint,
    PolicyScope,
    PolicyDecision,
    PIIDetectionPolicy,
    SchemaDriftPolicy,
    NullThresholdPolicy,
    DataRetentionPolicy
)

from datashredpy.datamesh.pipeline_integration import (
    DataProductPipeline,
    DataMeshIntegrationHelper,
    DataMeshExecutionContext
)

__all__ = [
    # Models
    "DataProduct",
    "DataProductContract",
    "Schema",
    "SchemaField",
    "DataQualityRule",
    "SLA",
    "DataType",
    "ComplianceLevel",
    "VersioningStrategy",
    # Validation
    "SchemaValidator",
    "QualityRuleEngine",
    "ContractValidator",
    # Governance
    "GovernanceEngine",
    "GovernancePolicy",
    "PolicyContext",
    "PolicyEvaluation",
    "EnforcementPoint",
    "PolicyScope",
    "PolicyDecision",
    "PIIDetectionPolicy",
    "SchemaDriftPolicy",
    "NullThresholdPolicy",
    "DataRetentionPolicy",
    # Integration
    "DataProductPipeline",
    "DataMeshIntegrationHelper",
    "DataMeshExecutionContext",
]

__version__ = "1.0.0"
__author__ = "PyDataShred Team"
