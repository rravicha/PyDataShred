import sys

sys.path.append('/workspaces/PyDataShred')
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
import pandas as pd
from deltalake import DeltaTable
 
 
def read_delta_file_to_dataframe(delta_file_path: r"tests_data/emp_delta_format/employee_data") -> pd.DataFrame:
    delta_file = DeltaTable(delta_file_path)
    df = delta_file.to_pandas()
    return df
 

def delta_file_func():
    delta_file_path = r"tests_data/emp_delta_format/employee_data"
    # Read the Delta Lake table and get the DataFrame
    df = read_delta_file_to_dataframe(delta_file_path)
    # Print the DataFrame
    print(df)
    #assert statements for testing
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['empid','empname','salary']
    assert df.shape == (6, 3)
    assert df.loc[0, 'empid'] == 1
    assert df.loc[5,'empname'] == 'Hitesh'

if __name__ == "__main__":
    delta_file_func()

