"""DataMesh for PyDataShred - Complete Usage Examples.

Demonstrates how to use the DataMesh layer with existing PyDataShred pipelines.
"""
import logging
import os
import sys
from datetime import datetime

from datashredpy.api.models import Domain, App, Resources
from datashredpy.datamesh.contract_validation import (
    SchemaValidator, QualityRuleEngine, ContractValidator
)
from datashredpy.datamesh.governance import (
    GovernanceEngine, PolicyContext, EnforcementPoint,
    PIIDetectionPolicy, SchemaDriftPolicy
)
from datashredpy.datamesh.models import (
    DataProduct, DataProductContract, Schema, SchemaField, DataType,
    DataQualityRule, SLA, ComplianceLevel, EXAMPLE_DATA_PRODUCT_DEFINITION
)
from datashredpy.datamesh.pipeline_integration import (
    DataProductPipeline, DataMeshIntegrationHelper
)

logger = logging.getLogger(__name__)


# ============================================================================
# EXAMPLE 1: Create a Data Product with Contract
# ============================================================================

def example_1_create_data_product():
    """
    Example: Define and create a data product with contract.
    
    This shows how to:
    - Define a data product
    - Create a versioned schema
    - Define quality rules and SLAs
    - Specify compliance requirements
    """
    print("\n" + "="*70)
    logger.info("EXAMPLE 1: Create a Data Product with Contract")
    print("="*70)
    
    # Define schema fields
    fields = [
        SchemaField(
            name="customer_id",
            data_type=DataType.STRING,
            nullable=False,
            description="Unique customer identifier",
            constraints=None
        ),
        SchemaField(
            name="email",
            data_type=DataType.STRING,
            nullable=False,
            description="Customer email (PII)",
            constraints={"pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}
        ),
        SchemaField(
            name="age",
            data_type=DataType.INTEGER,
            nullable=True,
            description="Customer age",
            constraints={"min": 0, "max": 150}
        ),
        SchemaField(
            name="signup_date",
            data_type=DataType.TIMESTAMP,
            nullable=False,
            description="Account creation timestamp"
        ),
        SchemaField(
            name="annual_revenue",
            data_type=DataType.DECIMAL,
            nullable=True,
            description="Annual revenue",
            constraints={"min": 0}
        )
    ]
    
    # Create schema
    schema = Schema(
        version="1.0.0",
        fields=fields
    )
    
    print(f"\n✓ Schema created: v{schema.version}")
    print(f"  Fields: {[f.name for f in schema.fields]}")
    
    # Define quality rules
    quality_rules = [
        DataQualityRule(
            rule_id="unique-customer-id",
            name="Customer ID uniqueness",
            rule_type="uniqueness",
            applies_to=["customer_id"],
            threshold=1.0,
            enabled=True
        ),
        DataQualityRule(
            rule_id="email-pattern",
            name="Valid email format",
            rule_type="pattern",
            applies_to=["email"],
            threshold=0.99,
            enabled=True
        ),
        DataQualityRule(
            rule_id="age-range",
            name="Age within valid range",
            rule_type="range",
            applies_to=["age"],
            threshold=0.95,
            enabled=True
        ),
        DataQualityRule(
            rule_id="null-check",
            name="No nulls in required fields",
            rule_type="null_check",
            applies_to=["customer_id", "email"],
            threshold=1.0,
            enabled=True
        )
    ]
    
    print(f"\n✓ Quality rules defined: {len(quality_rules)}")
    for rule in quality_rules:
        print(f"  - {rule.name} (threshold: {rule.threshold:.0%})")
    
    # Define SLA
    sla = SLA(
        freshness_hours=24,
        availability_percent=99.5,
        max_latency_seconds=3600,
        recovery_time_objective_minutes=30
    )
    
    print(f"\n✓ SLA defined:")
    print(f"  - Freshness: {sla.freshness_hours}h")
    print(f"  - Availability: {sla.availability_percent}%")
    print(f"  - Max latency: {sla.max_latency_seconds}s")
    
    # Create contract
    contract = DataProductContract(
        contract_id="customers-v1.0.0",
        product_id="customer-master",
        schema=schema,
        quality_rules=quality_rules,
        sla=sla,
        compliance_level=ComplianceLevel.CONFIDENTIAL,
        retention_days=365,
        pii_fields=["email"],
        tags=["customer", "confidential", "high-priority"]
    )
    
    print(f"\n✓ Contract created: {contract.contract_id}")
    print(f"  Compliance: {contract.compliance_level.value}")
    print(f"  Retention: {contract.retention_days} days")
    print(f"  PII fields: {contract.pii_fields}")
    
    # Create data product
    domain = Domain(domain_id=1, domain_name="Customer Analytics")
    app = App(app_id=101, app_name="Customer Ingestion", resources=Resources(source=None, target=None))
    
    product = DataProduct(
        product_id="customer-master",
        product_name="Customer Master Data",
        description="Single source of truth for customer information",
        owner_email="customer-team@company.com",
        owner_team="Customer Analytics",
        domain=domain,
        app=app,
        input_resources=[],
        output_resources=[],
        contract=contract,
        tags=["customer", "confidential", "high-priority"],
        documentation_url="https://docs.company.com/customer-master"
    )
    
    print(f"\n✓ Data Product created: {product.product_name}")
    print(f"  Owner: {product.owner_email}")
    print(f"  Domain: {product.domain.domain_name}")
    
    return product, contract


# ============================================================================
# EXAMPLE 2: Schema Validation
# ============================================================================

def example_2_schema_validation():
    """
    Example: Validate records against schema.
    
    Shows:
    - Single record validation
    - Batch validation
    - Error reporting
    """
    print("\n" + "="*70)
    logger.info("EXAMPLE 2: Schema Validation")
    print("="*70)
    
    # Create simple schema
    schema = Schema(
        version="1.0.0",
        fields=[
            SchemaField(name="id", data_type=DataType.INTEGER, nullable=False),
            SchemaField(name="name", data_type=DataType.STRING, nullable=False),
            SchemaField(name="age", data_type=DataType.INTEGER, nullable=True,
                       constraints={"min": 0, "max": 150})
        ]
    )
    
    validator = SchemaValidator(schema)
    
    # Valid record
    valid_record = {
        "id": 1,
        "name": "Alice",
        "age": 30
    }
    
    is_valid, errors = validator.validate_record(valid_record)
    print(f"\n✓ Valid record: {is_valid}")
    if errors:
        print(f"  Errors: {errors}")
    
    # Invalid record (missing required field)
    invalid_record_1 = {
        "id": 2,
        "age": 25
    }
    
    is_valid, errors = validator.validate_record(invalid_record_1)
    print(f"\n✗ Invalid record (missing name): {is_valid}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    
    # Invalid record (type mismatch)
    invalid_record_2 = {
        "id": "three",  # Should be integer
        "name": "Charlie",
        "age": 35
    }
    
    is_valid, errors = validator.validate_record(invalid_record_2)
    print(f"\n✗ Invalid record (type mismatch): {is_valid}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    
    # Invalid record (constraint violation)
    invalid_record_3 = {
        "id": 4,
        "name": "David",
        "age": 200  # Exceeds max
    }
    
    is_valid, errors = validator.validate_record(invalid_record_3)
    print(f"\n✗ Invalid record (constraint): {is_valid}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    
    # Batch validation
    records = [valid_record, invalid_record_1, invalid_record_2, invalid_record_3]
    batch_result = validator.validate_batch(records)
    
    print(f"\n✓ Batch validation result:")
    print(f"  Total: {batch_result['total_records']}")
    print(f"  Valid: {batch_result['valid_records']}")
    print(f"  Invalid: {batch_result['invalid_records']}")


# ============================================================================
# EXAMPLE 3: Schema Compatibility & Versioning
# ============================================================================

def example_3_schema_compatibility():
    """
    Example: Check schema backward compatibility.
    
    Shows:
    - Adding nullable fields (compatible)
    - Removing nullable fields (compatible)
    - Type changes (incompatible)
    - Removing required fields (incompatible)
    """
    print("\n" + "="*70)
    logger.info("EXAMPLE 3: Schema Compatibility & Versioning")
    print("="*70)
    
    # Original schema
    schema_v1 = Schema(
        version="1.0.0",
        fields=[
            SchemaField(name="id", data_type=DataType.STRING, nullable=False),
            SchemaField(name="name", data_type=DataType.STRING, nullable=False),
            SchemaField(name="email", data_type=DataType.STRING, nullable=True)
        ]
    )
    
    # Scenario 1: Add optional field (compatible)
    schema_v1_add = Schema(
        version="1.1.0",
        fields=[
            SchemaField(name="id", data_type=DataType.STRING, nullable=False),
            SchemaField(name="name", data_type=DataType.STRING, nullable=False),
            SchemaField(name="email", data_type=DataType.STRING, nullable=True),
            SchemaField(name="phone", data_type=DataType.STRING, nullable=True)  # New optional
        ]
    )
    
    compatible, issues = schema_v1_add.is_compatible_with(schema_v1)
    print(f"\n✓ Add optional field 'phone': Compatible = {compatible}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    
    # Scenario 2: Change type (incompatible)
    schema_v1_change = Schema(
        version="1.2.0",
        fields=[
            SchemaField(name="id", data_type=DataType.INTEGER, nullable=False),  # Changed!
            SchemaField(name="name", data_type=DataType.STRING, nullable=False),
            SchemaField(name="email", data_type=DataType.STRING, nullable=True)
        ]
    )
    
    compatible, issues = schema_v1_change.is_compatible_with(schema_v1)
    print(f"\n✗ Change 'id' type to INTEGER: Compatible = {compatible}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    
    # Scenario 3: Make required field optional (compatible)
    schema_v1_optional = Schema(
        version="1.3.0",
        fields=[
            SchemaField(name="id", data_type=DataType.STRING, nullable=False),
            SchemaField(name="name", data_type=DataType.STRING, nullable=True),  # Now optional
            SchemaField(name="email", data_type=DataType.STRING, nullable=True)
        ]
    )
    
    compatible, issues = schema_v1_optional.is_compatible_with(schema_v1)
    print(f"\n✓ Make 'name' optional: Compatible = {compatible}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")


# ============================================================================
# EXAMPLE 4: Governance Policy Evaluation
# ============================================================================

def example_4_governance():
    """
    Example: Evaluate governance policies.
    
    Shows:
    - PII detection
    - Schema drift prevention
    - Policy results and remediation
    """
    print("\n" + "="*70)
    logger.info("EXAMPLE 4: Governance Policy Evaluation")
    print("="*70)
    
    # Create data product
    product, contract = example_1_create_data_product()
    
    # Create governance engine
    engine = GovernanceEngine()
    
    print(f"\n✓ Governance engine initialized")
    print(f"  Active policies: {len(engine.policies)}")
    for policy in engine.policies.values():
        print(f"  - {policy.policy_name}")
    
    # Evaluate policies
    context = PolicyContext(
        product=product,
        contract=contract,
        enforcement_point=EnforcementPoint.PUBLICATION
    )
    
    result = engine.evaluate(context)
    
    print(f"\n{'✓' if result['passed'] else '✗'} Overall Decision: {result['overall_decision'].value}")
    
    if not result['passed']:
        print(f"\nViolations ({len(result['violations'])}):")
        for violation in result['violations']:
            print(f"  - {violation}")
    
    print(f"\nPolicy Evaluations:")
    for evaluation in result['evaluations']:
        status_symbol = "✓" if evaluation.decision.value == "allow" else "✗"
        print(f"  {status_symbol} {evaluation.policy_name}")
        print(f"      Decision: {evaluation.decision.value}")
        print(f"      Message: {evaluation.message}")
        if evaluation.remediation_actions:
            print(f"      Remediation:")
            for action in evaluation.remediation_actions:
                print(f"        - {action}")


# ============================================================================
# EXAMPLE 5: Pipeline Integration
# ============================================================================

def example_5_pipeline_integration():
    """
    Example: Integrate DataMesh with PyDataShred pipeline.
    
    Shows:
    - Wrapping existing pipelines
    - Executing with governance enforcement
    - Lifecycle management
    """
    print("\n" + "="*70)
    logger.info("EXAMPLE 5: Pipeline Integration with DataMesh")
    print("="*70)
    
    # Create data product
    product, contract = example_1_create_data_product()
    
    # Create governance engine
    engine = GovernanceEngine()
    
    # Create pipeline wrapper
    pipeline = DataProductPipeline(
        data_product=product,
        contract=contract,
        governance_engine=engine
    )
    
    print(f"\n✓ Pipeline created: {product.product_name}")
    print(f"  Contract: {contract.contract_id}")
    
    # Define transformation function
    def transform_customers(df):
        """Example transformation"""
        # This would contain real business logic
        return df.filter(lambda row: row['age'] is None or row['age'] >= 18)
    
    # Simulate ingestion phase
    print(f"\n▶ INGESTION PHASE")
    print(f"  Checking governance policies...")
    # In real scenario, would pass actual DataFrame
    # ingestion_result = pipeline.ingestion_phase(df_source, source_name="S3 bucket")
    print(f"  ✓ Governance check passed")
    print(f"  ✓ Schema validation passed")
    
    # Simulate transformation phase
    print(f"\n▶ TRANSFORMATION PHASE")
    print(f"  Applying business logic...")
    # transformation_result = pipeline.transformation_phase(df, transform_fn=transform_customers)
    print(f"  ✓ Transformation completed")
    
    # Simulate publication phase
    print(f"\n▶ PUBLICATION PHASE")
    print(f"  Validating data...")
    # publication_result = pipeline.publication_phase(df_output, target_name="Snowflake")
    print(f"  ✓ Validation passed")
    print(f"  ✓ Governance check passed")
    print(f"  ✓ Published to target")
    
    # Get execution summary
    summary = pipeline.get_execution_summary()
    print(f"\n✓ Execution Summary:")
    print(f"  Product: {summary['product_id']}")
    print(f"  Status: {summary['status']}")
    print(f"  Phases executed: {summary['phases']}")


# ============================================================================
# EXAMPLE 6: Discovery Portal Usage
# ============================================================================

def example_6_discovery_portal():
    """
    Example: Using the Discovery Portal API.
    
    Shows:
    - Registering products
    - Publishing contracts
    - Searching products
    - Validation endpoints
    """
    print("\n" + "="*70)
    logger.info("EXAMPLE 6: Discovery Portal API Usage")
    print("="*70)
    
    # These would be API calls in real usage
    
    # 1. Register product
    print(f"\n▶ Register Data Product")
    print(f'  POST /api/v1/datamesh/products/register')
    print(f'  Payload: {{"product_id": "customer-master", "product_name": "Customer Master"}}')
    print(f"  ✓ Response 201 Created")
    
    # 2. Publish contract
    print(f"\n▶ Publish Contract")
    print(f'  POST /api/v1/datamesh/products/customer-master/contracts')
    print(f'  Payload: {{contract definition}}')
    print(f"  ✓ Response 200 OK")
    
    # 3. Search products
    print(f"\n▶ Search Data Products")
    print(f'  POST /api/v1/datamesh/products/search')
    print(f'  Payload: {{"query": "customer", "tags": ["customer"]}}')
    print(f"  ✓ Response: 1 product found")
    
    # 4. Get product details
    print(f"\n▶ Get Product Details")
    print(f'  GET /api/v1/datamesh/products/customer-master')
    print(f"  ✓ Response: Product details with contract")
    
    # 5. Validate product
    print(f"\n▶ Validate Data Product")
    print(f'  POST /api/v1/datamesh/products/customer-master/validate')
    print(f"  ✓ Response: Validation report")
    
    # 6. List policies
    print(f"\n▶ List Governance Policies")
    print(f'  GET /api/v1/datamesh/governance/policies')
    print(f"  ✓ Response: 4 policies active")
    
    # 7. Get audit trail
    print(f"\n▶ Get Governance Audit Trail")
    print(f'  GET /api/v1/datamesh/governance/audit-trail')
    print(f"  ✓ Response: Compliance history")


# ============================================================================
# RUN ALL EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("PyDataShred DataMesh - Complete Examples")
    print("="*70)
    
    # Run examples
    example_1_create_data_product()
    example_2_schema_validation()
    example_3_schema_compatibility()
    example_4_governance()
    example_5_pipeline_integration()
    example_6_discovery_portal()
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")
