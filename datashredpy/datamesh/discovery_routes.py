"""
Data Product Discovery Portal - FastAPI Routes
===============================================
REST API for discovering, registering, and managing data products.
"""

import os
import sys
from typing import List, Optional
from datetime import datetime
import logging

if os.uname().nodename == 'zebronics':
    sys.path.append('/home/susi/workspace/github/PyDataShred')
else:
    sys.path.append('/workspaces/PyDataShred')

from fastapi import APIRouter, HTTPException, Query, Body
from datashredpy.datamesh.api_models import (
    RegisterDataProductRequest,
    PublishContractRequest,
    SearchDataProductsRequest,
    DataProductResponse,
    DataProductListResponse,
    ContractResponse,
    SchemaCompatibilityResponse,
    GovernanceEvaluationResponse,
    DataProductValidationResponse,
    ErrorResponse,
    SAMPLE_SEARCH_RESPONSE,
    SAMPLE_CONTRACT_RESPONSE,
    SAMPLE_GOVERNANCE_RESPONSE
)
from datashredpy.datamesh.models import (
    DataProduct,
    DataProductContract,
    Schema,
    SchemaField,
    DataType,
    DataQualityRule,
    SLA
)
from datashredpy.datamesh.contract_validation import ContractValidator
from datashredpy.datamesh.governance import GovernanceEngine, PolicyContext, EnforcementPoint
from datashredpy.api.models import Domain, App, Resources

logger = logging.getLogger(__name__)

# ============================================================================
# ROUTER SETUP
# ============================================================================

router = APIRouter(
    prefix="/api/v1/datamesh",
    tags=["Data Product Discovery & Governance"]
)

# In-memory storage (would be replaced with database)
_products_db: dict = {}
_contracts_db: dict = {}

# Governance engine (singleton)
_governance_engine = GovernanceEngine()


# ============================================================================
# DATA PRODUCT REGISTRATION
# ============================================================================

