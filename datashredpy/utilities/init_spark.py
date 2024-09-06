import sys
sys.path.append('/workspaces/PyDataShred')

from pyspark.sql import SparkSession
from datashredpy.helper.enums import ConfigOptions

class SparkSessionOption:
    _instance = None
    @classmethod
    def get_spark_instance(cls, app_name="MyApp", master="local[*]", config_options=None, snow_spark = False):
        ''' gets you an spark instance that can be shared across your application'''
        if snow_spark:
            config_options = {"spark.jars.packages" : "net.snowflake:spark-snowflake_2.12:2.9.0-spark_3.1"}
        if cls._instance is None:
            spark_builder = SparkSession.builder.appName(app_name).master(master)
            if config_options:
                for key, value in config_options.items():
                    spark_builder = spark_builder.config(key, value)
            cls._instance = spark_builder.getOrCreate()
        return cls._instance

    @staticmethod
    def get_spark_session(app_name="MyApp", master="local[*]", config_options=None):
        ''' gets you an spark session '''
        spark_builder = SparkSession.builder.appName(app_name).master(master)   
        if config_options:
            for key, value in config_options.items():
                spark_builder = spark_builder.config(key, value)
        spark_session = spark_builder.getOrCreate()
        return spark_session

if __name__ == "__main__":
    config = {
        ConfigOptions.Spark.SPARK_EXECUTOR_MEMORY.value:"2g",
        ConfigOptions.Spark.SPARK_EXECUTOR_CORES.value: "2",
        ConfigOptions.Spark.SPARK_DRIVER_MEMORY.value: "1g"
    }
    # The below is example of how to initiate spark session in your own module
    # spark = SparkSessionSingletopdatan.get_spark_session(config_options=config)
    spark = SparkSessionOption.get_spark_instance(config_options=config)
    print("Spark session created successfully!")
