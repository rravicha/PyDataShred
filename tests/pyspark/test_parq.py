import sys, os
sys.path.append('/workspaces/PyDataShred/')

from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
from datashredpy.utilities.init_spark import SparkSessionOption


#df=Data.read("/workspaces/PyDataShred/tests_data/MT cars.parquet",FileType.PARQUET)
#print(df)

#pip3 install pyarrow
import pandas as pd
def test_read_parquet():
    # df = Data.read('/workspaces/PyDataShred/tests_data/MT cars.parquet', FileType.PARQUET)
    spark = SparkSessionOption.get_spark_session()
    df=spark.read.parquet('/workspaces/PyDataShred/tests_data/MT cars.parquet')
    print(df.show())
    input()
    # try:
    #     assert True, 'first'
    #     assert 7 == 7, 'second'
    #     assert 1 == 1, 'third'
    #     assert isinstance(df, pd.DataFrame),'fourth'
    #     assert list(df.columns) == ['model', 'mpg', 'cyl', 'disp', 'hp', 'drat', 'wt', 'qsec', 'vs', 'am',
    #    'gear', 'carb'],'fifth'
    #     assert df.shape == (32,12),'sixth'
    #     assert df.loc[17, 'model'] == 'Fiatt 128','seventh'
    # except AssertionError as e:
    #     print(f'Assertion failed at the {str(e)} line')
    # exit(1)
    

if __name__=='__main__':
    test_read_parquet()
