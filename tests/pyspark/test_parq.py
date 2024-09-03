import sys
sys.path.append('/workspaces/PyDataShred/')

from datashredpy.utilities.init_spark import SparkSessionOption


def test_read_parquet():
    # spark = SparkSessionOption.get_spark_session()
    spark = SparkSessionOption.get_spark_instance()
    df=spark.read.parquet('tests_data/MT cars.parquet')
    print(df.show(999))

if __name__=='__main__':
    test_read_parquet()
    input()
