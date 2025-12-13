"""DataMesh Layer Models.

Defines core data product models, contracts, SLAs, and quality rules for PyDataShred.

This layer wraps the existing Client -> Domain -> App -> Resource hierarchy
and adds self-serve, discoverable data products with contracts and governance.
"""
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional, Literal

from datashredpy.api.models import Domain, App, Resources

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class DataType(str, Enum):
    """Supported schema data types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    TIMESTAMP = "timestamp"
    DATE = "date"
    BINARY = "binary"
    ARRAY = "array"
    STRUCT = "struct"
    DECIMAL = "decimal"


class VersioningStrategy(str, Enum):
    """Schema versioning strategies."""
    SEMANTIC = "semantic"  # v1.0.0
    TIMESTAMP = "timestamp"  # 20231213_120000
    HASH = "hash"  # Content-based


class ComplianceLevel(str, Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


# ============================================================================
# SCHEMA & CONTRACTS
# ============================================================================

@dataclass
class SchemaField:
    """Represents a single field in a schema."""
    name: str
    data_type: DataType
    nullable: bool = True
    description: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None  # e.g., {"min": 0, "max": 100}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.data_type.value,
            "nullable": self.nullable,
            "description": self.description,
            "constraints": self.constraints or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SchemaField":
        """Create from dictionary representation."""
        return cls(
            name=data["name"],
            data_type=DataType(data.get("type", "string")),
            nullable=data.get("nullable", True),
            description=data.get("description"),
            constraints=data.get("constraints")
        )


@dataclass
class Schema:
    """Versioned schema contract for data products."""
    version: str
    fields: List[SchemaField]
    versioning_strategy: VersioningStrategy = VersioningStrategy.SEMANTIC
    created_at: datetime = field(default_factory=datetime.utcnow)
    deprecated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "version": self.version,
            "versioning_strategy": self.versioning_strategy.value,
            "fields": [f.to_dict() for f in self.fields],
            "created_at": self.created_at.isoformat(),
            "deprecated": self.deprecated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Schema":
        """Create from dictionary representation."""
        return cls(
            version=data["version"],
            fields=[SchemaField.from_dict(f) for f in data.get("fields", [])],
            versioning_strategy=VersioningStrategy(data.get("versioning_strategy", "semantic")),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            deprecated=data.get("deprecated", False)
        )
    
    def is_compatible_with(self, other: "Schema") -> tuple[bool, List[str]]:
        """
        Check backward compatibility with another schema.
        
        Rules:
        - All required fields (nullable=False) in this schema must exist in other
        - Types must match exactly
        - Fields can be added as long as they're nullable
        - Fields can be removed if they're nullable
        
        Returns:
            (is_compatible, list_of_issues)
        """
        issues = []
        
        # Map other schema fields by name
        other_fields = {f.name: f for f in other.fields}
        
        # Check that all required fields in this schema exist in other
        for field in self.fields:
            if not field.nullable and field.name not in other_fields:
                issues.append(f"Required field '{field.name}' missing in target schema")
            elif field.name in other_fields:
                if field.data_type != other_fields[field.name].data_type:
                    issues.append(
                        f"Field '{field.name}' type mismatch: {field.data_type.value} -> "
                        f"{other_fields[field.name].data_type.value}"
                    )
        
        return len(issues) == 0, issues


@dataclass
class DataQualityRule:
    """Data quality rule enforced on data products."""
    rule_id: str
    name: str
    description: Optional[str] = None
    rule_type: Literal["null_check", "uniqueness", "range", "pattern", "custom"] = "custom"
    applies_to: Optional[List[str]] = None  # Field names; None = all fields
    threshold: float = 0.95  # % of rows that must pass
    enabled: bool = True
    custom_logic: Optional[str] = None  # SQL or Python expression
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "rule_type": self.rule_type,
            "applies_to": self.applies_to,
            "threshold": self.threshold,
            "enabled": self.enabled,
            "custom_logic": self.custom_logic
        }


@dataclass
class SLA:
    """Service Level Agreement for data products."""
    freshness_hours: int  # Max hours data can be stale
    availability_percent: float  # e.g., 99.5 means 99.5%
    max_latency_seconds: Optional[int] = None  # Ingestion latency
    recovery_time_objective_minutes: Optional[int] = None  # RTO
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "freshness_hours": self.freshness_hours,
            "availability_percent": self.availability_percent,
            "max_latency_seconds": self.max_latency_seconds,
            "recovery_time_objective_minutes": self.recovery_time_objective_minutes
        }


@dataclass
class DataProductContract:
    """
    Contract that defines obligations of a data product.
    This is the enforceable specification.
    """
    contract_id: str
    product_id: str
    schema: Schema
    quality_rules: List[DataQualityRule] = field(default_factory=list)
    sla: Optional[SLA] = None
    compliance_level: ComplianceLevel = ComplianceLevel.INTERNAL
    retention_days: int = 90
    pii_fields: List[str] = field(default_factory=list)  # Fields containing PII
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "contract_id": self.contract_id,
            "product_id": self.product_id,
            "schema": self.schema.to_dict(),
            "quality_rules": [r.to_dict() for r in self.quality_rules],
            "sla": self.sla.to_dict() if self.sla else None,
            "compliance_level": self.compliance_level.value,
            "retention_days": self.retention_days,
            "pii_fields": self.pii_fields,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataProductContract":
        """Create from dictionary representation."""
        return cls(
            contract_id=data["contract_id"],
            product_id=data["product_id"],
            schema=Schema.from_dict(data["schema"]),
            quality_rules=[DataQualityRule(**r) for r in data.get("quality_rules", [])],
            sla=SLA(**data["sla"]) if data.get("sla") else None,
            compliance_level=ComplianceLevel(data.get("compliance_level", "internal")),
            retention_days=data.get("retention_days", 90),
            pii_fields=data.get("pii_fields", []),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.utcnow().isoformat()))
        )


# ============================================================================
# DATA PRODUCT
# ============================================================================

@dataclass
class DataProduct:
    """
    Self-serve, discoverable data product.
    
    Wraps existing Domain/App objects and adds DataMesh properties.
    Represents a single source of truth for a dataset.
    """
    product_id: str
    product_name: str
    description: str
    owner_email: str
    domain: Domain  # The Domain this product belongs to
    app: App  # The App executing ingestion/transformation
    contract: DataProductContract  # The contract defining schema, quality, SLA
    
    # Optional fields
    owner_team: Optional[str] = None
    
    # Resources
    input_resources: List[Resources] = field(default_factory=list)  # Source data
    output_resources: List[Resources] = field(default_factory=list)  # Target data
    
    # Discovery & Metadata
    tags: List[str] = field(default_factory=list)
    documentation_url: Optional[str] = None
    sample_query: Optional[str] = None
    
    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deprecated: bool = False
    deprecation_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "description": self.description,
            "owner_email": self.owner_email,
            "owner_team": self.owner_team,
            "domain_name": self.domain.domain_name,
            "domain_id": self.domain.domain_id,
            "app_name": self.app.app_name,
            "app_id": self.app.app_id,
            "contract": self.contract.to_dict() if self.contract else None,
            "tags": self.tags,
            "documentation_url": self.documentation_url,
            "sample_query": self.sample_query,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deprecated": self.deprecated,
            "deprecation_date": self.deprecation_date.isoformat() if self.deprecation_date else None
        }


# ============================================================================
# EXAMPLE YAML DEFINITION (as Python dict)
# ============================================================================

EXAMPLE_DATA_PRODUCT_DEFINITION = {
    "product_id": "retail-transactions-prod",
    "product_name": "Retail Transactions",
    "description": "Real-time transaction data from retail POS systems",
    "owner_email": "data-platform@company.com",
    "owner_team": "Analytics",
    "tags": ["retail", "transactions", "high-value"],
    "documentation_url": "https://docs.company.com/data-products/retail-transactions",
    "sample_query": "SELECT transaction_id, amount, timestamp FROM retail_transactions WHERE date >= CURRENT_DATE - 7",
    "contract": {
        "contract_id": "retail-txn-v1.0.0",
        "product_id": "retail-transactions-prod",
        "schema": {
            "version": "1.0.0",
            "versioning_strategy": "semantic",
            "fields": [
                {
                    "name": "transaction_id",
                    "type": "string",
                    "nullable": False,
                    "description": "Unique transaction identifier",
                    "constraints": None
                },
                {
                    "name": "store_id",
                    "type": "integer",
                    "nullable": False,
                    "description": "Store identifier"
                },
                {
                    "name": "amount",
                    "type": "decimal",
                    "nullable": False,
                    "constraints": {"min": 0, "max": 999999.99}
                },
                {
                    "name": "currency",
                    "type": "string",
                    "nullable": False,
                    "constraints": {"pattern": "^[A-Z]{3}$"}
                },
                {
                    "name": "customer_email",
                    "type": "string",
                    "nullable": True,
                    "description": "Customer email (PII)"
                },
                {
                    "name": "timestamp",
                    "type": "timestamp",
                    "nullable": False,
                    "description": "Transaction timestamp in UTC"
                }
            ]
        },
        "quality_rules": [
            {
                "rule_id": "null-check-transaction-id",
                "name": "No null transaction IDs",
                "rule_type": "null_check",
                "applies_to": ["transaction_id"],
                "threshold": 1.0,
                "enabled": True
            },
            {
                "rule_id": "amount-range-check",
                "name": "Amount within valid range",
                "rule_type": "range",
                "applies_to": ["amount"],
                "threshold": 0.99,
                "enabled": True
            },
            {
                "rule_id": "uniqueness-transaction-id",
                "name": "Transaction IDs are unique",
                "rule_type": "uniqueness",
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
        "tags": ["retail", "transactions", "pii"]
    }
}
