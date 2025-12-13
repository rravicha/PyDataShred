"""
DataMesh Integration Layer
==========================
Integrates DataMesh governance, contracts, and discovery with existing
PyDataShred pipelines.

Provides:
- DataProduct lifecycle management
- Contract enforcement during pipeline execution
- Metadata publication post-run
- Backward compatibility with existing Domain/App/Resource models
"""

import os
import sys
from typing import Any, Dict, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass
import logging

if os.uname().nodename == 'zebronics':
    sys.path.append('/home/susi/workspace/github/PyDataShred')
else:
    sys.path.append('/workspaces/PyDataShred')

from datashredpy.datamesh.models import DataProduct, DataProductContract, ComplianceLevel
from datashredpy.datamesh.contract_validation import ContractValidator
from datashredpy.datamesh.governance import GovernanceEngine, PolicyContext, EnforcementPoint
from datashredpy.api.models import Domain, App, Resources

logger = logging.getLogger(__name__)


# ============================================================================
# EXECUTION CONTEXT & HOOKS
# ============================================================================

@dataclass
class DataMeshExecutionContext:
    """Context for DataMesh-aware pipeline execution."""
    data_product: DataProduct
    contract: DataProductContract
    
    # Execution phases
    on_ingestion_start: Optional[Callable] = None
    on_ingestion_complete: Optional[Callable] = None
    on_transformation_start: Optional[Callable] = None
    on_transformation_complete: Optional[Callable] = None
    on_publication_start: Optional[Callable] = None
    on_publication_complete: Optional[Callable] = None
    
    # Metadata
    execution_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "product_id": self.data_product.product_id,
            "contract_id": self.contract.contract_id,
            "execution_id": self.execution_id,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


# ============================================================================
# DATA PRODUCT WRAPPER FOR PIPELINES
# ============================================================================