@router.post(
    "/products/register",
    response_model=DataProductResponse,
    summary="Register a new data product",
    description="Register a new data product for discovery and governance"
)
def register_product(request: RegisterDataProductRequest):
    """
    Register a new data product.
    
    This endpoint creates a discoverable data product that wraps existing
    Domain/App objects. Triggers governance evaluation.
    """
    # Check if already exists
    if request.product_id in _products_db:
        raise HTTPException(status_code=409, detail=f"Product {request.product_id} already exists")
    
    try:
        # Create domain and app objects (would fetch from DB in real system)
        domain = Domain(
            domain_id=request.domain_id,
            domain_name=f"Domain-{request.domain_id}"
        )
        
        app = App(
            app_id=request.app_id,
            app_name=request.product_name,
            resources=Resources(source=None, target=None)
        )
        
        # Create data product
        product = DataProduct(
            product_id=request.product_id,
            product_name=request.product_name,
            description=request.description,
            owner_email=request.owner_email,
            owner_team=request.owner_team,
            domain=domain,
            app=app,
            input_resources=[],
            output_resources=[],
            tags=request.tags,
            documentation_url=request.documentation_url,
            sample_query=request.sample_query
        )
        
        # Store in "database"
        _products_db[request.product_id] = product
        
        logger.info(f"Registered data product: {request.product_id}")
        
        return DataProductResponse(
            product_id=product.product_id,
            product_name=product.product_name,
            description=product.description,
            owner_email=product.owner_email,
            owner_team=product.owner_team,
            domain_id=product.domain.domain_id,
            domain_name=product.domain.domain_name,
            app_id=product.app.app_id,
            app_name=product.app.app_name,
            tags=product.tags,
            documentation_url=product.documentation_url,
            sample_query=product.sample_query,
            created_at=product.created_at,
            updated_at=product.updated_at,
            deprecated=product.deprecated
        )
    
    except Exception as e:
        logger.error(f"Error registering product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CONTRACT MANAGEMENT
# ============================================================================

@router.post(
    "/products/{product_id}/contracts",
    response_model=ContractResponse,
    summary="Publish data product contract",
    description="Publish or update the contract for a data product"
)
def publish_contract(product_id: str, request: PublishContractRequest):
    """
    Publish a contract for a data product.
    
    Contract includes:
    - Schema definition and versioning
    - Data quality rules
    - SLA commitments
    - Compliance & retention policies
    """
    # Verify product exists
    if product_id not in _products_db:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    product = _products_db[product_id]
    
    try:
        # Parse schema fields
        schema_fields = []
        for field_def in request.schema_definition.get("fields", []):
            field = SchemaField(
                name=field_def["name"],
                data_type=DataType(field_def.get("type", "string")),
                nullable=field_def.get("nullable", True),
                description=field_def.get("description"),
                constraints=field_def.get("constraints")
            )
            schema_fields.append(field)
        
        schema = Schema(
            version=request.schema_version,
            fields=schema_fields
        )
        
        # Parse quality rules
        quality_rules = []
        for rule_def in request.quality_rules:
            rule = DataQualityRule(
                rule_id=rule_def.get("rule_id", f"rule-{len(quality_rules)}"),
                name=rule_def.get("name", "Unnamed rule"),
                description=rule_def.get("description"),
                rule_type=rule_def.get("rule_type", "custom"),
                applies_to=rule_def.get("applies_to"),
                threshold=rule_def.get("threshold", 0.95),
                enabled=rule_def.get("enabled", True)
            )
            quality_rules.append(rule)
        
        # Parse SLA
        sla = None
        if request.sla:
            sla = SLA(
                freshness_hours=request.sla["freshness_hours"],
                availability_percent=request.sla["availability_percent"],
                max_latency_seconds=request.sla.get("max_latency_seconds"),
                recovery_time_objective_minutes=request.sla.get("recovery_time_objective_minutes")
            )
        
        # Create contract
        contract = DataProductContract(
            contract_id=request.contract_id,
            product_id=product_id,
            schema=schema,
            quality_rules=quality_rules,
            sla=sla,
            compliance_level=request.compliance_level,
            retention_days=request.retention_days,
            pii_fields=request.pii_fields
        )
        
        # Evaluate governance policies
        context = PolicyContext(
            product=product,
            contract=contract,
            enforcement_point=EnforcementPoint.PUBLICATION
        )
        
        governance_result = _governance_engine.evaluate(context)
        
        if governance_result["overall_decision"].value == "deny":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Governance policy violation",
                    "violations": governance_result["violations"],
                    "remediation": [e.remediation_actions for e in governance_result["evaluations"] if e.remediation_actions]
                }
            )
        
        # Store contract
        _contracts_db[request.contract_id] = contract
        product.contract = contract
        product.updated_at = datetime.utcnow()
        
        logger.info(f"Published contract {request.contract_id} for product {product_id}")
        
        return ContractResponse(
            contract_id=contract.contract_id,
            product_id=contract.product_id,
            schema_version=contract.schema.version,
            fields=[
                {"name": f.name, "type": f.data_type.value, "nullable": f.nullable, 
                 "description": f.description, "constraints": f.constraints}
                for f in contract.schema.fields
            ],
            quality_rules=[
                {"rule_id": r.rule_id, "name": r.name, "rule_type": r.rule_type,
                 "applies_to": r.applies_to, "threshold": r.threshold, "enabled": r.enabled}
                for r in contract.quality_rules
            ],
            sla={"freshness_hours": contract.sla.freshness_hours,
                 "availability_percent": contract.sla.availability_percent,
                 "max_latency_seconds": contract.sla.max_latency_seconds,
                 "recovery_time_objective_minutes": contract.sla.recovery_time_objective_minutes}
            if contract.sla else None,
            compliance_level=contract.compliance_level.value,
            retention_days=contract.retention_days,
            pii_fields=contract.pii_fields,
            created_at=contract.created_at,
            updated_at=contract.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing contract: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/products/{product_id}/contracts/{contract_id}",
    response_model=ContractResponse,
    summary="Get data product contract",
    description="Retrieve contract for a data product"
)
def get_contract(product_id: str, contract_id: str):
    """Get contract details."""
    if contract_id not in _contracts_db:
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
    
    contract = _contracts_db[contract_id]
    
    return ContractResponse(
        contract_id=contract.contract_id,
        product_id=contract.product_id,
        schema_version=contract.schema.version,
        fields=[
            {"name": f.name, "type": f.data_type.value, "nullable": f.nullable}
            for f in contract.schema.fields
        ],
        quality_rules=[
            {"rule_id": r.rule_id, "name": r.name, "rule_type": r.rule_type,
             "threshold": r.threshold, "enabled": r.enabled}
            for r in contract.quality_rules
        ],
        sla=contract.sla.to_dict() if contract.sla else None,
        compliance_level=contract.compliance_level.value,
        retention_days=contract.retention_days,
        pii_fields=contract.pii_fields,
        created_at=contract.created_at,
        updated_at=contract.updated_at
    )


