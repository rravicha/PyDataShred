import sys
sys.path.append('/workspaces/PyDataShred/')
import numpy as np
 
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
         try:
            assert True, 'first'
            assert 7 == 7, 'second'
            assert 1 == 1, 'third'
            assert list(df.columns) == ['empid', 'empname', 'salary'], 'fifth'
            assert df.count() == 6, 'sixth'  # Use df.count() for number of rows
            assert df.filter(df.empname == 'Aditya').count() == 1, 'seventh'  # Use filter for specific value check
         except AssertionError as e:
            print(f'Assertion failed at the {str(e)} line')
            exit(1)

 
if __name__=='__main__':
 
    test_read_json()
    # input()