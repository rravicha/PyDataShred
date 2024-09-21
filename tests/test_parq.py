import sys
sys.path.append('/workspace/PyDataShred')
from datashredpy.helper.data import Data
from datashredpy.helper.enums import FileType
from tests.enums import TestFilePath
# pytest fixtures
def test_read_parquet():
    df =  Data.read('tests_data/HATCHBACK/cars.parquet', FileType.PARQUET)
    df.show(999)

if __name__=='__main__':
    test_read_parquet()