# ============================================================================
# DISCOVERY & SEARCH
# ============================================================================

@router.post(
    "/products/search",
    response_model=DataProductListResponse,
    summary="Search data products",
    description="Discover data products by keyword, domain, owner, tags"
)
def search_products(request: SearchDataProductsRequest):
    """
    Search and discover data products.
    
    Supports:
    - Free-text search across name, description
    - Filter by domain, owner, tags, compliance level
    - Pagination
    """
    results = []
    
    for product in _products_db.values():
        # Apply filters
        if request.domain_id and product.domain.domain_id != request.domain_id:
            continue
        
        if request.owner_email and product.owner_email != request.owner_email:
            continue
        
        if request.compliance_level and product.contract:
            if product.contract.compliance_level.value != request.compliance_level:
                continue
        
        if request.tags:
            if not all(tag in product.tags for tag in request.tags):
                continue
        
        if request.query:
            query_lower = request.query.lower()
            match = (
                query_lower in product.product_name.lower() or
                query_lower in product.description.lower() or
                any(query_lower in tag.lower() for tag in product.tags)
            )
            if not match:
                continue
        
        results.append(product)
    
    # Pagination
    total = len(results)
    paginated = results[request.skip : request.skip + request.limit]
    
    products_response = []
    for product in paginated:
        products_response.append(
            DataProductResponse(
                product_id=product.product_id,
                product_name=product.product_name,
                description=product.description,
                owner_email=product.owner_email,
                owner_team=product.owner_team,
                domain_id=product.domain.domain_id,
                domain_name=product.domain.domain_name,
                app_id=product.app.app_id,
                app_name=product.app.app_name,
                tags=product.tags,
                documentation_url=product.documentation_url,
                sample_query=product.sample_query,
                created_at=product.created_at,
                updated_at=product.updated_at,
                deprecated=product.deprecated
            )
        )
    
    return DataProductListResponse(
        total=total,
        skip=request.skip,
        limit=request.limit,
        products=products_response
    )


@router.get(
    "/products/{product_id}",
    response_model=DataProductResponse,
    summary="Get data product details",
    description="Retrieve full details of a data product"
)
def get_product(product_id: str):
    """Get data product details."""
    if product_id not in _products_db:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    product = _products_db[product_id]
    
    return DataProductResponse(
        product_id=product.product_id,
        product_name=product.product_name,
        description=product.description,
        owner_email=product.owner_email,
        owner_team=product.owner_team,
        domain_id=product.domain.domain_id,
        domain_name=product.domain.domain_name,
        app_id=product.app.app_id,
        app_name=product.app.app_name,
        tags=product.tags,
        documentation_url=product.documentation_url,
        sample_query=product.sample_query,
        created_at=product.created_at,
        updated_at=product.updated_at,
        deprecated=product.deprecated
    )


# ============================================================================
# VALIDATION & GOVERNANCE
# ============================================================================

