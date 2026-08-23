"""Data reading module for various file formats and data sources."""
import logging
from typing import Optional, List, Dict, Union

import pandas as pd
import requests
from snowflake.snowpark import Session
from pyspark.sql import DataFrame as SparkDataFrame

from datashredpy.utilities.init_spark import SparkSessionOption
from datashredpy.helper.enums import FileType, DbType, ApiType

logger = logging.getLogger(__name__)

class Data:
    """Data reader class supporting multiple file formats and data sources."""

    @classmethod
    def _read_csv_pandas(cls, rel_path: str, **options) -> pd.DataFrame:
        """Read CSV file using pandas."""
        return pd.read_csv(rel_path, **options)
    
    @classmethod
    def _read_json_pandas(cls, rel_path: str, **options) -> pd.DataFrame:
        """Read JSON file using pandas."""
        return pd.read_json(rel_path, **options)

    @classmethod
    def _read_xlsx_pandas(cls, rel_path: str, **options) -> pd.DataFrame:
        """Read Excel file using pandas."""
        return pd.read_excel(rel_path, engine='openpyxl')

    @classmethod
    def _read_parquet_pandas(cls, rel_path: str, **options) -> pd.DataFrame:
        """Read Parquet file using pandas."""
        return pd.read_parquet(rel_path)

    @classmethod
    def _read_xml_pandas(cls, rel_path: str, **options) -> pd.DataFrame:
        """Read XML file using ElementTree and pandas."""
        import xml.etree.ElementTree as ET
        
        tree = ET.parse(rel_path)
        root = tree.getroot()
        data = []
        for child in root:
            row = {}
            for elem in child:
                row[elem.tag] = elem.text
            data.append(row)
        return pd.DataFrame(data)

    @classmethod
    def _read_delta_pandas(cls, rel_path: str, **options) -> Optional[pd.DataFrame]:
        """Delta format reading not yet implemented for pandas."""
        logger.warning("Delta format reading not implemented for pandas backend")
        return None
    @classmethod
    def _read_csv_spark(cls, rel_path: str, **options) -> SparkDataFrame:
        """Read CSV file using Spark."""
        return cls.spark.read.option(
            "header", "true"
        ).option(
            "inferSchema", "true"
        ).csv(rel_path)
    
    @classmethod
    def _read_json_spark(cls, rel_path: str, **options) -> SparkDataFrame:
        """Read JSON file using Spark."""
        return cls.spark.read.json(rel_path)

    @classmethod
    def _read_xlsx_spark(cls, rel_path: str, **options) -> Optional[SparkDataFrame]:
        """Excel reading not implemented for Spark."""
        logger.warning("Excel format reading not implemented for Spark backend")
        return None
    
    @classmethod
    def _read_delta_spark(cls, rel_path: str, **options) -> SparkDataFrame:
        """Read Delta format using Spark."""
        return cls.spark.read.format("delta").load(rel_path)
   
    @classmethod
    def _read_parquet_spark(cls, rel_path: str, **options) -> SparkDataFrame:
        """Read Parquet file using Spark."""
        return cls.spark.read.parquet(rel_path)

    @classmethod
    def _read_xml_spark(cls, rel_path: str, **options) -> Optional[SparkDataFrame]:
        """XML reading not implemented for Spark."""
        logger.warning("XML format reading not implemented for Spark backend")
        return None

    @classmethod
    def _read_snowflake(cls, table_name: str, **snowpark_options) -> SparkDataFrame:
        """Read table from Snowflake using Snowpark."""
        return Session.builder.configs(snowpark_options).create().table(table_name)
    
    @classmethod
    def _read_api(cls, url: str, **options) -> List[Dict]:
        return requests.get(url).json()

    @classmethod
    def read(cls, rel_path: str, api_type: ApiType = None, file_type: FileType = None, db_type: DbType=None, use_pandas: Optional[bool] = False, use_spark: Optional[bool] = True, snowpark_options: Optional[dict] = False, **options):
        ''' Contains functions to read inbound using pandas and spark'''
        if api_type:
            if api_type == ApiType.DEFAULT_API:
                return cls._read_api(rel_path, **options)
            
        if db_type and db_type != DbType.SQLITE:
            logger.warning(f"Database type {db_type} not directly supported via read(). Use appropriate connector.")

        if use_pandas:
            if file_type == FileType.CSV:
                return cls._read_csv_pandas(rel_path, **options)
            if file_type==FileType.TSV:
                return cls._read_csv_pandas(rel_path, **options)
            if file_type ==FileType.JSON:
                return cls._read_json_pandas(rel_path, **options)
            if file_type == FileType.EXCEL:
                return cls._read_xlsx_pandas(rel_path, **options)
            if file_type == FileType.PARQUET:
                return cls._read_parquet_pandas(rel_path, **options)
            if file_type == FileType.DELTA:
                return cls._read_delta_pandas(rel_path, **options)
            if file_type == FileType.XML:
                return cls._read_xml_pandas(rel_path, **options)        
        
        if use_spark:
            
            cls.spark = SparkSessionOption.get_spark_instance()
            if file_type==FileType.SNOWFLAKE:
                return cls._read_snowflake(rel_path, **snowpark_options)
            if file_type==FileType.PARQUET:
                 return cls._read_parquet_spark(rel_path, **options)
            if file_type==FileType.CSV:
                return cls._read_csv_spark(rel_path, **options)
            if file_type==FileType.JSON:
                return cls._read_json_spark(rel_path, **options)
            if file_type==FileType.DELTA:
                delta_config ={
                    "spark.sql.extensions":"io.delta.sql.DeltaSparkSessionExtension"
                }
                cls.spark = SparkSessionOption.get_spark_instance(config_options=delta_config)
                return cls._read_delta_spark(rel_path, **options)

