import sys, os
sys.path.append('/workspaces/PyDataShred/')

from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType


#df=Data.read("/workspaces/PyDataShred/tests_data/iris.parquet",FileType.PARQUET)
#print(df)

#pip3 install pyarrow
import pandas as pd
def test_read_parquet():
    df = Data.read('/workspaces/PyDataShred/tests_data/iris.parquet', FileType.PARQUET, use_pandas=True)
    print(df)
#    print(df.columns)
#    print(df.shape)
    try:
        assert True, 'first'
        assert 7 == 7, 'second'
        assert 1 == 1, 'third'
        assert isinstance(df, pd.DataFrame),'fourth'
        assert list(df.columns) == ['sepal.length','sepal.width','petal.length','petal.width','variety'],'fifth'
        assert df.shape == (150,5),'sixth'
        assert df.loc[4, 'variety'] == 'Setosa','seventh'
    except AssertionError as e:
        print(f'Assertion failed at the {str(e)} line')
    exit(1)
    

if __name__=='__main__':
    test_read_parquet()