@router.post(
    "/products/{product_id}/validate",
    response_model=DataProductValidationResponse,
    summary="Validate data product",
    description="Validate data product against contract and governance policies"
)
def validate_product(product_id: str):
    """
    Validate a data product.
    
    Checks:
    - Schema consistency
    - Quality rules (if data available)
    - Governance policies
    """
    if product_id not in _products_db:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    product = _products_db[product_id]
    
    if not product.contract:
        raise HTTPException(status_code=400, detail=f"Product {product_id} has no contract")
    
    # Evaluate governance
    context = PolicyContext(
        product=product,
        contract=product.contract,
        enforcement_point=EnforcementPoint.PUBLICATION
    )
    
    governance_result = _governance_engine.evaluate(context)
    
    return DataProductValidationResponse(
        product_id=product_id,
        timestamp=datetime.utcnow(),
        governance_validation=GovernanceEvaluationResponse(
            passed=governance_result["passed"],
            overall_decision=governance_result["overall_decision"].value,
            violations=governance_result["violations"],
            requires_approval=governance_result["requires_approval"],
            evaluations=[
                {
                    "policy_id": e.policy_id,
                    "policy_name": e.policy_name,
                    "decision": e.decision.value,
                    "message": e.message,
                    "violations": e.violations
                }
                for e in governance_result["evaluations"]
            ]
        ),
        overall_passed=governance_result["passed"]
    )


@router.post(
    "/products/{product_id}/schema-compatibility",
    response_model=SchemaCompatibilityResponse,
    summary="Check schema backward compatibility",
    description="Verify new schema is backward compatible with previous version"
)
def check_schema_compatibility(
    product_id: str,
    old_contract_id: str = Query(..., description="Previous contract ID"),
    new_contract_id: str = Query(..., description="New contract ID")
):
    """Check backward compatibility between schema versions."""
    if old_contract_id not in _contracts_db or new_contract_id not in _contracts_db:
        raise HTTPException(status_code=404, detail="One or both contracts not found")
    
    old_contract = _contracts_db[old_contract_id]
    new_contract = _contracts_db[new_contract_id]
    
    validator = ContractValidator(new_contract)
    is_compatible, issues = validator.check_backward_compatibility(old_contract)
    
    return SchemaCompatibilityResponse(
        compatible=is_compatible,
        issues=issues,
        old_version=old_contract.schema.version,
        new_version=new_contract.schema.version
    )


# ============================================================================
# GOVERNANCE & COMPLIANCE
# ============================================================================

@router.get(
    "/governance/policies",
    summary="List governance policies",
    description="Get list of all registered governance policies"
)
def list_policies():
    """List all active governance policies."""
    return {
        "total": len(_governance_engine.policies),
        "policies": _governance_engine.list_policies()
    }


@router.get(
    "/governance/audit-trail",
    summary="Get governance audit trail",
    description="Retrieve audit log of governance policy evaluations"
)
def get_audit_trail(
    product_id: Optional[str] = Query(None, description="Filter by product ID"),
    limit: int = Query(100, description="Number of records to return")
):
    """Get governance audit trail."""
    return {
        "total": len(_governance_engine.evaluation_history),
        "records": _governance_engine.get_audit_trail(product_id, limit)
    }


# ============================================================================
# HEALTH & DISCOVERY
# ============================================================================

@router.get(
    "/health",
    summary="Health check",
    description="Check DataMesh API health"
)
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "products": len(_products_db),
        "contracts": len(_contracts_db),
        "policies": len(_governance_engine.policies)
    }


@router.get(
    "/stats",
    summary="DataMesh statistics",
    description="Get statistics about registered products and policies"
)
def get_stats():
    """Get DataMesh statistics."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "products": {
            "total": len(_products_db),
            "with_contracts": len([p for p in _products_db.values() if p.contract]),
            "deprecated": len([p for p in _products_db.values() if p.deprecated])
        },
        "contracts": len(_contracts_db),
        "governance": {
            "policies": len(_governance_engine.policies),
            "evaluations": len(_governance_engine.evaluation_history)
        }
    }
