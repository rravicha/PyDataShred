import sys
sys.path.append('/workspaces/PyDataShred/')
# sys.path.append('/workspaces/PyDataShred/tests_data/HATCHBACK')

from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
# pytest fixtures
def test_read_parquet():
    print('reading...')
    df = Data.read('/workspaces/PyDataShred/tests_data/HATCHBACK/cars.parquet', FileType.PARQUET)
    print('showing....')
    df.show(999)
    print('ending...')

if __name__=='__main__':
    test_read_parquet()