class DataProductPipeline:
    """
    Wraps an existing PyDataShred pipeline with DataMesh enforcement.
    
    Usage:
        product = DataProductPipeline(data_product, contract)
        product.ingestion_phase(df_source)
        product.transformation_phase(df, transform_fn)
        product.publication_phase(df_target)
    """
    
    def __init__(
        self,
        data_product: DataProduct,
        contract: DataProductContract,
        governance_engine: Optional[GovernanceEngine] = None
    ):
        """Initialize pipeline wrapper."""
        self.data_product = data_product
        self.contract = contract
        self.governance_engine = governance_engine or GovernanceEngine()
        self.context = DataMeshExecutionContext(
            data_product=data_product,
            contract=contract
        )
        self.validator = ContractValidator(contract)
        self.execution_log = []
    
    def ingestion_phase(self, df_source, source_name: str = "unknown") -> Dict[str, Any]:
        """
        Ingestion phase: Initial data load from source.
        
        Enforces:
        - Governance policies (INGESTION scope)
        - Basic schema validation
        
        Args:
            df_source: Source DataFrame (PySpark or Pandas)
            source_name: Name of source for logging
        
        Returns:
            {
                "passed": bool,
                "governance": {...},
                "schema_validation": {...},
                "record_count": int
            }
        """
        logger.info(f"[{self.data_product.product_id}] Starting INGESTION phase from {source_name}")
        
        self.context.start_time = datetime.utcnow()
        self.context.status = "running"
        
        # Call ingestion hook
        if self.context.on_ingestion_start:
            self.context.on_ingestion_start(self.context)
        
        results = {
            "phase": "ingestion",
            "source": source_name,
            "timestamp": datetime.utcnow().isoformat(),
            "passed": True,
            "governance": None,
            "schema_validation": None,
            "record_count": self._count_records(df_source)
        }
        
        try:
            # Governance check
            policy_context = PolicyContext(
                product=self.data_product,
                contract=self.contract,
                enforcement_point=EnforcementPoint.INGESTION
            )
            
            governance_result = self.governance_engine.evaluate(policy_context)
            results["governance"] = governance_result
            
            if not governance_result["passed"]:
                results["passed"] = False
                logger.error(f"Ingestion governance check FAILED: {governance_result['violations']}")
                return results
            
            # Schema validation
            if hasattr(df_source, "collect"):  # PySpark
                sample = df_source.limit(1000).collect()
                records = [row.asDict() for row in sample]
            else:  # Pandas
                records = df_source.head(1000).to_dict('records')
            
            schema_result = self.validator.schema_validator.validate_batch(records)
            results["schema_validation"] = schema_result
            
            if schema_result["invalid_records"] > 0:
                logger.warning(f"Schema validation found {schema_result['invalid_records']} invalid records")
            
            logger.info(f"Ingestion phase COMPLETED for {results['record_count']} records")
            self._log_execution("ingestion", "completed", results)
            
            # Call completion hook
            if self.context.on_ingestion_complete:
                self.context.on_ingestion_complete(self.context, results)
        
        except Exception as e:
            logger.error(f"Ingestion phase FAILED: {str(e)}")
            results["passed"] = False
            results["error"] = str(e)
            self._log_execution("ingestion", "failed", results)
        
        return results
    
    def transformation_phase(
        self,
        df: Any,
        transform_fn: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Transformation phase: Apply business logic.
        
        Enforces:
        - Governance policies (TRANSFORMATION scope)
        - Quality rules (warning level)
        
        Args:
            df: Input DataFrame
            transform_fn: Optional transformation function
        
        Returns:
            {
                "passed": bool,
                "governance": {...},
                "quality_report": {...},
                "output_records": int,
                "output_df": DataFrame
            }
        """
        logger.info(f"[{self.data_product.product_id}] Starting TRANSFORMATION phase")
        
        results = {
            "phase": "transformation",
            "timestamp": datetime.utcnow().isoformat(),
            "passed": True,
            "governance": None,
            "quality_report": None,
            "output_records": 0,
            "output_df": None
        }
        
        try:
            # Call transformation hook
            if self.context.on_transformation_start:
                self.context.on_transformation_start(self.context)
            
            # Apply transformation if provided
            output_df = df
            if transform_fn:
                logger.info("Applying transformation function")
                output_df = transform_fn(df)
            
            # Governance check
            policy_context = PolicyContext(
                product=self.data_product,
                contract=self.contract,
                enforcement_point=EnforcementPoint.TRANSFORMATION
            )
            
            governance_result = self.governance_engine.evaluate(policy_context)
            results["governance"] = governance_result
            
            if not governance_result["passed"]:
                logger.warning(f"Transformation governance warnings: {governance_result['violations']}")
            
            # Quality check (non-blocking for transformation)
            quality_result = self.validator.quality_engine.evaluate_rules(output_df)
            results["quality_report"] = quality_result
            
            results["output_records"] = self._count_records(output_df)
            results["output_df"] = output_df
            
            logger.info(f"Transformation phase COMPLETED, output: {results['output_records']} records")
            self._log_execution("transformation", "completed", results)
            
            # Call completion hook
            if self.context.on_transformation_complete:
                self.context.on_transformation_complete(self.context, results)
        
        except Exception as e:
            logger.error(f"Transformation phase FAILED: {str(e)}")
            results["passed"] = False
            results["error"] = str(e)
            self._log_execution("transformation", "failed", results)
        
        return results
    
    def publication_phase(
        self,
        df: Any,
        target_name: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Publication phase: Publish to target/catalog.
        
        Enforces:
        - Governance policies (PUBLICATION scope)
        - Schema validation
        - Quality rule enforcement
        - Compliance checks
        
        Args:
            df: Output DataFrame to publish
            target_name: Name of target for logging
        
        Returns:
            {
                "passed": bool,
                "governance": {...},
                "schema_validation": {...},
                "quality_report": {...},
                "record_count": int,
                "metadata": {...}
            }
        """
        logger.info(f"[{self.data_product.product_id}] Starting PUBLICATION phase to {target_name}")
        
        results = {
            "phase": "publication",
            "target": target_name,
            "timestamp": datetime.utcnow().isoformat(),
            "passed": True,
            "governance": None,
            "schema_validation": None,
            "quality_report": None,
            "record_count": self._count_records(df),
            "metadata": {}
        }
        
        try:
            # Call publication hook
            if self.context.on_publication_start:
                self.context.on_publication_start(self.context)
            
            # Full validation
            validation_report = self.validator.validate_data(
                df,
                validate_schema=True,
                validate_quality=True
            )
            
            results["schema_validation"] = validation_report.get("schema_validation")
            results["quality_report"] = validation_report.get("quality_validation")
            
            if not validation_report["overall_passed"]:
                results["passed"] = False
                logger.error("Publication validation FAILED")
                return results
            
            # Governance check
            policy_context = PolicyContext(
                product=self.data_product,
                contract=self.contract,
                enforcement_point=EnforcementPoint.PUBLICATION
            )
            
            governance_result = self.governance_engine.evaluate(policy_context)
            results["governance"] = governance_result
            
            if governance_result["requires_approval"]:
                results["requires_approval"] = True
                logger.warning("Publication requires compliance approval")
                return results
            
            if not governance_result["passed"]:
                results["passed"] = False
                logger.error(f"Publication governance check FAILED: {governance_result['violations']}")
                return results
            
            # Generate publication metadata
            results["metadata"] = {
                "product_id": self.data_product.product_id,
                "contract_id": self.contract.contract_id,
                "schema_version": self.contract.schema.version,
                "record_count": results["record_count"],
                "published_at": datetime.utcnow().isoformat(),
                "target": target_name,
                "compliance_level": self.contract.compliance_level.value,
                "quality_passed": results["quality_report"]["passed"]
            }
            
            logger.info(f"Publication phase COMPLETED, published {results['record_count']} records to {target_name}")
            self._log_execution("publication", "completed", results)
            
            # Call completion hook
            if self.context.on_publication_complete:
                self.context.on_publication_complete(self.context, results)
        
        except Exception as e:
            logger.error(f"Publication phase FAILED: {str(e)}")
            results["passed"] = False
            results["error"] = str(e)
            self._log_execution("publication", "failed", results)
        
        finally:
            self.context.end_time = datetime.utcnow()
            self.context.status = "completed" if results["passed"] else "failed"
        
        return results
    
    def _count_records(self, df) -> int:
        """Count records in DataFrame (framework-agnostic)."""
        if hasattr(df, "count"):  # PySpark
            return df.count()
        else:  # Pandas
            return len(df)
    
    def _log_execution(self, phase: str, status: str, details: Dict[str, Any]):
        """Log execution details."""
        log_entry = {
            "phase": phase,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        self.execution_log.append(log_entry)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        return {
            "product_id": self.data_product.product_id,
            "contract_id": self.contract.contract_id,
            "start_time": self.context.start_time.isoformat() if self.context.start_time else None,
            "end_time": self.context.end_time.isoformat() if self.context.end_time else None,
            "status": self.context.status,
            "phases": len(self.execution_log),
            "log": self.execution_log
        }


# ============================================================================
# INTEGRATION PATTERNS
# ============================================================================

class DataMeshIntegrationHelper:
    """Helper for integrating DataMesh with existing PyDataShred pipelines."""
    
    @staticmethod
    def wrap_existing_pipeline(
        domain: Domain,
        app: App,
        product_definition: Dict[str, Any],
        governance_engine: Optional[GovernanceEngine] = None
    ) -> DataProductPipeline:
        """
        Wrap an existing Domain/App pipeline with DataMesh.
        
        Args:
            domain: Existing Domain object
            app: Existing App object
            product_definition: Data product definition dict
            governance_engine: Optional custom governance engine
        
        Returns:
            DataProductPipeline ready for execution
        """
        # Create data product
        product = DataProduct(
            product_id=product_definition.get("product_id"),
            product_name=product_definition.get("product_name"),
            description=product_definition.get("description"),
            owner_email=product_definition.get("owner_email"),
            owner_team=product_definition.get("owner_team"),
            domain=domain,
            app=app,
            input_resources=product_definition.get("input_resources", []),
            output_resources=product_definition.get("output_resources", []),
            tags=product_definition.get("tags", [])
        )
        
        # Create contract from definition
        contract_def = product_definition.get("contract", {})
        contract = DataProductContract.from_dict({
            "contract_id": contract_def.get("contract_id", f"{product.product_id}-v1"),
            "product_id": product.product_id,
            "schema": contract_def.get("schema", {}),
            "quality_rules": contract_def.get("quality_rules", []),
            "sla": contract_def.get("sla"),
            "compliance_level": contract_def.get("compliance_level", "internal"),
            "retention_days": contract_def.get("retention_days", 90),
            "pii_fields": contract_def.get("pii_fields", []),
            "tags": contract_def.get("tags", [])
        })
        
        # Create pipeline
        pipeline = DataProductPipeline(
            data_product=product,
            contract=contract,
            governance_engine=governance_engine
        )
        
        logger.info(f"Wrapped pipeline {app.app_name} as DataProduct {product.product_id}")
        
        return pipeline


# ============================================================================
# INTEGRATION FLOW DIAGRAM
# ============================================================================

"""
DATAMESH INTEGRATION FLOW:
==========================

Existing PyDataShred Architecture:
┌─────────────────────────────────────┐
│ Client                              │
│  └─ Domain                          │
│      └─ App                         │
│          └─ Resources (in/out)      │
└─────────────────────────────────────┘

DataMesh Enhancement:
┌──────────────────────────────────────────────────┐
│ DataProduct (wraps Domain/App)                    │
│  ├─ Metadata: id, name, owner, tags             │
│  ├─ Links: domain, app                          │
│  └─ Contract:                                     │
│      ├─ Schema (versioned + compat check)       │
│      ├─ Quality Rules (enforceable)             │
│      ├─ SLA (freshness, availability)           │
│      └─ Compliance (retention, PII)             │
└──────────────────────────────────────────────────┘
           │
           ├─ Governance Engine
           │   ├─ PIIDetectionPolicy
           │   ├─ SchemaDriftPolicy
           │   ├─ NullThresholdPolicy
           │   └─ DataRetentionPolicy
           │
           └─ Discovery Portal
               ├─ REST APIs
               ├─ Metadata Catalog
               └─ Compliance Audit Trail

Pipeline Execution with DataMesh:
┌─────────────────────────────────────────────────────┐
│ User initiates pipeline                             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ INGESTION PHASE      │
        ├──────────────────────┤
        │ • Governance check   │
        │ • Schema validation  │
        │ • Source data count  │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ TRANSFORMATION PHASE │
        ├──────────────────────┤
        │ • Apply transforms   │
        │ • Quality check      │
        │ • Governance warn    │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ PUBLICATION PHASE    │
        ├──────────────────────┤
        │ • Full validation    │
        │ • Governance enforce │
        │ • Metadata publish   │
        │ • Catalog update     │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Execution Summary    │
        │ • Status             │
        │ • Metadata           │
        │ • Audit Trail        │
        └──────────────────────┘

Data Product Lifecycle:
1. DESIGN:    DataProduct definition + Contract
2. REGISTER:  Discovery Portal registration
3. VALIDATE:  Governance policy checks
4. EXECUTE:   Pipeline with enforcement
5. PUBLISH:   Metadata to catalog
6. DISCOVER:  Consumers find via portal
7. UPDATE:    Schema versioning + compatibility
"""
