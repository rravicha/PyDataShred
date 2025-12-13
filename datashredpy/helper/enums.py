"""Enumerations for file types, database types, and configuration options."""
from aenum import Enum as AEnum, MultiValueEnum


class DbType(MultiValueEnum):
    """Supported database types."""
    pass
    
class FileType(MultiValueEnum):
    """Supported file formats."""
    CSV = 'csv'
    TXT = 'txt'
    TSV = 'tsv'
    JSON = 'json'
    PARQUET = 'parquet'
    DELTA = 'delta'
    EXCEL = 'xlsx'
    XML = 'xml'
    HTML = 'html'
    PDF = 'pdf'
    SNOWFLAKE = 'snowflake'


class ApiType:
    """API type constants."""
    DEFAULT_API = 'api'

    
class ConfigOptions:
    """Configuration options for various services."""
    
    class Spark(MultiValueEnum):
        """Spark configuration options."""
        SPARK_EXECUTOR_MEMORY = "spark.executor.memory"
        SPARK_EXECUTOR_CORES = "spark.executor.cores"
        SPARK_DRIVER_MEMORY = "spark.driver.memory"
