from typing import Optional, List, Dict
import pandas as Pandas
import requests
from datashredpy.utilities.init_spark import SparkSessionOption
from datashredpy.helper.enums import FileType, DbType, ApiType
from datashredpy.utilities.init_spark import SparkSessionOption

class Utils:

    @staticmethod
    def raw_json_to_pyspark(raw_api_data:List[Dict]=None):
        spark = spark = SparkSessionOption.get_spark_instance()
        from pyspark.sql import Row
        return spark.createDataFrame(Row(**x) for x in raw_api_data)
