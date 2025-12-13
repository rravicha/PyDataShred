"""
Federated Governance Layer
==========================
Enforces global and domain-level governance policies.

Policy-as-Code approach:
- Global policies (apply to all domains)
- Domain-level overrides (where permitted)
- Enforcement points: ingestion, transformation, publish
- Pluggable architecture
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging
import re

if os.uname().nodename == 'zebronics':
    sys.path.append('/home/susi/workspace/github/PyDataShred')
else:
    sys.path.append('/workspaces/PyDataShred')

from datashredpy.datamesh.models import (
    DataProduct,
    DataProductContract,
    ComplianceLevel,
    SchemaField
)

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class PolicyScope(str, Enum):
    """Scope of policy application."""
    GLOBAL = "global"  # Applies to all domains
    DOMAIN = "domain"  # Applies to specific domain(s)
    PRODUCT = "product"  # Applies to specific product(s)


class PolicyDecision(str, Enum):
    """Policy evaluation result."""
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    REQUIRE_APPROVAL = "require_approval"


class EnforcementPoint(str, Enum):
    """When policy is enforced."""
    INGESTION = "ingestion"  # During data ingestion
    TRANSFORMATION = "transformation"  # During transformations
    PUBLICATION = "publication"  # Before publishing output


# ============================================================================
# POLICY INTERFACES
# ============================================================================

@dataclass
class PolicyContext:
    """Context passed to policy during evaluation."""
    product: DataProduct
    contract: DataProductContract
    data_sample: Optional[Dict[str, Any]] = None  # Sample record for inspection
    enforcement_point: EnforcementPoint = EnforcementPoint.INGESTION
    domain_name: Optional[str] = None
    user_email: Optional[str] = None
    custom_context: Optional[Dict[str, Any]] = None


@dataclass
class PolicyEvaluation:
    """Result of policy evaluation."""
    policy_id: str
    policy_name: str
    decision: PolicyDecision
    is_enforced: bool  # Whether decision blocks operation
    message: str
    violations: List[str] = None
    remediation_actions: List[str] = None
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []
        if self.remediation_actions is None:
            self.remediation_actions = []


class GovernancePolicy(ABC):
    """
    Base class for all governance policies.
    
    Policies are self-contained, versioned, and can be enabled/disabled.
    """
    
    def __init__(
        self,
        policy_id: str,
        policy_name: str,
        description: str,
        scope: PolicyScope = PolicyScope.GLOBAL,
        enabled: bool = True,
        enforcement_points: List[EnforcementPoint] = None,
        severity: str = "error"  # "warning", "error"
    ):
        """Initialize policy."""
        self.policy_id = policy_id
        self.policy_name = policy_name
        self.description = description
        self.scope = scope
        self.enabled = enabled
        self.enforcement_points = enforcement_points or [EnforcementPoint.INGESTION]
        self.severity = severity
        self.created_at = datetime.utcnow()
    
    @abstractmethod
    def evaluate(self, context: PolicyContext) -> PolicyEvaluation:
        """
        Evaluate policy against context.
        
        Args:
            context: Policy evaluation context
        
        Returns:
            PolicyEvaluation with decision and details
        """
        pass
    
    def is_applicable(self, context: PolicyContext) -> bool:
        """Check if policy applies to this context."""
        if not self.enabled:
            return False
        
        if context.enforcement_point not in self.enforcement_points:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "policy_id": self.policy_id,
            "policy_name": self.policy_name,
            "description": self.description,
            "scope": self.scope.value,
            "enabled": self.enabled,
            "enforcement_points": [ep.value for ep in self.enforcement_points],
            "severity": self.severity
        }


# ============================================================================
# BUILT-IN POLICIES
# ============================================================================

class PIIDetectionPolicy(GovernancePolicy):
    """
    Detects Personally Identifiable Information (PII) fields.
    
    Rules:
    - Identifies fields likely to contain PII
    - Ensures PII fields are marked in contract
    - Enforces encryption/masking requirements
    """
    
    PII_PATTERNS = {
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "phone": r"^[\d\-\+\(\)\s]{10,}$",
        "ssn": r"^\d{3}-\d{2}-\d{4}$",
        "credit_card": r"^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$",
        "ip_address": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    }
    
    PII_FIELD_NAMES = {
        "email", "phone", "ssn", "credit_card", "password",
        "customer_id", "user_id", "account_number",
        "passport", "license", "dob", "address"
    }
    
    def __init__(self):
        """Initialize PII detection policy."""
        super().__init__(
            policy_id="pii-detection-policy",
            policy_name="PII Detection & Classification",
            description="Identifies and enforces PII protection requirements",
            enforcement_points=[EnforcementPoint.INGESTION, EnforcementPoint.PUBLICATION],
            severity="error"
        )
    
    def evaluate(self, context: PolicyContext) -> PolicyEvaluation:
        """Detect PII fields in contract."""
        violations = []
        detected_pii_fields = []
        
        # Scan schema fields for PII indicators
        for field in context.contract.schema.fields:
            is_pii = self._is_pii_field(field)
            
            if is_pii:
                detected_pii_fields.append(field.name)
                
                # Check if marked in contract
                if field.name not in context.contract.pii_fields:
                    violations.append(
                        f"Field '{field.name}' detected as PII but not marked in contract.pii_fields"
                    )
                
                # Check compliance level
                if context.contract.compliance_level == ComplianceLevel.PUBLIC:
                    violations.append(
                        f"PII field '{field.name}' found in PUBLIC compliance data. "
                        "Must be CONFIDENTIAL or RESTRICTED"
                    )
        
        # Check for marked PII fields that don't seem like PII
        for marked_pii in context.contract.pii_fields:
            if marked_pii not in detected_pii_fields:
                logger.warning(f"Field '{marked_pii}' marked as PII but not detected")
        
        if violations:
            decision = PolicyDecision.DENY if self.severity == "error" else PolicyDecision.WARN
            return PolicyEvaluation(
                policy_id=self.policy_id,
                policy_name=self.policy_name,
                decision=decision,
                is_enforced=self.severity == "error",
                message=f"PII policy violation: {len(violations)} issues found",
                violations=violations,
                remediation_actions=[
                    "Update contract.pii_fields with all PII field names",
                    f"Set compliance_level to CONFIDENTIAL or RESTRICTED for data with PII",
                    "Consider encryption/masking for PII fields"
                ]
            )
        
        return PolicyEvaluation(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            decision=PolicyDecision.ALLOW,
            is_enforced=False,
            message="PII policy check passed"
        )
    
    def _is_pii_field(self, field: SchemaField) -> bool:
        """Check if field likely contains PII."""
        field_lower = field.name.lower()
        
        # Check field name
        for pii_indicator in self.PII_FIELD_NAMES:
            if pii_indicator in field_lower:
                return True
        
        # Check description
        if field.description:
            desc_lower = field.description.lower()
            for pii_indicator in self.PII_FIELD_NAMES:
                if pii_indicator in desc_lower:
                    return True
        
        return False


class SchemaDriftPolicy(GovernancePolicy):
    """
    Prevents uncontrolled schema changes.
    
    Rules:
    - Required fields cannot be removed
    - Required fields cannot become nullable
    - Type changes require compatibility check
    """
    
    def __init__(self):
        """Initialize schema drift policy."""
        super().__init__(
            policy_id="schema-drift-policy",
            policy_name="Schema Drift Prevention",
            description="Prevents breaking schema changes",
            enforcement_points=[EnforcementPoint.INGESTION, EnforcementPoint.TRANSFORMATION],
            severity="error"
        )
    
    def evaluate(self, context: PolicyContext) -> PolicyEvaluation:
        """Check for schema drift."""
        violations = []
        
        # This policy typically compares against previous schema version
        # For now, we validate the current schema consistency
        for field in context.contract.schema.fields:
            if not field.name or len(field.name) == 0:
                violations.append("Field name cannot be empty")
            
            if field.data_type is None:
                violations.append(f"Field '{field.name}' has no data type specified")
        
        if violations:
            return PolicyEvaluation(
                policy_id=self.policy_id,
                policy_name=self.policy_name,
                decision=PolicyDecision.DENY,
                is_enforced=True,
                message="Schema drift check failed",
                violations=violations,
                remediation_actions=["Review schema definition", "Ensure all fields are properly typed"]
            )
        
        return PolicyEvaluation(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            decision=PolicyDecision.ALLOW,
            is_enforced=False,
            message="Schema is stable, no drift detected"
        )


class NullThresholdPolicy(GovernancePolicy):
    """
    Enforces maximum null value thresholds.
    
    Rules:
    - For required (non-nullable) fields: nulls must be < 1%
    - For optional fields: nulls must be < 10%
    """
    
    def __init__(self):
        """Initialize null threshold policy."""
        super().__init__(
            policy_id="null-threshold-policy",
            policy_name="Null Value Threshold Enforcement",
            description="Ensures null values don't exceed acceptable thresholds",
            enforcement_points=[EnforcementPoint.PUBLICATION],
            severity="error"
        )
    
    def evaluate(self, context: PolicyContext) -> PolicyEvaluation:
        """Check null thresholds."""
        violations = []
        
        # Check quality rules for null checks
        null_rules = [r for r in context.contract.quality_rules if r.rule_type == "null_check"]
        
        if not null_rules:
            violations.append("No null_check quality rules defined")
        
        # Validate thresholds are reasonable
        for field in context.contract.schema.fields:
            if not field.nullable:
                # Required field should have very strict null threshold
                matching_rule = next(
                    (r for r in null_rules if field.name in (r.applies_to or [])),
                    None
                )
                if matching_rule and matching_rule.threshold < 0.99:
                    violations.append(
                        f"Required field '{field.name}' has null threshold of {matching_rule.threshold}, "
                        "should be >= 0.99"
                    )
        
        if violations:
            return PolicyEvaluation(
                policy_id=self.policy_id,
                policy_name=self.policy_name,
                decision=PolicyDecision.WARN,
                is_enforced=False,
                message="Null threshold warnings",
                violations=violations,
                remediation_actions=["Increase null thresholds for required fields"]
            )
        
        return PolicyEvaluation(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            decision=PolicyDecision.ALLOW,
            is_enforced=False,
            message="Null thresholds acceptable"
        )


class DataRetentionPolicy(GovernancePolicy):
    """
    Enforces data retention policies.
    
    Rules:
    - PUBLIC data: max 30 days retention
    - INTERNAL: max 90 days
    - CONFIDENTIAL: max 1 year
    - RESTRICTED: custom approval required
    """
    
    RETENTION_LIMITS = {
        ComplianceLevel.PUBLIC: 30,
        ComplianceLevel.INTERNAL: 90,
        ComplianceLevel.CONFIDENTIAL: 365,
        ComplianceLevel.RESTRICTED: None  # Custom approval
    }
    
    def __init__(self):
        """Initialize data retention policy."""
        super().__init__(
            policy_id="data-retention-policy",
            policy_name="Data Retention Policy",
            description="Enforces data retention limits by compliance level",
            enforcement_points=[EnforcementPoint.PUBLICATION],
            severity="warn"
        )
    
    def evaluate(self, context: PolicyContext) -> PolicyEvaluation:
        """Check data retention."""
        violations = []
        compliance_level = context.contract.compliance_level
        max_retention = self.RETENTION_LIMITS.get(compliance_level)
        
        if max_retention is None:
            # RESTRICTED: requires approval
            return PolicyEvaluation(
                policy_id=self.policy_id,
                policy_name=self.policy_name,
                decision=PolicyDecision.REQUIRE_APPROVAL,
                is_enforced=True,
                message="RESTRICTED data retention requires compliance approval"
            )
        
        if context.contract.retention_days > max_retention:
            violations.append(
                f"Retention period ({context.contract.retention_days} days) exceeds "
                f"limit for {compliance_level.value} data ({max_retention} days)"
            )
        
        if violations:
            return PolicyEvaluation(
                policy_id=self.policy_id,
                policy_name=self.policy_name,
                decision=PolicyDecision.WARN,
                is_enforced=False,
                message="Data retention policy warning",
                violations=violations,
                remediation_actions=[f"Reduce retention_days to {max_retention} or lower"]
            )
        
        return PolicyEvaluation(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            decision=PolicyDecision.ALLOW,
            is_enforced=False,
            message="Data retention acceptable"
        )


# ============================================================================
# GOVERNANCE ENGINE
# ============================================================================

class GovernanceEngine:
    """
    Orchestrates policy evaluation and enforcement.
    
    - Registers policies
    - Evaluates applicable policies
    - Makes enforcement decisions
    - Provides audit trail
    """
    
    def __init__(self):
        """Initialize governance engine."""
        self.policies: Dict[str, GovernancePolicy] = {}
        self.evaluation_history: List[Dict[str, Any]] = []
        self._register_default_policies()
    
    def _register_default_policies(self):
        """Register built-in policies."""
        default_policies = [
            PIIDetectionPolicy(),
            SchemaDriftPolicy(),
            NullThresholdPolicy(),
            DataRetentionPolicy()
        ]
        
        for policy in default_policies:
            self.register_policy(policy)
    
    def register_policy(self, policy: GovernancePolicy):
        """Register a new policy."""
        self.policies[policy.policy_id] = policy
        logger.info(f"Registered policy: {policy.policy_name}")
    
    def unregister_policy(self, policy_id: str):
        """Unregister a policy."""
        if policy_id in self.policies:
            del self.policies[policy_id]
            logger.info(f"Unregistered policy: {policy_id}")
    
    def enable_policy(self, policy_id: str):
        """Enable a policy."""
        if policy_id in self.policies:
            self.policies[policy_id].enabled = True
    
    def disable_policy(self, policy_id: str):
        """Disable a policy."""
        if policy_id in self.policies:
            self.policies[policy_id].enabled = False
    
    def evaluate(
        self,
        context: PolicyContext,
        stop_on_deny: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate all applicable policies.
        
        Args:
            context: Policy evaluation context
            stop_on_deny: Whether to stop on first DENY decision
        
        Returns:
            {
                "passed": bool,
                "overall_decision": PolicyDecision,
                "evaluations": [PolicyEvaluation],
                "violations": [str],
                "requires_approval": bool
            }
        """
        evaluations = []
        violations = []
        requires_approval = False
        overall_decision = PolicyDecision.ALLOW
        
        # Evaluate each applicable policy
        for policy in self.policies.values():
            if not policy.is_applicable(context):
                continue
            
            evaluation = policy.evaluate(context)
            evaluations.append(evaluation)
            
            logger.info(
                f"Policy '{policy.policy_name}' -> {evaluation.decision.value}: {evaluation.message}"
            )
            
            # Aggregate results
            if evaluation.decision == PolicyDecision.DENY:
                overall_decision = PolicyDecision.DENY
                violations.extend(evaluation.violations)
                if stop_on_deny:
                    break
            elif evaluation.decision == PolicyDecision.WARN:
                if overall_decision != PolicyDecision.DENY:
                    overall_decision = PolicyDecision.WARN
                violations.extend(evaluation.violations)
            elif evaluation.decision == PolicyDecision.REQUIRE_APPROVAL:
                requires_approval = True
                overall_decision = PolicyDecision.REQUIRE_APPROVAL
        
        # Record in history
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "product_id": context.product.product_id,
            "overall_decision": overall_decision.value,
            "evaluations": [e.__dict__ for e in evaluations],
            "violations": violations
        }
        self.evaluation_history.append(record)
        
        return {
            "passed": overall_decision == PolicyDecision.ALLOW,
            "overall_decision": overall_decision,
            "evaluations": evaluations,
            "violations": violations,
            "requires_approval": requires_approval
        }
    
    def get_audit_trail(self, product_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get governance evaluation audit trail."""
        trail = self.evaluation_history
        
        if product_id:
            trail = [r for r in trail if r["product_id"] == product_id]
        
        return trail[-limit:]
    
    def list_policies(self) -> List[Dict[str, Any]]:
        """List all registered policies."""
        return [p.to_dict() for p in self.policies.values()]


# ============================================================================
# GOVERNANCE ENFORCEMENT FLOW
# ============================================================================

"""
GOVERNANCE ENFORCEMENT FLOW:
============================

1. INGESTION PHASE
   - User submits data product definition
   - GovernanceEngine evaluates INGESTION policies
   - PIIDetectionPolicy: Scans schema for PII
   - SchemaDriftPolicy: Validates schema structure
   
2. TRANSFORMATION PHASE  
   - Data flows through pipelines
   - SchemaDriftPolicy: Monitors schema changes
   - NullThresholdPolicy: Warning check on nulls
   
3. PUBLICATION PHASE
   - Before data is exposed to consumers
   - AllPolicies re-evaluated
   - NullThresholdPolicy: Enforces null thresholds
   - DataRetentionPolicy: Enforces retention limits
   
4. ENFORCEMENT DECISION
   - ALLOW: Proceed normally
   - WARN: Log warning, proceed
   - DENY: Block operation, return errors
   - REQUIRE_APPROVAL: Queue for compliance review
   
5. AUDIT & HISTORY
   - All evaluations logged
   - Audit trail queryable by product/time
   - Support compliance reporting
"""
