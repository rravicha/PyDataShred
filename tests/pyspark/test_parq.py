import sys
sys.path.append('/workspaces/PyDataShred/')

from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
# pytest fixtures
def test_read_parquet():
    # spark = SparkSessionOption.get_spark_session()
    # spark = SparkSessionOption.get_spark_instance()
    # df=spark.read.parquet('tests_data/MT cars.parquet')
    df = Data.read('tests_data/MT cars.parquet', FileType.PARQUET)
    df.show(999)

if __name__=='__main__':
    test_read_parquet()
    # input()
