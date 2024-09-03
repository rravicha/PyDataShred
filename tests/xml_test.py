import sys
sys.path.append('/workspaces/PyDataShred')

import pytest
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
import pandas as pd
import numpy as np
def test_read_xml():
    df = Data.read('tests_data/emp_xml.xml', FileType.XML)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['emp_id','name','department','salary']
    assert df.shape == (3, 4)
    
    assert df.loc[0, 'name'] == 'John Doe'
    print(df.loc[0,'salary'])
    assert int(df.loc[0, 'salary']) == 50000


if __name__=='__main__':
    test_read_xml()