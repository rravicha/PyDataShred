import sys
sys.path.append('/workspaces/PyDataShred')

import pytest
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
import pandas as pd
import numpy as np
def test_read_xml():
    df = Data.read('tests_data/emp_xml.xml', FileType.XML)
    print (df)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['emp_id','name']
    assert df.shape == (3, 2)
    assert df.loc[0, 'emp_id'] == 1
    assert df.loc[1,'name'] == 'Jane Smith'
    print(pd.DataFrame)

if __name__=='__main__':
    test_read_xml()