from dataclasses import dataclass
from typing import List, Union, Optional
from datetime import datetime
from pydantic import BaseModel, validator
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    current_timestamp, 
    lit, 
    when, 
    col
)

class SparkDataFrameModel(BaseModel):
    """Pydantic model for validating PySpark DataFrame properties"""
    columns: List[str]
    is_empty: bool

    @validator('columns')
    def validate_required_columns(cls, columns):
        required_cols = ['start_date', 'end_date', 'etl_flag']
        if not all(col in columns for col in required_cols):
            raise ValueError(f"DataFrame must contain audit columns: {required_cols}")
        return columns

class ETLConfig(BaseModel):
    """Configuration model for ETL process"""
    key_columns: Union[str, List[str]]
    source_schema: Optional[List[str]] = None
    target_schema: Optional[List[str]] = None

    @validator('key_columns')
    def validate_key_columns(cls, v):
        if isinstance(v, str):
            return [v]
        return v

@dataclass
class ETL:
    source_df: DataFrame
    target_df: DataFrame
    key_columns: Union[str, List[str]]
    
    def __post_init__(self):
        # Validate configuration
        self.config = ETLConfig(key_columns=self.key_columns)
        self._validate_dataframes()
    
    def _validate_dataframes(self):
        """Validate DataFrame structures"""
        # Validate source DataFrame
        if not isinstance(self.source_df, DataFrame):
            raise ValueError("source_df must be a PySpark DataFrame")
            
        # Validate target DataFrame if not empty
        if not self.target_df.rdd.isEmpty():
            target_model = SparkDataFrameModel(
                columns=self.target_df.columns,
                is_empty=False
            )
            
    def apply_scd2(self) -> DataFrame:
        """
        Applies SCD Type 2 logic to merge source and target DataFrames
        Returns: DataFrame with SCD Type 2 implementation
        """
        # Add audit columns to source
        source_with_dates = self.source_df.withColumn(
            "start_date", current_timestamp()
        ).withColumn(
            "end_date", lit(None)
        ).withColumn(
            "etl_flag", lit("current")
        )
        
        if self.target_df.rdd.isEmpty():
            print("Initial load - returning source data with audit columns")
            source_with_dates.show()
            return source_with_dates
            
        # Find changed records
        join_condition = []
        for key in self.config.key_columns:
            join_condition.append(self.source_df[key] == self.target_df[key])
            
        changed_records = self.source_df.join(
            self.target_df,
            join_condition,
            "outer"
        ).filter(
            (col("source." + self.config.key_columns[0]).isNotNull()) &
            (
                (col("target." + self.config.key_columns[0]).isNull()) |
                (sum([when(col("source." + c) != col("target." + c), 1)
                     .otherwise(0) for c in self.source_df.columns 
                     if c not in self.config.key_columns]) > 0)
            )
        )
        
        # Update existing records
        updated_target = self.target_df.withColumn(
            "end_date",
            when(
                col(self.config.key_columns[0]).isin(
                    [r[0] for r in changed_records.select(self.config.key_columns[0]).collect()]
                ),
                current_timestamp()
            ).otherwise(col("end_date"))
        ).withColumn(
            "etl_flag",
            when(
                col(self.config.key_columns[0]).isin(
                    [r[0] for r in changed_records.select(self.config.key_columns[0]).collect()]
                ),
                "expired"
            ).otherwise(col("etl_flag"))
        )
        
        # Combine updated records
        final_df = updated_target.union(source_with_dates)
        
        print("Final DataFrame with SCD Type 2 implementation:")
        final_df.orderBy(self.config.key_columns + ["start_date"]).show()
        
        return final_df.orderBy(self.config.key_columns + ["start_date"])
