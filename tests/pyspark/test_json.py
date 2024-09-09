import sys
sys.path.append('/workspaces/PyDataShred/')
 
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType

csv_path= 'tests_data/emp.csv'
#json_path='tests_data/emp_pyspark.json'
# pytest fixtures
def test_read_json():
    # spark = SparkSessionOption.get_spark_session()~
    # spark = SparkSessionOption.get_spark_instance()
    # df=spark.read.parquet('tests_data/MT cars.parquet')
    
    

    df = Data.read(csv_path, FileType.JSON)
    

    if df is None:
        print("df creation failed")
    else:

         df.show(999)
 
if __name__=='__main__':
 
    test_read_json()
    # input()