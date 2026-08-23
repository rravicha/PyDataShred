"""Data Product Discovery Portal - API Models.

Pydantic models for REST API request/response.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# REQUEST MODELS
# ============================================================================

class RegisterDataProductRequest(BaseModel):
    """Request to register a new data product."""
    product_id: str = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Human-readable product name")
    description: str = Field(..., description="Detailed product description")
    owner_email: str = Field(..., description="Owner email address")
    owner_team: Optional[str] = Field(None, description="Owner team name")
    domain_id: int = Field(..., description="Parent domain ID")
    app_id: int = Field(..., description="Application ID")
    tags: List[str] = Field(default_factory=list, description="Search tags")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    sample_query: Optional[str] = Field(None, description="Example query for consumers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "retail-transactions-prod",
                "product_name": "Retail Transactions",
                "description": "Real-time transaction data from retail POS",
                "owner_email": "data-team@company.com",
                "owner_team": "Analytics",
                "domain_id": 1,
                "app_id": 1,
                "tags": ["retail", "transactions", "high-value"],
                "documentation_url": "https://docs.company.com/retail-transactions",
                "sample_query": "SELECT * FROM transactions WHERE date >= CURRENT_DATE - 7"
            }
        }


class PublishContractRequest(BaseModel):
    """Request to publish/update data product contract."""
    product_id: str = Field(..., description="Product ID")
    contract_id: str = Field(..., description="Contract ID")
    schema_version: str = Field(..., description="Schema version")
    schema_definition: Dict[str, Any] = Field(..., description="Schema fields")
    quality_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Quality rules")
    sla: Optional[Dict[str, Any]] = Field(None, description="SLA definition")
    compliance_level: str = Field(default="internal", description="Compliance level")
    retention_days: int = Field(default=90, description="Retention period")
    pii_fields: List[str] = Field(default_factory=list, description="PII field names")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "retail-transactions-prod",
                "contract_id": "retail-txn-v1.0.0",
                "schema_version": "1.0.0",
                "schema_definition": {
                    "fields": [
                        {"name": "transaction_id", "type": "string", "nullable": False},
                        {"name": "amount", "type": "decimal", "nullable": False}
                    ]
                },
                "quality_rules": [
                    {
                        "rule_id": "null-check",
                        "name": "No nulls",
                        "rule_type": "null_check",
                        "threshold": 1.0
                    }
                ],
                "sla": {
                    "freshness_hours": 1,
                    "availability_percent": 99.9
                },
                "compliance_level": "confidential",
                "retention_days": 365,
                "pii_fields": ["customer_email"]
            }
        }


class SearchDataProductsRequest(BaseModel):
    """Request to search data products."""
    query: Optional[str] = Field(None, description="Free-text search query")
    domain_id: Optional[int] = Field(None, description="Filter by domain ID")
    owner_email: Optional[str] = Field(None, description="Filter by owner email")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (AND logic)")
    compliance_level: Optional[str] = Field(None, description="Filter by compliance level")
    skip: int = Field(default=0, description="Pagination offset")
    limit: int = Field(default=20, description="Pagination limit")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "transaction",
                "domain_id": 1,
                "tags": ["retail", "high-value"],
                "skip": 0,
                "limit": 20
            }
        }


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class SchemaFieldResponse(BaseModel):
    """Schema field in response."""
    name: str
    type: str
    nullable: bool
    description: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None


class QualityRuleResponse(BaseModel):
    """Quality rule in response."""
    rule_id: str
    name: str
    rule_type: str
    applies_to: Optional[List[str]] = None
    threshold: float
    enabled: bool


class SLAResponse(BaseModel):
    """SLA in response."""
    freshness_hours: int
    availability_percent: float
    max_latency_seconds: Optional[int] = None
    recovery_time_objective_minutes: Optional[int] = None


class ContractResponse(BaseModel):
    """Data product contract response."""
    contract_id: str
    product_id: str
    schema_version: str
    fields: List[SchemaFieldResponse]
    quality_rules: List[QualityRuleResponse]
    sla: Optional[SLAResponse] = None
    compliance_level: str
    retention_days: int
    pii_fields: List[str]
    created_at: datetime
    updated_at: datetime


class DataProductResponse(BaseModel):
    """Data product in response."""
    product_id: str
    product_name: str
    description: str
    owner_email: str
    owner_team: Optional[str] = None
    domain_id: int
    domain_name: str
    app_id: int
    app_name: str
    tags: List[str]
    documentation_url: Optional[str] = None
    sample_query: Optional[str] = None
    contract: Optional[ContractResponse] = None
    created_at: datetime
    updated_at: datetime
    deprecated: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "retail-transactions-prod",
                "product_name": "Retail Transactions",
                "description": "Real-time transaction data",
                "owner_email": "data-team@company.com",
                "owner_team": "Analytics",
                "domain_id": 1,
                "domain_name": "Retail",
                "app_id": 1,
                "app_name": "Transaction Ingestion",
                "tags": ["retail", "transactions"],
                "created_at": "2024-12-13T10:00:00",
                "updated_at": "2024-12-13T10:00:00",
                "deprecated": False
            }
        }


class DataProductListResponse(BaseModel):
    """List of data products with pagination."""
    total: int
    skip: int
    limit: int
    products: List[DataProductResponse]


class SchemaCompatibilityResponse(BaseModel):
    """Schema compatibility check result."""
    compatible: bool
    issues: List[str] = Field(default_factory=list)
    old_version: str
    new_version: str


class GovernanceEvaluationResponse(BaseModel):
    """Governance policy evaluation result."""
    passed: bool
    overall_decision: str
    violations: List[str] = Field(default_factory=list)
    requires_approval: bool
    evaluations: List[Dict[str, Any]] = Field(default_factory=list)


class DataProductValidationResponse(BaseModel):
    """Complete data product validation result."""
    product_id: str
    timestamp: datetime
    schema_validation: Optional[Dict[str, Any]] = None
    quality_validation: Optional[Dict[str, Any]] = None
    governance_validation: Optional[GovernanceEvaluationResponse] = None
    overall_passed: bool


class ErrorResponse(BaseModel):
    """Error response."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


