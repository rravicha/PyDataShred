import sys
sys.path.append('/workspaces/PyDataShred/')

from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType, DbType
# pytest fixtures
def test_read_parquet():
    df = Data.read('tests_data/MT cars.parquet', DbType.SQLITE)
    print(df)
    # df.show(999)

if __name__=='__main__':
    test_read_parquet()
    # input()
