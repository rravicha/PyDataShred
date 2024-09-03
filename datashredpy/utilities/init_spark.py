import sys
sys.path.append('/workspaces/PyDataShred')

from pyspark.sql import SparkSession
from datashredpy.helper.enums import Spark as SparkEnum

class SparkSessionOption:
    _instance = None
    @classmethod
    def get_spark_instance(cls, app_name="MyApp", master="local[*]", config_options=None):
        ''' gets you an spark instance that can be shared across your application'''
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
        SparkEnum.ConfigOptions.SPARK_EXECUTOR_MEMORY.value:"2g",
        SparkEnum.ConfigOptions.SPARK_EXECUTOR_CORES.value: "2",
        SparkEnum.ConfigOptions.SPARK_DRIVER_MEMORY.value: "1g"
    }
    # The below is example of how to initiate spark session in your own module
    # spark = SparkSessionSingleton.get_spark_session(config_options=config)
    spark = SparkSessionSingleton.get_spark_instance(config_options=config)
    print("Spark session created successfully!")