# ============================================================================
# SAMPLE API RESPONSES
# ============================================================================

SAMPLE_SEARCH_RESPONSE = {
    "total": 1,
    "skip": 0,
    "limit": 20,
    "products": [
        {
            "product_id": "retail-transactions-prod",
            "product_name": "Retail Transactions",
            "description": "Real-time transaction data from retail POS systems",
            "owner_email": "data-team@company.com",
            "owner_team": "Analytics",
            "domain_id": 1,
            "domain_name": "Retail",
            "app_id": 1,
            "app_name": "Transaction Ingestion",
            "tags": ["retail", "transactions", "high-value"],
            "documentation_url": "https://docs.company.com/retail-transactions",
            "sample_query": "SELECT * FROM transactions WHERE date >= CURRENT_DATE - 7",
            "created_at": "2024-12-13T10:00:00",
            "updated_at": "2024-12-13T10:00:00",
            "deprecated": False
        }
    ]
}

SAMPLE_CONTRACT_RESPONSE = {
    "contract_id": "retail-txn-v1.0.0",
    "product_id": "retail-transactions-prod",
    "schema_version": "1.0.0",
    "fields": [
        {
            "name": "transaction_id",
            "type": "string",
            "nullable": False,
            "description": "Unique transaction identifier"
        },
        {
            "name": "amount",
            "type": "decimal",
            "nullable": False,
            "description": "Transaction amount",
            "constraints": {"min": 0, "max": 999999.99}
        },
        {
            "name": "timestamp",
            "type": "timestamp",
            "nullable": False,
            "description": "Transaction timestamp in UTC"
        }
    ],
    "quality_rules": [
        {
            "rule_id": "null-check-transaction-id",
            "name": "No null transaction IDs",
            "rule_type": "null_check",
            "applies_to": ["transaction_id"],
            "threshold": 1.0,
            "enabled": True
        }
    ],
    "sla": {
        "freshness_hours": 1,
        "availability_percent": 99.9,
        "max_latency_seconds": 300,
        "recovery_time_objective_minutes": 15
    },
    "compliance_level": "confidential",
    "retention_days": 365,
    "pii_fields": ["customer_email"],
    "created_at": "2024-12-13T10:00:00",
    "updated_at": "2024-12-13T10:00:00"
}

SAMPLE_GOVERNANCE_RESPONSE = {
    "passed": False,
    "overall_decision": "deny",
    "violations": [
        "PII field 'customer_email' detected but not marked in contract.pii_fields",
        "Data with PII marked as PUBLIC. Must be CONFIDENTIAL or RESTRICTED"
    ],
    "requires_approval": False,
    "evaluations": [
        {
            "policy_id": "pii-detection-policy",
            "policy_name": "PII Detection & Classification",
            "decision": "deny",
            "is_enforced": True,
            "message": "PII policy violation: 2 issues found",
            "violations": [
                "PII field 'customer_email' detected but not marked",
                "PII in PUBLIC data"
            ],
            "remediation_actions": [
                "Update contract.pii_fields with PII field names",
                "Set compliance_level to CONFIDENTIAL or RESTRICTED"
            ]
        }
    ]
}
