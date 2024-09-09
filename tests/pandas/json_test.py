import sys
sys.path.append('/workspaces/PyDataShred')

import pytest
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
import pandas as pd
import numpy as np
def test_read_json():
    df = Data.read('tests_data/emp.json', FileType.JSON)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['Emp_id','Emp_name','salary']
    assert df.shape == (4, 3)
    assert df.loc[0, 'Emp_id'] == 1
    assert df.loc[1,'Emp_name'] == 'Aditya'
    
    print(df)




if __name__=='__main__':
    test_read_json()