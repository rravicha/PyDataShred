"""
Schema Validation & Quality Enforcement Engine
==============================================
Validates data against DataProduct contracts at runtime.
- Schema validation
- Quality rule enforcement
- Backward compatibility checks
"""

import os
import sys
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime
import logging

if os.uname().nodename == 'zebronics':
    sys.path.append('/home/susi/workspace/github/PyDataShred')
else:
    sys.path.append('/workspaces/PyDataShred')

from datashredpy.datamesh.models import (
    DataProductContract,
    Schema,
    SchemaField,
    DataQualityRule,
    DataType
)

logger = logging.getLogger(__name__)


# ============================================================================
# SCHEMA VALIDATOR
# ============================================================================

class SchemaValidator:
    """Validates data against schema contracts."""
    
    def __init__(self, schema: Schema):
        """Initialize with a schema."""
        self.schema = schema
        self.field_map = {f.name: f for f in schema.fields}
    
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a single record against schema.
        
        Args:
            record: Dictionary representing a row/record
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for missing required fields
        for field in self.schema.fields:
            if field.name not in record:
                if not field.nullable:
                    errors.append(f"Required field '{field.name}' is missing")
                continue
            
            value = record[field.name]
            
            # Check null for non-nullable fields
            if value is None and not field.nullable:
                errors.append(f"Field '{field.name}' cannot be null")
                continue
            
            # Skip further checks if null and nullable
            if value is None:
                continue
            
            # Type validation
            type_error = self._validate_type(field.name, value, field.data_type)
            if type_error:
                errors.append(type_error)
            
            # Constraint validation
            if field.constraints:
                constraint_errors = self._validate_constraints(field.name, value, field.constraints)
                errors.extend(constraint_errors)
        
        # Check for extra fields
        for field_name in record:
            if field_name not in self.field_map:
                logger.warning(f"Extra field '{field_name}' not in schema")
        
        return len(errors) == 0, errors
    
    def _validate_type(self, field_name: str, value: Any, expected_type: DataType) -> Optional[str]:
        """Validate value type."""
        type_map = {
            DataType.STRING: (str,),
            DataType.INTEGER: (int,),
            DataType.FLOAT: (float, int),  # int can convert to float
            DataType.BOOLEAN: (bool,),
            DataType.TIMESTAMP: (str, datetime),
            DataType.DATE: (str,),
            DataType.BINARY: (bytes,),
            DataType.DECIMAL: (float, int, str),
            DataType.ARRAY: (list,),
            DataType.STRUCT: (dict,),
        }
        
        allowed_types = type_map.get(expected_type, ())
        if not isinstance(value, allowed_types):
            return f"Field '{field_name}': expected {expected_type.value}, got {type(value).__name__}"
        
        return None
    
    def _validate_constraints(self, field_name: str, value: Any, constraints: Dict[str, Any]) -> List[str]:
        """Validate field constraints."""
        errors = []
        
        # Range checks
        if "min" in constraints and value < constraints["min"]:
            errors.append(f"Field '{field_name}': value {value} below minimum {constraints['min']}")
        
        if "max" in constraints and value > constraints["max"]:
            errors.append(f"Field '{field_name}': value {value} exceeds maximum {constraints['max']}")
        
        # Pattern (regex) check
        if "pattern" in constraints:
            import re
            pattern = constraints["pattern"]
            if not re.match(pattern, str(value)):
                errors.append(f"Field '{field_name}': value '{value}' does not match pattern {pattern}")
        
        # Enum check
        if "enum" in constraints:
            allowed = constraints["enum"]
            if value not in allowed:
                errors.append(f"Field '{field_name}': value '{value}' not in allowed values {allowed}")
        
        return errors
    
    def validate_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate batch of records.
        
        Returns:
            {
                "total_records": int,
                "valid_records": int,
                "invalid_records": int,
                "error_summary": {field_name: [errors]}
            }
        """
        results = {
            "total_records": len(records),
            "valid_records": 0,
            "invalid_records": 0,
            "error_summary": {}
        }
        
        for record in records:
            is_valid, errors = self.validate_record(record)
            
            if is_valid:
                results["valid_records"] += 1
            else:
                results["invalid_records"] += 1
                for error in errors:
                    if error not in results["error_summary"]:
                        results["error_summary"][error] = 0
                    results["error_summary"][error] += 1
        
        return results


# ============================================================================
# QUALITY RULE ENGINE
# ============================================================================

class QualityRuleEngine:
    """Enforces data quality rules on datasets."""
    
    def __init__(self, contract: DataProductContract):
        """Initialize with a contract."""
        self.contract = contract
        self.rules = [r for r in contract.quality_rules if r.enabled]
    
    def evaluate_rules(self, df) -> Dict[str, Any]:
        """
        Evaluate all rules against a DataFrame.
        Supports both PySpark and Pandas DataFrames.
        
        Args:
            df: PySpark DataFrame or Pandas DataFrame
        
        Returns:
            {
                "passed": bool,
                "rules_evaluated": int,
                "rules_passed": int,
                "rules_failed": int,
                "details": {rule_id: {status, pass_rate, message}}
            }
        """
        results = {
            "passed": True,
            "rules_evaluated": len(self.rules),
            "rules_passed": 0,
            "rules_failed": 0,
            "details": {}
        }
        
        for rule in self.rules:
            rule_result = self._evaluate_rule(df, rule)
            results["details"][rule.rule_id] = rule_result
            
            if rule_result["status"] == "PASSED":
                results["rules_passed"] += 1
            else:
                results["rules_failed"] += 1
                results["passed"] = False
        
        return results
    
    def _evaluate_rule(self, df, rule: DataQualityRule) -> Dict[str, Any]:
        """Evaluate a single rule."""
        try:
            # Detect framework (PySpark vs Pandas)
            is_spark = hasattr(df, "select")  # PySpark has select method
            
            if rule.rule_type == "null_check":
                return self._check_nulls(df, rule, is_spark)
            elif rule.rule_type == "uniqueness":
                return self._check_uniqueness(df, rule, is_spark)
            elif rule.rule_type == "range":
                return self._check_range(df, rule, is_spark)
            elif rule.rule_type == "pattern":
                return self._check_pattern(df, rule, is_spark)
            elif rule.rule_type == "custom":
                return self._check_custom(df, rule, is_spark)
            else:
                return {"status": "UNKNOWN", "pass_rate": 0, "message": f"Unknown rule type: {rule.rule_type}"}
        
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.rule_id}: {str(e)}")
            return {"status": "ERROR", "pass_rate": 0, "message": str(e)}
    
    def _check_nulls(self, df, rule: DataQualityRule, is_spark: bool) -> Dict[str, Any]:
        """Check for null values."""
        fields = rule.applies_to or [f.name for f in self.contract.schema.fields]
        
        if is_spark:
            total = df.count()
            non_null_count = df.select([f for f in fields]).na.drop().count()
            pass_rate = non_null_count / total if total > 0 else 0
        else:
            total = len(df)
            non_null_count = df[fields].notna().all(axis=1).sum()
            pass_rate = non_null_count / total if total > 0 else 0
        
        status = "PASSED" if pass_rate >= rule.threshold else "FAILED"
        return {
            "status": status,
            "pass_rate": pass_rate,
            "threshold": rule.threshold,
            "message": f"Null check on {fields}: {pass_rate:.2%} passed (threshold: {rule.threshold:.2%})"
        }
    
    def _check_uniqueness(self, df, rule: DataQualityRule, is_spark: bool) -> Dict[str, Any]:
        """Check for unique values."""
        fields = rule.applies_to or []
        
        if not fields:
            return {"status": "FAILED", "pass_rate": 0, "message": "No fields specified for uniqueness check"}
        
        if is_spark:
            total = df.count()
            distinct = df.select(*fields).distinct().count()
            pass_rate = distinct / total if total > 0 else 0
        else:
            total = len(df)
            distinct = df[fields].drop_duplicates().shape[0]
            pass_rate = distinct / total if total > 0 else 0
        
        status = "PASSED" if pass_rate >= rule.threshold else "FAILED"
        return {
            "status": status,
            "pass_rate": pass_rate,
            "threshold": rule.threshold,
            "message": f"Uniqueness check on {fields}: {pass_rate:.2%} unique (threshold: {rule.threshold:.2%})"
        }
    
    def _check_range(self, df, rule: DataQualityRule, is_spark: bool) -> Dict[str, Any]:
        """Check value ranges."""
        # Simplified: assumes numeric fields
        fields = rule.applies_to or []
        if not fields:
            return {"status": "FAILED", "pass_rate": 0, "message": "No fields specified for range check"}
        
        field = fields[0]
        schema_field = next((f for f in self.contract.schema.fields if f.name == field), None)
        
        if not schema_field or not schema_field.constraints:
            return {"status": "FAILED", "pass_rate": 0, "message": f"No range constraints for {field}"}
        
        min_val = schema_field.constraints.get("min")
        max_val = schema_field.constraints.get("max")
        
        if is_spark:
            total = df.count()
            if min_val is not None and max_val is not None:
                valid = df.filter((df[field] >= min_val) & (df[field] <= max_val)).count()
            elif min_val is not None:
                valid = df.filter(df[field] >= min_val).count()
            else:
                valid = df.filter(df[field] <= max_val).count()
            pass_rate = valid / total if total > 0 else 0
        else:
            total = len(df)
            if min_val is not None and max_val is not None:
                valid = ((df[field] >= min_val) & (df[field] <= max_val)).sum()
            elif min_val is not None:
                valid = (df[field] >= min_val).sum()
            else:
                valid = (df[field] <= max_val).sum()
            pass_rate = valid / total if total > 0 else 0
        
        status = "PASSED" if pass_rate >= rule.threshold else "FAILED"
        return {
            "status": status,
            "pass_rate": pass_rate,
            "threshold": rule.threshold,
            "message": f"Range check on {field}: {pass_rate:.2%} in range [{min_val}, {max_val}]"
        }
    
    def _check_pattern(self, df, rule: DataQualityRule, is_spark: bool) -> Dict[str, Any]:
        """Check pattern (regex) matching."""
        import re
        fields = rule.applies_to or []
        if not fields:
            return {"status": "FAILED", "pass_rate": 0, "message": "No fields specified for pattern check"}
        
        field = fields[0]
        schema_field = next((f for f in self.contract.schema.fields if f.name == field), None)
        
        if not schema_field or not schema_field.constraints or "pattern" not in schema_field.constraints:
            return {"status": "FAILED", "pass_rate": 0, "message": f"No pattern constraint for {field}"}
        
        pattern = schema_field.constraints["pattern"]
        
        if is_spark:
            total = df.count()
            valid = df.filter(df[field].rlike(pattern)).count()
            pass_rate = valid / total if total > 0 else 0
        else:
            total = len(df)
            valid = df[field].astype(str).str.match(pattern).sum()
            pass_rate = valid / total if total > 0 else 0
        
        status = "PASSED" if pass_rate >= rule.threshold else "FAILED"
        return {
            "status": status,
            "pass_rate": pass_rate,
            "threshold": rule.threshold,
            "message": f"Pattern check on {field}: {pass_rate:.2%} matches pattern {pattern}"
        }
    
    def _check_custom(self, df, rule: DataQualityRule, is_spark: bool) -> Dict[str, Any]:
        """Evaluate custom logic."""
        if not rule.custom_logic:
            return {"status": "FAILED", "pass_rate": 0, "message": "No custom logic provided"}
        
        try:
            # For Spark: use SQL expression
            if is_spark:
                df.createOrReplaceTempView("temp_data")
                result_df = df.sparkSession.sql(f"SELECT * FROM temp_data WHERE {rule.custom_logic}")
                valid = result_df.count()
                total = df.count()
                pass_rate = valid / total if total > 0 else 0
            else:
                # For Pandas: evaluate expression
                valid = df.eval(rule.custom_logic).sum()
                total = len(df)
                pass_rate = valid / total if total > 0 else 0
            
            status = "PASSED" if pass_rate >= rule.threshold else "FAILED"
            return {
                "status": status,
                "pass_rate": pass_rate,
                "threshold": rule.threshold,
                "message": f"Custom rule: {pass_rate:.2%} records passed (threshold: {rule.threshold:.2%})"
            }
        except Exception as e:
            return {"status": "ERROR", "pass_rate": 0, "message": f"Custom logic error: {str(e)}"}


# ============================================================================
# CONTRACT VALIDATOR
# ============================================================================

class ContractValidator:
    """Validates data against a complete contract."""
    
    def __init__(self, contract: DataProductContract):
        """Initialize with a contract."""
        self.contract = contract
        self.schema_validator = SchemaValidator(contract.schema)
        self.quality_engine = QualityRuleEngine(contract)
    
    def validate_data(self, df, validate_schema: bool = True, validate_quality: bool = True) -> Dict[str, Any]:
        """
        Validate data against full contract.
        
        Args:
            df: PySpark or Pandas DataFrame
            validate_schema: Whether to validate schema
            validate_quality: Whether to validate quality rules
        
        Returns:
            Complete validation report
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "contract_id": self.contract.contract_id,
            "overall_passed": True,
            "schema_validation": None,
            "quality_validation": None
        }
        
        if validate_schema:
            # Convert DataFrame to records for schema validation
            if hasattr(df, "collect"):  # PySpark
                records = df.collect()
                records = [row.asDict() for row in records]
            else:  # Pandas
                records = df.to_dict('records')
            
            report["schema_validation"] = self.schema_validator.validate_batch(records)
            if report["schema_validation"]["invalid_records"] > 0:
                report["overall_passed"] = False
        
        if validate_quality:
            report["quality_validation"] = self.quality_engine.evaluate_rules(df)
            if not report["quality_validation"]["passed"]:
                report["overall_passed"] = False
        
        return report
    
    def check_backward_compatibility(self, old_contract: DataProductContract) -> Tuple[bool, List[str]]:
        """
        Check if new contract is backward compatible with old contract.
        
        Args:
            old_contract: Previous contract version
        
        Returns:
            (is_compatible, list_of_issues)
        """
        return self.contract.schema.is_compatible_with(old_contract.schema)
