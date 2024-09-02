import sys
sys.path.append('/workspaces/PyDataShred')

import pytest
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
import pandas as pd
import numpy as np
def test_read_tsv():
    df = Data.read('tests_data/emp.tsv', FileType.TSV,sep = '\t')
    print(df.shape)
    # assert isinstance(df, pd.DataFrame)
    # print (list(df.columns))
    # assert list(df.columns) == ['empid','empname','salary']
    # assert df.shape == (6, 3)
    # assert df.loc[0, 'empid'] == 1
    # assert df.loc[2,'empname'] == 'Aditya'

if __name__=='__main__':
    test_read_tsv()