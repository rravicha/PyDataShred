from aenum import Enum as AEnum, MultiValueEnum

class DbType(MultiValueEnum):
    SQLITE = ['sqlite' , 'sqlite3']
class FileType(MultiValueEnum):
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
    
class ConfigOptions:
    class Spark(MultiValueEnum):
        SPARK_EXECUTOR_MEMORY = "spark.executor.memory"
        SPARK_EXECUTOR_CORES = "spark.executor.cores"
        SPARK_DRIVER_MEMORY = "spark.driver.memory"
